from __future__ import annotations

import json
import random
import time
from pathlib import Path
from urllib.parse import quote_plus

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from app.parser import parse_search_results
from config import settings


class LinkedInScraper:
    LOGIN_URL = "https://www.linkedin.com/login"
    BASE_SEARCH_URL = "https://www.linkedin.com/search/results/content/?keywords={keyword}&sortBy=%22date_posted%22"

    TIME_FILTER_PARAM = {
        "past_hour": "&datePosted=%22past-24h%22",
        "past_24_hours": "&datePosted=%22past-24h%22",
        "past_7_days": "&datePosted=%22past-week%22",
        "past_30_days": "&datePosted=%22past-month%22",
    }

    def __init__(self) -> None:
        chrome_options = Options()
        if settings.headless_mode:
            chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--window-size=1366,768")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--no-sandbox")

        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options,
        )
        self.cookies_file = Path(settings.cookie_file)

    def close(self) -> None:
        self.driver.quit()

    def _human_delay(self, low: float = 2.0, high: float = 5.0) -> None:
        time.sleep(random.uniform(low, high))

    def login(self) -> None:
        self.driver.get("https://www.linkedin.com")
        if self._load_cookies_if_available():
            self.driver.refresh()
            if "feed" in self.driver.current_url or "linkedin.com" in self.driver.current_url:
                return

        self.driver.get(self.LOGIN_URL)
        WebDriverWait(self.driver, 25).until(EC.presence_of_element_located((By.ID, "username")))

        self.driver.find_element(By.ID, "username").send_keys(settings.linkedin_email)
        self.driver.find_element(By.ID, "password").send_keys(settings.linkedin_password)
        self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

        self._human_delay(4, 6)
        self._save_cookies()

    def search_posts(self, keyword: str, time_filter: str, max_posts: int | None = None) -> list[dict]:
        target = max_posts or settings.max_posts
        filter_param = self.TIME_FILTER_PARAM.get(time_filter, self.TIME_FILTER_PARAM["past_24_hours"])
        search_url = self.BASE_SEARCH_URL.format(keyword=quote_plus(keyword)) + filter_param

        self.driver.get(search_url)
        self._human_delay()

        collected: list[dict] = []
        previous_count = 0

        for _ in range(10):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            self._human_delay(2, 3)

            parsed = parse_search_results(self.driver.page_source)
            collected = parsed

            if len(collected) >= target:
                break
            if len(collected) == previous_count:
                break
            previous_count = len(collected)

        return collected[:target]

    def _save_cookies(self) -> None:
        cookies = self.driver.get_cookies()
        with self.cookies_file.open("w", encoding="utf-8") as f:
            json.dump(cookies, f)

    def _load_cookies_if_available(self) -> bool:
        if not self.cookies_file.exists():
            return False

        try:
            with self.cookies_file.open("r", encoding="utf-8") as f:
                cookies = json.load(f)

            self.driver.get("https://www.linkedin.com")
            for cookie in cookies:
                cookie.pop("sameSite", None)
                self.driver.add_cookie(cookie)
            return True
        except (json.JSONDecodeError, TimeoutException, NoSuchElementException):
            return False
