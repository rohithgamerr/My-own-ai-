
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "online", "message": "Lumina Minimal Server is Live!"}

@app.post("/chat")
async def chat(data: dict):
    return {"response": "Minimal server is working! AI Engine is still being calibrated."}
