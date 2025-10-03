from app.agents.supervisor import graph_app
from app.agents.state import AgentState
# Import our document parser from Phase 1
from app.utils.document_parser import parse_document

# --- STEP 1: PREPARE THE DOCUMENT TEXT ---

# Define the path to your sample contract
# Make sure this file exists and has some numbered clauses!
SAMPLE_DOC_PATH = "../data/contracts/sample1.docx"

# Parse the document to get its text content
print(f"--- Reading document from: {SAMPLE_DOC_PATH} ---")
parsed_content = parse_document(SAMPLE_DOC_PATH)

# Combine all paragraphs into a single string
# (This handles the list of dicts format from our DOCX parser)
document_text = "\n".join([p['text'] for p in parsed_content])


# --- STEP 2: DEFINE THE INITIAL STATE ---

# Now, use the real document text in the initial state
initial_input: AgentState = {
    "document_id": "doc123",
    "document_text": document_text, # Use the text we just read
    # Initialize other fields as empty
    "parsed_clauses": [],
    "clause_categories": {},
    "identified_risks": [],
    "missing_clauses": [],
    "comparison_result": {},
    "qa_messages": [],
    "current_step": "start",
    "error": ""
}

def main():
    print("\n--- Starting Graph Workflow ---")
    
    # The `stream` method runs the graph and yields the state after each step
    for step in graph_app.stream(initial_input):
        # The key of the dictionary is the name of the node that just finished
        node_name = list(step.keys())[0]
        state_after_step = list(step.values())[0]
        
        print(f"\n--- After Node: {node_name} ---")
        # Let's print the parsed clauses after the parser runs
        if node_name == "parser":
            print(f"   - Clauses Parsed: {len(state_after_step.get('parsed_clauses', []))}")
        print(f"Current Step: {state_after_step['current_step']}")

    print("\n--- Graph Workflow Finished ---")

if __name__ == "__main__":
    main()