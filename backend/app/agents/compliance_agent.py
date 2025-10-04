from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import re
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from app.core.config import settings
from .state import AgentState
# --- 1. DEFINE RULE SETS AND OUTPUT MODELS ---

GDPR_RULES = [
    {
        'requirement': 'Data Processing Agreement (DPA)',
        'keywords': ['personal data', 'data subject', 'processor', 'controller', 'data processing'],
        'severity': 'critical',
        'description': 'Checks if the contract contains language that constitutes a DPA, governing the processing of personal data.'
    },
    {
        'requirement': 'Right to Erasure (Right to be Forgotten)',
        'keywords': ['delete', 'erasure', 'right to be forgotten', 'remove data'],
        'severity': 'high',
        'description': 'Checks if the contract acknowledges the data subject\'s right to have their personal data erased.'
    },
]
# In a real app, you would add many more rule sets here.

class ComplianceResult(BaseModel):
    """A single compliance check result."""
    requirement: str = Field(description="The specific compliance requirement that was checked.")
    is_compliant: bool = Field(description="Whether the document is compliant with the requirement.")
    clause_text: Optional[str] = Field(description="The specific text of the clause that addresses the requirement.")
    assessment: str = Field(description="The LLM's detailed assessment of the compliance status.")
    severity: str = Field(description="The severity of a potential non-compliance issue.")

class ComplianceOutput(BaseModel):
    """The complete compliance analysis for the document."""
    results: List[ComplianceResult]



# --- 2. BUILD THE COMPLIANCE VERIFICATION CHAIN ---

llm = ChatOpenAI(model="gpt-4-turbo", temperature=0, api_key=settings.OPENAI_API_KEY)
parser = PydanticOutputParser(pydantic_object=ComplianceResult)

compliance_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an expert in legal compliance. Your task is to analyze a contract to verify if it meets a specific compliance requirement.
            
            Based on the full text of the contract, determine if the requirement is met.
            - If it is met, set `is_compliant` to True, extract the specific clause text that satisfies it, and explain why.
            - If it is not met or not mentioned, set `is_compliant` to False and explain what is missing.
            
            {format_instructions}
            """,
        ),
        (
            "human",
            """Please verify the following compliance requirement against the contract text.

            Requirement: {requirement}
            Requirement Description: {description}
            
            Full Contract Text:
            <CONTRACT>
            {full_text}
            </CONTRACT>
            """,
        ),
    ]
).partial(format_instructions=parser.get_format_instructions())

compliance_chain = compliance_prompt | llm | parser

# --- 3. CREATE THE AGENT'S CORE LOGIC ---

class ComplianceAgent:
    """Agent that checks a document against a set of compliance rules."""

    def _keyword_check(self, text: str, rules: List[Dict]) -> Dict[str, bool]:
        """Fast check to see if any keywords for a rule exist in the text."""
        print("   Running fast keyword check...")
        results = {}
        for rule in rules:
            found = any(re.search(r'\b' + keyword + r'\b', text, re.IGNORECASE) for keyword in rule['keywords'])
            results[rule['requirement']] = found
            print(f"   - Requirement '{rule['requirement']}': Keywords {'FOUND' if found else 'NOT FOUND'}")
        return results

    def run(self, document_text: str) -> ComplianceOutput:
        """Runs the full hybrid compliance check."""
        keyword_results = self._keyword_check(document_text, GDPR_RULES)
        
        final_results = []
        for rule in GDPR_RULES:
            requirement = rule['requirement']
            print(f"   Running detailed LLM check for: '{requirement}'...")
            
            if not keyword_results[requirement]:
                # If keywords are missing, we can flag it without calling the LLM
                result = ComplianceResult(
                    requirement=requirement,
                    is_compliant=False,
                    clause_text=None,
                    assessment="The requirement is likely not met as none of the relevant keywords were found in the document.",
                    severity=rule['severity']
                )
            else:
                # Keywords were found, so run the more expensive LLM check
                try:
                    result = compliance_chain.invoke({
                        "requirement": requirement,
                        "description": rule['description'],
                        "full_text": document_text
                    })
                    # Add the severity from our rule definition to the LLM's result
                    result.severity = rule['severity']
                except Exception as e:
                    print(f"   An error occurred during LLM compliance check: {e}")
                    result = ComplianceResult(
                        requirement=requirement,
                        is_compliant=False,
                        clause_text=None,
                        assessment=f"An error occurred during analysis: {e}",
                        severity=rule['severity']
                    )
            
            final_results.append(result)

        return ComplianceOutput(results=final_results)

# --- 4. DEFINE THE LANGGRAPH NODE ---

def compliance_node(state: AgentState) -> AgentState:
    print("---NODE: Compliance Checker---")
    
    agent = ComplianceAgent()
    result = agent.run(state["document_text"])
    
    # We need to add 'compliance_results' to the AgentState
    state["compliance_results"] = result.results
    state["current_step"] = "Compliance Check Complete"

    print(f"---COMPLIANCE CHECK COMPLETE---")
    print(f"   - Performed {len(result.results)} checks.")
    
    return state