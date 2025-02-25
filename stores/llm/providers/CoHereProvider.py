import logging
import cohere

from ..LLMEnums import CohereEnums, DocumentTypeEnum
from ..LLMInterface import LLMInterface


class CohereProvider(LLMInterface):
    def __init__(self, api_key: str,
                 default_input_max_characters: int = 1000,
                 default_generation_max_output_tokens: int = 2000,
                 default_generation_temperature: float = 0.1):
        """
        Initialize the CohereProvider with the given parameters.

        :param api_key: API key for Cohere client authentication.
        :param default_input_max_characters: The default max characters to process per text input (default: 1000).
        :param default_generation_max_output_tokens: The default max tokens for text generation (default: 2000).
        :param default_generation_temperature: The default temperature for generation (default: 0.1).
        """
        self.api_key = api_key
        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.default_generation_temperature = default_generation_temperature

        self.generation_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None

        self.client = cohere.Client(api_key=self.api_key)
        self.enums = CohereEnums

        self.logger = logging.getLogger(__name__)

    def set_generation_model(self, model_id: str):
        """
        Set the generation model ID.

        :param model_id: The ID of the generation model to use.
        """
        self.generation_model_id = model_id

    def set_embedding_model(self, model_id: str, embedding_size: int):
        """
        Set the embedding model ID and embedding size.

        :param model_id: The ID of the embedding model to use.
        :param embedding_size: The expected size of the embeddings.
        """
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size

    def process_text(self, text: str):
        """
        Process the text input, trimming it to the maximum allowed characters.

        :param text: The text to process.
        :return: The processed text.
        """
        return text[:self.default_input_max_characters]

    def generate_text(self, prompt: str, chat_history: list, max_output_tokens: int, temperature: float = None):
        """
        Generate text using the Cohere API.

        :param prompt: The prompt to generate text from.
        :param chat_history: The chat history for the model to refer to.
        :param max_output_tokens: The maximum number of tokens for output.
        :param temperature: The temperature for the generation process (default: None, uses default).
        :return: The generated text or None if failed.
        """
        if not self.client:
            self.logger.error("Cohere client not initialized")
            return None

        if not self.generation_model_id:
            self.logger.error("Generation model for Cohere was not set")
            return None

        max_output_tokens = max_output_tokens if max_output_tokens else self.default_generation_max_output_tokens
        temperature = temperature if temperature else self.default_generation_temperature

        response = self.client.chat(
            model=self.generation_model_id,
            chat_history=chat_history,
            messages=self.process_text(prompt),
            max_tokens=max_output_tokens,
            temperature=temperature,
        )

        if not response or not response.text:
            self.logger.error("Error while generating text using Cohere")
            return None

        return response.text

    def embed_text(self, text: str, document_type: str = None):
        """
        Embed text using the Cohere API.

        :param text: The text to embed.
        :param document_type: The type of document (e.g., query or document).
        :return: The embedding or None if failed.
        """
        if not self.client:
            self.logger.error("Cohere client not initialized")
            return None

        if not self.embedding_model_id:
            self.logger.error("Cohere embedding model not initialized")
            return None

        input_type = CohereEnums.DOCUMENT
        if document_type == DocumentTypeEnum.QUERY:
            input_type = CohereEnums.QUERY

        response = self.client.embed(
            model=self.embedding_model_id,
            texts=self.process_text(text),
            input_type=input_type
        )

        # Check the size of the embedding before returning
        embedding = response.embeddings[0]
        if len(embedding) != self.embedding_size:
            self.logger.warning(
                f"Invalid embedding size: {len(embedding)} (expected {self.embedding_size})"
            )
            return None

        return embedding

    def construct_prompt(self, prompt: str, role: str):
        """
        Construct a prompt with a given role.

        :param prompt: The prompt text.
        :param role: The role associated with the prompt.
        :return: A dictionary containing the role and processed prompt.
        """
        return {
            "role": role,
            "text": self.process_text(prompt)
        }
