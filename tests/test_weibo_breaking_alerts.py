from datetime import datetime, timedelta, timezone

from service.weibo_alert_state import AlertEvent, EventStatus
from service.weibo_breaking_alerts import (
    TransitionAction,
    advance_event,
    assess,
    normalize_title,
    render_notification,
)


def item(**overrides):
    values = {
        "title": "测试事件",
        "url": "https://weibo.com/x",
        "rank": 10,
        "hot": 100,
        "tags": [],
    }
    values.update(overrides)
    return values


def event(**overrides):
    started = datetime(2026, 8, 31, tzinfo=timezone.utc)
    values = {
        "event_key": "测试事件",
        "round_id": 1,
        "status": EventStatus.OBSERVED,
        "first_seen_at": started,
        "last_seen_at": started,
        "last_rank": 10,
        "last_hot": 100,
        "last_tags": (),
        "missing_streak": 0,
        "rank_decline_streak": 0,
        "notified_at": None,
        "retry_count": 0,
        "completed_at": None,
    }
    values.update(overrides)
    return AlertEvent(**values)


def test_new_top_ten_item_with_breaking_tag_reaches_threshold():
    assessment = assess(
        previous=None,
        current=item(rank=1, hot=0, tags=["当前爆词"]),
    )

    assert assessment.score == 8
    assert assessment.is_breaking is True
    assert assessment.reasons == ["新上榜", "Top 3", "爆点标签"]


def test_tag_outside_top_twenty_is_not_breaking():
    assessment = assess(previous=None, current=item(rank=21, hot=0, tags=["爆"]))

    assert assessment.is_breaking is False


def test_renderer_matches_the_approved_plain_text_format():
    text = render_notification(
        title="测试事件",
        url="https://weibo.com/x",
        previous_rank=None,
        rank=1,
        tags=["当前爆词"],
        reasons=["新上榜", "Top 10", "爆点标签"],
    )

    assert text == (
        "💥💥💥 微博突发爆点\n【测试事件】\n"
        "排名：新上榜 → 第1\n标签：当前爆词\n"
        "触发：新上榜 + Top 10 + 爆点标签\n链接：https://weibo.com/x"
    )


def test_renderer_omits_tag_line_when_item_has_no_tags():
    assert "标签：" not in render_notification(
        title="测试事件",
        url="https://weibo.com/x",
        previous_rank=20,
        rank=5,
        tags=[],
        reasons=["排名跃升", "Top 10"],
    )


def test_rank_jump_into_top_twenty_is_a_strong_breaking_signal():
    assessment = assess(previous=item(rank=35), current=item(rank=20))

    assert assessment.score == 3
    assert assessment.is_breaking is False
    assert assessment.reasons == ["排名跃升", "Top 20"]


def test_rank_jump_with_additional_recommendation_label_reaches_threshold():
    assessment = assess(previous=item(rank=35), current=item(rank=20, tags=["新", "荐"]))

    assert assessment.score == 5
    assert assessment.is_breaking is True
    assert assessment.reasons == ["排名跃升", "Top 20", "推荐或新标签"]


def test_rank_jump_of_thirty_scores_the_higher_tier():
    assessment = assess(previous=item(rank=50), current=item(rank=20))

    assert assessment.score == 4
    assert assessment.reasons == ["排名跃升", "Top 20"]


def test_heat_doubling_into_top_twenty_is_a_strong_breaking_signal():
    assessment = assess(previous=item(rank=20, hot=100), current=item(rank=20, hot=200))

    assert assessment.score == 3
    assert assessment.is_breaking is False
    assert assessment.reasons == ["热度翻倍", "Top 20"]


def test_heat_tripling_scores_the_higher_tier():
    assessment = assess(previous=item(rank=20, hot=100), current=item(rank=20, hot=300))

    assert assessment.score == 4
    assert assessment.reasons == ["热度翻倍", "Top 20"]


def test_zero_heat_never_counts_as_heat_growth():
    assessment = assess(previous=item(rank=10, hot=0), current=item(rank=10, hot=10000))

    assert assessment.score == 2
    assert assessment.reasons == ["Top 10"]
    assert assessment.is_breaking is False


def test_normalize_title_makes_full_width_and_collapsed_space_titles_equal():
    assert normalize_title("  孙　宇晨   说 长文  ") == "孙 宇晨 说 长文"
    assert normalize_title("孙 宇晨 说 长文") == normalize_title("孙　宇晨 说\u3000长文")


def test_advance_event_marks_then_completes_after_two_absent_snapshots():
    now = datetime(2026, 8, 31, tzinfo=timezone.utc)
    first = advance_event(event(), current=None, now=now)
    second = advance_event(event(missing_streak=1), current=None, now=now)

    assert first.action is TransitionAction.MARK_MISSING
    assert first.missing_streak == 1
    assert second.action is TransitionAction.COMPLETE
    assert second.missing_streak == 2


def test_advance_event_completes_after_two_consecutive_rank_declines():
    now = datetime(2026, 8, 31, tzinfo=timezone.utc)
    first = advance_event(event(last_rank=10), current=item(rank=11), now=now)
    second = advance_event(
        event(last_rank=11, rank_decline_streak=1), current=item(rank=12), now=now
    )

    assert first.action is TransitionAction.SEEN
    assert first.rank_decline_streak == 1
    assert second.action is TransitionAction.COMPLETE
    assert second.rank_decline_streak == 2


def test_completed_event_restarts_only_after_twelve_hours_with_a_fresh_top_ten_item():
    finished = datetime(2026, 8, 31, tzinfo=timezone.utc)
    completed = event(status=EventStatus.COMPLETED, completed_at=finished)

    too_soon = advance_event(
        completed, current=item(rank=1), now=finished + timedelta(hours=11)
    )
    not_top_ten = advance_event(
        completed, current=item(rank=11), now=finished + timedelta(hours=12)
    )
    restarted = advance_event(
        completed, current=item(rank=10), now=finished + timedelta(hours=12)
    )

    assert too_soon.action is TransitionAction.IGNORE
    assert not_top_ten.action is TransitionAction.IGNORE
    assert restarted.action is TransitionAction.RESTART
