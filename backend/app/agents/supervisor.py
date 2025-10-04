from langgraph.graph import StateGraph, END
from .state import AgentState
from .parser_agent import document_parser_node
from .risk_agent import risk_assessment_node
from .comparison_agent import comparison_node
from .rag_agent import rag_node

# --- DEFINE AGENT NODES (Placeholders for now) ---
# In a real system, each of these would be a call to a dedicated agent class.
# For now, they are simple functions that print a message.

def route_task(state: AgentState):
    """The 'traffic cop' that directs the workflow."""
    task_type = state.get("task_type")
    print(f"---ROUTING: Task type is '{task_type}'---")
    if task_type == "analyze":
        return "parser"
    elif task_type == "compare":
        return "comparison"
    elif task_type == "qa":
        return "rag"
    else:
        # A fallback to end the graph if the task type is unknown
        return END


def compliance_node(state: AgentState):
    print("---NODE: Compliance Checker (Placeholder)---")
    state['current_step'] = "Compliance Check Complete"
    return state

# --- BUILD THE GRAPH (Corrected Version) ---

workflow = StateGraph(AgentState)

# Add all the action nodes
workflow.add_node("parser", document_parser_node)
workflow.add_node("risk_assessor", risk_assessment_node)
workflow.add_node("comparison", comparison_node)
workflow.add_node("rag", rag_node)
# This is the correct way to start with a routing decision.
# We are NOT adding 'router' as a node.
workflow.set_conditional_entry_point(
    route_task,
    {
        "parser": "parser",
        "comparison": "comparison",
        "rag": "rag",
        END: END
    }
)

# Define the rest of the flow
workflow.add_edge("parser", "risk_assessor")
workflow.add_edge("risk_assessor", END)
workflow.add_edge("comparison", END)
workflow.add_edge("rag", END)
graph_app = workflow.compile()