from datetime import datetime, timedelta, timezone
import sqlite3
import threading
from zoneinfo import ZoneInfo

import pytest

from service import weibo_alert_state
from service.weibo_alert_state import AlertStateStore, EventStatus, WeiboSnapshotItem


def test_budget_allows_only_five_delivered_events(tmp_path):
    store = AlertStateStore(tmp_path / "alerts.sqlite3")
    now = datetime(2026, 8, 31, 9, tzinfo=timezone.utc)

    for _ in range(5):
        assert store.reserve_daily_delivery(now) is True
    assert store.reserve_daily_delivery(now) is False


def test_completed_event_can_only_start_new_round_after_twelve_hours(tmp_path):
    store = AlertStateStore(tmp_path / "alerts.sqlite3")
    finished = datetime(2026, 8, 31, 0, tzinfo=timezone.utc)
    store.complete("事件", finished)

    assert store.can_restart("事件", finished + timedelta(hours=11)) is False
    assert store.can_restart("事件", finished + timedelta(hours=12)) is True


def test_new_store_reads_events_persisted_at_the_same_path(tmp_path):
    path = tmp_path / "alerts.sqlite3"
    seen_at = datetime(2026, 8, 31, 9, tzinfo=timezone.utc)
    first_store = AlertStateStore(path)
    first_store.upsert_seen("事件", seen_at, rank=3, hot=123, tags=["爆", "新"])

    event = AlertStateStore(path).load_event("事件")

    assert event is not None
    assert event.status is EventStatus.OBSERVED
    assert event.last_rank == 3
    assert event.last_hot == 123
    assert event.last_tags == ("爆", "新")
    assert event.last_seen_at == seen_at


def test_latest_complete_snapshot_persists_across_store_reloads(tmp_path):
    path = tmp_path / "alerts.sqlite3"
    store = AlertStateStore(path)

    assert store.load_latest_snapshot() is None
    store.replace_latest_snapshot(
        [
            WeiboSnapshotItem(
                event_key="事件",
                title="事件",
                url="https://weibo.com/x",
                rank=1,
                hot=123,
                tags=("爆", "新"),
            )
        ]
    )

    snapshot = AlertStateStore(path).load_latest_snapshot()
    assert snapshot is not None
    assert snapshot["事件"].rank == 1
    assert snapshot["事件"].tags == ("爆", "新")


def test_no_subscribers_does_not_consume_daily_budget(tmp_path):
    store = AlertStateStore(tmp_path / "alerts.sqlite3")
    now = datetime(2026, 8, 31, 9, tzinfo=timezone.utc)
    store.upsert_seen("事件", now, rank=1, hot=100, tags=[])

    store.mark_no_subscribers("事件")

    assert store.load_event("事件").status is EventStatus.NO_SUBSCRIBERS
    assert all(store.reserve_daily_delivery(now) for _ in range(5))


def test_missing_twice_then_complete_records_finished_time(tmp_path):
    store = AlertStateStore(tmp_path / "alerts.sqlite3")
    seen_at = datetime(2026, 8, 31, 9, tzinfo=timezone.utc)
    finished = seen_at + timedelta(hours=1)
    store.upsert_seen("事件", seen_at, rank=1, hot=100, tags=[])

    assert store.mark_missing("事件").missing_streak == 1
    assert store.mark_missing("事件").missing_streak == 2
    store.complete("事件", finished)

    event = store.load_event("事件")
    assert event.status is EventStatus.COMPLETED
    assert event.completed_at == finished
    assert store.active_event_keys() == set()


def test_state_markers_update_one_existing_event(tmp_path):
    store = AlertStateStore(tmp_path / "alerts.sqlite3")
    seen_at = datetime(2026, 8, 31, 9, tzinfo=timezone.utc)
    store.upsert_seen("事件", seen_at, rank=1, hot=100, tags=[])

    store.mark_retry("事件")
    assert store.load_event("事件").retry_count == 1
    store.mark_notified("事件", seen_at)
    assert store.load_event("事件").status is EventStatus.NOTIFIED
    assert store.load_event("事件").notified_at == seen_at
    store.mark_failed("事件")
    assert store.load_event("事件").status is EventStatus.FAILED


def test_dispatching_fences_unknown_delivery_but_known_error_can_retry(tmp_path):
    store = AlertStateStore(tmp_path / "alerts.sqlite3")
    now = datetime(2026, 8, 31, 9, tzinfo=timezone.utc)
    store.upsert_seen("事件", now, rank=1, hot=100, tags=[])
    assert store.reserve_daily_delivery(now, event_key="事件") is True

    assert store.mark_dispatching("事件").status is EventStatus.DISPATCHING
    # A known client-side exception recovers the event for exactly one retry.
    retry = store.mark_retry("事件")
    assert retry.status is EventStatus.OBSERVED
    assert retry.retry_count == 1
    assert store.reserve_daily_delivery(now, event_key="事件") is True


def test_seen_update_resets_missing_and_accepts_caller_rank_decline_streak(tmp_path):
    store = AlertStateStore(tmp_path / "alerts.sqlite3")
    first_seen = datetime(2026, 8, 31, 9, tzinfo=timezone.utc)
    store.upsert_seen("事件", first_seen, rank=5, hot=100, tags=[])
    store.mark_missing("事件")

    event = store.upsert_seen(
        "事件",
        first_seen + timedelta(minutes=30),
        rank=8,
        hot=200,
        tags=["当前爆词"],
        rank_decline_streak=1,
    )

    assert event.missing_streak == 0
    assert event.rank_decline_streak == 1
    assert event.last_rank == 8
    assert event.last_hot == 200
    assert event.last_tags == ("当前爆词",)


def test_restart_creates_next_round_only_after_completed_cooldown(tmp_path):
    store = AlertStateStore(tmp_path / "alerts.sqlite3")
    finished = datetime(2026, 8, 31, 0, tzinfo=timezone.utc)
    store.complete("事件", finished)

    with pytest.raises(ValueError, match="12-hour cooldown"):
        store.upsert_seen(
            "事件", finished + timedelta(hours=11), 1, 100, ["新"], restart=True
        )

    event = store.upsert_seen(
        "事件", finished + timedelta(hours=12), 1, 100, ["新"], restart=True
    )

    assert event.round_id == 2
    assert event.status is EventStatus.OBSERVED
    assert event.completed_at is None


def test_reservation_release_frees_a_daily_delivery_slot(tmp_path):
    store = AlertStateStore(tmp_path / "alerts.sqlite3")
    now = datetime(2026, 8, 31, 9, tzinfo=timezone.utc)

    for index in range(5):
        assert store.reserve_daily_delivery(now, event_key=f"事件{index}")
    assert store.reserve_daily_delivery(now, event_key="第六个") is False

    assert store.release_daily_delivery(now, "事件0") is True
    assert store.reserve_daily_delivery(now, event_key="第六个") is True


def test_finalized_reservation_keeps_its_daily_delivery_slot(tmp_path):
    store = AlertStateStore(tmp_path / "alerts.sqlite3")
    now = datetime(2026, 8, 31, 9, tzinfo=timezone.utc)

    assert store.reserve_daily_delivery(now, event_key="已发送") is True
    assert store.finalize_daily_delivery(now, "已发送") is True
    for index in range(4):
        assert store.reserve_daily_delivery(now, event_key=f"事件{index}")
    assert store.reserve_daily_delivery(now, event_key="第六个") is False
    assert store.release_daily_delivery(now, "已发送") is False
    assert store.reserve_daily_delivery(now, event_key="第六个") is False


@pytest.mark.parametrize("outcome", ["no_subscribers", "failed"])
def test_terminal_non_delivery_releases_reservation_for_sixth_candidate(tmp_path, outcome):
    store = AlertStateStore(tmp_path / "alerts.sqlite3")
    now = datetime(2026, 8, 31, 9, tzinfo=timezone.utc)
    for index in range(5):
        key = f"事件{index}"
        store.upsert_seen(key, now, rank=1, hot=100, tags=[])
        assert store.reserve_daily_delivery(now, event_key=key)

    if outcome == "no_subscribers":
        store.mark_no_subscribers("事件0")
    else:
        store.mark_failed("事件0")

    assert store.reserve_daily_delivery(now, event_key="第六个") is True


def test_completed_event_ignores_all_state_markers(tmp_path):
    store = AlertStateStore(tmp_path / "alerts.sqlite3")
    finished = datetime(2026, 8, 31, 9, tzinfo=timezone.utc)
    store.complete("事件", finished)

    for marker in (
        lambda: store.mark_notified("事件", finished),
        lambda: store.mark_no_subscribers("事件"),
        lambda: store.mark_retry("事件"),
        lambda: store.mark_failed("事件"),
        lambda: store.mark_suppressed_by_budget("事件"),
    ):
        assert marker().status is EventStatus.COMPLETED
        assert store.active_event_keys() == set()


def test_daily_budget_uses_asia_shanghai_calendar_day(tmp_path):
    store = AlertStateStore(tmp_path / "alerts.sqlite3")
    before_midnight = datetime(2026, 8, 31, 15, 59, tzinfo=timezone.utc)
    after_midnight = datetime(2026, 8, 31, 16, 0, tzinfo=timezone.utc)

    assert before_midnight.astimezone(ZoneInfo("Asia/Shanghai")).date().isoformat() == "2026-08-31"
    assert after_midnight.astimezone(ZoneInfo("Asia/Shanghai")).date().isoformat() == "2026-09-01"
    for index in range(5):
        assert store.reserve_daily_delivery(before_midnight, event_key=f"前{index}")
    assert store.reserve_daily_delivery(after_midnight, event_key="次日") is True


def test_persisted_timestamps_are_normalized_to_utc(tmp_path):
    store = AlertStateStore(tmp_path / "alerts.sqlite3")
    shanghai_time = datetime(2026, 8, 31, 9, tzinfo=ZoneInfo("Asia/Shanghai"))

    event = store.upsert_seen("事件", shanghai_time, rank=1, hot=100, tags=[])

    assert event.first_seen_at == datetime(2026, 8, 31, 1, tzinfo=timezone.utc)
    assert event.first_seen_at.tzinfo is timezone.utc
    reloaded = AlertStateStore(tmp_path / "alerts.sqlite3").load_event("事件")
    assert reloaded.last_seen_at == datetime(2026, 8, 31, 1, tzinfo=timezone.utc)
    assert reloaded.last_seen_at.tzinfo is timezone.utc


def test_public_time_inputs_require_timezone_aware_datetimes(tmp_path):
    store = AlertStateStore(tmp_path / "alerts.sqlite3")
    naive = datetime(2026, 8, 31, 9)

    with pytest.raises(ValueError, match="timezone-aware"):
        store.upsert_seen("事件", naive, rank=1, hot=100, tags=[])
    with pytest.raises(ValueError, match="timezone-aware"):
        store.complete("事件", naive)
    with pytest.raises(ValueError, match="timezone-aware"):
        store.reserve_daily_delivery(naive)
    with pytest.raises(ValueError, match="timezone-aware"):
        store.can_restart("事件", naive)


def test_memory_database_path_is_rejected(tmp_path):
    del tmp_path

    with pytest.raises(ValueError, match="persistent file path"):
        AlertStateStore(":memory:")


def test_finalize_uses_the_original_shanghai_day_of_a_cross_midnight_reservation(
    tmp_path,
):
    path = tmp_path / "alerts.sqlite3"
    store = AlertStateStore(path)
    before_midnight = datetime(2026, 8, 31, 23, 59, tzinfo=ZoneInfo("Asia/Shanghai"))
    after_midnight = before_midnight + timedelta(minutes=2)

    assert store.reserve_daily_delivery(before_midnight, event_key="事件") is True
    assert store.reserve_daily_delivery(after_midnight, event_key="事件") is True
    with sqlite3.connect(path) as connection:
        assert connection.execute(
            "SELECT COUNT(*) FROM daily_delivery_reservations WHERE event_key = '事件'"
        ).fetchone() == (1,)
    assert store.finalize_daily_delivery(after_midnight, "事件") is True

    with sqlite3.connect(path) as connection:
        assert connection.execute(
            "SELECT delivered_count FROM daily_delivery_budget WHERE day = '2026-08-31'"
        ).fetchone() == (1,)
        assert connection.execute("SELECT COUNT(*) FROM daily_delivery_reservations").fetchone() == (0,)


def test_release_uses_the_original_shanghai_day_of_a_cross_midnight_reservation(
    tmp_path,
):
    path = tmp_path / "alerts.sqlite3"
    store = AlertStateStore(path)
    before_midnight = datetime(2026, 8, 31, 23, 59, tzinfo=ZoneInfo("Asia/Shanghai"))
    after_midnight = before_midnight + timedelta(minutes=2)

    assert store.reserve_daily_delivery(before_midnight, event_key="事件") is True
    assert store.release_daily_delivery(after_midnight, "事件") is True

    with sqlite3.connect(path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM daily_delivery_budget").fetchone() == (0,)
        assert connection.execute("SELECT COUNT(*) FROM daily_delivery_reservations").fetchone() == (0,)


def test_immediate_budget_consumption_counts_pending_reservations(tmp_path):
    store = AlertStateStore(tmp_path / "alerts.sqlite3")
    now = datetime(2026, 8, 31, 9, tzinfo=timezone.utc)

    assert store.reserve_daily_delivery(now, event_key="A") is True
    for _ in range(4):
        assert store.reserve_daily_delivery(now) is True
    assert store.reserve_daily_delivery(now) is False
    assert store.finalize_daily_delivery(now, "A") is True
    assert store.reserve_daily_delivery(now) is False


def test_complete_wins_against_a_concurrent_marker_after_it_reads_observed(
    tmp_path, monkeypatch
):
    store = AlertStateStore(tmp_path / "alerts.sqlite3")
    now = datetime(2026, 8, 31, 9, tzinfo=timezone.utc)
    store.upsert_seen("事件", now, rank=1, hot=100, tags=[])
    original_connect = weibo_alert_state.sqlite3.connect
    marker_read = threading.Event()
    allow_marker_update = threading.Event()
    complete_updated = threading.Event()

    class ConnectionProxy:
        def __init__(self, connection):
            object.__setattr__(self, "_connection", connection)

        def __getattr__(self, name):
            return getattr(self._connection, name)

        def __setattr__(self, name, value):
            setattr(self._connection, name, value)

    class BlockingMarkerConnection(ConnectionProxy):
        def execute(self, statement, parameters=()):
            result = self._connection.execute(statement, parameters)
            if "SELECT status FROM events" in statement:
                marker_read.set()
                assert allow_marker_update.wait(timeout=5)
            return result

    class ObservedCompleteConnection(ConnectionProxy):
        def execute(self, statement, parameters=()):
            result = self._connection.execute(statement, parameters)
            if statement.startswith("UPDATE events SET status"):
                complete_updated.set()
            return result

    def fake_connect(*args, **kwargs):
        connection = original_connect(*args, **kwargs)
        if threading.current_thread().name == "marker":
            return BlockingMarkerConnection(connection)
        if threading.current_thread().name == "completer":
            return ObservedCompleteConnection(connection)
        return connection

    monkeypatch.setattr(weibo_alert_state.sqlite3, "connect", fake_connect)
    marker = threading.Thread(
        name="marker", target=lambda: store.mark_notified("事件", now)
    )
    completer = threading.Thread(
        name="completer", target=lambda: store.complete("事件", now)
    )
    marker.start()
    assert marker_read.wait(timeout=5)
    completer.start()
    complete_updated.wait(timeout=0.2)
    allow_marker_update.set()
    marker.join(timeout=5)
    completer.join(timeout=5)

    assert not marker.is_alive()
    assert not completer.is_alive()
    assert store.load_event("事件").status is EventStatus.COMPLETED
    assert store.active_event_keys() == set()
