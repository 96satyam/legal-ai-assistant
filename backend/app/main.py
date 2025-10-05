from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import engine, Base
import app.models # Import the models package

from app.api import documents, analysis, qa
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
    allow_origins=[
        "https://localhost:3000",  # Your Word add-in
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# --- End CORS Configuration ---
app.include_router(analysis.router, prefix="/api")
app.include_router(qa.router, prefix="/api")

app.include_router(documents.router)
app.include_router(analysis.router)
@app.get("/", tags=["Health Check"])
def read_root():
    return {"status": "ok", "message": "Welcome to the AI Legal Assistant API!"}