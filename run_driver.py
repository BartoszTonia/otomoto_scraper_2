from __future__ import annotations

from playwright.sync_api import (
    Browser,
    BrowserContext,
    Error,
    Page,
    Playwright,
    TimeoutError as PlaywrightTimeoutError,
    sync_playwright,
)


class BrowserSession:
    """Playwright browser session with simple retry logic for Otomoto pages."""

    def __init__(self, headless: bool = True, timeout_ms: int = 25_000) -> None:
        self._playwright: Playwright = sync_playwright().start()
        self._browser: Browser = self._playwright.chromium.launch(
            headless=headless,
            args=["--disable-blink-features=AutomationControlled"],
        )
        self._context: BrowserContext = self._browser.new_context(
            locale="pl-PL",
            viewport={"width": 1920, "height": 1080},
            user_agent=(
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            ),
        )
        self._timeout_ms = timeout_ms

    def close(self) -> None:
        self._context.close()
        self._browser.close()
        self._playwright.stop()

    def fetch_html(self, url: str, wait_selector: str | None = None) -> tuple[str, str]:
        page: Page = self._context.new_page()

        try:
            for attempt in range(3):
                try:
                    page.goto(url, wait_until="domcontentloaded", timeout=self._timeout_ms)
                    if wait_selector:
                        page.wait_for_selector(wait_selector, timeout=6_000)
                    else:
                        page.wait_for_load_state("networkidle", timeout=10_000)
                    title = page.title()
                    html = page.content()
                    print(f">>> {title} - loaded")
                    return title, html
                except (PlaywrightTimeoutError, Error):
                    if attempt == 2:
                        raise
                    print(">>>>> retry page load")
            raise RuntimeError("unreachable")
        finally:
            page.close()
