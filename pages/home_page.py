from selenium.webdriver.common.by import By

from pages.base_page import BasePage

class HomePage(BasePage):

    def __init__(self, driver):
        super().__init__(driver)

    def navigate_to_home(self,config):
        """Navigate to home page"""
        self.logger.info(f"Navigating to home: {config['base_url']}")
        self.navigate_to(config["base_url"])

    def navigate_to_login_page(self):
        """Navigate to login page"""
        self.logger.info("Navigating to Login Page")
        login_link = (By.XPATH, "//ul/li/a[contains(normalize-space(text()), 'Signup / Login')]")
        self.click(login_link)
        from pages.login_page import LoginPage
        return LoginPage(self.driver)