from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from typing import List, Dict

from app.core.config import settings
from app.utils.document_parser import extract_clauses
from .state import AgentState

# --- 1. DEFINE THE CLASSIFICATION CHAIN ---

# Initialize the "brain" of our agent, the LLM
llm = ChatOpenAI(model="gpt-4", temperature=0, api_key=settings.OPENAI_API_KEY)

# Define the prompt template - the instructions for the LLM
classification_prompt = ChatPromptTemplate.from_template(
    """Classify the following contract clause into ONE of the following categories:

    - Payment Terms
    - Intellectual Property
    - Confidentiality
    - Termination
    - Liability
    - Dispute Resolution
    - General Provisions
    - Other (If it does not fit into any of the above categories)

    Clause:
    {clause_text}

    Classification:"""
)

# Define the output parser to clean up the LLM's response
output_parser = StrOutputParser()

# Create the full LCEL chain by "piping" the components together
classification_chain = classification_prompt | llm | output_parser


# --- 2. BUILD THE AGENT'S CORE LOGIC ---

class DocumentParserAgent:
    """This agent is responsible for parsing and structuring the document."""
    
    def run(self, document_text: str) -> Dict:
        """
        Processes the document text to extract and classify clauses.
        """
        print("   Running clause extraction from Phase 1...")
        # Use our utility from Phase 1 to get clauses
        clauses = extract_clauses(document_text)
        
        print(f"   Found {len(clauses)} clauses. Now classifying with LLM...")
        
        classified_clauses = []
        for clause in clauses:
            # For each clause, invoke our classification chain
            category = classification_chain.invoke({"clause_text": clause["content"]})
            
            classified_clauses.append({
                "clause_number": clause["clause_number"],
                "text": clause["content"],
                "category": category.strip()
            })
            print(f"   - Classified clause {clause['clause_number']} as '{category.strip()}'")

        return {"parsed_clauses": classified_clauses}
    


# --- 3. DEFINE THE LANGGRAPH NODE ---

def document_parser_node(state: AgentState) -> AgentState:
    """
    The LangGraph node that executes the document parsing agent.
    """
    print("---NODE: Document Parser---")
    
    document_text = state.get("document_text")
    if not document_text:
        return {**state, "error": "No document text found in state."}

    parser_agent = DocumentParserAgent()
    result = parser_agent.run(document_text)
    
    # Update the shared state with the results from this agent
    state['parsed_clauses'] = result['parsed_clauses']
    state['current_step'] = "Parsing Complete"
    
    print("---PARSING COMPLETE---")
    print(f"   - Parsed {len(state['parsed_clauses'])} clauses.")
    
    return state