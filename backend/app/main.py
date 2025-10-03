from fastapi import FastAPI

# Create an instance of the FastAPI class
app = FastAPI(title="Agentic AI Legal Assistant")

# Define a "route" using a decorator
# This tells FastAPI that the function below handles GET requests to the "/" URL
@app.get("/", tags=["Health Check"])
def read_root():
    """
    Root endpoint to check if the API is running.
    """
    return {"status": "ok", "message": "Welcome to the AI Legal Assistant API!"}