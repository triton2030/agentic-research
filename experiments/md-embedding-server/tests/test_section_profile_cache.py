from __future__ import annotations

import json
import sqlite3

from navigator import section_profile


class TrackingConnection(sqlite3.Connection):
    def commit(self) -> None:
        self.commit_calls = getattr(self, "commit_calls", 0) + 1
        super().commit()

    def rollback(self) -> None:
        self.rollback_calls = getattr(self, "rollback_calls", 0) + 1
        super().rollback()


def _make_profile_conn(section_count: int = 1) -> TrackingConnection:
    conn = sqlite3.connect(":memory:", factory=TrackingConnection)
    conn.execute(
        "CREATE TABLE sections ("
        "section_id TEXT,"
        "scope TEXT,"
        "relative_path TEXT,"
        "start_line INTEGER,"
        "level INTEGER,"
        "heading_text TEXT,"
        "heading_chain TEXT,"
        "body TEXT,"
        "token_count INTEGER,"
        "profile_type TEXT,"
        "profile_subject TEXT,"
        "profile_owns_terms TEXT,"
        "profile_mentions TEXT,"
        "profile_evidence TEXT,"
        "profile_confidence REAL,"
        "profile_version TEXT,"
        "profile_model TEXT,"
        "profile_classified_at TEXT,"
        "profile_source_mtime REAL,"
        "profile_method TEXT"
        ")"
    )
    for idx in range(section_count):
        conn.execute(
            "INSERT INTO sections ("
            "section_id, scope, relative_path, start_line, level, "
            "heading_text, heading_chain, body, token_count"
            ") VALUES (?, 'sections', ?, ?, 2, ?, ?, ?, 12)",
            (
                f"s{idx}",
                f"file-{idx}.md",
                idx + 1,
                "Runtime Rule",
                "Runtime Rule",
                "Always verify evidence. Never claim done without tests.",
            ),
        )
    conn.commit()
    conn.commit_calls = 0
    conn.rollback_calls = 0
    return conn


def test_profile_auto_success_caches_llm_path(monkeypatch) -> None:
    calls: list[str] = []

    class Client:
        def __init__(self, **kwargs):
            pass

        def completion(self, **kwargs):
            calls.append(kwargs["model"])
            return json.dumps(
                {
                    "type": "rule",
                    "subject": "LLM classified rule",
                    "owns_terms": ["rule"],
                    "mentions": [],
                    "evidence_sources": [],
                    "confidence": 0.91,
                }
            )

    monkeypatch.setattr(section_profile, "OpenRouterClient", Client)
    conn = _make_profile_conn()

    first = section_profile.profile_corpus(conn, mode="auto", model="test-llm")
    second = section_profile.profile_corpus(conn, mode="auto", model="test-llm")
    row = conn.execute(
        "SELECT profile_model, profile_method, profile_subject FROM sections"
    ).fetchone()

    assert first["profiled"] == 1
    assert first["skipped_cached"] == 0
    assert second["profiled"] == 0
    assert second["skipped_cached"] == 1
    assert calls == ["test-llm"]
    assert row == ("test-llm", "llm", "LLM classified rule")


def test_profile_auto_fallback_caches_heuristic_path(monkeypatch) -> None:
    calls: list[str] = []

    class Client:
        def __init__(self, **kwargs):
            pass

        def completion(self, **kwargs):
            calls.append(kwargs["model"])
            raise RuntimeError("completion unavailable")

    monkeypatch.setattr(section_profile, "OpenRouterClient", Client)
    conn = _make_profile_conn()

    stats = section_profile.profile_corpus(conn, mode="auto", model="test-llm")
    row = conn.execute(
        "SELECT profile_model, profile_method, profile_type FROM sections"
    ).fetchone()

    assert stats["profiled"] == 1
    assert stats["failed"] == 0
    assert calls == ["test-llm"]
    assert row == (section_profile.HEURISTIC_MODEL, "heuristic", "rule")


def test_profile_commits_each_write_before_next_classification(monkeypatch) -> None:
    conn = _make_profile_conn(section_count=2)
    classification_transaction_states: list[bool] = []
    original = section_profile.classify_section_heuristic

    def spy(section):
        classification_transaction_states.append(conn.in_transaction)
        return original(section)

    monkeypatch.setattr(section_profile, "classify_section_heuristic", spy)

    stats = section_profile.profile_corpus(conn, mode="heuristic")

    assert stats["profiled"] == 2
    assert classification_transaction_states == [False, False]
    assert conn.commit_calls == 2
