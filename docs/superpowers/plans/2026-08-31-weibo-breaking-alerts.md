# 微博突发爆点提醒 Implementation Plan

> **2026-09-02 更新：** 已取消每日五条播报上限。本计划中涉及每日配额、额度结算或第五/第六条限制的历史描述均由当前实现和运维说明取代。

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 每 30 分钟分析微博热搜变化，以评分和去重状态机识别突发爆点，并通过 qq-bot 的 `Notify` RPC 向现有微博热搜订阅者发送每日最多五条的纯文本提醒。

**Architecture:** `spider-server` 在单独的监控任务中拉取完整榜单，并把事件和每日配额持久化到 SQLite。领域层只负责快照比较、评分、状态转换和消息渲染；qq-bot 传输层只负责调用 `Notify`。应用启动时先建立不告警的基线，随后按 30 分钟周期运行。

**Tech Stack:** Python 3.11、grpcio、protobuf、schedule、SQLite（标准库）、pytest；qq-bot `QQBotService.Notify`。

---

## 文件结构

| 路径 | 职责 |
| --- | --- |
| `protocol/qqbot.proto` | qq-bot `Notify` 的 Python 客户端协议快照。 |
| `protocol/gen.sh` | 同时生成 Spider 与 QQBot 的 Python protobuf/gRPC 文件。 |
| `pb/qqbot_pb2.py`、`pb/qqbot_pb2.pyi`、`pb/qqbot_pb2_grpc.py` | 由协议生成的客户端桩。 |
| `service/qqbot_notify.py` | 10 秒超时的 `Notify` 适配器和通知结果分类。 |
| `service/weibo_alert_state.py` | SQLite 事件、快照、配额与状态持久化。 |
| `service/weibo_breaking_alerts.py` | 标题标准化、评分、状态机和纯文本渲染。 |
| `job/weibo_breaking_alerts.py` | 拉取榜单、调用领域层、限额与重试编排。 |
| `job/__init__.py` | 注册启动基线和每 30 分钟任务。 |
| `util/config.py` | QQBot 地址和 SQLite 状态文件路径配置。 |
| `tests/test_qqbot_notify.py` | QQBot RPC 适配器测试。 |
| `tests/test_weibo_alert_state.py` | SQLite 状态与每日配额测试。 |
| `tests/test_weibo_breaking_alerts.py` | 评分、去重、完成、12 小时再爆发和消息测试。 |
| `tests/test_weibo_breaking_alert_job.py` | 基线、配额、投递结果和重试的端到端任务测试。 |

qq-bot 已在 `5b3d403` 提供 `Notify`；本计划不修改 qq-bot 业务代码。部署时必须使用包含该提交的 qq-bot 镜像。

### Task 1: 添加 QQBot Notify 协议与生成支持

**Files:**
- Create: `protocol/qqbot.proto`
- Modify: `protocol/gen.sh`
- Create: `pb/qqbot_pb2.py`
- Create: `pb/qqbot_pb2.pyi`
- Create: `pb/qqbot_pb2_grpc.py`
- Test: `tests/test_qqbot_notify.py`

- [ ] **Step 1: 写出失败的协议契约测试**

```python
from pb import qqbot_pb2


def test_qqbot_notify_request_has_content_field():
    request = qqbot_pb2.NotifyReq(content="爆点")

    assert request.content == "爆点"
```

- [ ] **Step 2: 验证测试失败**

Run: `PYTHONPATH=. .venv/bin/pytest tests/test_qqbot_notify.py::test_qqbot_notify_request_has_content_field -v`

Expected: FAIL with an import error because `pb.qqbot_pb2` does not exist.

- [ ] **Step 3: 添加最小协议快照和生成脚本支持**

Create `protocol/qqbot.proto`:

```proto
syntax = "proto3";

package proto;

service QQBotService {
  rpc Notify(NotifyReq) returns (Resp) {}
}

message NotifyReq {
  string content = 1;
}

message Resp {
  string message = 1;
}
```

Update `protocol/gen.sh` so it generates both `spider.proto` and `qqbot.proto`, then rewrites each generated `*_pb2_grpc.py` import to `from pb import <name>_pb2 as <name>__pb2`. Keep `PYTHON_BIN` override and location-independent paths.

- [ ] **Step 4: Generate and verify the contract**

Run: `PYTHON_BIN=.venv/bin/python bash protocol/gen.sh && PYTHONPATH=. .venv/bin/pytest tests/test_qqbot_notify.py::test_qqbot_notify_request_has_content_field -v`

Expected: PASS.

- [ ] **Step 5: Commit the protocol boundary**

```bash
git add protocol/qqbot.proto protocol/gen.sh pb/qqbot_pb2.py pb/qqbot_pb2.pyi pb/qqbot_pb2_grpc.py tests/test_qqbot_notify.py
git commit -m "feat: add qqbot Notify protobuf client"
```

### Task 2: 实现 QQBot Notify 传输适配器

**Files:**
- Create: `service/qqbot_notify.py`
- Modify: `util/config.py`
- Modify: `tests/test_qqbot_notify.py`

- [ ] **Step 1: 写出失败的通知结果测试**

```python
import pytest
from service.qqbot_notify import NotifyOutcome, QQBotNotifier


class Stub:
    def Notify(self, request, timeout):
        assert request.content == "正文"
        assert timeout == 10
        return type("Response", (), {"message": "没有可推送的订阅者"})()


def test_notifier_classifies_no_subscribers():
    notifier = QQBotNotifier("qq-bot:9090", stub_factory=lambda _address: Stub())

    assert notifier.notify("正文") is NotifyOutcome.NO_SUBSCRIBERS


def test_notifier_propagates_rpc_error():
    class FailingStub:
        def Notify(self, _request, timeout):
            raise RuntimeError("unavailable")

    notifier = QQBotNotifier("qq-bot:9090", stub_factory=lambda _address: FailingStub())

    with pytest.raises(RuntimeError, match="unavailable"):
        notifier.notify("正文")
```

- [ ] **Step 2: 验证测试失败**

Run: `PYTHONPATH=. .venv/bin/pytest tests/test_qqbot_notify.py -v`

Expected: FAIL because `service.qqbot_notify` is absent.

- [ ] **Step 3: 实现最小适配器与配置**

Implement the following public boundary:

```python
class NotifyOutcome(Enum):
    DELIVERED = "delivered"
    NO_SUBSCRIBERS = "no_subscribers"


class QQBotNotifier:
    def __init__(self, address: str, stub_factory=None): ...
    def notify(self, content: str) -> NotifyOutcome: ...
```

The default `stub_factory` must create `grpc.insecure_channel(address)`, build `qqbot_pb2_grpc.QQBotServiceStub`, invoke `Notify(qqbot_pb2.NotifyReq(content=content), timeout=10)`, return `NO_SUBSCRIBERS` only for the exact message `没有可推送的订阅者`, and return `DELIVERED` otherwise. Do not catch `grpc.RpcError` in this class.

Add `EnvConfig.qqbot_grpc_addr()` returning `QQ_BOT_GRPC_ADDR`, and fail job initialization with a clear `RuntimeError` when it is empty. Add `EnvConfig.weibo_alert_state_path()` returning `WEIBO_ALERT_STATE_PATH` and similarly require it.

- [ ] **Step 4: 验证适配器**

Run: `PYTHONPATH=. .venv/bin/pytest tests/test_qqbot_notify.py -v`

Expected: PASS.

- [ ] **Step 5: Commit the transport adapter**

```bash
git add service/qqbot_notify.py util/config.py tests/test_qqbot_notify.py
git commit -m "feat: add qqbot breaking-alert notifier"
```

### Task 3: 实现持久化事件状态和每日预算

**Files:**
- Create: `service/weibo_alert_state.py`
- Test: `tests/test_weibo_alert_state.py`

- [ ] **Step 1: 写出失败的 SQLite 状态测试**

```python
from datetime import datetime, timezone
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

    assert store.can_restart("事件", finished.replace(hour=11)) is False
    assert store.can_restart("事件", finished.replace(hour=12)) is True
```

- [ ] **Step 2: 验证测试失败**

Run: `PYTHONPATH=. .venv/bin/pytest tests/test_weibo_alert_state.py -v`

Expected: FAIL because the state store is absent.

- [ ] **Step 3: 实现 SQLite 状态存储**

Create an `AlertStateStore` using `sqlite3` with these tables:

```sql
CREATE TABLE events (
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
CREATE TABLE daily_delivery_budget (
  day TEXT PRIMARY KEY,
  delivered_count INTEGER NOT NULL
);
```

Expose `load_event`, `upsert_seen`, `mark_missing`, `complete`, `mark_notified`, `mark_no_subscribers`, `mark_retry`, `mark_failed`, `reserve_daily_delivery`, `can_restart`, and `active_event_keys`. `reserve_daily_delivery` must use one SQLite transaction and increment only when it returns `True`. Statuses are `OBSERVED`, `NOTIFIED`, `COMPLETED`, `NO_SUBSCRIBERS`, `FAILED`, and `SUPPRESSED_BY_BUDGET`.

- [ ] **Step 4: 扩展状态边界测试并验证**

Add tests that reopen only completed events after 12 hours, do not consume budget for no-subscriber outcomes, and preserve data after constructing a second store against the same path.

Run: `PYTHONPATH=. .venv/bin/pytest tests/test_weibo_alert_state.py -v`

Expected: PASS.

- [ ] **Step 5: Commit state persistence**

```bash
git add service/weibo_alert_state.py tests/test_weibo_alert_state.py
git commit -m "feat: persist Weibo alert event state"
```

### Task 4: 实现评分、状态转换和消息渲染

**Files:**
- Create: `service/weibo_breaking_alerts.py`
- Test: `tests/test_weibo_breaking_alerts.py`

- [ ] **Step 1: 写出失败的领域规则测试**

```python
from service.weibo_breaking_alerts import assess, render_notification


def test_new_top_ten_item_with_breaking_tag_reaches_threshold():
    assessment = assess(previous=None, current={
        "title": "测试事件", "url": "https://weibo.com/x", "rank": 1,
        "hot": 0, "tags": ["当前爆词"],
    })

    assert assessment.score == 8
    assert assessment.is_breaking is True
    assert assessment.reasons == ["新上榜", "Top 3", "爆点标签"]


def test_tag_outside_top_twenty_is_not_breaking():
    assessment = assess(previous=None, current={
        "title": "测试事件", "url": "https://weibo.com/x", "rank": 21,
        "hot": 0, "tags": ["爆"],
    })

    assert assessment.is_breaking is False


def test_renderer_matches_the_approved_plain_text_format():
    text = render_notification(
        title="测试事件", url="https://weibo.com/x", previous_rank=None,
        rank=1, tags=["当前爆词"], reasons=["新上榜", "Top 10", "爆点标签"],
    )

    assert text == (
        "💥💥💥 微博突发爆点\\n【测试事件】\\n"
        "排名：新上榜 → 第1\\n标签：当前爆词\\n"
        "触发：新上榜 + Top 10 + 爆点标签\\n链接：https://weibo.com/x"
    )
```

- [ ] **Step 2: 验证测试失败**

Run: `PYTHONPATH=. .venv/bin/pytest tests/test_weibo_breaking_alerts.py -v`

Expected: FAIL because the domain module is absent.

- [ ] **Step 3: 实现纯领域函数**

Implement `normalize_title`, `assess`, `render_notification`, and `advance_event` with no gRPC or SQLite calls.

`assess` must:

- award score exactly as in the approved specification;
- require a strong signal: new Top 10, rank increase >=15 into Top 20, heat increase >=100% into Top 20, or a breaking tag in Top 20;
- return `is_breaking=False` below score 5 or without a strong signal;
- use `hot=0` as “heat unavailable”, never as a heat-growth calculation.

`advance_event` must complete an event after two absent snapshots or two consecutive rank declines, and only permit a new round after 12 hours plus a fresh Top 10 appearance. It must return a state transition rather than writing persistence itself.

- [ ] **Step 4: 验证领域行为**

Add tests for rank jump, heat doubling, two absent snapshots, two rank declines, 12-hour reappearance, and normalized-title equality.

Run: `PYTHONPATH=. .venv/bin/pytest tests/test_weibo_breaking_alerts.py -v`

Expected: PASS.

- [ ] **Step 5: Commit the domain layer**

```bash
git add service/weibo_breaking_alerts.py tests/test_weibo_breaking_alerts.py
git commit -m "feat: score and deduplicate Weibo breaking events"
```

### Task 5: 编排采样、基线、配额与单次重试

**Files:**
- Create: `job/weibo_breaking_alerts.py`
- Modify: `job/__init__.py`
- Test: `tests/test_weibo_breaking_alert_job.py`

- [ ] **Step 1: 写出失败的任务测试**

```python
def test_first_snapshot_creates_baseline_without_notification(tmp_path):
    notifier = FakeNotifier()
    monitor = build_monitor(tmp_path, notifier, [top_one_breaking_snapshot()])

    monitor.run_once()

    assert notifier.contents == []


def test_second_snapshot_notifies_once_then_deduplicates(tmp_path):
    notifier = FakeNotifier()
    monitor = build_monitor(tmp_path, notifier, [baseline_snapshot(), top_one_breaking_snapshot()])

    monitor.run_once()
    monitor.run_once()
    monitor.run_once()

    assert len(notifier.contents) == 1
    assert notifier.contents[0].startswith("💥💥💥 微博突发爆点")
```

- [ ] **Step 2: 验证测试失败**

Run: `PYTHONPATH=. .venv/bin/pytest tests/test_weibo_breaking_alert_job.py -v`

Expected: FAIL because the monitor job is absent.

- [ ] **Step 3: 实现监控编排器**

Implement `WeiboBreakingAlertMonitor(fetch_hot_list, state_store, notifier, clock)` and `run_once()`.

`run_once()` must fetch all entries through `get_weibo_hot()`, write the initial snapshot as a baseline without scoring or notifying, assess subsequent snapshots, update absent entries, and call `notifier.notify()` only for eligible first-time events. When daily capacity is exhausted, mark events `SUPPRESSED_BY_BUDGET` and never backfill them on a later day. When `Notify` raises, keep the event eligible for exactly one retry on the next run; after the second error mark `FAILED`. When `Notify` returns `NO_SUBSCRIBERS`, mark `NO_SUBSCRIBERS` and do not retry.

In `job/__init__.py`, construct the monitor once, call `run_once()` once at startup to establish the baseline, then register:

```python
schedule.every(30).minutes.do(monitor.run_once)
```

Wrap each startup/run invocation in a logging boundary so a failed Weibo fetch or QQ RPC does not stop the existing Bing wallpaper scheduler.

- [ ] **Step 4: 验证编排边界**

Add fake-clock tests for five delivered events per day, no-subscriber handling, one retry then failure, completed-event silence, and a 12-hour Top 10 reappearance generating a second notification.

Run: `PYTHONPATH=. .venv/bin/pytest tests/test_weibo_breaking_alert_job.py -v`

Expected: PASS.

- [ ] **Step 5: Commit scheduler integration**

```bash
git add job/weibo_breaking_alerts.py job/__init__.py tests/test_weibo_breaking_alert_job.py
git commit -m "feat: monitor and notify Weibo breaking alerts"
```

### Task 6: 全量验证和配置运行手册

**Files:**
- Create: `docs/weibo-breaking-alerts-operations.md`
- Modify: `README.md`
- Test: `tests/test_weibo_breaking_alerts.py`

- [ ] **Step 1: 写出环境配置文档**

Document these required runtime variables without recording secrets:

```text
WEIBO_COOKIE=<existing secret reference>
QQ_BOT_GRPC_ADDR=qq-bot:9090
WEIBO_ALERT_STATE_PATH=/var/lib/spider-alerts/weibo-alerts.sqlite3
```

The runbook must require a durable single-writer mount at `/var/lib/spider-alerts`; an ephemeral container filesystem is not acceptable because it would lose de-duplication and resend alerts after a Pod restart. Include deployment verification commands for checking the mounted path, calling the `Notify` dependency, and reading only monitor logs.

- [ ] **Step 2: Run focused and full verification**

Run:

```bash
PYTHONPATH=. .venv/bin/pytest tests/test_qqbot_notify.py tests/test_weibo_alert_state.py tests/test_weibo_breaking_alerts.py tests/test_weibo_breaking_alert_job.py -v
PYTHONPATH=. .venv/bin/pytest -v
PYTHON_BIN=.venv/bin/python bash protocol/gen.sh
PYTHONPATH=. .venv/bin/pytest -v
git diff --check
```

Expected: all tests pass, protocol generation is idempotent, and `git diff --check` has no output.

- [ ] **Step 3: Commit operational documentation**

```bash
git add docs/weibo-breaking-alerts-operations.md README.md
git commit -m "docs: add Weibo breaking-alert operations guide"
```

- [ ] **Step 4: Deploy only after explicit approval**

Set the two non-secret variables and mount the durable state path in the `spider` Deployment. Confirm the qq-bot image contains `Notify` before restarting `spider`. Do not send synthetic production alerts; verify the first run only writes a baseline.

### Task 7: Final integration review and delivery

**Files:**
- Review: all files above

- [ ] **Step 1: Inspect the final diff and state-machine coverage**

Run:

```bash
git status --short
git log --oneline origin/master..HEAD
PYTHONPATH=. .venv/bin/pytest -v
```

Expected: only intended tracked changes, all tests pass, and each implementation commit is present.

- [ ] **Step 2: Request code review before merge/push**

Review specifically for: protobuf import generation, SQLite transaction safety, baseline behavior, daily budget accounting, 12-hour reopening, duplicate sends, and unhandled `grpc.RpcError` paths.

- [ ] **Step 3: Push and verify CI only after explicit approval**

Push the reviewed commits, verify Docker build and rollout, then inspect the first production baseline run. Do not manually invoke `Notify` with test content against real subscribers.
