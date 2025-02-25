from enum import Enum


class LLMEnums(Enum):
    """
    Enum representing the supported language model types.
    """
    OPENAI = "OPENAI"
    COHERE = "COHERE"


class OpenAIEnums(Enum):
    """
    Enum representing the different roles for OpenAI interactions.
    """
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class CohereEnums(Enum):
    """
    Enum representing the different roles for Cohere interactions.
    """
    SYSTEM = "SYSTEM"
    USER = "USER"
    ASSISTANT = "CHATBOT"
    DOCUMENT = "search_document"
    QUERY = "search_query"


class DocumentTypeEnum(Enum):
    """
    Enum representing the type of document (either a document or a query).
    """
    DOCUMENT = "document"
    QUERY = "query"
