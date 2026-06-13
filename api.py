from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import os

from dotenv import load_dotenv
load_dotenv()

from utils.db import insert_decision, update_decision_vector_id
from utils.vector_store import add_decision_to_vector_store
from utils.ai_extractor import extract_decision_from_text, extract_text_from_pdf
from utils.recommender import generate_recommendation

app = FastAPI(title="EchoMind API", version="1.0.0")

# Allow the frontend (any local origin) to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

import os
from fastapi.responses import RedirectResponse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
DIST_DIR = os.path.join(BASE_DIR, "frontend-friendly-hub", "dist")
ASSETS_DIR = os.path.join(DIST_DIR, "assets")

# Serve the frontend static files if directory exists
if os.path.isdir(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

    @app.get("/")
    async def serve_frontend():
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))
elif os.path.isdir(DIST_DIR):
    app.mount("/static", StaticFiles(directory=DIST_DIR), name="static")
    
    # Vite builds place JS/CSS in the /assets folder by default. Mount it so index.html can load them.
    if os.path.isdir(ASSETS_DIR):
        app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")

    @app.get("/")
    async def serve_frontend():
        return FileResponse(os.path.join(DIST_DIR, "index.html"))
else:
    @app.get("/")
    async def serve_frontend():
        return RedirectResponse(url="/docs")



# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class SearchRequest(BaseModel):
    query: str

class CaptureRequest(BaseModel):
    problem_description: str
    context: Optional[str] = ""
    options_considered: Optional[str] = ""
    decision_taken: str
    reasoning: str
    outcome: Optional[str] = ""

class ConfirmRequest(BaseModel):
    problem_description: str
    context: Optional[str] = ""
    options_considered: Optional[str] = ""
    decision_taken: str
    reasoning: str
    outcome: Optional[str] = ""


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.post("/api/search")
async def search(req: SearchRequest):
    """Search organizational memory and return an AI recommendation."""
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    try:
        recommendation, cases = generate_recommendation(req.query)
        # Convert any non-serializable types to strings for safety
        serializable_cases = []
        for case in cases:
            serializable_cases.append({k: str(v) if v is not None else "" for k, v in case.items()})
        return {"recommendation": recommendation, "cases": serializable_cases}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/capture")
async def capture(req: CaptureRequest):
    """Manually capture and embed an expert decision."""
    try:
        data = {
            "problem_description": req.problem_description,
            "context": req.context,
            "options_considered": req.options_considered,
            "decision_taken": req.decision_taken,
            "reasoning": req.reasoning,
            "outcome": req.outcome,
            "status": "manual_entry",
        }
        inserted = insert_decision(data)
        decision_id = inserted.get("id")
        if not decision_id:
            raise HTTPException(status_code=500, detail="Failed to insert decision into database.")

        vector_id = add_decision_to_vector_store(decision_id, req.problem_description, req.decision_taken)
        update_decision_vector_id(decision_id, vector_id)
        return {"success": True, "decision_id": str(decision_id)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/upload")
async def upload(file: UploadFile = File(...)):
    """Accept a .txt or .pdf file and return AI-extracted structured decision data."""
    if not (file.filename.endswith(".txt") or file.filename.endswith(".pdf")):
        raise HTTPException(status_code=400, detail="Only .txt and .pdf files are supported.")
    try:
        file_bytes = await file.read()
        if file.filename.endswith(".pdf"):
            text = extract_text_from_pdf(file_bytes)
        else:
            text = file_bytes.decode("utf-8")

        extracted = extract_decision_from_text(text)
        return {"success": True, "data": extracted}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/confirm")
async def confirm(req: ConfirmRequest):
    """Save AI-extracted (and user-reviewed) decision data to DB and vector store."""
    try:
        data = {
            "problem_description": req.problem_description,
            "context": req.context,
            "options_considered": req.options_considered,
            "decision_taken": req.decision_taken,
            "reasoning": req.reasoning,
            "outcome": req.outcome,
            "status": "ai_extracted",
        }
        inserted = insert_decision(data)
        decision_id = inserted.get("id")
        if not decision_id:
            raise HTTPException(status_code=500, detail="Failed to insert decision into database.")

        vector_id = add_decision_to_vector_store(decision_id, req.problem_description, req.decision_taken)
        update_decision_vector_id(decision_id, vector_id)
        return {"success": True, "decision_id": str(decision_id)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health():
    """Simple health check."""
    return {
        "status": "ok",
        "openai": bool(os.environ.get("OPENAI_API_KEY")),
        "supabase": bool(os.environ.get("SUPABASE_URL") and os.environ.get("SUPABASE_KEY")),
        "pinecone": bool(os.environ.get("PINECONE_API_KEY")),
    }
