import os
from multipart import file_path
from langchain_community.document_loaders import PyMuPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from models import ProcessingEnum
from .BaseController import BaseController
from . import ProjectController


class ProcessController(BaseController):
    def __init__(self, project_id: str):
        super().__init__()
        self.project_id = project_id
        self.project_path = ProjectController().get_project_path(project_id=self.project_id)

    def get_file_extension(self, file_id: str):
        """
        Get the file extension from the file ID.

        :param file_id: The file ID.
        :return: The file extension.
        """
        return os.path.splitext(file_id)[-1]

    def get_file_loader(self, file_id: str):
        """
        Get the appropriate file loader based on the file extension.

        :param file_id: The file ID.
        :return: The corresponding file loader or None if the file type is unsupported.
        """
        file_ext = self.get_file_extension(file_id=file_id)
        file_path = os.path.join(self.project_path, file_id)

        if not os.path.exists(file_path):
            return None

        if file_ext == ProcessingEnum.TXT.value:
            return TextLoader(file_path, encoding='utf-8')
        if file_ext == ProcessingEnum.PDF.value:
            return PyMuPDFLoader(file_path)
        return None

    def get_file_content(self, file_id: str):
        """
        Load the content of the file.

        :param file_id: The file ID.
        :return: The content of the file or None if the loader is not available.
        """
        loader = self.get_file_loader(file_id=file_id)
        if loader:
            return loader.load()
        return None

    def process_file_content(self, file_content: list, file_id: str, chunk_size: int = 1000,
                              overlap_size: int = 100, max_chunks: int = None):
        """
        Split the file content into chunks using RecursiveCharacterTextSplitter with additional improvements.

        :param file_content: The content of the file (list of text and metadata).
        :param file_id: The file ID.
        :param chunk_size: The size of each chunk. Default is 1000.
        :param overlap_size: The overlap between chunks. Default is 100.
        :param max_chunks: The maximum number of chunks. Default is None (no limit).
        :return: A list of chunks after splitting.
        """
        # Ensure the file content list is not empty
        if not file_content:
            raise ValueError("The file content list is empty. Please provide valid content.")

        # Clean the text from extra spaces
        file_content_text = [
            rec.page_content.strip().replace("\n", " ").replace("\t", " ")
            for rec in file_content if rec.page_content.strip()
        ]

        file_content_metadata = [
            rec.metadata for rec in file_content
        ]

        # Create TextSplitter with the required settings
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap_size,
            length_function=len
        )

        # Split the text into chunks using the metadata
        chunks = text_splitter.create_documents(file_content_text, metadatas=file_content_metadata)

        # Apply the max_chunks limit if provided
        if max_chunks:
            chunks = chunks[:max_chunks]

        return chunks
