#!/usr/bin/env python3
import argparse
import json
import os
import sys
from datetime import date, datetime
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover - handled by runtime usage
    print("Playwright is required. Install with: pip install playwright && playwright install chromium")
    sys.exit(1)


DEFAULT_BASE_URL = "http://127.0.0.1:8000"
DEFAULT_EMAIL = "calendar.qa@example.com"
DEFAULT_VIEWPORT = "1440x900"


def parse_bool(value: str) -> bool:
    return value.strip().lower() not in {"0", "false", "no", "off"}


def parse_viewport(value: str) -> dict:
    if "x" not in value:
        raise ValueError("Viewport must be formatted as WIDTHxHEIGHT, e.g., 1440x900")
    width, height = value.split("x", 1)
    return {"width": int(width), "height": int(height)}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_cases(case_ids: list[str] | None) -> list[dict]:
    fixture_path = repo_root() / "lifeos" / "tests" / "fixtures" / "calendar_time_canvas_cases.json"
    payload = json.loads(fixture_path.read_text())
    cases = payload.get("cases", [])
    if case_ids:
        wanted = set(case_ids)
        cases = [case for case in cases if case.get("id") in wanted]
    cases.sort(key=lambda case: case.get("date", ""))
    return cases


def parse_date(date_str: str) -> date:
    return datetime.strptime(date_str, "%Y-%m-%d").date()


def ensure_view(page, view: str) -> None:
    page.click(f'.cal-view-btn[data-view="{view}"]')
    page.wait_for_selector(f"#cal-{view}-view", state="visible")


def wait_for_events(page, view: str) -> None:
    selectors = {
        "day": ".cal-event-card, .cal-all-day-chip",
        "week": ".cal-event-card, .cal-week-all-day-bar",
        "month": ".cal-month-bar, .cal-more-btn",
    }
    selector = selectors.get(view, ".cal-event-card")
    page.wait_for_selector(selector, timeout=15000, state="attached")


def navigate_days(page, current: date, target: date) -> None:
    diff_days = (target - current).days
    if diff_days == 0:
        return
    button = "#cal-nav-next" if diff_days > 0 else "#cal-nav-prev"
    steps = abs(diff_days)
    for _ in range(steps):
        page.click(button)
        page.wait_for_timeout(30)


def open_quickview(page, view: str) -> bool:
    selector_order = [
        ".cal-event-card",
        ".cal-all-day-chip",
        ".cal-week-all-day-bar",
        ".cal-month-bar",
    ]
    for selector in selector_order:
        locator = page.locator(selector)
        if locator.count() == 0:
            continue
        try:
            target = locator.first
            target.scroll_into_view_if_needed()
            target.hover(timeout=5000, force=True)
            page.wait_for_selector("#cal-quickview", state="visible", timeout=3000)
            return True
        except Exception:
            continue
    return False


def login(page, base_url: str, email: str, password: str, login_path: str) -> None:
    page.goto(f"{base_url}{login_path}", wait_until="networkidle")

    login_email = page.locator("#lp-email")
    if login_email.count() > 0:
        login_email.fill(email)
        page.fill("#lp-password", password)
        page.click("#lp-login-form button[type=submit]")
        page.wait_for_url("**/calendar/**", timeout=15000)
        page.wait_for_selector("#cal-nav-today", timeout=15000)
        return

    # Fallback: if already authenticated, the calendar view is available.
    if page.locator("#cal-nav-today").count() > 0:
        page.wait_for_selector("#cal-nav-today", timeout=5000)
        return

    current = page.url
    raise RuntimeError(f"Login form not found. Current URL: {current}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture Calendar time-canvas snapshots with Playwright.")
    parser.add_argument("--case", action="append", dest="cases", help="Capture a specific case id (repeatable).")
    args = parser.parse_args()

    base_url = os.getenv("BASE_URL", DEFAULT_BASE_URL).rstrip("/")
    login_path = os.getenv("LOGIN_PATH", "/login")
    email = os.getenv("CALENDAR_EMAIL", DEFAULT_EMAIL)
    password = os.getenv("CALENDAR_PASSWORD")
    if not password:
        print("Missing CALENDAR_PASSWORD environment variable.")
        return 1

    output_dir = Path(os.getenv(
        "OUTPUT_DIR",
        repo_root() / "lifeos" / "docs" / "tasks" / "phase_4_calendar_time_canvas_ui_snapshots",
    ))
    output_dir.mkdir(parents=True, exist_ok=True)

    headless = parse_bool(os.getenv("HEADLESS", "1"))
    viewport = parse_viewport(os.getenv("VIEWPORT", DEFAULT_VIEWPORT))

    cases = load_cases(args.cases)
    if not cases:
        print("No cases found to capture.")
        return 1

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(viewport=viewport)
        page = context.new_page()

        login(page, base_url, email, password, login_path)
        ensure_view(page, "day")
        page.click("#cal-nav-today")
        page.wait_for_timeout(200)

        current_date = date.today()

        for case in cases:
            case_id = case.get("id")
            view = case.get("view", "day")
            target_date = parse_date(case.get("date"))

            ensure_view(page, "day")
            navigate_days(page, current_date, target_date)
            current_date = target_date

            ensure_view(page, view)
            wait_for_events(page, view)

            page.evaluate("window.scrollTo(0, 0)")
            screenshot_path = output_dir / f"case_{case_id}.png"
            page.screenshot(path=str(screenshot_path), full_page=True)
            print(f"Captured {screenshot_path}")

            if open_quickview(page, view):
                quickview_path = output_dir / f"case_{case_id}_quickview.png"
                page.screenshot(path=str(quickview_path), full_page=True)
                print(f"Captured {quickview_path}")
                page.mouse.move(0, 0)
                page.wait_for_timeout(150)

        context.close()
        browser.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
