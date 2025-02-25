import logging
from openai import OpenAI
from ..LLMEnums import OpenAIEnums
from ..LLMInterface import LLMInterface


class OpenAIProvider(LLMInterface):
    def __init__(self, api_key: str, api_url: str = None,
                 default_input_max_characters: int = 1000,
                 default_generation_max_output_tokens: int = 2000,
                 default_generation_temperature: float = 0.1):
        """
        Initialize the OpenAIProvider with the given parameters.

        :param api_key: API key for OpenAI client authentication.
        :param api_url: Optional API base URL.
        :param default_input_max_characters: Max characters allowed for input text (default: 1000).
        :param default_generation_max_output_tokens: Max tokens for output generation (default: 2000).
        :param default_generation_temperature: Temperature for generation (default: 0.1).
        """
        self.api_key = api_key
        self.api_url = api_url
        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.default_generation_temperature = default_generation_temperature

        self.generation_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.api_url if self.api_url and len(self.api_url) else None,  # Using api_base instead of api_url
        )
        self.enums = OpenAIEnums
        self.logger = logging.getLogger(__name__)

    def set_generation_model(self, model_id: str):
        """
        Set the generation model ID for text generation.

        :param model_id: The ID of the generation model to use.
        """
        self.generation_model_id = model_id

    def set_embedding_model(self, model_id: str, embedding_size: int):
        """
        Set the embedding model ID and size.

        :param model_id: The ID of the embedding model to use.
        :param embedding_size: The size of the embedding.
        """
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size

    def process_text(self, text: str):
        """
        Process the text input by trimming it to the maximum allowed characters.

        :param text: The text to process.
        :return: The processed text.
        """
        return text[:self.default_input_max_characters]

    def generate_text(self, prompt: str, chat_history: list, max_output_tokens: int = None, temperature: float = None):
        """
        Generate text using the OpenAI API.

        :param prompt: The prompt to generate text from.
        :param chat_history: The chat history to provide context for the generation.
        :param max_output_tokens: The maximum number of output tokens.
        :param temperature: The temperature for the generation.
        :return: The generated text or None if an error occurs.
        """
        if not self.client:
            self.logger.error("OpenAI client not initialized")
            return None

        if not self.generation_model_id:
            self.logger.error("Generation model for OpenAI was not set")
            return None

        max_output_tokens = max_output_tokens if max_output_tokens else self.default_generation_max_output_tokens
        temperature = temperature if temperature else self.default_generation_temperature
        chat_history.append(self.construct_prompt(prompt=prompt, role=OpenAIEnums.USER.value))

        response = self.client.chat.completions.create(
            model=self.generation_model_id,
            messages=chat_history,
            max_tokens=max_output_tokens,
            temperature=temperature,
        )

        if not response or not response.choices or len(response.choices) == 0 or not response.choices[0].message:
            self.logger.error("Error while generating text using OpenAI")
            return None

        return response.choices[0].message.content

    def embed_text(self, text: str, document_type: str = None):
        """
        Embed text using the OpenAI API.

        :param text: The text to embed.
        :param document_type: The type of document (e.g., query or document).
        :return: The embedding or None if an error occurs.
        """
        if not self.client:
            self.logger.error("OpenAI client not initialized")
            return None

        if not self.embedding_model_id:
            self.logger.error("OpenAI embedding model not initialized")
            return None

        response = self.client.embeddings.create(
            model=self.embedding_model_id,
            input=text,
        )

        if not response or not response.data or len(response.data) == 0 or not response.data[0].embedding:
            self.logger.error("Error while embedding text using OpenAI")
            return None

        return response.data[0].embedding

    def construct_prompt(self, prompt: str, role: str):
        """
        Construct a prompt with a given role.

        :param prompt: The prompt text.
        :param role: The role associated with the prompt (e.g., user or system).
        :return: A dictionary containing the role and processed prompt.
        """
        return {
            "role": role,
            "content": self.process_text(prompt)
        }
