from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

class DriverFactory:

    @staticmethod
    def get_driver(browser_name="chrome"):
        if browser_name.lower() == "chrome":
            return webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        elif browser_name.lower() == "firefox":
            return webdriver.Firefox()
        raise Exception(f"Browser {browser_name} is not supported")
