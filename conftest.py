import allure
import pytest
from selenium.webdriver.support.wait import WebDriverWait

from core.config_loader import ConfigLoader
from core.driver_factory import DriverFactory
from utils.test_data_loader import TestDataLoader
from utils.logger_config import setup_logging

# Setup logging
setup_logging()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()

    # Access the driver from the test item
    # This works if 'driver' is a fixture used in the test
    driver = item.funcargs.get("driver") if "driver" in item.funcargs else None

    if rep.failed:
        if driver:
            try:
                # Use f-string properly for the filename
                file_path = f"reports/screenshots/failure_{rep.when}_{item.name}.png"
                driver.save_screenshot(file_path)

                allure.attach(
                    driver.get_screenshot_as_png(),
                    name=f"failure_{rep.when}_{item.name}",
                    attachment_type=allure.attachment_type.PNG
                )
            except Exception as e:
                print(f"\n[Allure Hook Error] Failed to capture screenshot: {e}")
        else:
            print(f"\n[Allure Hook Warning] No driver found for {item.name}")


@pytest.fixture(scope="session")
def config():
    return ConfigLoader.load_config()


@pytest.fixture
def users_data():
    return TestDataLoader.load_json("user_credentials.json")


@pytest.fixture
def context_state(driver):
    """
    Dictionary to share state between steps.
    """
    return {"driver": driver, "wait": WebDriverWait(driver, 10)}


@pytest.fixture(scope="function")
def driver(config):
    """
    Initializes the WebDriver instance based on config.
    """
    driver = DriverFactory.get_driver(config["browser"])
    driver.get(config["base_url"])
    driver.maximize_window()
    yield driver
    # Teardown happens after the hook has finished,
    # ensuring the driver is still alive for the screenshot.
    driver.quit()