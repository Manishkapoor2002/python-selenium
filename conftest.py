import allure
import pytest
import logging
from selenium.webdriver.support.wait import WebDriverWait

from core import driver_manager
from core.config_loader import ConfigLoader
from core.driver_manager import DriverManager
from utils.test_data_loader import TestDataLoader
from utils.logger_config import setup_logging
from utils.screenshot_manager import ScreenshotManager

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Global driver store for accessing driver in hooks
_driver_store = {}


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook to capture screenshots on test failures before driver is quit.
    Uses tryfirst=True to run before other hooks ensuring driver is still active.
    Captures driver before fixture teardown runs.
    """
    outcome = yield
    rep = outcome.get_result()

    # Only capture screenshots on failure
    if rep.failed and call.when in ("setup", "call", "teardown"):
        # Access driver from global store or funcargs
        driver = _driver_store.get(item.nodeid)

        # Fallback: try to get driver from funcargs if not in store
        if not driver and hasattr(item, "funcargs"):
            driver = item.funcargs.get("driver")
            # For pytest-bdd, context_state contains the driver
            if not driver and "context_state" in item.funcargs:
                context = item.funcargs.get("context_state")
                if context and isinstance(context, dict) and "driver" in context:
                    driver = context["driver"]

        if driver:
            try:
                screenshot_manager = ScreenshotManager()
                screenshot_path = screenshot_manager.capture_screenshot(
                    driver,
                    item.name,
                    call.when
                )

                if screenshot_path:
                    # Attach screenshot to Allure report
                    allure.attach.file(
                        screenshot_path,
                        name=f"{item.name}_{call.when}",
                        attachment_type=allure.attachment_type.PNG
                    )
                    logger.info(f"Screenshot attached to Allure report: {screenshot_path}")
            except Exception as e:
                logger.error(f"Error capturing screenshot for {item.name}: {e}")
        else:
            logger.debug(f"Driver not available for screenshot capture in {item.name}")


@pytest.fixture(scope="session")
def config():
    """Load configuration once per session"""
    return ConfigLoader.load_config()


@pytest.fixture
def users_data():
    """Load test data from JSON file"""
    return TestDataLoader.load_json("user_credentials.json")


@pytest.fixture
def context_state(driver):
    """
    Fixture to share state between BDD steps.
    Contains driver and wait object for explicit waits.
    """
    return {"driver": driver, "wait": WebDriverWait(driver, 10)}


@pytest.fixture(scope="function")
def driver(request, config):
    """
    Initialize and provide WebDriver instance for each test.
    Uses SingletonDriver to manage driver lifecycle.
    Stores driver in global store for access in pytest_runtest_makereport hook.
    """
    driver_manager = DriverManager()
    _driver = driver_manager.get_driver(config["browser"])
    _driver.get(config["base_url"])
    _driver.maximize_window()

    # Store driver for access in hooks
    _driver_store[request.node.nodeid] = _driver

    yield _driver

    # Cleanup: Remove from store and quit driver
    _driver_store.pop(request.node.nodeid, None)
    driver_manager.quit_driver()
