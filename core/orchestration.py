import os
import logging
from typing import List, Dict, Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.documents import Document

# Conditional imports based on provider configuration
from langchain_community.llms import Ollama
from langchain_google_genai import ChatGoogleGenerativeAI

from data.vector_store import LocalVectorStore

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HybridLLMOrchestrator:
    """
    Manages prompt construction, semantic retrieval, and hybrid LLM execution 
    (Local-First SLM or Cloud-Accelerated API).
    """
    def __init__(self, 
                 vector_store: LocalVectorStore,
                 provider: str = "local",
                 model_name: str = "mistral",
                 temperature: float = 0.0):
        self.vector_store = vector_store
        self.provider = provider.lower()
        self.model_name = model_name
        self.temperature = temperature
        
        # 2. Hybrid LLM Gateway Configuration
        self.llm = self._initialize_llm()
        
        # 3. Anti-Hallucination Guardrails
        self.prompt_template = self._build_anti_hallucination_prompt()

    def _initialize_llm(self):
        """
        Dynamically initializes the selected LLM pathway.
        """
        logger.info(f"Initializing LLM Gateway. Pathway: {self.provider.upper()}, Model: {self.model_name}")
        
        if self.provider == "local":
            # Local-First (Air-Gapped): Connects to local Ollama instance
            try:
                # Requires Ollama to be running on localhost:11434 with the specified model pulled
                return Ollama(model=self.model_name, temperature=self.temperature)
            except Exception as e:
                logger.error(f"Failed to initialize local Ollama SLM: {e}")
                raise e
                
        elif self.provider == "cloud":
            # Cloud-Accelerated: Google Gemini (Flash or Pro) within free tier limits
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                logger.warning("GOOGLE_API_KEY not found in environment for Cloud provider.")
                
            try:
                return ChatGoogleGenerativeAI(
                    model=self.model_name, # e.g., 'gemini-1.5-flash'
                    temperature=self.temperature,
                    google_api_key=api_key
                )
            except Exception as e:
                logger.error(f"Failed to initialize Google Gemini API: {e}")
                raise e
        else:
            raise ValueError(f"Unsupported LLM pathway: {self.provider}. Use 'local' or 'cloud'.")

    def _build_anti_hallucination_prompt(self) -> ChatPromptTemplate:
        """
        Constructs a highly structured system prompt mandating zero hallucination.
        """
        system_template = """You are a highly analytical, factual reasoning engine. Your sole purpose is to answer the user's question based strictly and exclusively on the provided Context. 

CRITICAL RULES:
1. Do NOT rely on your internal training knowledge or external information under any circumstances.
2. If the precise answer is not explicitly contained within the provided Context chunks, you MUST output exactly: "I lack sufficient information in the provided context to answer this query." Do not fabricate, guess, or extrapolate.
3. Keep your answer concise, direct, and directly attribute your findings to the provided context.

Context History (if applicable):
{chat_history}

Retrieved Context:
{context}

User Query: {question}"""

        return ChatPromptTemplate.from_template(system_template)

    def retrieve_context(self, query: str, k: int = 4) -> List[Document]:
        """
        1. Semantic Vector Search: Converts natural language to vector via local embeddings
        and retrieves top-k semantically relevant chunks from ChromaDB.
        """
        logger.info(f"Executing semantic search for query: '{query}' (Retrieving Top-{k})")
        retriever = self.vector_store.get_retriever(search_kwargs={"k": k})
        return retriever.invoke(query)

    def _format_docs(self, docs: List[Document]) -> str:
        """
        Stitches document chunks and their critical metadata (filename/page) into a unified string.
        """
        formatted_docs = []
        for i, doc in enumerate(docs):
            source = doc.metadata.get("filename", "Unknown Source")
            page = doc.metadata.get("page_number", "Unknown Page")
            formatted_docs.append(f"[Source: {source}, Page: {page}]\n{doc.page_content}")
        return "\n\n---\n\n".join(formatted_docs)

    def generate_response(self, query: str, chat_history: str = "") -> Dict[str, Any]:
        """
        4. Context Window Assembly & Execution: Unifies the system prompt, retrieved chunks, 
        and the query into the LCEL chain for generation.
        """
        # Step 1: Semantic Retrieval via local vector space
        retrieved_docs = self.retrieve_context(query)
        context_string = self._format_docs(retrieved_docs)
        
        # Step 2: Assemble Pipeline (LangChain Expression Language)
        rag_chain = (
            {
                "context": lambda x: context_string, 
                "question": RunnablePassthrough(),
                "chat_history": lambda x: chat_history
            }
            | self.prompt_template
            | self.llm
            | StrOutputParser()
        )
        
        # Step 3: Execute Chain Hybrid execution
        logger.info("Context window assembled. Invoking LLM reasoning engine...")
        try:
            response = rag_chain.invoke(query)
            return {
                "answer": response,
                "source_documents": retrieved_docs
            }
        except Exception as e:
            logger.error(f"Error during LLM execution: {e}")
            raise e

if __name__ == "__main__":
    # Example initialization (requires ChromaDB initialized and Ollama/API key present)
    pass
