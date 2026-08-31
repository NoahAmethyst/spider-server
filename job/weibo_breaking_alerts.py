"""Orchestrate Weibo rank sampling and QQ breaking-news notifications."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from datetime import datetime, timezone
from typing import Any

from service.qqbot_notify import NotifyOutcome, QQBotNotifier
from service.weibo_alert_state import (
    AlertEvent,
    AlertStateStore,
    EventStatus,
    WeiboSnapshotItem,
)
from service.weibo_breaking_alerts import (
    TransitionAction,
    advance_event,
    assess,
    normalize_title,
    render_notification,
)
from service.weibo_hot import get_weibo_hot
from util.config import EnvConfig
from util.logger import logger


class WeiboBreakingAlertMonitor:
    """Compare complete rank snapshots and send each eligible event at most once."""

    def __init__(
        self,
        fetch_hot_list: Callable[[], Iterable[Mapping[str, Any] | object]],
        state_store: AlertStateStore,
        notifier: QQBotNotifier,
        clock: Callable[[], datetime],
    ):
        self._fetch_hot_list = fetch_hot_list
        self._state_store = state_store
        self._notifier = notifier
        self._clock = clock

    def run_once(self) -> None:
        """Fetch one complete snapshot and process its state transitions.

        Fetch failures intentionally escape this method: the scheduler registers
        a logging boundary around every invocation, while callers that use this
        class directly can decide their own retry policy.
        """
        now = self._clock()
        current_snapshot = self._snapshot_items(self._fetch_hot_list())
        previous_snapshot = self._state_store.load_latest_snapshot()

        if previous_snapshot is None:
            self._write_baseline(current_snapshot.values(), now)
            return

        for event_key in self._state_store.active_event_keys() - current_snapshot.keys():
            self._record_absence(event_key, now)

        for event_key, current in current_snapshot.items():
            previous_snapshot_item = previous_snapshot.get(event_key)
            previous_event = self._state_store.load_event(event_key)
            if previous_event is not None and previous_event.status is EventStatus.DISPATCHING:
                # The process may have died after QQ accepted the RPC. Without
                # an idempotency key in the protocol we must prefer suppressing
                # an uncertain result to risking a duplicate user notification.
                logger.warning(
                    "Weibo breaking-alert dispatch outcome is unknown; suppressing resend "
                    "for event=%s",
                    event_key,
                )
                continue
            transition = advance_event(
                previous_event,
                current,
                now,
                is_new_appearance=event_key not in previous_snapshot,
            )
            if transition.action is TransitionAction.IGNORE:
                continue
            if transition.action is TransitionAction.COMPLETE:
                self._state_store.complete(event_key, now)
                continue

            restart = transition.action is TransitionAction.RESTART
            observed = self._state_store.upsert_seen(
                event_key,
                now,
                rank=current.rank,
                hot=current.hot,
                tags=current.tags,
                rank_decline_streak=transition.rank_decline_streak,
                restart=restart,
            )
            self._maybe_notify(
                observed,
                current,
                previous_snapshot_item=None if restart else previous_snapshot_item,
                now=now,
            )

        # Persist even when a notifier error was classified for a later retry.
        self._state_store.replace_latest_snapshot(current_snapshot.values())

    def _write_baseline(
        self, current_items: Iterable[WeiboSnapshotItem], now: datetime
    ) -> None:
        items = tuple(current_items)
        for item in items:
            self._state_store.upsert_seen(
                item.event_key,
                now,
                rank=item.rank,
                hot=item.hot,
                tags=item.tags,
            )
        self._state_store.replace_latest_snapshot(items)

    def _record_absence(self, event_key: str, now: datetime) -> None:
        previous_event = self._state_store.load_event(event_key)
        if previous_event is None:
            return
        if previous_event.status is EventStatus.DISPATCHING:
            logger.warning(
                "Weibo breaking-alert dispatch outcome is unknown; retaining event=%s",
                event_key,
            )
            return
        transition = advance_event(previous_event, None, now)
        if transition.action is TransitionAction.COMPLETE:
            self._state_store.complete(event_key, now)
        elif transition.action is TransitionAction.MARK_MISSING:
            self._state_store.mark_missing(event_key)

    def _maybe_notify(
        self,
        event: AlertEvent,
        current: WeiboSnapshotItem,
        previous_snapshot_item: WeiboSnapshotItem | None,
        *,
        now: datetime,
    ) -> None:
        if event.status is not EventStatus.OBSERVED:
            return

        assessment = assess(previous_snapshot_item, current)
        retrying = event.retry_count == 1
        if not retrying and not assessment.is_breaking:
            return

        logger.info(
            "Weibo breaking-alert eligible event=%s score=%s reasons=%s retry=%s",
            event.event_key,
            assessment.score,
            "+".join(assessment.reasons),
            retrying,
        )

        if not self._state_store.reserve_daily_delivery(now, event.event_key):
            self._state_store.mark_suppressed_by_budget(event.event_key)
            logger.info("Weibo breaking-alert budget suppressed event=%s", event.event_key)
            return

        content = render_notification(
            title=current.title,
            url=current.url,
            previous_rank=(
                previous_snapshot_item.rank if previous_snapshot_item is not None else None
            ),
            rank=current.rank,
            tags=current.tags,
            reasons=assessment.reasons,
        )
        dispatch = self._state_store.mark_dispatching(event.event_key)
        if dispatch.status is not EventStatus.DISPATCHING:
            logger.warning(
                "Weibo breaking-alert dispatch state changed before Notify; suppressing event=%s",
                event.event_key,
            )
            return
        logger.info("Weibo breaking-alert Notify dispatch started event=%s", event.event_key)
        try:
            outcome = self._notifier.notify(content)
        except Exception:
            if retrying:
                self._state_store.mark_failed(event.event_key)
                logger.exception("Weibo breaking-alert Notify retry failed event=%s", event.event_key)
            else:
                self._state_store.mark_retry(event.event_key)
                logger.exception(
                    "Weibo breaking-alert Notify failed; will retry once event=%s",
                    event.event_key,
                )
            return

        if outcome is NotifyOutcome.NO_SUBSCRIBERS:
            self._state_store.mark_no_subscribers(event.event_key)
            logger.info("Weibo breaking-alert has no subscribers event=%s", event.event_key)
            return

        if not self._state_store.finalize_daily_delivery(now, event.event_key):
            # Notify has already succeeded, so terminally deduplicate it rather
            # than risk a duplicate delivery if durable budget settlement fails.
            logger.error(
                "Weibo breaking-alert delivery settlement failed; retaining unknown "
                "dispatch event=%s",
                event.event_key,
            )
            return
        self._state_store.mark_notified(event.event_key, now)
        logger.info("Weibo breaking-alert Notify delivered event=%s", event.event_key)

    @staticmethod
    def _snapshot_items(
        entries: Iterable[Mapping[str, Any] | object],
    ) -> dict[str, WeiboSnapshotItem]:
        snapshot: dict[str, WeiboSnapshotItem] = {}
        for entry in entries:
            title = str(_field(entry, "title"))
            event_key = normalize_title(title)
            if not event_key:
                continue
            item = WeiboSnapshotItem(
                event_key=event_key,
                title=title,
                url=str(_field(entry, "url", "")),
                rank=int(_field(entry, "rank")),
                hot=int(_field(entry, "hot", 0) or 0),
                tags=tuple(str(tag) for tag in _field(entry, "tags", ())),
            )
            existing = snapshot.get(event_key)
            if existing is None or item.rank < existing.rank:
                snapshot[event_key] = item
        return snapshot


def build_weibo_breaking_alert_monitor() -> WeiboBreakingAlertMonitor:
    """Build the production monitor from non-secret environment configuration."""
    address = EnvConfig.qqbot_grpc_addr()
    state_path = EnvConfig.weibo_alert_state_path()
    if not address:
        raise RuntimeError("QQ_BOT_GRPC_ADDR is required for Weibo breaking alerts")
    if not state_path:
        raise RuntimeError("WEIBO_ALERT_STATE_PATH is required for Weibo breaking alerts")
    return WeiboBreakingAlertMonitor(
        fetch_hot_list=get_weibo_hot,
        state_store=AlertStateStore(state_path),
        notifier=QQBotNotifier(address),
        clock=lambda: datetime.now(timezone.utc),
    )


_MISSING = object()


def _field(item: Mapping[str, Any] | object, name: str, default: Any = _MISSING) -> Any:
    value = item.get(name, _MISSING) if isinstance(item, Mapping) else getattr(item, name, _MISSING)
    if value is _MISSING:
        if default is _MISSING:
            raise KeyError(f"missing Weibo hot-list field: {name}")
        return default
    return value
