import os
import shutil
import logging
from typing import List

from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LocalVectorStore:
    """
    Manages a localized, zero-cost vector database using ChromaDB 
    and HuggingFace local embeddings for air-gapped environments.
    """
    def __init__(self, 
                 collection_name: str = "local_rag_collection",
                 persist_directory: str = "./data/vector_db"):
        
        self.collection_name = collection_name
        self.persist_directory = os.path.abspath(persist_directory)
        
        # 1. Local Embeddings: Initialize zero-cost HuggingFace embeddings
        # all-MiniLM-L6-v2 is an excellent balance of speed and semantic capability
        logger.info("Initializing local HuggingFace embeddings (all-MiniLM-L6-v2)...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            # Enforce execution on CPU for maximum compatibility, 
            # but can be flipped to 'cuda' or 'mps' if acceleration is available
            model_kwargs={'device': 'cpu'}, 
            encode_kwargs={'normalize_embeddings': True} # Normalization helps with cosine similarity
        )
        
        # 2. ChromaDB Initialization: Connect to local persistent storage
        self.vector_db = self._init_chroma()

    def _init_chroma(self) -> Chroma:
        """
        Initializes the Chroma persistent client securely on the local filesystem.
        """
        os.makedirs(self.persist_directory, exist_ok=True)
        
        logger.info(f"Connecting to localized ChromaDB at {self.persist_directory}")
        return Chroma(
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
            persist_directory=self.persist_directory
        )

    def ingest_chunks(self, chunks: List[Document]):
        """
        3. Chunk Ingestion: Receives chunked text documents, mathematically embeds them,
        and securely stores them in the local ChromaDB collection.
        """
        if not chunks:
            logger.warning("No chunks provided for ingestion.")
            return

        logger.info(f"Ingesting {len(chunks)} chunks into ChromaDB collection '{self.collection_name}'...")
        try:
            self.vector_db.add_documents(chunks)
            # Modern LangChain Chroma integrations auto-persist when persist_directory is set
            logger.info("Successfully embedded and stored all chunks. Data safely persisted.")
        except Exception as e:
            logger.error(f"Failed to ingest chunks into Vector Store: {e}")
            raise e

    def reset_state(self):
        """
        4. Automated State Reset: Dynamically clears the active ChromaDB collection 
        to prevent semantic cross-contamination between different user sessions 
        or document contexts.
        """
        logger.info(f"Resetting vector state: Clearing collection '{self.collection_name}'...")
        try:
            # Safest way to guarantee zero cross-contamination is wiping the physical directory
            if os.path.exists(self.persist_directory):
                shutil.rmtree(self.persist_directory)
                logger.info(f"Deleted persistent storage at {self.persist_directory}")
            
            # Re-initialize a fresh, empty vector database
            self.vector_db = self._init_chroma()
            logger.info("Vector space reset completed successfully. State is strictly isolated and clean.")
        except Exception as e:
            logger.error(f"Error occurred while resetting vector state: {e}")
            raise e
            
    def get_retriever(self, search_kwargs={"k": 4}):
        """
        Returns a localized retriever interface for the underlying vector store.
        """
        return self.vector_db.as_retriever(search_kwargs=search_kwargs)

if __name__ == "__main__":
    # Example sanity check usage
    pass
