from abc import ABC, abstractmethod


class LLMInterface(ABC):
    """
    Abstract base class for Language Model interfaces.

    This class defines the essential methods that any language model provider
    (e.g., OpenAI, Cohere) must implement to handle text generation and embedding.
    """

    @abstractmethod
    def set_generation_model(self, model_id: str):
        """
        Set the generation model ID.

        :param model_id: The ID of the generation model to use.
        """
        pass

    @abstractmethod
    def set_embedding_model(self, model_id: str, embedding_size: int) -> object:
        """
        Set the embedding model ID and embedding size.

        :param model_id: The ID of the embedding model to use.
        :param embedding_size: The size of the embedding.
        :return: The embedding model object.
        """
        pass

    @abstractmethod
    def generate_text(self, prompt: str, chat_history: list, max_output_tokens: int, temperature: float = None):
        """
        Generate text based on the given prompt and chat history.

        :param prompt: The prompt for the text generation.
        :param chat_history: The history of the conversation or previous messages.
        :param max_output_tokens: The maximum number of tokens to generate.
        :param temperature: The temperature for text generation (default is None).
        :return: The generated text.
        """
        pass

    @abstractmethod
    def embed_text(self, text: str, document_type: str):
        """
        Embed the given text using the specified embedding model.

        :param text: The text to be embedded.
        :param document_type: The type of document (e.g., 'document', 'query').
        :return: The generated embedding for the text.
        """
        pass

    @abstractmethod
    def construct_prompt(self, prompt: str, role: str):
        """
        Construct a prompt with a given role.

        :param prompt: The prompt text.
        :param role: The role of the sender (e.g., 'system', 'user').
        :return: A dictionary containing the role and processed prompt.
        """
        pass
