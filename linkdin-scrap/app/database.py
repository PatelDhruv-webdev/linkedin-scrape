from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterable

from config import settings

DB_PATH = Path(settings.sqlite_db_path)


@contextmanager
def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recruiter_name TEXT,
                recruiter_url TEXT,
                company TEXT,
                post_content TEXT,
                post_url TEXT UNIQUE,
                post_date TEXT,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                search_keyword TEXT,
                bookmarked INTEGER DEFAULT 0,
                notes TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS searches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                keyword TEXT,
                time_filter TEXT,
                results_found INTEGER,
                searched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def save_posts(posts: Iterable[dict], keyword: str) -> int:
    inserted = 0
    with get_conn() as conn:
        for post in posts:
            try:
                conn.execute(
                    """
                    INSERT INTO posts (
                        recruiter_name, recruiter_url, company, post_content,
                        post_url, post_date, search_keyword
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        post.get("recruiter_name"),
                        post.get("recruiter_url"),
                        post.get("company"),
                        post.get("post_content"),
                        post.get("post_url"),
                        post.get("post_date"),
                        keyword,
                    ),
                )
                inserted += 1
            except sqlite3.IntegrityError:
                continue
    return inserted


def log_search(keyword: str, time_filter: str, results_found: int) -> None:
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO searches (keyword, time_filter, results_found) VALUES (?, ?, ?)",
            (keyword, time_filter, results_found),
        )


def latest_results(limit: int = 100) -> list[sqlite3.Row]:
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT * FROM posts
            ORDER BY scraped_at DESC, id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return rows
