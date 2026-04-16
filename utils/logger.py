# OpenCortex
# utils/logger.py

# Import Libraries
import logging

# Function to setup logger
def setup_logger(name):
    logger = logging.getLogger(name)
    
    # Only add handlers if they don't exist to prevent duplicates
    if not logger.handlers:
        # Set the logger level
        logger.setLevel(logging.INFO)
        console_handler = logging.StreamHandler()
        
        # Format the logger
        formatter = logging.Formatter(
            fmt='[%(levelname)s] %(asctime)s - %(name)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Set the formatter for the console handler
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger

