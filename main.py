from fastapi import FastAPI
from routes import base, data, nlp, file
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings
from stores.llm.LLMProviderFactory import LLMProviderFactory
from stores.vectordb.VectorDBProviderFactory import VectorDBProviderFactory
from stores.templates.template_parser import TemplateParser
from contextlib import asynccontextmanager  # Import for async context manager
from fastapi.middleware.cors import CORSMiddleware


# Create lifespan function
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the startup and shutdown processes for the FastAPI app.

    - Connects to MongoDB
    - Sets up LLM and VectorDB clients
    - Sets up the Template Parser
    - Handles shutdown processes
    """
    # ------ Startup Code ------
    settings = get_settings()

    # Connect to MongoDB
    try:
        app.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URL)
        app.db_client = app.mongo_conn[settings.MONGODB_DATABASE]
        print("✅ Connected to MongoDB!")
    except Exception as e:
        print(f"❌ Error connecting to MongoDB: {e}")

    # Setup LLM and VectorDB
    llm_provider_factory = LLMProviderFactory(settings)
    vectordb_provider_factory = VectorDBProviderFactory(settings)

    # Setup Generation Client
    app.generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(model_id=settings.GENERATION_MODEL_ID)

    # Setup Embedding Client
    app.embedding_client = llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
    app.embedding_client.embedding_model_id = settings.EMBEDDING_MODEL_ID
    app.embedding_client.embedding_size = settings.EMBEDDING_MODEL_SIZE

    # Setup VectorDB Client
    app.vectordb_client = vectordb_provider_factory.create(provider=settings.VECTOR_DB_BACKEND)
    app.vectordb_client.connect()

    # Setup Template Parser
    app.template_parser = TemplateParser(language=settings.PRIMARY_LANG, default_language=settings.DEFAULT_LANG)

    yield  # Execution proceeds to the app lifecycle here

    # ------ Shutdown Code ------
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


# Create FastAPI app with lifespan handler
app = FastAPI(lifespan=lifespan)  # Main change here

# Setup CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for CORS
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Include Routers
app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)
# app.include_router(file.file_router)  # Uncomment this line to include the file router
