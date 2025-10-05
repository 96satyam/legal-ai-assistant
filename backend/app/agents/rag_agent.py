# in app/agents/rag_agent.py
import logging
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from .state import AgentState
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, api_key=settings.OPENAI_API_KEY)

def rag_node(state: AgentState) -> AgentState:
    """
    RAG node for Q&A functionality.
    Answers questions based on the document text.
    """
    logger.info("---NODE: RAG Q&A---")
    
    # Get the last user question
    qa_messages = state.get("qa_messages", [])
    if not qa_messages:
        logger.warning("No Q&A messages found")
        state["error"] = "No question provided"
        return state
    
    # Find the last user message
    question = None
    for msg in reversed(qa_messages):
        if msg.get("role") == "user":
            question = msg.get("content")
            break
    
    if not question:
        logger.warning("No user question found in messages")
        state["error"] = "No question found"
        return state
    
    document_text = state.get("document_text", "")
    
    if not document_text:
        logger.warning("No document text available for Q&A")
        state["error"] = "No document text available"
        return state
    
    logger.info(f"Processing question: {question[:100]}...")
    
    # Create Q&A prompt
    qa_prompt = ChatPromptTemplate.from_template(
        """You are a legal assistant helping to analyze a contract. 
        
Based on the following contract text, answer the user's question accurately and concisely.

Contract Text:
{document_text}

Question: {question}

Instructions:
1. Provide a clear, direct answer based only on the contract text
2. Quote relevant sections when possible
3. If the answer isn't in the contract, say so clearly
4. Keep your answer focused and professional

Answer:"""
    )
    
    try:
        # Get answer from LLM
        response = (qa_prompt | llm).invoke({
            "document_text": document_text[:4000],  # Limit to avoid token limits
            "question": question
        })
        
        answer = response.content
        
        # Add assistant response to messages
        state["qa_messages"].append({
            "role": "assistant",
            "content": answer,
            "citations": []  # Can be enhanced to extract citations
        })
        
        logger.info("Q&A response generated successfully")
        state["current_step"] = "qa_complete"
        
    except Exception as e:
        logger.error(f"Q&A processing failed: {e}")
        state["error"] = f"Q&A failed: {str(e)}"
        state["qa_messages"].append({
            "role": "assistant",
            "content": f"I encountered an error processing your question: {str(e)}",
            "citations": []
        })
    
    return state