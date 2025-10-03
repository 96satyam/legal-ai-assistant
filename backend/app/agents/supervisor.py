from langgraph.graph import StateGraph, END
from .state import AgentState
from .parser_agent import document_parser_node
# --- DEFINE AGENT NODES (Placeholders for now) ---
# In a real system, each of these would be a call to a dedicated agent class.
# For now, they are simple functions that print a message.



def risk_assessment_node(state: AgentState):
    print("---Step 2: ASSESSING RISKS---")
    # In the future, this will call the real risk agent
    state['current_step'] = "Risk Assessment Complete"
    return state

def compliance_node(state: AgentState):
    print("---Step 3: CHECKING COMPLIANCE---")
    # In the future, this will call the real compliance agent
    state['current_step'] = "Compliance Check Complete"
    return state

# --- BUILD THE GRAPH ---

# 1. Initialize the StateGraph with our AgentState
workflow = StateGraph(AgentState)

# 2. Add the nodes to the graph
workflow.add_node("parser", document_parser_node) 
workflow.add_node("risk_assessor", risk_assessment_node)
workflow.add_node("compliance_checker", compliance_node)

# 3. Define the connections (edges) between the nodes
# This defines the linear flow of our analysis.
workflow.set_entry_point("parser")
workflow.add_edge("parser", "risk_assessor")
workflow.add_edge("risk_assessor", "compliance_checker")
workflow.add_edge("compliance_checker", END) # The END node signifies the workflow is finished

# 4. Compile the graph into a runnable object
# This is the final "app" we can call to run our workflow.
graph_app = workflow.compile()