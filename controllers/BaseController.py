import os
import random
import string
from helpers.config import get_settings, Settings


class BaseController:
    def __init__(self):
        # Initialize settings and base paths
        self.app_settings = get_settings()
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.file_dir = os.path.join(self.base_dir, "assets/files")
        self.database_dir = os.path.join(self.base_dir, "assets/database")

    def generate_random_string(self, length: int = 12) -> str:
        """
        Generate a random string consisting of lowercase letters and digits.

        :param length: Length of the random string to generate (default is 12).
        :return: Random string of the specified length.
        """
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

    def get_database_path(self, db_name: str) -> str:
        """
        Get the path to the database directory. Creates the directory if it doesn't exist.

        :param db_name: Name of the database directory.
        :return: Path to the database directory.
        """
        database_path = os.path.join(self.database_dir, db_name)
        if not os.path.exists(database_path):
            os.makedirs(database_path)
        return database_path
