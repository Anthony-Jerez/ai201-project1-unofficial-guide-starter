import chromadb
from chromadb.utils import embedding_functions
from ingest import process_all_docs
from constants import DOCS_DIR 

def setup_vector_store():
    client = chromadb.PersistentClient(path="./chroma_db")

    # Load the local embedding model
    embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

    # Create the collection using cosine distance
    collection = client.get_or_create_collection(
        name="qc_professor_reviews",
        embedding_function=embedding_func,
        metadata={"hnsw:space": "cosine"} # Forces cosine similarity (0.0 to 1.0)
    )

    # If the vector database is empty, populate it
    if collection.count() == 0:
        print("Database empty. Loading and chunking documents...")
        chunks = process_all_docs(DOCS_DIR)
        
        documents = []
        metadatas = []
        ids = []
        
        # Track position per file to satisfy the metadata requirement
        position_tracker = {}
        
        for i, chunk in enumerate(chunks):
            # Grab the rich metadata dictionary created in ingest.py
            meta = chunk["metadata"]
            source_file = meta["source"]
            
            # Increment position count for this specific file
            position_tracker[source_file] = position_tracker.get(source_file, 0) + 1
            
            documents.append(chunk["text"])
            
            # Inject the position tracking into the existing rich metadata dictionary
            meta["position_in_file"] = position_tracker[source_file]
            
            metadatas.append(meta)
            ids.append(f"chunk_{i}")
            
        print(f"Embedding {len(chunks)} chunks into ChromaDB...")
        collection.add(documents=documents, metadatas=metadatas, ids=ids)
        print("Vector store populated successfully!\n")
    else:
        print(f"Database loaded. Found {collection.count()} chunks.\n")

    return collection

def test_retrieval(collection):
    """Tests 3 specific questions from the Evaluation Plan."""
    
    test_queries = [
        "Does Professor Jerry Waxman allow students to use electronics like phones or computers during his lectures?",
        "What advice do students give to prepare for exams in Cuneyt Akinlar's introductory CSCI 111 course?",
        "What is a common student complaint regarding the formatting and presentation of Gaurish Telang's lecture slides?"
    ]

    for q_idx, query in enumerate(test_queries, 1):
        print(f"--- TEST QUERY {q_idx} ---")
        print(f"Q: {query}")
        
        # We explicitly request 'distances' to be returned
        results = collection.query(
            query_texts=[query],
            n_results=5,
            include=["documents", "metadatas", "distances"]
        )

        for i in range(len(results['documents'][0])):
            doc = results['documents'][0][i]
            meta = results['metadatas'][0][i]
            dist = results['distances'][0][i]
            
            print(f"\nResult {i+1} | Source: {meta['source']} (Pos: {meta['position_in_file']}) | Distance: {dist:.4f}")
            # Print the matched chunk
            print(f"Text: {doc}")
            
        print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    db_collection = setup_vector_store()
    test_retrieval(db_collection)