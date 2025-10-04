from typing_extensions import TypedDict
from typing import List, Dict, Any

class AgentState(TypedDict):
    """
    This TypedDict represents the shared state of our agent system.
    It's the central "project folder" that all agents read from and write to.
    """
    task_type: str
    document_id: str
    document_text: str
    document_text_2: str

    # Data extracted by the Parser Agent
    parsed_clauses: List[Dict]
    clause_categories: Dict[str, str]

    # Data added by the Risk Agent
    identified_risks: List[Dict]

    # Data for other agents we will build later
    missing_clauses: List[str]
    comparison_result: Dict
    compliance_results: List[Dict] 
    qa_messages: List[Dict] # For conversational Q&A

    # Workflow management
    current_step: str
    error: str