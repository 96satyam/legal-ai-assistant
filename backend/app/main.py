from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import engine, Base
import app.models # Import the models package
from app.api import documents

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Agentic AI Legal Assistant")

# --- CORS Configuration ---
# Define the list of allowed origins (your frontend's URL)
origins = [
    "http://localhost:3000",  # For React Web Dashboard
    "http://localhost:3001",  # A potential second port
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allow all methods (GET, POST, etc.)
    allow_headers=["*"], # Allow all headers
)
# --- End CORS Configuration ---

app.include_router(documents.router)

@app.get("/", tags=["Health Check"])
def read_root():
    return {"status": "ok", "message": "Welcome to the AI Legal Assistant API!"}