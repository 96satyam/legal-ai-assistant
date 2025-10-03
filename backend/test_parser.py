from app.utils.document_parser import parse_document, extract_clauses, extract_entities

# Make sure you have a file at this path!
TEST_DOC_PATH = "../data/contracts/sample.docx" 

def main():
    print(f"--- Parsing Document: {TEST_DOC_PATH} ---")
    
    # Use our unified parser
    parsed_content = parse_document(TEST_DOC_PATH)
    
    if isinstance(parsed_content, list): # It's a DOCX
        # Combine all paragraphs into a single text block
        full_text = "\n".join([p['text'] for p in parsed_content])
    else: # It's a PDF
        full_text = parsed_content
    
    print("\n--- Extracted Text (first 300 chars) ---")
    print(full_text[:300] + "...")
    
    print("\n--- Extracting Clauses ---")
    clauses = extract_clauses(full_text)
    if clauses:
        print(f"Found {len(clauses)} clauses.")
        print("First clause found:", clauses[0])
    else:
        print("No clauses found with the current pattern.")
        
    print("\n--- Extracting Entities ---")
    entities = extract_entities(full_text)
    print("Entities found:", entities)


if __name__ == "__main__":
    main()