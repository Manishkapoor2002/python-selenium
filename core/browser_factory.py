from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions


class BrowserFactory:
    @staticmethod
    def get_browser(browser_name="chrome"):
        browser_name = browser_name.lower()

        if browser_name == "chrome":
            options = ChromeOptions()
            options.add_argument("--disable-extensions")
            return webdriver.Chrome(options=options)
        elif browser_name == "firefox":
            options = FirefoxOptions()
            return webdriver.Firefox(options=options)
        elif browser_name == "edge":
            options = EdgeOptions()
            options.add_argument("--disable-extensions")
            return webdriver.Edge(options=options)
        else:
            raise ValueError(f"Browser '{browser_name}' is not supported. Use chrome, firefox, or edge.")
