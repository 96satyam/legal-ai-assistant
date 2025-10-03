from fastapi import FastAPI
from app.core.database import engine, Base
# Import your models so SQLAlchemy knows about them
from app.models import user, document, analysis

# This command tells SQLAlchemy to create all tables based on the models it finds
# that inherit from our "Base" class.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Agentic AI Legal Assistant")

@app.get("/", tags=["Health Check"])
def read_root():
    """
    Root endpoint to check if the API is running.
    """
    return {"status": "ok", "message": "Welcome to the AI Legal Assistant API!"}