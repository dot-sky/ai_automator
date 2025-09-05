import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core import secrets_manager

if __name__ == "__main__":
    secrets_manager.delete_credentials()
