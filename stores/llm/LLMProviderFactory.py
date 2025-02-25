from .providers import OpenAIProvider
from .providers.CoHereProvider import CohereProvider
from .LLMEnums import LLMEnums


class LLMProviderFactory:
    """
    Factory class to create instances of different LLM (Language Model) providers.

    Based on the provided provider name, it creates and returns an instance of the corresponding provider
    (e.g., OpenAIProvider or CohereProvider).
    """

    def __init__(self, config: dict):
        """
        Initialize the LLMProviderFactory with the given configuration.

        :param config: The configuration dictionary containing API keys and other settings.
        """
        self.config = config

    def create(self, provider: str):
        """
        Create and return an instance of the specified LLM provider.

        :param provider: The name of the provider (e.g., 'OPENAI', 'COHERE').
        :return: An instance of the corresponding LLM provider (OpenAIProvider or CohereProvider), or None if not found.
        """
        if provider == LLMEnums.OPENAI.value:
            return OpenAIProvider(
                api_key=self.config.OPENAI_API_KEY,
                api_url=self.config.OPENAI_API_URL,
                default_input_max_characters=self.config.INPUT_DAFAULT_MAX_CHARACTERS,
                default_generation_max_output_tokens=self.config.GENERATION_DAFAULT_MAX_TOKENS,
                default_generation_temperature=self.config.GENERATION_DAFAULT_TEMPERATURE
            )

        if provider == LLMEnums.COHERE.value:
            return CohereProvider(
                api_key=self.config.COHERE_API_KEY,
                default_input_max_characters=self.config.INPUT_DAFAULT_MAX_CHARACTERS,
                default_generation_max_output_tokens=self.config.GENERATION_DAFAULT_MAX_TOKENS,
                default_generation_temperature=self.config.GENERATION_DAFAULT_TEMPERATURE
            )

        return None
