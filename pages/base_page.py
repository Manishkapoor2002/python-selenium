import logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        self.logger = logging.getLogger(__name__)

    def navigate_to(self, url):
        self.logger.info(f"Navigating to {url}")
        self.driver.get(url)

    def click(self, locator):
        self.logger.info(f"Clicking on element: {locator}")
        self.wait.until(EC.element_to_be_clickable(locator)).click()

    def enter_text(self, locator, text):
        self.logger.info(f"Entering text into element: {locator}")
        self.wait.until(EC.visibility_of_element_located(locator)).send_keys(text)

    def get_text(self, locator):
        self.logger.info(f"Getting text from element: {locator}")
        return self.wait.until(EC.visibility_of_element_located(locator)).text

    def is_displayed(self, locator):
        self.logger.info(f"Checking if element is displayed: {locator}")
        return self.wait.until(EC.visibility_of_element_located(locator)).is_displayed()

