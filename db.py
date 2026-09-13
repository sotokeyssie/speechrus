"""SQLite helpers for the Speech R' Us public site."""
from __future__ import annotations

import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
DB_PATH = DATA_DIR / "site.db"


def get_conn() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def init_db() -> None:
    conn = get_conn()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL DEFAULT 'Administradora'
        );

        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slug TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            excerpt TEXT NOT NULL DEFAULT '',
            body TEXT NOT NULL DEFAULT '',
            cover TEXT NOT NULL DEFAULT '',
            category TEXT NOT NULL DEFAULT 'Consejos',
            status TEXT NOT NULL DEFAULT 'draft',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            published_at TEXT,
            slides TEXT NOT NULL DEFAULT '',
            author TEXT NOT NULL DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS appointment_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parent_name TEXT NOT NULL,
            child_name TEXT NOT NULL DEFAULT '',
            child_age TEXT NOT NULL DEFAULT '',
            phone TEXT NOT NULL,
            email TEXT NOT NULL DEFAULT '',
            clinic TEXT NOT NULL DEFAULT 'Hormigueros',
            service TEXT NOT NULL DEFAULT '',
            preferred TEXT NOT NULL DEFAULT '',
            notes TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'nueva',
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS info_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL DEFAULT '',
            email TEXT NOT NULL DEFAULT '',
            topic TEXT NOT NULL DEFAULT 'Información general',
            message TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'nueva',
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS team (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            credential TEXT NOT NULL DEFAULT '',
            sort INTEGER NOT NULL DEFAULT 0,
            visible INTEGER NOT NULL DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            title_en TEXT NOT NULL DEFAULT '',
            when_at TEXT NOT NULL DEFAULT '',
            place TEXT NOT NULL DEFAULT '',
            notes TEXT NOT NULL DEFAULT '',
            notes_en TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS quotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quote TEXT NOT NULL,
            quote_en TEXT NOT NULL DEFAULT '',
            who TEXT NOT NULL DEFAULT '',
            visible INTEGER NOT NULL DEFAULT 1,
            sort INTEGER NOT NULL DEFAULT 0
        );
        """
    )
    cols = {r[1] for r in conn.execute("PRAGMA table_info(articles)").fetchall()}
    for col, spec in (
        ("slides", "TEXT NOT NULL DEFAULT ''"),
        ("author", "TEXT NOT NULL DEFAULT ''"),
        ("title_en", "TEXT NOT NULL DEFAULT ''"),
        ("excerpt_en", "TEXT NOT NULL DEFAULT ''"),
        ("body_en", "TEXT NOT NULL DEFAULT ''"),
        ("cover_en", "TEXT NOT NULL DEFAULT ''"),
        ("category_en", "TEXT NOT NULL DEFAULT ''"),
        ("slides_en", "TEXT NOT NULL DEFAULT ''"),
    ):
        if col not in cols:
            conn.execute(f"ALTER TABLE articles ADD COLUMN {col} {spec}")
    conn.commit()
    conn.close()


def fetch_all(sql: str, params: tuple = ()) -> list[sqlite3.Row]:
    conn = get_conn()
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return rows


def fetch_one(sql: str, params: tuple = ()) -> sqlite3.Row | None:
    conn = get_conn()
    row = conn.execute(sql, params).fetchone()
    conn.close()
    return row


def execute(sql: str, params: tuple = ()) -> int:
    conn = get_conn()
    cur = conn.execute(sql, params)
    conn.commit()
    last_id = cur.lastrowid or 0
    conn.close()
    return int(last_id)


def settings_map() -> dict[str, str]:
    rows = fetch_all("SELECT key, value FROM settings")
    return {r["key"]: r["value"] for r in rows}


def set_setting(key: str, value: str) -> None:
    execute(
        "INSERT INTO settings(key, value) VALUES(?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, value),
    )
