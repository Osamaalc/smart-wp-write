import json
import re
import threading
import types
from typing import List

from models.db_schemes import Project, DataChunk
from stores.llm.LLMEnums import DocumentTypeEnum
from stores.templates.locales.ar.rag import footer_prompt
from .BaseController import BaseController


class NLPController(BaseController):
    def __init__(self, vectordb_client, embedding_client, generation_client,template_parser):
        super().__init__()

        self.vectordb_client = vectordb_client
        self.embedding_client = embedding_client
        self.generation_client = generation_client
        self.template_parser=template_parser

    def create_collection_name(self, project_id: str):
        return f"collection_{project_id}".strip()

    def reset_vector_db_collection(self, project: Project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        return self.vectordb_client.delete_collection(collection_name=collection_name)

    def get_vector_db_collection_info(self, project: Project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        collection_info = self.vectordb_client.get_collection_info(collection_name=collection_name)

        # return json.loads(json.dumps(collection_info, default=lambda o: o.__dict__))

        # Use regex to extract the JSON part
        match = re.search(r'config=({.*})>', str(collection_info), re.DOTALL)
        if match:
            json_str = match.group(1)
            config_data = json.loads(json_str)
            return config_data

        else:
            return "Error from database"
    # def get_vector_db_collection_info(self, project: Project):
    #     collection_name = self.create_collection_name(project_id=project.project_id)
    #     collection_info = self.vectordb_client.get_collection_info(collection_name=collection_name)
    #
    #     def custom_serializer(o):
    #         # معالجة كائنات البايت
    #         if isinstance(o, bytes):
    #             return o.decode('utf-8', errors='replace')
    #
    #         # معالجة mappingproxy (القاموس غير القابل للتعديل)
    #         elif isinstance(o, types.MappingProxyType):
    #             return dict(o)  # تحويله إلى قاموس عادي
    #
    #         # معالجة الكائنات الأخرى التي لها __dict__
    #         elif hasattr(o, '__dict__'):
    #             return o.__dict__
    #
    #         # أنواع غير مدعومة
    #         else:
    #             raise TypeError(f"نوع غير مدعوم: {type(o)}")
    #
    #     return json.loads(json.dumps(collection_info, default=custom_serializer))

    def index_info_vector_db(self, project: Project, chunks: List[DataChunk],chunks_ids:List[int], do_rest: bool = False):
        # step1: get collection name
        collection_name = self.create_collection_name(project_id=project.project_id)

        # step2: manage items
        texts = [c.chunk_text for c in chunks]
        metadata = [c.chunk_metadata for c in chunks]

        vectors = [
            self.embedding_client.embed_text(text=texts, document_type=DocumentTypeEnum.DOCUMENT.value)

            for text in texts
        ]

        # step3: create collection if not exists
        self.vectordb_client.create_collection(collection_name=collection_name,do_reset=do_rest,embedding_size=self.embedding_client.embedding_size)
        # step4: insert info vector db
        is_inserted = self.vectordb_client.insert_many(
            collection_name=collection_name,
            texts=texts,
            vectors=vectors,
            metadata=metadata,
            record_ids=chunks_ids,
            # embedding_size=self.embedding_client.embedding_size  # ✅ تمرير حجم التضمين هنا
        )

        return True
    def search_vector_db_collection(self, project: Project,text:str,limit:int=10):

        # step1: get collection name
        collection_name = self.create_collection_name(project_id=project.project_id)
        # step2: get text embedding vector
        vector = self.embedding_client.embed_text(text=[text], document_type=DocumentTypeEnum.DOCUMENT.value)
        if not vector or len(vector) == 0:
            return False

        # step3: do semantic search

        result = self.vectordb_client.search_by_vector(collection_name=collection_name, vector=vector, limit=limit)
        if not result:
            return False
        return result


    def answer_rag_question(self,project: Project,query:str,limit:int=10):
        answer, full_prompt, chat_history=None,None,None
        # step1:
        retrieved_document = self.search_vector_db_collection(project=project,text=query,limit=limit)
        if not retrieved_document or len(retrieved_document) == 0:
            return answer,full_prompt,chat_history

        system_prompt=self.template_parser.get("rag","system_prompt")


        document_prompt="/n".join([
            self.template_parser.get("rag","document_prompt",{
                "doc_num":idx +1,
                "chunk_text":doc.text,
            })
            for idx,doc in enumerate(retrieved_document)
        ])

        footer_prompts=self.template_parser.get("rag","footer_prompt")

        chat_history=[
            self.generation_client.construct_prompt(
                prompt=system_prompt,
                role=self.generation_client.enums.SYSTEM.value
            )
        ]

        full_prompt="/n/n".join([document_prompt,footer_prompts])

        answer= self.generation_client.generate_text(prompt=full_prompt,chat_history=chat_history)

        return answer,full_prompt,chat_history
