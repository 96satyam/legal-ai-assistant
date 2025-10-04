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

def main():
    print("\n--- Starting RAG Workflow ---")
    
    # Turn 1: Initial Question
    print("\n--- Turn 1: Asking the first question... ---")
    initial_state = {
        "task_type": "qa",
        "document_id": "doc123",
        "qa_messages": [{"role": "human", "content": "How long is the confidentiality period?"}],
        # Initialize other fields as empty
        "document_text": "", "document_text_2": "", "parsed_clauses": [], 
        "clause_categories": {}, "identified_risks": [], "missing_clauses": [],
        "comparison_result": None, "current_step": "", "error": ""
    }
    state_after_turn1 = run_conversation_turn(initial_state)
    print("\nAI Response:", state_after_turn1["qa_messages"][-1]["content"])
    
    # Turn 2: Follow-up Question
    print("\n\n--- Turn 2: Asking a follow-up question... ---")
    # The new state is the final state from the previous turn, with a new question appended.
    state_for_turn2 = state_after_turn1
    state_for_turn2["qa_messages"].append({"role": "human", "content": "What are the exclusions to this?"})
    
    state_after_turn2 = run_conversation_turn(state_for_turn2)
    print("\nAI Response:", state_after_turn2["qa_messages"][-1]["content"])

if __name__ == "__main__":
    main()