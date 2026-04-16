# OpenCortex
# utils/logger.py

# Import Libraries
import logging

def setup_logger(name):
    logger = logging.getLogger(name)
    
    # Only add handlers if they don't exist to prevent duplicates
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        console_handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger

