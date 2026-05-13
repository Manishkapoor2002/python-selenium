from pages.base_page import BasePage
from selenium.webdriver.common.by import By


class LoginPage(BasePage):

    def __init__(self, driver):
        super().__init__(driver)

    def enter_login_credentials(self, email, password):
        """Enter email and password and submit login form"""
        self.logger.info("Entering login credentials for: %s, password: ***", email)
        email_input = (By.XPATH, "//input[@type='email' and @data-qa='login-email']")
        password_input = (By.XPATH, "//input[@type='password' and @data-qa='login-password']")
        login_button = (By.XPATH, "//button[@type='submit' and @data-qa='login-button']")
        
        self.enter_text(email_input, email)
        self.enter_text(password_input, password)
        self.click(login_button)

        from pages.home_page import HomePage
        return HomePage(self.driver)
