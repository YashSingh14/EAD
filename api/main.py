import os
import shutil
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ingest.ingestion import DocumentIngestionPipeline
from data.vector_store import LocalVectorStore
from core.orchestration import HybridLLMOrchestrator

app = FastAPI(title="Enterprise RAG API")

# Configure CORS for Vite React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8501", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize singletons
vector_store = LocalVectorStore()
ingestion_pipeline = DocumentIngestionPipeline()

# Temp directory for uploads
UPLOAD_DIR = "./data/temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class ChatRequest(BaseModel):
    query: str
    provider: str = "local"
    model_name: str = "mistral"

class ChatResponse(BaseModel):
    answer: str
    citations: List[dict]

@app.post("/api/upload")
async def upload_documents(files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")
        
    processed_count = 0
    all_chunks = []
    
    for file in files:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        try:
            # Process and chunk the document using our LangChain pipeline
            chunks = ingestion_pipeline.process_document(file_path)
            all_chunks.extend(chunks)
            processed_count += 1
        except Exception as e:
            print(f"Error processing {file.filename}: {e}")
        finally:
            # Clean up temp file to maintain zero-footprint state
            if os.path.exists(file_path):
                os.remove(file_path)
                
    if all_chunks:
        # Ingest into ChromaDB Local Vector Store
        vector_store.ingest_chunks(all_chunks)
        
    return {"status": "success", "files_processed": processed_count, "chunks_indexed": len(all_chunks)}

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Initialize Orchestrator dynamically based on user config from React
        orchestrator = HybridLLMOrchestrator(
            vector_store=vector_store,
            provider=request.provider,
            model_name=request.model_name
        )
        
        # Generate Response using the semantic router
        result = orchestrator.generate_response(request.query)
        
        # Map LangChain Documents to UI Citations Format
        citations = []
        for doc in result["source_documents"]:
            citations.append({
                "filename": doc.metadata.get("filename", "Unknown Source"),
                "page": doc.metadata.get("page_number", 1),
                "snippet": doc.page_content
            })
            
        return ChatResponse(answer=result["answer"], citations=citations)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/reset")
async def reset_store():
    vector_store.reset_store()
    return {"status": "success", "message": "Vector store memory completely reset."}
