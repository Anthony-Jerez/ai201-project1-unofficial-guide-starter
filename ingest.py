import os
import re
from constants import DOCS_DIR

def load_and_clean_file(filepath):
    """Read a single file and perform cleaning tasks"""
    with open(filepath, "r", encoding="utf-8") as f:
        raw_text = f.read()

    # Setup regex for cleaning
    source_tag_pattern = re.compile(r"\\s*")
    cleaned_text = re.sub(source_tag_pattern, "", raw_text)
    
    return cleaned_text

def chunk_document(cleaned_text, filename):
    """Take clean text, extract metadata, and build chunk payloads."""
    document_chunks = []
    
    # Split by structural delimiter
    parts = [part.strip() for part in cleaned_text.split("---") if part.strip()]
    if not parts:
        return document_chunks

    # Isolate the global header block
    global_header = parts[0].strip()
    header_lines = global_header.split('\n')
    
    # Extract the specific variables
    prof_name = header_lines[0].replace("Professor Name: ", "").strip()
    avg_take_again = header_lines[1].replace("Avg Would take again: ", "").strip()
    avg_diff = header_lines[2].replace("Avg Level of Difficulty: ", "").strip()
    avg_rating = header_lines[3].replace("Avg Overall Rating: ", "").strip()

    # The subsequent parts are the individual student reviews
    reviews = parts[1:]

    for review in reviews:
        if len(review) == 0:
            continue
            
        # Payload: Only prepend the professor's name to keep the semantic signal strong
        final_chunk_text = f"Professor Name: {prof_name}\n\n{review}"
        
        # Attach payload and metadata to chunk
        chunk_data = {
            "text": final_chunk_text,
            "metadata": {
                "source": filename,
                "professor_name": prof_name,
                "avg_take_again": avg_take_again,
                "avg_difficulty": avg_diff,
                "avg_rating": avg_rating
            }
        }
        document_chunks.append(chunk_data)

    return document_chunks

def process_all_docs(docs_dir=DOCS_DIR):
    """The main orchestrator that loops through the documents directory."""
    all_chunks = []

    for filename in os.listdir(docs_dir):
        if not filename.endswith(".txt"):
            continue

        filepath = os.path.join(docs_dir, filename)
        
        # Call our document loading and chunking functions
        cleaned_text = load_and_clean_file(filepath)
        chunks = chunk_document(cleaned_text, filename)
        
        all_chunks.extend(chunks)

    return all_chunks

if __name__ == "__main__":
    # Run the orchestrated pipeline
    chunks = process_all_docs(DOCS_DIR)
    
    print(f"Total chunks generated: {len(chunks)}\n")
    print("--- INSPECTING FIRST 5 CHUNKS ---\n")
    
    for i in range(min(5, len(chunks))):
        print(f"CHUNK {i+1} (Source: {chunks[i]['metadata']['source']}):")
        print(chunks[i]["text"])
        print("\n" + "="*60 + "\n")