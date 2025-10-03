import re
from typing import List, Dict, Any
import docx
from PyPDF2 import PdfReader
import spacy

# Load the spaCy model once when the module is loaded
# This is more efficient than loading it in the function every time.
nlp = spacy.load("en_core_web_sm")

def parse_docx(file_path: str) -> List[Dict[str, str]]:
    """
    Parses a .docx file and extracts paragraphs with their text and style.

    Args:
        file_path: The path to the Word document.

    Returns:
        A list of dictionaries, where each dict contains a paragraph's 'text' and 'style'.
    """
    try:
        doc = docx.Document(file_path)
        parsed_content = []
        for para in doc.paragraphs:
            # We only care about paragraphs that contain text
            if para.text.strip():
                parsed_content.append({
                    'text': para.text,
                    'style': para.style.name
                })
        return parsed_content
    except Exception as e:
        print(f"Error parsing DOCX file {file_path}: {e}")
        return []

def parse_pdf(file_path: str) -> str:
    """
    Parses a .pdf file and extracts all text.

    Args:
        file_path: The path to the PDF document.

    Returns:
        A single string containing all the text from the PDF.
    """
    try:
        with open(file_path, "rb") as f:
            reader = PdfReader(f)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            return text
    except Exception as e:
        print(f"Error parsing PDF file {file_path}: {e}")
        return ""

def parse_document(file_path: str) -> Any:
    """
    A unified parser that handles different document types based on extension.

    Args:
        file_path: The path to the document.

    Returns:
        The parsed content, format depends on the file type.
    """
    if file_path.endswith(".docx"):
        return parse_docx(file_path)
    elif file_path.endswith(".pdf"):
        # For simplicity, we'll process the raw PDF text later
        return parse_pdf(file_path)
    else:
        raise ValueError("Unsupported file type. Please use .docx or .pdf")
    

def clean_text(text: str) -> str:
    """
    Cleans raw text by removing excessive whitespace and normalizing line breaks.
    """
    # Replace multiple spaces/tabs with a single space
    text = re.sub(r'\s+', ' ', text)
    # Remove leading/trailing whitespace from each line
    text = "\n".join(line.strip() for line in text.splitlines())
    return text.strip()

def extract_clauses(full_text: str) -> List[Dict[str, Any]]:
    """
    Extracts numbered clauses from a contract text using regular expressions.
    """
    # Regex to find patterns like "1.", "1.1.", "1.1.1.", "(a)", etc.
    # This is a starting point and can be refined.
    clause_pattern = re.compile(r"^\s*(\d+(?:\.\d+)*\.?|\([a-zA-Z0-9]+\))\s+")
    
    lines = full_text.splitlines()
    clauses = []
    current_clause_content = []
    current_clause_number = None

    for line in lines:
        match = clause_pattern.match(line)
        if match:
            # If we found a new clause number, save the previous one
            if current_clause_number is not None:
                clauses.append({
                    "clause_number": current_clause_number,
                    "content": "\n".join(current_clause_content).strip()
                })
            
            # Start a new clause
            current_clause_number = match.group(1).strip()
            # The content is the rest of the line after the number
            content_after_match = line[match.end():].strip()
            current_clause_content = [content_after_match] if content_after_match else []
        elif current_clause_number is not None:
            # This line is part of the current clause
            current_clause_content.append(line)

    # Add the last clause after the loop finishes
    if current_clause_number is not None:
        clauses.append({
            "clause_number": current_clause_number,
            "content": "\n".join(current_clause_content).strip()
        })
        
    return clauses

def extract_entities(text: str) -> Dict[str, List[str]]:
    """
    Extracts named entities (like organizations, dates, money) from text using spaCy.
    
    """
    doc = nlp(text)
    entities = {
        "organizations": [],
        "dates": [],
        "money": []
    }
    for ent in doc.ents:
        if ent.label_ == "ORG":
            entities["organizations"].append(ent.text)
        elif ent.label_ == "DATE":
            entities["dates"].append(ent.text)
        elif ent.label_ == "MONEY":
            entities["money"].append(ent.text)
            
    # Remove duplicates
    for key in entities:
        entities[key] = list(set(entities[key]))
        
    return entities