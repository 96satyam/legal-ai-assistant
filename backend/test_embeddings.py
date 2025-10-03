from app.utils.document_parser import parse_document
from app.utils.embeddings import index_document, search_documents

# Make sure you have a sample DOCX file here
TEST_DOC_PATH = "../data/contracts/sample1.docx" 

def main():
    print("--- 1. Parsing and preparing document ---")
    parsed_content = parse_document(TEST_DOC_PATH)
    full_text = "\n".join([p['text'] for p in parsed_content])
    
    doc_id = "sample_contract_01"
    metadata = {"filename": "sample.docx", "source": "local"}
    
    print(f"--- 2. Indexing document: {doc_id} ---")
    # This will chunk the text, embed it, and store it in ChromaDB.
    # This step involves API calls to OpenAI and may take a moment.
    index_document(doc_id=doc_id, text=full_text, metadata=metadata)
    
    print("\n--- 3. Testing search functionality ---")
    query = "What is the confidentiality period?"
    print(f"Query: '{query}'")
    
    # Search for the 3 most relevant chunks
    search_results = search_documents(query=query, n_results=3)
    
    print("\n--- Search Results ---")
    for i, result in enumerate(search_results):
        print(f"Result {i+1}:")
        # CHANGE THIS LINE:
        print(f"  Score: {result['score']:.4f}") # Changed from 'Distance' to 'Score'
        print(f"  Content: {result['content'][:150]}...")
        print("-" * 20)

if __name__ == "__main__":
    main()