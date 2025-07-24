import logging 
import os 
from datetime import datetime 
 
 
def get_logger(name: str = "AppLogger", log_file: str = "app.log"): 
    log_dir = "./logger" 
    os.makedirs(log_dir, exist_ok=True) 
    full_log_path = os.path.join(log_dir, log_file) 
 
    logger = logging.getLogger(name) 
    logger.setLevel(logging.DEBUG) 
 
    # Avoid adding duplicate handlers 
    if not logger.handlers: 
        file_handler = logging.FileHandler(full_log_path) 
        file_handler.setLevel(logging.DEBUG) 
 
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s') 
        file_handler.setFormatter(formatter) 
 
        logger.addHandler(file_handler) 
 
    return logger 