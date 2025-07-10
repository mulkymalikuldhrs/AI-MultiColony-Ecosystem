# colony/core/config_loader.py
import os
from dotenv import load_dotenv

load_dotenv()

def get_config(key, default=None):
    return os.getenv(key, default)
