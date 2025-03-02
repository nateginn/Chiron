"""
Logging system for debugging and monitoring.
"""
import logging
import os
from pathlib import Path
from datetime import datetime

def get_logger(name):
    """Get a logger instance for the specified module."""
    logger = logging.getLogger(name)
    
    # Only configure the logger if it hasn't been configured
    if not logger.handlers:
        logger.setLevel(os.getenv('LOG_LEVEL', 'INFO'))
        
        # Create formatters
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # Create file handler
        log_path = os.getenv('LOG_PATH', 'data/logs')
        Path(log_path).mkdir(parents=True, exist_ok=True)
        
        log_file = Path(log_path) / f"{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def setup_logger():
    """Setup the root logger."""
    return get_logger('chiron')
