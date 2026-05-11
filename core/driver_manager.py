import threading
from typing import Optional

from selenium.webdriver.remote.webdriver import WebDriver

from core.browser_factory import BrowserFactory


class DriverManager:
    """
    Thread-safe Singleton driver manager.

    - One DriverManager instance process-wide (Singleton), guarded by a lock
      using double-checked locking to avoid races under pytest-xdist or
      multi-threaded execution.
    - Each thread gets its OWN WebDriver instance via threading.local(), so
      concurrent workers/threads don't share or clobber browser sessions.
    - quit_driver() only quits the CURRENT thread's driver.
    """

    _instance: Optional["DriverManager"] = None
    _instance_lock = threading.Lock()
    _thread_local = threading.local()

    def __new__(cls) -> "DriverManager":
        # Double-checked locking: cheap path when already created.
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    # ---------- internal helpers ----------
    def _get_local_driver(self) -> Optional[WebDriver]:
        return getattr(self._thread_local, "driver", None)

    def _set_local_driver(self, driver: Optional[WebDriver]) -> None:
        self._thread_local.driver = driver

    # ---------- public API ----------
    def get_driver(self, browser_name: str = "chrome", options: Optional[dict] = None) -> WebDriver:
        """
        Return the WebDriver for the CURRENT thread, creating it if missing
        or if the previous session has been closed/crashed.
        """
        driver = self._get_local_driver()

        if driver is None or getattr(driver, "session_id", None) is None:
            # Forward options only when provided, to stay compatible with
            # BrowserFactory signatures that don't accept an options dict.
            if options:
                driver = BrowserFactory.get_browser(browser_name, options)
            else:
                driver = BrowserFactory.get_browser(browser_name)
            self._set_local_driver(driver)

        return driver

    def has_driver(self) -> bool:
        """True if the current thread has a live driver session."""
        driver = self._get_local_driver()
        return driver is not None and getattr(driver, "session_id", None) is not None

    def quit_driver(self) -> None:
        """Quit ONLY the current thread's driver; leave other threads untouched."""
        driver = self._get_local_driver()
        if driver is not None:
            try:
                driver.quit()
            finally:
                self._set_local_driver(None)
