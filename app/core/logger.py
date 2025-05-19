import logging
from logging.handlers import RotatingFileHandler
import os

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Define log format
log_format = logging.Formatter(
    "[%(asctime)s] %(levelname)s in %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(log_format)

# File handler — rotates at 5MB, keeps 3 backups
file_handler = RotatingFileHandler("logs/app.log", maxBytes=5_000_000, backupCount=3)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(log_format)

# Create the logger
logger = logging.getLogger("JobApplicationTracker")
logger.setLevel(logging.INFO)
logger.addHandler(console_handler)
logger.addHandler(file_handler)
logger.propagate = False  # prevent double logging
