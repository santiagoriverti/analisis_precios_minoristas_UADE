"""Memoria persistente del proyecto: SQLite para estado de runs y cache de resultados.

Permite que el orquestador multi-agente recuerde:
  - Qué análisis se corrieron y cuándo
  - Dónde están los archivos de resultados
  - Qué períodos ya fueron procesados
  - Historial de conversaciones con el agente
"""
from __future__ import annotations

import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from ..config.settings import MEMORY_DB

log = logging.getLogger(__name__)

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS runs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    run_type    TEXT NOT NULL,      -- 'daily', 'semester', 'consolidation', 'map', 'ranking'
    period      TEXT,               -- 'YYYY-MM-DD' o 'YYYY-S'
    status      TEXT NOT NULL,      -- 'started', 'completed', 'failed'
    started_at  TEXT NOT NULL,
    finished_at TEXT,
    output_path TEXT,
    notes       TEXT
);

CREATE TABLE IF NOT EXISTS artifacts (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id      INTEGER REFERENCES runs(id),
    artifact_type TEXT NOT NULL,    -- 'excel', 'parquet', 'map_html', 'chart_png'
    path        TEXT NOT NULL,
    period      TEXT,
    description TEXT,
    created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS agent_sessions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id  TEXT NOT NULL UNIQUE,
    task        TEXT,
    messages    TEXT,               -- JSON serializado
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS kv_store (
    key         TEXT PRIMARY KEY,
    value       TEXT NOT NULL,
    updated_at  TEXT NOT NULL
);
"""


class MemoryManager:
    """Interfaz de alto nivel sobre la base de datos de memoria."""

    def __init__(self, db_path: Path | None = None):
        self.db_path = Path(db_path or MEMORY_DB)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._conn() as conn:
            conn.executescript(SCHEMA_SQL)

    # ── Runs ───────────────────────────────────────────────────────────────

    def start_run(self, run_type: str, period: str | None = None, notes: str | None = None) -> int:
        with self._conn() as conn:
            cur = conn.execute(
                "INSERT INTO runs (run_type, period, status, started_at, notes) VALUES (?,?,?,?,?)",
                (run_type, period, "started", _now(), notes),
            )
            run_id = cur.lastrowid
        log.info("Run iniciado: id=%d type=%s period=%s", run_id, run_type, period)
        return run_id

    def complete_run(self, run_id: int, output_path: str | None = None):
        with self._conn() as conn:
            conn.execute(
                "UPDATE runs SET status='completed', finished_at=?, output_path=? WHERE id=?",
                (_now(), output_path, run_id),
            )

    def fail_run(self, run_id: int, error: str):
        with self._conn() as conn:
            conn.execute(
                "UPDATE runs SET status='failed', finished_at=?, notes=? WHERE id=?",
                (_now(), error, run_id),
            )

    def get_last_run(self, run_type: str, period: str | None = None) -> dict | None:
        with self._conn() as conn:
            if period:
                row = conn.execute(
                    "SELECT * FROM runs WHERE run_type=? AND period=? ORDER BY id DESC LIMIT 1",
                    (run_type, period),
                ).fetchone()
            else:
                row = conn.execute(
                    "SELECT * FROM runs WHERE run_type=? ORDER BY id DESC LIMIT 1",
                    (run_type,),
                ).fetchone()
        return dict(row) if row else None

    def list_completed_periods(self, run_type: str) -> list[str]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT DISTINCT period FROM runs WHERE run_type=? AND status='completed' AND period IS NOT NULL ORDER BY period",
                (run_type,),
            ).fetchall()
        return [r["period"] for r in rows]

    # ── Artifacts ─────────────────────────────────────────────────────────

    def register_artifact(self, run_id: int, artifact_type: str, path: Path,
                          period: str | None = None, description: str | None = None):
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO artifacts (run_id, artifact_type, path, period, description, created_at) VALUES (?,?,?,?,?,?)",
                (run_id, artifact_type, str(path), period, description, _now()),
            )

    def find_artifact(self, artifact_type: str, period: str | None = None) -> Path | None:
        with self._conn() as conn:
            if period:
                row = conn.execute(
                    "SELECT path FROM artifacts WHERE artifact_type=? AND period=? ORDER BY id DESC LIMIT 1",
                    (artifact_type, period),
                ).fetchone()
            else:
                row = conn.execute(
                    "SELECT path FROM artifacts WHERE artifact_type=? ORDER BY id DESC LIMIT 1",
                    (artifact_type,),
                ).fetchone()
        if row:
            p = Path(row["path"])
            return p if p.exists() else None
        return None

    def list_artifacts(self, artifact_type: str | None = None) -> list[dict]:
        with self._conn() as conn:
            if artifact_type:
                rows = conn.execute(
                    "SELECT * FROM artifacts WHERE artifact_type=? ORDER BY id DESC",
                    (artifact_type,),
                ).fetchall()
            else:
                rows = conn.execute("SELECT * FROM artifacts ORDER BY id DESC").fetchall()
        return [dict(r) for r in rows]

    # ── Agent sessions ─────────────────────────────────────────────────────

    def save_session(self, session_id: str, task: str, messages: list[dict]):
        now = _now()
        with self._conn() as conn:
            conn.execute(
                """INSERT INTO agent_sessions (session_id, task, messages, created_at, updated_at)
                   VALUES (?,?,?,?,?)
                   ON CONFLICT(session_id) DO UPDATE SET messages=excluded.messages, updated_at=excluded.updated_at""",
                (session_id, task, json.dumps(messages, ensure_ascii=False), now, now),
            )

    def load_session(self, session_id: str) -> dict | None:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM agent_sessions WHERE session_id=?", (session_id,)
            ).fetchone()
        if row:
            d = dict(row)
            d["messages"] = json.loads(d["messages"])
            return d
        return None

    # ── KV store ───────────────────────────────────────────────────────────

    def set(self, key: str, value: Any):
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO kv_store (key, value, updated_at) VALUES (?,?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at",
                (key, json.dumps(value, ensure_ascii=False, default=str), _now()),
            )

    def get(self, key: str, default: Any = None) -> Any:
        with self._conn() as conn:
            row = conn.execute("SELECT value FROM kv_store WHERE key=?", (key,)).fetchone()
        return json.loads(row["value"]) if row else default

    def summary(self) -> dict:
        with self._conn() as conn:
            runs = conn.execute("SELECT run_type, status, COUNT(*) as n FROM runs GROUP BY run_type, status").fetchall()
            arts = conn.execute("SELECT artifact_type, COUNT(*) as n FROM artifacts GROUP BY artifact_type").fetchall()
        return {
            "runs": [dict(r) for r in runs],
            "artifacts": [dict(a) for a in arts],
        }


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")
