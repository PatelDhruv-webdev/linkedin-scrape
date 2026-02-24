# linkdin scrap (Phase 1 MVP)

Local Flask + Selenium app for monitoring LinkedIn recruiter posts by keyword.

## Implemented in this MVP
- LinkedIn login via `.env` credentials
- Cookie caching for session reuse
- Keyword search + time-filtered search URL
- Basic parsing of feed cards
- SQLite persistence (`posts`, `searches`)
- Basic HTML UI to trigger search and list results
- Preview route at `/preview` so you can see the UI without LinkedIn login or Selenium running

## Run locally
1. Create virtual env and install:
   ```bash
   pip install -r requirements.txt
   ```
2. Copy env template:
   ```bash
   cp .env.example .env
   ```
3. Update `.env` with your LinkedIn credentials.
4. Start app:
   ```bash
   python run.py
   ```
5. Open:
   - Main page: `http://127.0.0.1:5000`
   - Instant preview: `http://127.0.0.1:5000/preview`

> Use a dedicated LinkedIn account as recommended in your PRD.
