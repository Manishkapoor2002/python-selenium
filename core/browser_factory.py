from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService


class BrowserFactory:
    @staticmethod
    def get_browser(browser_name="chrome"):
        browser_name = browser_name.lower()

        if browser_name == "chrome":
            return webdriver.Chrome()
        elif browser_name == "firefox":
            return webdriver.Firefox()
        elif browser_name == "edge":
            return webdriver.Edge()
        else:
            raise ValueError(f"Browser '{browser_name}' is not supported. Use chrome, firefox, or edge.")


if __name__ == "__main__":
    driver = BrowserFactory.get_browser()          # defaults to chrome
    # driver = BrowserFactory.get_browser("firefox")
    # driver = BrowserFactory.get_browser("edge")

    driver.get("https://www.google.com")
    print(f"Title: {driver.title}")
    driver.quit()