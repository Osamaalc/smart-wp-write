import os


class TemplateParser:
    """
    Class to manage and parse language templates for the application.
    It allows switching between languages and retrieving localized strings.
    """

    def __init__(self, language: str = None, default_language: str = 'en'):
        """
        Initialize TemplateParser with the specified language.

        :param language: The language to use (if None, defaults to the default language).
        :param default_language: The default language to fall back on (default is 'en').
        """
        self.current_path = os.path.dirname(os.path.abspath(__file__))
        self.default_language = default_language
        self.language = None

        self.set_language(language)

    def set_language(self, language: str):
        """
        Set the language for the templates.

        :param language: The language to set.
        """
        if not language:
            self.language = self.default_language

        language_path = os.path.join(self.current_path, "locales", language)
        if os.path.exists(language_path):
            self.language = language
        else:
            self.language = self.default_language

    def get(self, group: str, key: str, vars: dict = {}):
        """
        Retrieve the localized string for the given group and key.

        :param group: The group of the template (e.g., 'errors', 'messages').
        :param key: The key for the specific localized string within the group.
        :param vars: A dictionary of variables to substitute in the template (optional).
        :return: The localized string, or None if not found.
        """
        if not group or not key:
            return None

        group_path = os.path.join(self.current_path, "locales", self.language, f"{group}.py")
        targeted_language = self.language

        if not os.path.exists(group_path):
            group_path = os.path.join(self.current_path, "locales", self.default_language, f"{group}.py")
            targeted_language = self.default_language

        if not os.path.exists(group_path):
            return None

        # Import the group module
        module = __import__(f"stores.templates.locales.{targeted_language}.{group}", fromlist=[group])

        if not module:
            return None

        key_attribute = getattr(module, key)
        return key_attribute.safe_substitute(vars)
