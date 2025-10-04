from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing import List, Dict
from app.core.config import settings
from .state import AgentState

# --- 1. DEFINE THE STRUCTURED OUTPUT MODELS ---

class Risk(BaseModel):
    """A single identified legal risk."""
    clause_text: str = Field(description="The specific text of the clause that contains the risk.")
    risk_level: str = Field(description="The severity of the risk (low, medium, high, or critical).")
    description: str = Field(description="A detailed explanation of why this clause is a risk.")
    mitigation: str = Field(description="A suggestion on how to modify the clause to reduce the risk.")

class RiskAnalysisOutput(BaseModel):
    """The complete risk analysis for a set of clauses."""
    risks: List[Risk] = Field(description="A list of all identified risks.")
    overall_risk_score: str = Field(description="An overall assessment of the contract's risk level (low, medium, high, critical).")



# Initialize the LLM
llm = ChatOpenAI(model="gpt-4-turbo", temperature=0, api_key=settings.OPENAI_API_KEY)

# Create an instance of our Pydantic Output Parser
parser = PydanticOutputParser(pydantic_object=RiskAnalysisOutput)

# Create the prompt template
risk_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an expert legal risk analyst. Your task is to analyze contract clauses for potential risks.

            Focus on identifying common legal risks such as:
            - Unlimited or one-sided liability
            - Vague or ambiguous obligations
            - One-sided termination rights
            - Broad indemnification clauses
            - Missing protective clauses for our client

            For each clause, you must provide a detailed risk assessment.
            
            {format_instructions}
            """,
        ),
        (
            "human",
            """Please analyze these contract clauses for potential legal risks:

            <CLAUSES>
            {clauses_text}
            </CLAUSES>
            """,
        ),
    ]
).partial(format_instructions=parser.get_format_instructions())

# Create the full LCEL chain
risk_assessment_chain = risk_prompt | llm | parser



# --- 3. CREATE THE AGENT'S CORE LOGIC ---

class RiskAssessmentAgent:
    """This agent analyzes parsed clauses to identify legal risks."""
    
    def run(self, parsed_clauses: List[Dict]) -> RiskAnalysisOutput:
        """
        Processes the clauses and returns a structured risk analysis.
        """
        print(f"   Analyzing {len(parsed_clauses)} clauses for risks...")

        # Format the clauses into a single string for the prompt
        clauses_text = "\n\n".join(
            [f"Clause {c.get('clause_number', 'N/A')}: {c.get('text', '')}" for c in parsed_clauses]
        )

        # Invoke the chain
        # The Pydantic parser will automatically handle validation and conversion
        try:
            analysis_result = risk_assessment_chain.invoke({"clauses_text": clauses_text})
            return analysis_result
        except Exception as e:
            print(f"   An error occurred during risk analysis: {e}")
            # Return an empty result in case of an error
            return RiskAnalysisOutput(risks=[], overall_risk_score="unknown")

# --- 4. DEFINE THE LANGGRAPH NODE ---

def risk_assessment_node(state: AgentState) -> AgentState:
    """
    The LangGraph node that executes the risk assessment agent.
    """
    print("---NODE: Risk Assessor---")
    
    parsed_clauses = state.get("parsed_clauses")
    if not parsed_clauses:
        print("   - No clauses to analyze. Skipping risk assessment.")
        return state

    agent = RiskAssessmentAgent()
    analysis_result = agent.run(parsed_clauses)
    
    # Update the shared state with the results
    state['identified_risks'] = analysis_result.risks
    state['current_step'] = "Risk Assessment Complete"
    
    print("---RISK ASSESSMENT COMPLETE---")
    print(f"   - Identified {len(analysis_result.risks)} risks.")
    print(f"   - Overall Contract Risk: {analysis_result.overall_risk_score}")
    
    return state