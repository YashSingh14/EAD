import os
from pinecone import Pinecone, ServerlessSpec
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
import logging

load_dotenv()

api_key = os.environ.get("PINECONE_API_KEY")
index_name = os.environ.get("PINECONE_INDEX_NAME", "echomind-mvp")

pc = None
index = None
embeddings_model = None

if api_key:
    pc = Pinecone(api_key=api_key)
    
    # Check if index exists, if not try to create it (Serverless by default for MVP)
    # Using cosine similarity as requested in TRD
    if index_name not in pc.list_indexes().names():
        try:
            pc.create_index(
                name=index_name,
                dimension=1536, # Dimension for text-embedding-3-small
                metric='cosine',
                spec=ServerlessSpec(
                    cloud='aws',
                    region='us-east-1' # Default fallback, adjust if needed
                )
            )
        except Exception as e:
            logging.error(f"Error creating Pinecone index: {e}")
            
    index = pc.Index(index_name)
    
if os.environ.get("OPENAI_API_KEY"):
    embeddings_model = OpenAIEmbeddings(model="text-embedding-3-small")

def generate_embedding(text: str) -> list[float]:
    """Generates an embedding for the given text."""
    if not embeddings_model:
        raise Exception("OpenAI embeddings model is not initialized.")
    return embeddings_model.embed_query(text)

def add_decision_to_vector_store(decision_id: str, problem_text: str, decision_text: str):
    """
    Embeds the problem and decision text and stores it in Pinecone.
    """
    if not index:
        raise Exception("Pinecone index is not initialized.")
        
    # Combine text for embedding
    combined_text = f"Problem: {problem_text}\nDecision & Reasoning: {decision_text}"
    vector = generate_embedding(combined_text)
    
    metadata = {
        "decision_id": str(decision_id),
        "text": combined_text
    }
    
    # Upsert using decision_id as the vector ID
    index.upsert(vectors=[(str(decision_id), vector, metadata)])
    return str(decision_id)

def search_similar_decisions(query: str, top_k: int = 3) -> list:
    """
    Searches for similar decisions in Pinecone using the query string.
    Returns a list of metadata dictionaries containing decision_ids.
    """
    if not index:
        raise Exception("Pinecone index is not initialized.")
        
    query_vector = generate_embedding(query)
    results = index.query(vector=query_vector, top_k=top_k, include_metadata=True)
    
    return results.get('matches', [])
