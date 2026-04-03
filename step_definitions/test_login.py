import pytest_check as check
from pages.home_page import HomePage
from pytest_bdd import scenarios, given, when, then
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# Load the feature file
scenarios('../features/login.feature')


# --- Background Steps ---
@given("I am on the home page")
def navigate_home(context_state):
    # Pass the driver to your updated Selenium Page Object
    homepage = HomePage(context_state["driver"])
    context_state["homepage"] = homepage


@given("I should see the \"Features Items\" heading")
def verify_features_items_heading(context_state):
    wait = context_state["wait"]
    # Replaced get_by_role with an XPath equivalent
    heading = wait.until(EC.visibility_of_element_located(
        (By.CLASS_NAME, "features_items")
    ))
    assert heading.is_displayed()


# --- When Steps ---
@when("I navigate to the login page")
def navigate_to_login(context_state):
    homepage = context_state["homepage"]
    loginpage = homepage.navigate_to_login_page()
    context_state["loginpage"] = loginpage


@when("I log in with valid credentials")
def login_valid_user(context_state, users_data):
    loginpage = context_state["loginpage"]
    email = users_data["valid_user"]["useremail"]
    password = users_data["valid_user"]["password"]

    context_state["homepage"] = loginpage.enter_login_credentials(email, password)


@when("I log in with invalid credentials")
def login_invalid_user(context_state, users_data):
    loginpage = context_state["loginpage"]
    email = users_data["invalid_user"]["useremail"]
    password = users_data["invalid_user"]["password"]

    loginpage.enter_login_credentials(email, password)


# --- Then Steps ---
@then("I should see the \"Login to your account\" heading")
def verify_login_heading(context_state):
    wait = context_state["wait"]
    heading = wait.until(EC.visibility_of_element_located(
        (By.CLASS_NAME, "login-form")
    ))
    assert heading.is_displayed()


@then("I should see the \"Logout\" link")
def verify_logout_visible(context_state):
    wait = context_state["wait"]
    logout_link = wait.until(EC.visibility_of_element_located(
        (By.XPATH, "//ul/li/a[contains(normalize-space(text()), 'Logout')]")
    ))
    assert logout_link.is_displayed()


@then("I should see the \"Signup / Login\" link")
def verify_signup_login_visible(context_state):
    wait = context_state["wait"]
    login_link = wait.until(EC.visibility_of_element_located(
        (By.XPATH, "//ul/li/a[contains(normalize-space(text()), 'Signup / Login')]")
    ))
    assert login_link.is_displayed()


@then("I look for a non-existent heading to trigger a failure")
def failing_step_for_screenshot(context_state):
    driver = context_state["driver"]

    # Simulating Playwright's soft=True using pytest-check
    # If the element isn't found, it won't instantly kill the test flow
    try:
        element = WebDriverWait(driver, 3).until(EC.visibility_of_element_located(
            (By.XPATH, "//*[contains(text(), 'This heading does not exist')]")
        ))
        check.is_true(element.is_displayed(), "Expected non-existent heading to be visible")
    except Exception as e:
        check.is_true(False, f"Soft assertion failed, element not found: {e}")