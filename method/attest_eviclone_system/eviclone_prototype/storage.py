from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path), timeout=30.0)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    init_db(conn)
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            dataset_path TEXT NOT NULL,
            policy TEXT NOT NULL,
            model TEXT,
            with_llm INTEGER NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS evidence_cards (
            run_id INTEGER NOT NULL,
            pair_id INTEGER NOT NULL,
            gold_label INTEGER NOT NULL,
            pred_label INTEGER,
            verdict TEXT NOT NULL,
            confidence REAL,
            card_json TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            PRIMARY KEY (run_id, pair_id)
        )
        """
    )
    conn.commit()


def get_or_create_run(
    conn: sqlite3.Connection,
    *,
    name: str,
    dataset_path: Path,
    policy: str,
    model: str,
    with_llm: bool,
) -> int:
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        """
        INSERT OR IGNORE INTO runs (name, dataset_path, policy, model, with_llm, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (name, str(dataset_path), policy, model, 1 if with_llm else 0, now),
    )
    row = conn.execute("SELECT id FROM runs WHERE name=?", (name,)).fetchone()
    conn.commit()
    if not row:
        raise RuntimeError(f"failed to create run: {name}")
    return int(row[0])


def upsert_card(conn: sqlite3.Connection, run_id: int, card: dict[str, Any]) -> None:
    decision = card.get("decision", {})
    pred = decision.get("pred_label")
    pred_db = int(pred) if pred in (0, 1) else None
    conn.execute(
        """
        INSERT INTO evidence_cards
        (run_id, pair_id, gold_label, pred_label, verdict, confidence, card_json, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(run_id, pair_id) DO UPDATE SET
            gold_label=excluded.gold_label,
            pred_label=excluded.pred_label,
            verdict=excluded.verdict,
            confidence=excluded.confidence,
            card_json=excluded.card_json,
            updated_at=excluded.updated_at
        """,
        (
            run_id,
            int(card["pair_id"]),
            int(card["gold"]["label"]),
            pred_db,
            str(decision.get("verdict", "unknown")),
            decision.get("confidence"),
            json.dumps(card, ensure_ascii=False),
            datetime.now(timezone.utc).isoformat(),
        ),
    )
