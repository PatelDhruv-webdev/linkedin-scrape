from __future__ import annotations

from flask import Blueprint, redirect, render_template, request, url_for

from app.database import latest_results, log_search, save_posts
from config import settings

bp = Blueprint("main", __name__)

SAMPLE_PREVIEW_RESULTS = [
    {
        "recruiter_name": "Sarah Malik",
        "company": "Recruiter @ Amazon",
        "post_date": "2 hours ago",
        "post_content": "We're actively hiring warehouse team leads in Dallas and Austin. If you have shift-management experience, DM me your resume.",
        "post_url": "https://www.linkedin.com/feed/update/sample-1",
    },
    {
        "recruiter_name": "James Okafor",
        "company": "HR Manager @ Shopify",
        "post_date": "5 hours ago",
        "post_content": "Looking for a project manager with PMP cert and e-commerce operations background. Remote and hybrid roles available.",
        "post_url": "https://www.linkedin.com/feed/update/sample-2",
    },
]


@bp.get("/")
def index():
    return render_template("index.html", default_time_filter=settings.default_time_filter)


@bp.get("/preview")
def preview():
    return render_template(
        "results.html",
        results=SAMPLE_PREVIEW_RESULTS,
        keyword="preview-demo",
        inserted=len(SAMPLE_PREVIEW_RESULTS),
        preview_mode=True,
    )


@bp.post("/search")
def search():
    keyword = request.form.get("query", "").strip()
    time_filter = request.form.get("time_filter", settings.default_time_filter)
    if not keyword:
        return redirect(url_for("main.results"))

    try:
        from app.scraper import LinkedInScraper
    except ModuleNotFoundError as exc:
        return render_template(
            "results.html",
            results=[],
            keyword=keyword,
            inserted="0",
            error_message=f"Missing dependency: {exc}. Install requirements first.",
        )

    scraper = LinkedInScraper()
    try:
        scraper.login()
        posts = scraper.search_posts(keyword=keyword, time_filter=time_filter)
    finally:
        scraper.close()

    inserted = save_posts(posts, keyword)
    log_search(keyword, time_filter, inserted)

    return redirect(url_for("main.results", keyword=keyword, inserted=inserted))


@bp.get("/results")
def results():
    rows = latest_results(limit=settings.max_posts)
    return render_template(
        "results.html",
        results=rows,
        keyword=request.args.get("keyword", ""),
        inserted=request.args.get("inserted", "0"),
        preview_mode=False,
    )
