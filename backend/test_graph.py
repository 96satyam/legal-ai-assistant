from app.agents.supervisor import graph_app
from app.agents.state import AgentState

# Define an initial input to kick off the workflow
initial_input: AgentState = {
    "document_id": "doc123",
    "document_text": "This is a sample contract...",
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
    print("--- Starting Graph Workflow ---")
    
    # The `stream` method runs the graph and yields the state after each step
    for step in graph_app.stream(initial_input):
        # The key of the dictionary is the name of the node that just finished
        node_name = list(step.keys())[0]
        state_after_step = list(step.values())[0]
        
        print(f"\n--- After Node: {node_name} ---")
        print(f"Current Step: {state_after_step['current_step']}")

    print("\n--- Graph Workflow Finished ---")

if __name__ == "__main__":
    main()