from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.documents import Document
from typing import List, Dict

from app.core.config import settings

# --- INITIALIZATION ---

# 1. Initialize the OpenAI Embedding Model (this stays the same)
embedding_function = OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY)

# 2. Initialize the LangChain Chroma vector store
# This wrapper class handles the communication with ChromaDB for us.
vector_store = Chroma(
    collection_name="contracts",
    embedding_function=embedding_function,
    persist_directory="../../data/chroma" # The directory to save the database
)

# --- TEXT PROCESSING AND INDEXING ---

def index_document(doc_id: str, text: str, metadata: Dict):
    """
    Chunks a document, creates LangChain Document objects, and stores them in Chroma.
    """
    # 1. Chunk the text
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
    )
    chunks = text_splitter.split_text(text)
    
    # 2. Create LangChain Document objects
    # The LangChain wrapper expects data in its own `Document` format.
    documents = []
    for i, chunk in enumerate(chunks):
        # Create a metadata dictionary for each chunk
        doc_metadata = {
            "doc_id": doc_id,
            "chunk_id": i,
            **metadata # Add original document metadata
        }
        doc = Document(page_content=chunk, metadata=doc_metadata)
        documents.append(doc)

    # 3. Add the documents to the vector store
    vector_store.add_documents(documents)
    print(f"Successfully indexed {len(documents)} chunks for document {doc_id}.")

# --- SEARCH AND RETRIEVAL ---

def search_documents(query: str, n_results: int = 5) -> List[Dict]:
    """
    Searches the vector store for documents similar to the query.
    """
    # The `similarity_search_with_score` method returns documents and their similarity scores.
    results_with_scores = vector_store.similarity_search_with_score(query, k=n_results)
    
    # Format the results for easier use
    formatted_results = []
    for doc, score in results_with_scores:
        formatted_results.append({
            "content": doc.page_content,
            "metadata": doc.metadata,
            "score": score # Lower score is better (more similar)
        })
        
    return formatted_results