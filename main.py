from fastapi import FastAPI
from routes import base, data, nlp,file
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings
from stores.llm.LLMProviderFactory import LLMProviderFactory
from stores.vectordb.VectorDBProviderFactory import VectorDBProviderFactory
from stores.templates.template_parser import TemplateParser

# إنشاء تطبيق FastAPI
app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware

# بعد إنشاء التطبيق
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # يمكنك تحديد نطاقات محددة ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],  # أو تحديد ["POST", "OPTIONS"]
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_span():
    settings = get_settings()

    # الاتصال بقاعدة بيانات MongoDB
    try:
        app.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URL)
        app.db_client = app.mongo_conn[settings.MONGODB_DATABASE]
        print("✅ Connected to MongoDB!")
    except Exception as e:
        print(f"❌ Error connecting to MongoDB: {e}")

    # إعداد موفر LLM
    llm_provider_factory = LLMProviderFactory(settings)
    vectordb_provider_factory = VectorDBProviderFactory(settings)

    # إعداد عميل توليد النصوص
    app.generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(model_id=settings.GENERATION_MODEL_ID)

    # إعداد عميل التضمين (Embedding)
    app.embedding_client = llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
    app.embedding_client.embedding_model_id = settings.EMBEDDING_MODEL_ID
    app.embedding_client.embedding_size = settings.EMBEDDING_MODEL_SIZE

    # ✅ إعداد قاعدة بيانات المتجهات Weaviate
    app.vectordb_client = vectordb_provider_factory.create(provider=settings.VECTOR_DB_BACKEND)
    app.vectordb_client.connect()

    app.template_parser = TemplateParser(language=settings.PRIMARY_LANG, default_language=settings.DEFAULT_LANG)

@app.on_event("shutdown")
async def shutdown_span():
    try:
        if hasattr(app, "mongo_conn"):
            app.mongo_conn.close()
            print("✅ MongoDB connection closed.")
    except Exception as e:
        print(f"❌ Error closing MongoDB connection: {e}")

    try:
        if hasattr(app, 'vectordb_client'):
            app.vectordb_client.disconnect()
            print("✅ VectorDB connection closed successfully.")
    except Exception as e:
        print(f"❌ Error while disconnecting VectorDB client: {e}")

# تضمين Routers في التطبيق
app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)
# app.include_router(file.file_router)

