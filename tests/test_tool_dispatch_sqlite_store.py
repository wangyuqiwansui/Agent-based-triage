"""Transactional store tests for tool dispatch / 工具调度事务存储测试。"""

from __future__ import annotations

from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DIR = ROOT / "skills" / "harness-engineering-patterns" / "runtime"
sys.path.insert(0, str(RUNTIME_DIR))

from tool_dispatch import (  # noqa: E402
    LeaseDisposition,
    ToolDispatchConflictError,
)
from tool_dispatch_sqlite_store import (  # noqa: E402
    SQLITE_TOOL_DISPATCH_SCHEMA_VERSION,
    SqliteToolDispatchStore,
)


NOW = "2026-07-24T08:00:00Z"
LATER = "2026-07-24T08:02:00Z"
HASH_A = "sha256:" + "a" * 64


def test_concurrent_store_instances_share_one_lease(tmp_path: Path) -> None:
    path = tmp_path / "shared.sqlite"
    first_store = SqliteToolDispatchStore(path)
    second_store = SqliteToolDispatchStore(path)

    first = first_store.acquire(
        idempotency_key="business-key",
        intent_hash=HASH_A,
        action_id="ACTION_1",
        attempt_id="ATTEMPT_1",
        acquired_at=NOW,
        lease_seconds=60,
        retry_authorized=False,
    )
    second = second_store.acquire(
        idempotency_key="business-key",
        intent_hash=HASH_A,
        action_id="ACTION_1",
        attempt_id="ATTEMPT_1",
        acquired_at=NOW,
        lease_seconds=60,
        retry_authorized=False,
    )

    assert first.disposition is LeaseDisposition.ACQUIRED
    assert second.disposition is LeaseDisposition.BUSY
    assert first.lease_binding == second.lease_binding


def test_expired_write_lease_becomes_unknown_not_reassigned(tmp_path: Path) -> None:
    store = SqliteToolDispatchStore(tmp_path / "expired.sqlite")
    store.acquire(
        idempotency_key="business-key",
        intent_hash=HASH_A,
        action_id="ACTION_1",
        attempt_id="ATTEMPT_1",
        acquired_at=NOW,
        lease_seconds=30,
        retry_authorized=False,
    )

    reacquire = store.acquire(
        idempotency_key="business-key",
        intent_hash=HASH_A,
        action_id="ACTION_2",
        attempt_id="ATTEMPT_2",
        acquired_at=LATER,
        lease_seconds=30,
        retry_authorized=True,
    )

    assert reacquire.disposition is LeaseDisposition.VERIFY_UNKNOWN
    assert store.idempotency_status("business-key")["status"] == "unknown"


def test_conflicting_idempotency_intent_fails_closed(tmp_path: Path) -> None:
    store = SqliteToolDispatchStore(tmp_path / "conflict.sqlite")
    store.acquire(
        idempotency_key="business-key",
        intent_hash=HASH_A,
        action_id="ACTION_1",
        attempt_id="ATTEMPT_1",
        acquired_at=NOW,
        lease_seconds=60,
        retry_authorized=False,
    )

    with pytest.raises(ToolDispatchConflictError, match="conflicts"):
        store.acquire(
            idempotency_key="business-key",
            intent_hash="sha256:" + "b" * 64,
            action_id="ACTION_2",
            attempt_id="ATTEMPT_2",
            acquired_at=NOW,
            lease_seconds=60,
            retry_authorized=False,
        )


def test_store_health_reports_mechanics_without_secret_content(
    tmp_path: Path,
) -> None:
    store = SqliteToolDispatchStore(tmp_path / "health.sqlite")

    health = store.health_check()

    assert health["healthy"] is True
    assert health["schema_version"] == SQLITE_TOOL_DISPATCH_SCHEMA_VERSION
    assert health["journal_mode"] == "wal"
    assert health["quick_check"] == "ok"
    assert "idempotency_key" not in health
    assert "lease_token" not in health
