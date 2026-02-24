from __future__ import annotations

from bs4 import BeautifulSoup


def parse_search_results(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    posts: list[dict] = []

    cards = soup.select("div.feed-shared-update-v2")
    for card in cards:
        author_anchor = card.select_one("a.app-aware-link")
        author_text = card.select_one("span.update-components-actor__name")
        headline = card.select_one("span.update-components-actor__description")
        post_link = card.select_one('a[href*="/feed/update/"]')
        post_text = card.select_one("div.update-components-text")
        date_text = card.select_one("span.update-components-actor__sub-description")

        posts.append(
            {
                "recruiter_name": author_text.get_text(" ", strip=True) if author_text else "Unknown",
                "recruiter_url": author_anchor.get("href", "") if author_anchor else "",
                "company": headline.get_text(" ", strip=True) if headline else "",
                "post_content": post_text.get_text(" ", strip=True) if post_text else "",
                "post_url": post_link.get("href", "") if post_link else "",
                "post_date": date_text.get_text(" ", strip=True) if date_text else "",
            }
        )

    unique: dict[str, dict] = {}
    for post in posts:
        key = post.get("post_url") or f"{post.get('recruiter_name')}::{post.get('post_content', '')[:40]}"
        unique[key] = post

    return list(unique.values())
