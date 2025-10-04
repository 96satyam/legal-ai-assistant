# in app/agents/supervisor.py
import logging
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from langgraph.graph import StateGraph, END

from .state import AgentState
from .parser_agent import document_parser_node
from .risk_agent import risk_assessment_node
from .comparison_agent import comparison_node
from .rag_agent import rag_node
from .compliance_agent import compliance_node

from app.core.config import settings

# --- 1. SET UP PROFESSIONAL LOGGING ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- 2. BUILD THE FINAL REPORT AGGREGATION CHAIN ---

llm = ChatOpenAI(model="gpt-4-turbo", temperature=0, api_key=settings.OPENAI_API_KEY)

aggregator_prompt = ChatPromptTemplate.from_template(
    """You are a senior legal counsel. Your task is to synthesize the findings from your team of junior analysts into a single, comprehensive executive summary.

    You have been provided with the following data:
    - A list of parsed contract clauses.
    - A list of identified legal risks.
    - A list of compliance check results.

    Please generate a final report in Markdown format with the following sections:
    1.  **Executive Summary:** A high-level overview of the contract's purpose, key risks, and overall compliance status.
    2.  **Key Risk Analysis:** Detail the most critical risks found, explaining their potential impact and suggested mitigations.
    3.  **Compliance Assessment:** Summarize the findings of the compliance checks.

    Here is the data from your team:

    <RISKS>
    {identified_risks}
    </RISKS>

    <COMPLIANCE_RESULTS>
    {compliance_results}
    </COMPLIANCE_RESULTS>

    <CLAUSES>
    {parsed_clauses}
    </CLAUSES>
    """
)

aggregation_chain = aggregator_prompt | llm | StrOutputParser()


# --- 3. DEFINE THE NEW AGGREGATOR AND ERROR HANDLER NODES ---

def aggregator_node(state: AgentState) -> AgentState:
    """The final node that synthesizes all findings into a report."""
    logging.info("---NODE: Aggregating Final Report---")
    
    # You can add more context here if needed
    report = aggregation_chain.invoke({
        "identified_risks": state["identified_risks"],
        "compliance_results": state["compliance_results"],
        "parsed_clauses": state["parsed_clauses"]
    })
    
    state["final_report"] = report
    state["current_step"] = "Report Generated"
    logging.info("---FINAL REPORT GENERATED---")
    return state

def error_node(state: AgentState) -> AgentState:
    """A dedicated node to handle and log errors."""
    logging.error(f"---ERROR ENCOUNTERED--- \n {state['error']}")
    return state

# --- 4. DEFINE THE SUPERVISOR'S ROUTING LOGIC ---

def route_task(state: AgentState):
    """The 'traffic cop' that directs the workflow."""
    # Check for errors first
    if state.get("error"):
        logging.warning("Error detected, routing to error handler.")
        return "error"

    task_type = state.get("task_type")
    logging.info(f"---ROUTING: Task type is '{task_type}'---")
    
    if task_type == "analyze":
        return "parser"
    elif task_type == "compare":
        return "comparison"
    elif task_type == "qa":
        return "rag"
    else:
        return END

# --- 5. BUILD THE FINAL, ROBUST GRAPH ---

workflow = StateGraph(AgentState)

# Add all nodes to the graph
workflow.add_node("parser", document_parser_node)
workflow.add_node("risk_assessor", risk_assessment_node)
workflow.add_node("compliance_checker", compliance_node)
workflow.add_node("aggregator", aggregator_node) # New node
workflow.add_node("error", error_node)           # New node
workflow.add_node("comparison", comparison_node)
workflow.add_node("rag", rag_node)

# Set the entry point and routing
workflow.set_conditional_entry_point(
    route_task,
    {
        "parser": "parser",
        "comparison": "comparison",
        "rag": "rag",
        "error": "error",
        END: END
    }
)

# Define all the connections
workflow.add_edge("parser", "risk_assessor")
workflow.add_edge("risk_assessor", "compliance_checker")
workflow.add_edge("compliance_checker", "aggregator") # <-- New edge
workflow.add_edge("aggregator", END)                  # <-- New edge
workflow.add_edge("comparison", END)
workflow.add_edge("rag", END)
workflow.add_edge("error", END) # Errors lead to the end

# Compile the final graph
graph_app = workflow.compile()