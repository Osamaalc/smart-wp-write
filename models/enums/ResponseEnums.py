from enum import Enum


class ResponseSignal(Enum):
    """
    إشارات الاستجابة التي يمكن استخدامها في التطبيق.
    """
    FILE_VALIDATION_SUCCESS = "file_validation_successfully"
    FILE_TYPE_NOT_SUPPORTED = "file_type_not_supported"
    FILE_SIZE_TOO_LARGE = "file_size_too_large"
    FILE_UPLOAD_FAILED = "file_upload_failed"
    FILE_UPLOAD_SUCCESS = "file_upload_successfully"
    PROCESSING_FAILED = "processing_failed"
    PROCESSING_SUCCESS = "processing_successfully"
    NO_FILES_ERROR = "no_found_files"
    FILE_ID_ERROR="no_file_found_with_this_id"
    FILE_NOT_FOUND_ERROR="file_not_found"
    INSERT_INTO_VECTORDB_ERROR="insert_into_vectordb_error"
    INSERT_INTO_VECTORDB_SUCCESS="insert_into_vectordb_successfully"
    VECTORBD_COLLECTION_RETRIEVED="vectorbd_collection_retrieved"
    VECTORDB_SEARCH_ERROR="vectorbd_search_error"
    VECTORDB_SEARCH_SUCCESS="vectorbd_search_successfully"
    RAG_ANSWER_ERROR="rag_answer_error"
    RAG_ANSWER_SUCCESS="rag_answer_successfully"