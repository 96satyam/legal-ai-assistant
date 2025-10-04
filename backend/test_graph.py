from app.agents.supervisor import graph_app
from app.agents.state import AgentState
from app.utils.embeddings import index_document
from app.utils.document_parser import parse_document

# --- STEP 1: INDEX A DOCUMENT ---
# The RAG agent needs a document in the vector store to talk about.
print("--- Indexing a sample document for RAG... ---")
doc_text = "\n".join([p['text'] for p in parse_document("../data/contracts/sample1.docx")])
index_document(doc_id="doc123", text=doc_text, metadata={"source": "sample1.docx"})
print("--- Indexing complete. ---")

# --- STEP 2: RUN A CONVERSATION ---

def run_conversation_turn(state: AgentState):
    """Helper function to run one turn of the conversation."""
    final_state = None
    for step in graph_app.stream(state):
        node_name = list(step.keys())[0]
        state_after_step = list(step.values())[0]
        print(f"\n--- After Node: {node_name} ---")
        final_state = state_after_step
    return final_state

def main_analyze():
    print("--- Starting Full Analysis Workflow ---")
    doc_text = "\n".join([p['text'] for p in parse_document("../data/contracts/sample1.docx")])

    initial_state = {
        "task_type": "analyze",
        "document_id": "doc_analyze_123",
        "document_text": doc_text,
        # ... initialize all other fields to be empty/None
        "document_text_2": "", "parsed_clauses": [], "clause_categories": {},
        "identified_risks": [], "missing_clauses": [], "comparison_result": None,
        "compliance_results": [], "qa_messages": [], "current_step": "start", "error": ""
    }

    final_state = None
    for step in graph_app.stream(initial_state):
        node_name = list(step.keys())[0]
        state_after_step = list(step.values())[0]
        print(f"\n--- After Node: {node_name} ---")
        final_state = state_after_step

    print("\n--- Graph Workflow Finished ---")

    if final_state and final_state.get("compliance_results"):
        print("\n\n--- COMPLIANCE RESULTS ---")
        for result in final_state["compliance_results"]:
            print(f"  - Requirement: {result.requirement}")
            print(f"    Compliant: {'Yes' if result.is_compliant else 'No'}")
            print(f"    Severity: {result.severity}")
            print(f"    Assessment: {result.assessment}\n")

if __name__ == "__main__":
    main_analyze()