"""
Logging utilities for Autonomous Agent Colony
"""

import logging
import sys
from pathlib import Path
from datetime import datetime

def setup_logger():
    """Setup main system logger"""
    project_root = Path(__file__).parent.parent.parent
    logs_dir = project_root / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Setup file handler
    log_file = logs_dir / f"colony_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    
    # Setup console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Setup root logger
    logger = logging.getLogger("autonomous_colony")
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def get_logger(name: str):
    """Get logger for specific module"""
    return logging.getLogger(f"autonomous_colony.{name}")
