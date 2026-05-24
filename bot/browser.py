from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext, Playwright


class BrowserManager:
    def __init__(self):
        self._playwright: Playwright = None
        self._browser: Browser = None
        self._context: BrowserContext = None
        self.page: Page = None

    def start(self, headless: bool = False) -> Page:
        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(
            headless=headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-extensions",
                "--no-sandbox",
            ],
        )
        browser_version = (self._browser.version or "124.0.0.0").split()[0]
        self._context = self._browser.new_context(
            viewport={"width": 1366, "height": 900},
            screen={"width": 1366, "height": 900},
            device_scale_factor=1,
            is_mobile=False,
            has_touch=False,
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                f"Chrome/{browser_version} Safari/537.36"
            ),
            locale="de-DE",
            timezone_id="Europe/Berlin",
            color_scheme="light",
            ignore_https_errors=True,
        )
        self._context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', { get: () => undefined });"
        )
        self.page = self._context.new_page()
        self.page.set_default_timeout(15000)
        self.page.set_default_navigation_timeout(45000)
        return self.page

    def stop(self):
        try:
            if self._context:
                self._context.close()
        except Exception:
            pass
        try:
            if self._browser:
                self._browser.close()
        except Exception:
            pass
        try:
            if self._playwright:
                self._playwright.stop()
        except Exception:
            pass
        self._browser = None
        self._context = None
        self._playwright = None
        self.page = None
