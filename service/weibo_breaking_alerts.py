"""Pure domain rules for detecting and deduplicating Weibo breaking events."""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Mapping, Protocol, Sequence


BREAKING_TAGS = frozenset({"爆", "沸", "当前爆词"})
PROMOTION_TAGS = frozenset({"新", "荐"})
RESTART_COOLDOWN = timedelta(hours=12)


@dataclass(frozen=True)
class Assessment:
    """The explainable score assigned to one rank-list observation."""

    score: int
    is_breaking: bool
    reasons: list[str]


class DomainEventStatus(str, Enum):
    """The minimal event status vocabulary needed by the pure state machine."""

    OBSERVED = "observed"
    COMPLETED = "completed"


@dataclass(frozen=True)
class DomainEvent:
    """A persistence-independent event snapshot for domain callers and tests."""

    event_key: str
    round_id: int
    status: DomainEventStatus
    first_seen_at: datetime
    last_seen_at: datetime
    last_rank: int
    last_hot: int
    last_tags: tuple[str, ...]
    missing_streak: int
    rank_decline_streak: int
    notified_at: datetime | None
    retry_count: int
    completed_at: datetime | None


class EventLike(Protocol):
    """Structural contract accepted from a persistence adapter such as Task 3."""

    status: object
    completed_at: datetime | None
    missing_streak: int
    rank_decline_streak: int
    last_rank: int


class TransitionAction(str, Enum):
    """Persistence-agnostic state change the caller should apply."""

    SEEN = "seen"
    MARK_MISSING = "mark_missing"
    COMPLETE = "complete"
    RESTART = "restart"
    IGNORE = "ignore"


@dataclass(frozen=True)
class EventTransition:
    """The next state-machine action and caller-maintained streak values."""

    action: TransitionAction
    missing_streak: int
    rank_decline_streak: int


def normalize_title(title: str) -> str:
    """Produce a stable event key from visually equivalent Weibo titles."""
    return " ".join(unicodedata.normalize("NFKC", title).split())


def assess(
    previous: Mapping[str, Any] | object | None,
    current: Mapping[str, Any] | object,
) -> Assessment:
    """Score an item against the preceding snapshot without side effects."""
    rank = int(_field(current, "rank"))
    hot = int(_field(current, "hot", 0) or 0)
    tags = _tags(current)
    score = 0
    reasons: list[str] = []
    strong_signal = False

    if previous is None:
        score += 2
        reasons.append("新上榜")
        strong_signal = rank <= 10
    else:
        previous_rank = _field(previous, "rank", None)
        if previous_rank is None:
            previous_rank = _field(previous, "last_rank")
        previous_rank = int(previous_rank)
        rank_gain = previous_rank - rank
        if rank_gain >= 30:
            score += 3
            reasons.append("排名跃升")
            strong_signal = rank <= 20
        elif rank_gain >= 15:
            score += 2
            reasons.append("排名跃升")
            strong_signal = rank <= 20

        previous_hot = _field(previous, "hot", None)
        if previous_hot is None:
            previous_hot = _field(previous, "last_hot", 0)
        previous_hot = int(previous_hot or 0)
        if previous_hot > 0 and hot > 0:
            if hot >= previous_hot * 3:
                score += 3
                reasons.append("热度翻倍")
                strong_signal = strong_signal or rank <= 20
            elif hot >= previous_hot * 2:
                score += 2
                reasons.append("热度翻倍")
                strong_signal = strong_signal or rank <= 20

    top_score, top_reason = _top_score(rank)
    score += top_score
    if top_reason:
        reasons.append(top_reason)

    if BREAKING_TAGS.intersection(tags):
        score += 3
        reasons.append("爆点标签")
        strong_signal = strong_signal or rank <= 20

    if PROMOTION_TAGS.intersection(tags):
        score += 1
        reasons.append("推荐或新标签")

    return Assessment(
        score=score,
        is_breaking=score >= 5 and strong_signal,
        reasons=reasons,
    )


def render_notification(
    *,
    title: str,
    url: str,
    previous_rank: int | None,
    rank: int,
    tags: Sequence[str],
    reasons: Sequence[str],
) -> str:
    """Render the approved plain-text QQ notification without Markdown."""
    ranking = f"新上榜 → 第{rank}" if previous_rank is None else f"第{previous_rank} → 第{rank}"
    lines = [
        "💥💥💥 微博突发爆点",
        f"【{normalize_title(title)}】",
        f"排名：{ranking}",
    ]
    if tags:
        lines.append(f"标签：{'、'.join(str(tag) for tag in tags)}")
    lines.extend((f"触发：{' + '.join(reasons)}", f"链接：{url}"))
    return "\n".join(lines)


def advance_event(
    previous: EventLike | None,
    current: Mapping[str, Any] | object | None,
    now: datetime,
    *,
    is_new_appearance: bool = False,
) -> EventTransition:
    """Recommend the next event transition; the caller persists the result.

    Two absent snapshots or two consecutive numerically worse ranks complete an
    active event. A completed event may only restart after its 12-hour quiet
    period and a newly observed Top-10 item.
    """
    if previous is None:
        return EventTransition(TransitionAction.SEEN, 0, 0)

    if _is_completed(previous.status):
        if (
            current is not None
            and previous.completed_at is not None
            and now - previous.completed_at >= RESTART_COOLDOWN
            and is_new_appearance
            and int(_field(current, "rank")) <= 10
        ):
            return EventTransition(TransitionAction.RESTART, 0, 0)
        return EventTransition(
            TransitionAction.IGNORE,
            previous.missing_streak,
            previous.rank_decline_streak,
        )

    if current is None:
        missing_streak = previous.missing_streak + 1
        action = (
            TransitionAction.COMPLETE
            if missing_streak >= 2
            else TransitionAction.MARK_MISSING
        )
        return EventTransition(action, missing_streak, 0)

    rank = int(_field(current, "rank"))
    rank_decline_streak = (
        previous.rank_decline_streak + 1 if rank > previous.last_rank else 0
    )
    action = (
        TransitionAction.COMPLETE
        if rank_decline_streak >= 2
        else TransitionAction.SEEN
    )
    return EventTransition(action, 0, rank_decline_streak)


def _top_score(rank: int) -> tuple[int, str | None]:
    if rank <= 3:
        return 3, "Top 3"
    if rank <= 10:
        return 2, "Top 10"
    if rank <= 20:
        return 1, "Top 20"
    return 0, None


def _tags(item: Mapping[str, Any] | object) -> set[str]:
    raw_tags = _field(item, "tags", ())
    if isinstance(raw_tags, str):
        return {raw_tags}
    return {str(tag) for tag in raw_tags}


def _is_completed(status: object) -> bool:
    """Accept this module's enum and a persistence layer's compatible enum."""
    return getattr(status, "value", status) == DomainEventStatus.COMPLETED.value


_MISSING = object()


def _field(item: Mapping[str, Any] | object, name: str, default: Any = _MISSING) -> Any:
    if isinstance(item, Mapping):
        value = item.get(name, _MISSING)
    else:
        value = getattr(item, name, _MISSING)
    if value is _MISSING:
        if default is _MISSING:
            raise KeyError(f"missing event field: {name}")
        return default
    return value
