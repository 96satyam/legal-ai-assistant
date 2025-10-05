from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import List, Dict
import logging

from app.agents.supervisor import graph_app
from app.agents.state import AgentState

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/qa",
    tags=["Q&A"]
)

# Store document contexts in memory (in production, use a proper database)
document_store: Dict[str, str] = {}

class QuestionRequest(BaseModel):
    document_id: str
    question: str
    document_text: str = ""  # Optional: provide if not stored

@router.post("/ask")
async def ask_question(request: QuestionRequest):
    """
    Ask a question about a document
    """
    try:
        logger.info(f"Received Q&A request for document: {request.document_id}")
        
        # Get or store document text
        if request.document_text:
            document_store[request.document_id] = request.document_text
        
        doc_text = document_store.get(request.document_id, request.document_text)
        
        if not doc_text:
            raise HTTPException(
                status_code=400, 
                detail="Document text not found. Please analyze the document first."
            )
        
        # Set up state for Q&A
        initial_state: AgentState = {
            "task_type": "qa",
            "document_id": request.document_id,
            "document_text": doc_text,
            "document_text_2": "",
            "parsed_clauses": [],
            "clause_categories": {},
            "identified_risks": [],
            "missing_clauses": [],
            "comparison_result": {},
            "compliance_results": [],
            "qa_messages": [
                {"role": "user", "content": request.question}
            ],
            "final_report": "",
            "current_step": "start",
            "error": ""
        }
        
        # Run the Q&A workflow
        final_state = None
        for step in graph_app.stream(initial_state):
            final_state = list(step.values())[0]
        
        if not final_state:
            raise HTTPException(status_code=500, detail="Q&A processing failed")
        
        # Extract the answer from qa_messages
        qa_messages = final_state.get("qa_messages", [])
        
        # The last message should be the assistant's response
        answer = None
        citations = []
        
        if qa_messages:
            for msg in reversed(qa_messages):
                if msg.get("role") == "assistant":
                    answer = msg.get("content")
                    citations = msg.get("citations", [])
                    break
        
        if not answer:
            raise HTTPException(status_code=500, detail="No answer generated")
        
        logger.info("Q&A complete. Returning answer.")
        
        return {
            "answer": answer,
            "citations": citations,
            "document_id": request.document_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Q&A error: {e}")
        raise HTTPException(status_code=500, detail=str(e))