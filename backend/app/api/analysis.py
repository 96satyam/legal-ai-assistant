from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
import logging

from app.agents.supervisor import graph_app
from app.agents.state import AgentState

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

router = APIRouter(
    prefix="/analysis",
    tags=["Analysis"]
)

# Define the data model for the incoming request
class AnalysisRequest(BaseModel):
    document_text: str

@router.post("/")
async def run_analysis(request: AnalysisRequest):
    """
    Receives document text, runs the full analysis workflow, 
    and returns the final aggregated report.
    """
    try:
        logging.info("Received request for analysis.")
        
        # 1. Set up the initial state for the LangGraph workflow
        initial_state: AgentState = {
            "task_type": "analyze",
            "document_id": "doc_from_word", # A simple identifier
            "document_text": request.document_text,
            "document_text_2": "",
            "parsed_clauses": [],
            "clause_categories": {},
            "identified_risks": [],
            "missing_clauses": [],
            "comparison_result": {},
            "compliance_results": [],
            "qa_messages": [],
            "final_report": "",

            "current_step": "start",
            "error": ""
        }
        
        # 2. Run the graph and stream the results
        final_state = None
        for step in graph_app.stream(initial_state):
            # The last step will contain the final state
            final_state = list(step.values())[0]

        # 3. Extract and return the final report
        if final_state and final_state.get("final_report"):
            logging.info("Analysis complete. Returning final report.")
            # We also return the identified risks for the highlighting feature
            return {
                "report": final_state["final_report"],
                "risks": final_state["identified_risks"]
            }
        else:
            logging.error("Analysis failed to generate a report.")
            raise HTTPException(status_code=500, detail="Analysis failed to generate a report.")
            
    except Exception as e:
        logging.error(f"An error occurred during analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))