from pydantic import BaseModel, Field
from typing import List, Dict
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from app.core.config import settings
from app.utils.document_parser import extract_clauses
from .state import AgentState

# --- Pydantic Models (No Change) ---
class Change(BaseModel):
    type: str = Field(description="The type of change: 'added', 'removed', or 'modified'.")
    clause_number_a: str = Field(description="Clause number from Document A (if applicable).")
    text_a: str = Field(description="The text from Document A (if applicable).")
    clause_number_b: str = Field(description="Clause number from Document B (if applicable).")
    text_b: str = Field(description="The text from Document B (if applicable).")
    explanation: str = Field(description="An LLM-generated explanation of the change's significance.")

class ComparisonOutput(BaseModel):
    changes: List[Change]


# --- Utilities and Chains (No Change) ---
embedding_model = OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY)
llm = ChatOpenAI(model="gpt-4", temperature=0, api_key=settings.OPENAI_API_KEY)
explanation_prompt = ChatPromptTemplate.from_template(
    """You are a legal analyst. Explain the key difference and legal significance between these two versions of a contract clause.

    Version A: {text_a}
    Version B: {text_b}

    Explanation:"""
)
explanation_chain = explanation_prompt | llm | StrOutputParser()


# --- AGENT LOGIC (OPTIMIZED VERSION) ---
class ComparisonAgent:
    """Agent that compares two contract documents efficiently."""
    
    def run(self, doc_a_text: str, doc_b_text: str) -> ComparisonOutput:
        print("   Extracting clauses from both documents...")
        clauses_a = extract_clauses(doc_a_text)
        clauses_b = extract_clauses(doc_b_text)
        
        # **OPTIMIZATION 1: Batch embed all clauses at once**
        print("   Embedding all clauses in two batch API calls...")
        texts_a = [c["content"] for c in clauses_a]
        texts_b = [c["content"] for c in clauses_b]
        embeddings_a = embedding_model.embed_documents(texts_a)
        embeddings_b = embedding_model.embed_documents(texts_b)

        # **OPTIMIZATION 2: Calculate all similarities at once**
        print("   Calculating similarity matrix...")
        # This creates a matrix where similarity_matrix[i][j] is the similarity
        # between clause i from doc A and clause j from doc B.
        similarity_matrix = cosine_similarity(embeddings_a, embeddings_b)
        
        changes = []
        matched_b_indices = set()

        # Find matches for clauses in Document A
        print("   Aligning clauses and identifying changes...")
        for i, clause_a in enumerate(clauses_a):
            # **OPTIMIZATION 3: Find best match instantly using the matrix**
            best_match_idx = np.argmax(similarity_matrix[i])
            best_match_score = similarity_matrix[i][best_match_idx]
            
            # Categorize the change
            if best_match_score > 0.98: # Stricter threshold for "identical"
                matched_b_indices.add(best_match_idx)
            elif best_match_score > 0.75: # Threshold for "modified"
                if best_match_idx in matched_b_indices: continue # Already matched to a better candidate
                matched_b_indices.add(best_match_idx)
                clause_b = clauses_b[best_match_idx]
                explanation = explanation_chain.invoke({"text_a": clause_a["content"], "text_b": clause_b["content"]})
                changes.append(Change(
                    type="modified",
                    clause_number_a=clause_a["clause_number"], text_a=clause_a["content"],
                    clause_number_b=clause_b["clause_number"], text_b=clause_b["content"],
                    explanation=explanation
                ))
            else: # No good match found
                changes.append(Change(type="removed", clause_number_a=clause_a["clause_number"], text_a=clause_a["content"], clause_number_b="", text_b="", explanation="This clause from Document A was not found in Document B."))

        # Identify added clauses from Document B
        for j, clause_b in enumerate(clauses_b):
            if j not in matched_b_indices:
                changes.append(Change(type="added", clause_number_a="", text_a="", clause_number_b=clause_b["clause_number"], text_b=clause_b["content"], explanation="This clause was newly added in Document B."))
        
        return ComparisonOutput(changes=changes)

# --- LANGGRAPH NODE (No Change) ---
def comparison_node(state: AgentState) -> AgentState:
    print("---NODE: Document Comparison---")
    agent = ComparisonAgent()
    # Note: the state needs document_text and document_text_2
    result = agent.run(state["document_text"], state.get("document_text_2", ""))
    state["comparison_result"] = result
    state['current_step'] = "Comparison Complete"
    print(f"   - Comparison found {len(result.changes)} changes.")
    return state