from datetime import datetime, timedelta, timezone

import pytest

from service.weibo_alert_state import AlertStateStore, EventStatus


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
