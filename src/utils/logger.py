"""Logging configuration"""

import logging
import sys
from pathlib import Path
from datetime import datetime


def setup_logging(log_dir: str = "logs", log_level: str = "INFO") -> logging.Logger:
    """
    Set up application logging

    Args:
        log_dir: Directory for log files
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)

    Returns:
        Root logger instance
    """
    # Create logs directory
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    # Log file with timestamp
    log_file = log_path / f"video_archive_{datetime.now():%Y%m%d_%H%M%S}.log"

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )

    logger = logging.getLogger()
    logger.info("="*60)
    logger.info("Video Archive Tool - Yambo Studio")
    logger.info("="*60)
    logger.info(f"Log file: {log_file}")
    logger.info(f"Log level: {log_level}")

    return logger
