from __future__ import annotations

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    linkedin_email: str = os.getenv("LINKEDIN_EMAIL", "")
    linkedin_password: str = os.getenv("LINKEDIN_PASSWORD", "")
    headless_mode: bool = os.getenv("HEADLESS_MODE", "False").lower() == "true"
    default_time_filter: str = os.getenv("DEFAULT_TIME_FILTER", "past_24_hours")
    max_posts: int = int(os.getenv("MAX_POSTS", "50"))
    sqlite_db_path: str = os.getenv("SQLITE_DB_PATH", "linkedin_monitor.db")
    cookie_file: str = os.getenv("COOKIE_FILE", "linkedin_cookies.json")


settings = Settings()
