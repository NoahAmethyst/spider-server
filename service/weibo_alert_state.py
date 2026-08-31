"""Durable storage for the Weibo breaking-alert state machine."""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Iterable, Iterator


DAILY_DELIVERY_LIMIT = 5
RESTART_COOLDOWN = timedelta(hours=12)


class EventStatus(str, Enum):
    OBSERVED = "observed"
    NOTIFIED = "notified"
    COMPLETED = "completed"
    NO_SUBSCRIBERS = "no_subscribers"
    FAILED = "failed"
    SUPPRESSED_BY_BUDGET = "suppressed_by_budget"


@dataclass(frozen=True)
class AlertEvent:
    event_key: str
    round_id: int
    status: EventStatus
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


class AlertStateStore:
    """SQLite-backed event state and global daily delivery budget."""

    def __init__(self, path: str | Path):
        self._path = str(path)
        if self._path != ":memory:":
            Path(self._path).parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def load_event(self, event_key: str) -> AlertEvent | None:
        with self._connection() as connection:
            row = connection.execute(
                "SELECT * FROM events WHERE event_key = ?", (event_key,)
            ).fetchone()
        return self._event_from_row(row) if row else None

    def upsert_seen(
        self,
        event_key: str,
        seen_at: datetime,
        rank: int,
        hot: int,
        tags: Iterable[str],
        rank_decline_streak: int = 0,
        *,
        restart: bool = False,
    ) -> AlertEvent:
        """Record a seen item and clear its absent-snapshot streak.

        ``restart`` is intentionally explicit: callers must first use
        :meth:`can_restart` before beginning a new round of a completed event.
        """
        tags_json = json.dumps(list(tags), ensure_ascii=False)
        with self._connection() as connection:
            row = connection.execute(
                "SELECT * FROM events WHERE event_key = ?", (event_key,)
            ).fetchone()
            if row is None:
                connection.execute(
                    """
                    INSERT INTO events (
                        event_key, round_id, status, first_seen_at, last_seen_at,
                        last_rank, last_hot, last_tags_json, missing_streak,
                        rank_decline_streak, retry_count
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        event_key,
                        1,
                        EventStatus.OBSERVED.value,
                        self._dump_time(seen_at),
                        self._dump_time(seen_at),
                        rank,
                        hot,
                        tags_json,
                        0,
                        rank_decline_streak,
                        0,
                    ),
                )
            elif restart:
                if EventStatus(row["status"]) is not EventStatus.COMPLETED:
                    raise ValueError("only completed events can start a new round")
                completed_at = self._load_time(row["completed_at"])
                if completed_at is None or seen_at - completed_at < RESTART_COOLDOWN:
                    raise ValueError("completed events require a 12-hour cooldown")
                connection.execute(
                    """
                    UPDATE events
                    SET round_id = ?, status = ?, first_seen_at = ?, last_seen_at = ?,
                        last_rank = ?, last_hot = ?, last_tags_json = ?,
                        missing_streak = 0, rank_decline_streak = ?, notified_at = NULL,
                        retry_count = 0, completed_at = NULL
                    WHERE event_key = ?
                    """,
                    (
                        row["round_id"] + 1,
                        EventStatus.OBSERVED.value,
                        self._dump_time(seen_at),
                        self._dump_time(seen_at),
                        rank,
                        hot,
                        tags_json,
                        rank_decline_streak,
                        event_key,
                    ),
                )
            else:
                connection.execute(
                    """
                    UPDATE events
                    SET last_seen_at = ?, last_rank = ?, last_hot = ?,
                        last_tags_json = ?, missing_streak = 0,
                        rank_decline_streak = ?
                    WHERE event_key = ?
                    """,
                    (
                        self._dump_time(seen_at),
                        rank,
                        hot,
                        tags_json,
                        rank_decline_streak,
                        event_key,
                    ),
                )
        event = self.load_event(event_key)
        assert event is not None
        return event

    def mark_missing(self, event_key: str) -> AlertEvent:
        return self._mark_and_load(
            event_key,
            "missing_streak = missing_streak + 1",
        )

    def complete(self, event_key: str, finished_at: datetime) -> AlertEvent:
        """Complete an event, creating a minimal completed record if necessary."""
        with self._connection() as connection:
            row = connection.execute(
                "SELECT event_key FROM events WHERE event_key = ?", (event_key,)
            ).fetchone()
            if row is None:
                timestamp = self._dump_time(finished_at)
                connection.execute(
                    """
                    INSERT INTO events (
                        event_key, round_id, status, first_seen_at, last_seen_at,
                        last_rank, last_hot, last_tags_json, completed_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        event_key,
                        1,
                        EventStatus.COMPLETED.value,
                        timestamp,
                        timestamp,
                        0,
                        0,
                        "[]",
                        timestamp,
                    ),
                )
            else:
                connection.execute(
                    "UPDATE events SET status = ?, completed_at = ? WHERE event_key = ?",
                    (EventStatus.COMPLETED.value, self._dump_time(finished_at), event_key),
                )
        event = self.load_event(event_key)
        assert event is not None
        return event

    def mark_notified(self, event_key: str, notified_at: datetime) -> AlertEvent:
        return self._mark_and_load(
            event_key,
            "status = ?, notified_at = ?",
            EventStatus.NOTIFIED.value,
            self._dump_time(notified_at),
        )

    def mark_no_subscribers(self, event_key: str) -> AlertEvent:
        return self._mark_and_load(
            event_key, "status = ?", EventStatus.NO_SUBSCRIBERS.value
        )

    def mark_retry(self, event_key: str) -> AlertEvent:
        return self._mark_and_load(event_key, "retry_count = retry_count + 1")

    def mark_failed(self, event_key: str) -> AlertEvent:
        return self._mark_and_load(event_key, "status = ?", EventStatus.FAILED.value)

    def mark_suppressed_by_budget(self, event_key: str) -> AlertEvent:
        return self._mark_and_load(
            event_key, "status = ?", EventStatus.SUPPRESSED_BY_BUDGET.value
        )

    def reserve_daily_delivery(self, now: datetime) -> bool:
        """Reserve one of the five delivery slots for ``now``'s local day."""
        day = now.date().isoformat()
        with self._connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                "SELECT delivered_count FROM daily_delivery_budget WHERE day = ?", (day,)
            ).fetchone()
            delivered_count = row["delivered_count"] if row else 0
            if delivered_count >= DAILY_DELIVERY_LIMIT:
                connection.commit()
                return False
            if row is None:
                connection.execute(
                    "INSERT INTO daily_delivery_budget (day, delivered_count) VALUES (?, ?)",
                    (day, 1),
                )
            else:
                connection.execute(
                    "UPDATE daily_delivery_budget SET delivered_count = ? WHERE day = ?",
                    (delivered_count + 1, day),
                )
            connection.commit()
            return True

    def can_restart(self, event_key: str, at: datetime) -> bool:
        event = self.load_event(event_key)
        return bool(
            event
            and event.status is EventStatus.COMPLETED
            and event.completed_at is not None
            and at - event.completed_at >= RESTART_COOLDOWN
        )

    def active_event_keys(self) -> set[str]:
        with self._connection() as connection:
            rows = connection.execute(
                "SELECT event_key FROM events WHERE status != ?",
                (EventStatus.COMPLETED.value,),
            ).fetchall()
        return {row["event_key"] for row in rows}

    def _mark_and_load(self, event_key: str, assignment: str, *values: object) -> AlertEvent:
        with self._connection() as connection:
            cursor = connection.execute(
                f"UPDATE events SET {assignment} WHERE event_key = ?", (*values, event_key)
            )
            if cursor.rowcount != 1:
                raise KeyError(f"unknown event: {event_key}")
        event = self.load_event(event_key)
        assert event is not None
        return event

    def _initialize(self) -> None:
        with self._connection() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS events (
                    event_key TEXT PRIMARY KEY,
                    round_id INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    first_seen_at TEXT NOT NULL,
                    last_seen_at TEXT NOT NULL,
                    last_rank INTEGER NOT NULL,
                    last_hot INTEGER NOT NULL,
                    last_tags_json TEXT NOT NULL,
                    missing_streak INTEGER NOT NULL DEFAULT 0,
                    rank_decline_streak INTEGER NOT NULL DEFAULT 0,
                    notified_at TEXT,
                    retry_count INTEGER NOT NULL DEFAULT 0,
                    completed_at TEXT
                );
                CREATE TABLE IF NOT EXISTS daily_delivery_budget (
                    day TEXT PRIMARY KEY,
                    delivered_count INTEGER NOT NULL
                );
                """
            )

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self._path)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        except BaseException:
            connection.rollback()
            raise
        finally:
            connection.close()

    @staticmethod
    def _dump_time(value: datetime) -> str:
        return value.isoformat()

    @staticmethod
    def _load_time(value: str | None) -> datetime | None:
        return datetime.fromisoformat(value) if value is not None else None

    @classmethod
    def _event_from_row(cls, row: sqlite3.Row) -> AlertEvent:
        return AlertEvent(
            event_key=row["event_key"],
            round_id=row["round_id"],
            status=EventStatus(row["status"]),
            first_seen_at=cls._load_time(row["first_seen_at"]),
            last_seen_at=cls._load_time(row["last_seen_at"]),
            last_rank=row["last_rank"],
            last_hot=row["last_hot"],
            last_tags=tuple(json.loads(row["last_tags_json"])),
            missing_streak=row["missing_streak"],
            rank_decline_streak=row["rank_decline_streak"],
            notified_at=cls._load_time(row["notified_at"]),
            retry_count=row["retry_count"],
            completed_at=cls._load_time(row["completed_at"]),
        )
