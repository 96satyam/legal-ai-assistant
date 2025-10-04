from app.agents.supervisor import graph_app
from app.agents.state import AgentState
from app.utils.document_parser import parse_document

# --- PREPARE TWO DOCUMENTS ---
doc_a_text = "\n".join([p['text'] for p in parse_document("../data/contracts/sample1.docx")])
doc_b_text = "\n".join([p['text'] for p in parse_document("../data/contracts/sample2.docx")])

# --- DEFINE INITIAL STATE FOR COMPARISON ---
initial_input: AgentState = {
    "task_type": "compare",
    "document_id": "doc_A",
    "document_text": doc_a_text,
    "document_text_2": doc_b_text,
    # Initialize other fields
    "parsed_clauses": [], "clause_categories": {}, "identified_risks": [],
    "missing_clauses": [], "comparison_result": None, "qa_messages": [],
    "current_step": "start", "error": ""
}

def main():
    print("\n--- Starting Comparison Workflow ---")
    final_state = None
    for step in graph_app.stream(initial_input):
        node_name = list(step.keys())[0]
        state_after_step = list(step.values())[0]
        print(f"\n--- After Node: {node_name} ---")
        print(f"Current Step: {state_after_step['current_step']}")
        final_state = state_after_step

    print("\n--- Graph Workflow Finished ---")

    if final_state and final_state.get("comparison_result"):
        print("\n\n--- COMPARISON RESULTS ---")
        for change in final_state["comparison_result"].changes:
            print(f"  - Type: {change.type}")
            print(f"    Text A: {change.text_a[:100]}...")
            print(f"    Text B: {change.text_b[:100]}...")
            print(f"    Explanation: {change.explanation}\n")

if __name__ == "__main__":
    main()