from datetime import datetime, timedelta, timezone

from job.weibo_breaking_alerts import WeiboBreakingAlertMonitor
from service.qqbot_notify import NotifyOutcome
from service.weibo_alert_state import AlertEvent, AlertStateStore, EventStatus


class FakeClock:
    def __init__(self, now=datetime(2026, 8, 31, 9, tzinfo=timezone.utc)):
        self.now = now

    def __call__(self):
        return self.now

    def advance(self, delta):
        self.now += delta


class SnapshotFetcher:
    def __init__(self, snapshots):
        self._snapshots = snapshots
        self._index = 0

    def __call__(self):
        snapshot = self._snapshots[min(self._index, len(self._snapshots) - 1)]
        self._index += 1
        return snapshot


class FakeNotifier:
    def __init__(self, outcomes=()):
        self._outcomes = list(outcomes)
        self.contents = []

    def notify(self, content):
        self.contents.append(content)
        outcome = self._outcomes.pop(0) if self._outcomes else NotifyOutcome.DELIVERED
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


def item(title, rank=1, hot=0, tags=("爆",)):
    return {
        "title": title,
        "url": f"https://weibo.com/{title}",
        "rank": rank,
        "hot": hot,
        "tags": list(tags),
    }


def build_monitor(tmp_path, notifier, snapshots, clock=None, *, path=None):
    return WeiboBreakingAlertMonitor(
        SnapshotFetcher(snapshots),
        AlertStateStore(path or tmp_path / "alerts.sqlite3"),
        notifier,
        clock or FakeClock(),
    )


def test_first_snapshot_creates_baseline_without_notification(tmp_path):
    notifier = FakeNotifier()
    monitor = build_monitor(tmp_path, notifier, [[item("爆点")]])

    monitor.run_once()

    assert notifier.contents == []
    assert monitor._state_store.load_event("爆点").status is EventStatus.OBSERVED


def test_new_top_one_breaking_event_notifies_once_then_deduplicates(tmp_path):
    notifier = FakeNotifier()
    monitor = build_monitor(
        tmp_path,
        notifier,
        [[item("基线", rank=30, tags=())], [item("爆点", rank=1)], [item("爆点", rank=1)]],
    )

    monitor.run_once()
    monitor.run_once()
    monitor.run_once()

    assert len(notifier.contents) == 1
    assert notifier.contents[0].startswith("💥💥💥 微博突发爆点\n【爆点】")
    assert "排名：新上榜 → 第1" in notifier.contents[0]
    assert monitor._state_store.load_event("爆点").status is EventStatus.NOTIFIED


def test_daily_budget_suppresses_the_sixth_breaking_event(tmp_path):
    notifier = FakeNotifier()
    six_events = [item(f"爆点{index}", rank=1) for index in range(6)]
    monitor = build_monitor(tmp_path, notifier, [[item("基线", rank=30, tags=())], six_events])

    monitor.run_once()
    monitor.run_once()

    assert len(notifier.contents) == 5
    assert monitor._state_store.load_event("爆点5").status is EventStatus.SUPPRESSED_BY_BUDGET


def test_no_subscribers_is_terminal_and_does_not_consume_budget(tmp_path):
    notifier = FakeNotifier([NotifyOutcome.NO_SUBSCRIBERS])
    monitor = build_monitor(
        tmp_path,
        notifier,
        [[item("基线", rank=30, tags=())], [item("爆点")], [item("爆点")]],
    )

    monitor.run_once()
    monitor.run_once()
    monitor.run_once()

    assert len(notifier.contents) == 1
    assert monitor._state_store.load_event("爆点").status is EventStatus.NO_SUBSCRIBERS
    assert all(
        monitor._state_store.reserve_daily_delivery(monitor._clock(), f"补位{index}")
        for index in range(5)
    )


def test_notify_error_retries_exactly_once_then_becomes_terminal(tmp_path):
    notifier = FakeNotifier([RuntimeError("first"), RuntimeError("second")])
    monitor = build_monitor(
        tmp_path,
        notifier,
        [[item("基线", rank=30, tags=())], [item("爆点")], [item("爆点")], [item("爆点")]],
    )

    monitor.run_once()
    monitor.run_once()
    monitor.run_once()
    monitor.run_once()

    assert len(notifier.contents) == 2
    event = monitor._state_store.load_event("爆点")
    assert event.status is EventStatus.FAILED
    assert event.retry_count == 1


def test_completed_event_only_restarts_after_quiet_new_top_ten_appearance(tmp_path):
    notifier = FakeNotifier()
    clock = FakeClock()
    monitor = build_monitor(
        tmp_path,
        notifier,
        [
            [item("事件", rank=1, tags=())],
            [item("事件", rank=2, tags=())],
            [item("事件", rank=3, tags=())],
            [item("事件", rank=1, tags=("爆",))],
            [],
            [item("事件", rank=1, tags=("爆",))],
        ],
        clock,
    )

    monitor.run_once()
    monitor.run_once()
    monitor.run_once()
    assert monitor._state_store.load_event("事件").status is EventStatus.COMPLETED

    clock.advance(timedelta(hours=12))
    monitor.run_once()  # Still in the preceding full snapshot, so not a new appearance.
    assert monitor._state_store.load_event("事件").round_id == 1
    monitor.run_once()
    monitor.run_once()

    event = monitor._state_store.load_event("事件")
    assert event.round_id == 2
    assert event.status is EventStatus.NOTIFIED
    assert len(notifier.contents) == 1


def test_reloaded_snapshot_prevents_existing_item_from_being_treated_as_new(tmp_path):
    path = tmp_path / "alerts.sqlite3"
    first_notifier = FakeNotifier()
    first = build_monitor(
        tmp_path,
        first_notifier,
        [[item("已在榜", rank=1, tags=("新",))]],
        path=path,
    )
    first.run_once()

    second_notifier = FakeNotifier()
    second = build_monitor(
        tmp_path,
        second_notifier,
        [[item("已在榜", rank=1, tags=("新",))]],
        path=path,
    )
    second.run_once()

    assert second_notifier.contents == []
    event = second._state_store.load_event("已在榜")
    assert isinstance(event, AlertEvent)
    assert event.status is EventStatus.OBSERVED
