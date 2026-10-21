import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from ai_engine import LuminaAIEngine
from relationship_engine import RelationshipExtractionEngine

app = FastAPI(title="Lumina Mind AI API")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Engines
# In production, the API key should come from an environment variable
API_KEY = os.getenv("OPENAI_API_KEY", "«redacted:sk-…»")
engine = LuminaAIEngine(api_key=API_KEY)
rel_engine = RelationshipExtractionEngine(api_key=API_KEY)

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        answer = engine.query(request.message)
        return ChatResponse(response=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...), 
    source: Optional[str] = Form(None), 
    category: Optional[str] = Form(None)
):
    try:
        content = await file.read()
        text = content.decode("utf-8")
        metadata = {"source": source or file.filename, "category": category or "general"}
        
        chunks_count = engine.ingest_document(text, metadata)
        rel_engine.extract_and_store(text)
        return {"status": "success", "chunks_ingested": chunks_count, "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/graph")
async def get_graph():
    try:
        return rel_engine.get_graph()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/knowledge-map")
async def get_knowledge_map():
    # The current LuminaAIEngine doesn't have a structured map method, 
    # but we can return the current vector store state or a placeholder
    # For now, we return basic info about the vector store
    try:
        # Chroma doesn't provide a simple 'map' of all contents without querying,
        # but we can return a summary or the persistence directory.
        return {
            "status": "active",
            "db_path": "./lumina_db",
            "engine": "gpt-4o",
            "embedding_model": "text-embedding-3-small"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
