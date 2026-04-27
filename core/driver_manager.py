from core.browser_factory import BrowserFactory


class DriverManager:
    _instance = None
    _driver = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_driver(self, browser_name="chrome"):
        if self._driver is None or self._driver.session_id is None:
            self._driver = BrowserFactory.get_browser(browser_name)
        return self._driver

    def quit_driver(self):
        if self._driver is not None:
            self._driver.quit()
            self._driver = None
