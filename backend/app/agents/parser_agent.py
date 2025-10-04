from pydantic import BaseModel, Field
from typing import List, Dict
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI

from app.core.config import settings
from app.utils.document_parser import extract_clauses
from .state import AgentState
import json

# --- 1. DEFINE A MORE COMPLEX STRUCTURED OUTPUT ---

class ClauseClassification(BaseModel):
    clause_number: str = Field(description="The number of the clause, e.g., '1.1' or 'a'.")
    category: str = Field(description="The classification category for this clause.")

class ClassificationOutput(BaseModel):
    classifications: List[ClauseClassification] = Field(description="A list of all classified clauses.")

# --- 2. UPDATE THE CLASSIFICATION CHAIN ---

llm = ChatOpenAI(model="gpt-4-turbo", temperature=0, api_key=settings.OPENAI_API_KEY)

# Create a Pydantic parser for our new, more complex output
pydantic_parser = PydanticOutputParser(pydantic_object=ClassificationOutput)

# Update the prompt to handle a list of clauses and ask for JSON
classification_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an expert at classifying legal contract clauses.
            
            Your task is to analyze a list of clauses provided by the user and classify each one into ONE of the following categories:
            - Payment Terms
            - Intellectual Property
            - Confidentiality
            - Termination
            - Liability
            - Dispute Resolution
            - General Provisions
            - Other

            Please provide your output as a single, valid JSON object containing a list of classifications.
            
            {format_instructions}
            """,
        ),
        (
            "human",
            """Please classify the following contract clauses:

            <CLAUSES>
            {clauses_json}
            </CLAUSES>
            """,
        ),
    ]
).partial(format_instructions=pydantic_parser.get_format_instructions())

# Create the chain with the new Pydantic parser
classification_chain = classification_prompt | llm | pydantic_parser


# --- 3. REFACTOR THE AGENT'S CORE LOGIC ---

class DocumentParserAgent:
    """This agent now processes all clauses in a single batch."""
    
    def run(self, document_text: str) -> Dict:
        print("   Running clause extraction from Phase 1...")
        clauses = extract_clauses(document_text)
        print(f"   Found {len(clauses)} clauses. Now classifying with a single LLM call...")
        
        # Convert clauses to a JSON string to pass to the prompt
        clauses_json = json.dumps(clauses)
        
        # Invoke the chain ONCE for all clauses
        result = classification_chain.invoke({"clauses_json": clauses_json})
        
        # Combine original text with the new categories
        clause_map = {c["clause_number"]: c["content"] for c in clauses}
        classified_clauses = []
        for classification in result.classifications:
            classified_clauses.append({
                "clause_number": classification.clause_number,
                "text": clause_map.get(classification.clause_number, ""),
                "category": classification.category
            })
        
        return {"parsed_clauses": classified_clauses}

# --- 4. THE LANGGRAPH NODE (No changes needed) ---
def document_parser_node(state: AgentState) -> AgentState:
    print("---NODE: Document Parser---")
    
    document_text = state.get("document_text")
    if not document_text:
        state["error"] = "No document text found in state."
        return state

    parser_agent = DocumentParserAgent()
    result = parser_agent.run(document_text)
    
    state['parsed_clauses'] = result['parsed_clauses']
    state['current_step'] = "Parsing Complete"
    
    print("---PARSING COMPLETE---")
    print(f"   - Parsed and classified {len(state['parsed_clauses'])} clauses in a single batch.")
    
    return state