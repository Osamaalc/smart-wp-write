import json
import logging
import re
import threading
from typing import List

from models.db_schemes import Project, DataChunk
from stores.llm.LLMEnums import DocumentTypeEnum
from stores.templates.locales.ar.rag import footer_prompt
from .BaseController import BaseController


class NLPController(BaseController):
    def __init__(self, vectordb_client, embedding_client, generation_client, template_parser):
        super().__init__()
        self.logger = logging.getLogger(__name__)  # ✅ Add logger here
        self.vectordb_client = vectordb_client
        self.embedding_client = embedding_client
        self.generation_client = generation_client
        self.template_parser = template_parser

    def create_collection_name(self, project_id: str):
        """Create a collection name based on project ID."""
        return f"collection_{project_id}".strip()

    def reset_vector_db_collection(self, project: Project):
        """Reset vector database collection for the given project."""
        collection_name = self.create_collection_name(project_id=project.project_id)
        return self.vectordb_client.delete_collection(collection_name=collection_name)

    def get_vector_db_collection_info(self, project: Project):
        """Get collection information for the given project."""
        collection_name = self.create_collection_name(project_id=project.project_id)
        collection_info = self.vectordb_client.get_collection_info(collection_name=collection_name)

        # Extract JSON part from collection info
        match = re.search(r'config=({.*})>', str(collection_info), re.DOTALL)
        if match:
            json_str = match.group(1)
            config_data = json.loads(json_str)
            return config_data
        else:
            return "Error from database"

    def index_info_vector_db(self, project: Project, chunks: List[DataChunk], chunks_ids: List[int], do_rest: bool = False):
        """
        Insert vectors into the Weaviate database after converting text with OpenAI Embeddings.

        :param project: Project object to store its data.
        :param chunks: List of text chunks to insert.
        :param chunks_ids: List of UUIDs for each chunk.
        :param do_rest: If True, reset the collection if it exists.
        :return: True if insertion was successful, otherwise False.
        """
        collection_name = self.create_collection_name(project_id=project.project_id)

        # Process texts and metadata
        texts = [chunk.chunk_text.strip() for chunk in chunks]
        metadata = [chunk.chunk_metadata for chunk in chunks]

        # Preprocess and embed text
        def preprocess_text(text: str) -> str:
            text = text.strip()
            text = re.sub(r'[^\w\s]', '', text.lower())  # Remove symbols and convert to lowercase
            return text

        vectors = []
        for text in texts:
            clean_text = preprocess_text(text)
            vector = self.embedding_client.embed_text(text=clean_text, document_type=DocumentTypeEnum.DOCUMENT.value)

            if vector is None or len(vector) != 1536:
                raise ValueError("❌ Invalid vector: Length must be 1536.")

            vectors.append(vector)

        # Create collection if not exists
        self.vectordb_client.create_collection(
            collection_name=collection_name,
            do_reset=do_rest,
            embedding_size=self.embedding_client.embedding_size
        )

        # Insert data into the database
        is_inserted = self.vectordb_client.insert_many(
            collection_name=collection_name,
            texts=texts,
            vectors=vectors,
            metadata=metadata,
            record_ids=chunks_ids
        )

        # Log the result
        if is_inserted:
            self.logger.info(f"✅ Successfully inserted {len(chunks)} records into '{collection_name}'")
        else:
            self.logger.error(f"❌ Failed to insert records into '{collection_name}'")

        return is_inserted

    def search_vector_db_collection(self, project: Project, text: str, limit: int = 10):
        """
        Perform semantic search on the vector database collection.

        :param project: Project object to get the collection name.
        :param text: Query text for search.
        :param limit: Maximum number of search results.
        :return: Search results or False if no results found.
        """
        collection_name = self.create_collection_name(project_id=project.project_id)

        # Get text embedding vector
        vector = self.embedding_client.embed_text(text=[text], document_type=DocumentTypeEnum.DOCUMENT.value)
        if not vector or len(vector) == 0:
            return False

        # Perform semantic search
        result = self.vectordb_client.search_by_vector(
            collection_name=collection_name,
            vector=vector,
            limit=limit,
            query_text=text,
            min_score=0.75,  # Minimum similarity score
            use_hybrid=True,  # Enable hybrid search
            enable_fallback=True  # Enable fallback search
        )

        return result if result else False

    def answer_rag_question(self, project: Project, query: str, limit: int = 10):
        """
        Generate an answer for the RAG (Retrieve and Generate) model.

        :param project: Project object to get the collection.
        :param query: User query for which the answer is generated.
        :param limit: Maximum number of documents to retrieve.
        :return: Answer, full prompt, and chat history.
        """
        answer, full_prompt, chat_history = None, None, None

        # Step 1: Retrieve documents
        retrieved_document = self.search_vector_db_collection(project=project, text=query, limit=limit)
        if not retrieved_document or len(retrieved_document) == 0:
            return answer, full_prompt, chat_history

        # Step 2: Prepare system prompt
        system_prompt = self.template_parser.get("rag", "system_prompt")

        # Step 3: Document prompt
        document_prompt = "\n".join([
            self.template_parser.get("rag", "document_prompt", {
                "doc_num": idx + 1,
                "chunk_text": doc.text,
            })
            for idx, doc in enumerate(retrieved_document)
        ])

        # Step 4: Footer prompt with user query
        footer_prompts = self.template_parser.get("rag", "footer_prompt", {
            "query": query
        })

        # Step 5: Chat history
        chat_history = [
            self.generation_client.construct_prompt(
                prompt=system_prompt,
                role=self.generation_client.enums.SYSTEM.value
            )
        ]

        # Step 6: Combine all prompts
        full_prompt = "\n\n".join([document_prompt, footer_prompts])

        # Step 7: Generate the final answer
        answer = self.generation_client.generate_text(prompt=full_prompt, chat_history=chat_history)

        return answer, full_prompt, chat_history
