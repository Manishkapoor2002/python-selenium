import logging
from pathlib import Path
from datetime import datetime


class ScreenshotManager:
    """Manages screenshot capture with proper directory handling and naming"""
    
    def __init__(self, base_path="reports/screenshots"):
        self.logger = logging.getLogger(__name__)
        self.screenshot_dir = Path(base_path)
        self._ensure_directory_exists()
    
    def _ensure_directory_exists(self):
        """Create screenshot directory if it doesn't exist"""
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
    
    def capture_screenshot(self, driver, test_name, failure_stage):
        """
        Capture screenshot with timestamp and meaningful name
        
        Args:
            driver: Selenium WebDriver instance
            test_name: Name of the test
            failure_stage: Stage when failure occurred (setup, call, teardown)
        
        Returns:
            str: Path to saved screenshot or None if capture fails
        """
        if not driver:
            self.logger.warning("Driver is None, cannot capture screenshot")
            return None
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            filename = f"{test_name}_{failure_stage}_{timestamp}.png"
            file_path = self.screenshot_dir / filename
            
            driver.save_screenshot(str(file_path))
            self.logger.info(f"Screenshot captured: {file_path}")
            return str(file_path)
        except Exception as e:
            self.logger.error(f"Failed to capture screenshot for {test_name}: {e}")
            return None

