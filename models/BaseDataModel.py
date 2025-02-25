from helpers.config import get_settings, Settings


class BaseDataModel:
    def __init__(self, db_client: object):
        """
        Initialize the BaseDataModel with the provided database client.

        :param db_client: The database client used for interactions with the database.
        """
        self.db_client = db_client
        self.settings = get_settings()
