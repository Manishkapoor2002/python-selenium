import logging
import logging.config
from pathlib import Path


def setup_logging():
    """Setup logging configuration for the test suite"""
    log_dir = Path(__file__).parent.parent / "log"
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "test.log"),
            logging.StreamHandler()
        ]
    )

