from langchain_openai import ChatOpenAI
# Corrected imports for chain helpers
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
# The rest of your imports
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory

from app.core.config import settings
from app.utils.embeddings import vector_store
from .state import AgentState

# --- 1. SETUP THE CORE RAG COMPONENTS ---

# Initialize the LLM we'll use for answering
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, api_key=settings.OPENAI_API_KEY)

# The Retriever is the component that fetches relevant documents from our vector store
retriever = vector_store.as_retriever(search_kwargs={"k": 5})

# This is the prompt for the main Q&A part of the chain.
# It instructs the LLM to answer based ONLY on the provided context.
qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful legal assistant. Answer the user's questions based on the context provided. If you can't answer the question with the given context, say 'I am not sure.'\n\nContext:\n{context}"),
        ("human", "{input}"),
    ]
)

# This chain takes a question and the retrieved documents and generates an answer.
question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)


# --- 2. ADD CONVERSATIONAL MEMORY ---

# This prompt helps the LLM rewrite a follow-up question into a self-contained one
history_aware_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "Given the chat history and a follow-up question, rephrase the question to be a standalone question."),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
    ]
)

# This chain takes the history and a new question, and creates a new, standalone question
history_aware_retriever_chain = create_history_aware_retriever(
    llm, retriever, history_aware_prompt
)

# This is our final, complete RAG chain.
# It will first rewrite the question based on history, then retrieve documents,
# and finally, generate an answer.
rag_chain = create_retrieval_chain(history_aware_retriever_chain, question_answer_chain)

# This is a dictionary that will act as our in-memory session history
session_histories = {}

def get_session_history(session_id: str):
    """Gets the chat history for a given session, creating one if it doesn't exist."""
    if session_id not in session_histories:
        session_histories[session_id] = ChatMessageHistory()
    return session_histories[session_id]

# Finally, we wrap our RAG chain in a special runnable that manages the history
conversational_rag_chain = RunnableWithMessageHistory(
    rag_chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
    output_messages_key="answer",
)

# --- 3. DEFINE THE LANGGRAPH NODE ---
def rag_node(state: AgentState) -> AgentState:
    print("---NODE: RAG Q&A---")

    # Get the latest question from the state
    question = state["qa_messages"][-1]["content"]

    # We use the document_id as the session_id for the chat history
    session_id = state["document_id"]

    # Invoke the conversational chain
    result = conversational_rag_chain.invoke(
        {"input": question},
        config={"configurable": {"session_id": session_id}}
    )

    # Append the AI's answer to the message list
    state["qa_messages"].append({"role": "ai", "content": result["answer"]})

    print("---RAG Q&A COMPLETE---")
    return state