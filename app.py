import os
import gradio as gr
from groq import Groq
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Groq client
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def ask_assistant(question):
    """Handles the RAG pipeline: Retrieve -> Format -> Generate"""
    
    # Retrieve the top 5 most relevant chunks from ChromaDB
    from vector_store import setup_vector_store
    collection = setup_vector_store()
    
    search_results = collection.query(
        query_texts=[question],
        n_results=5,
        include=["documents", "metadatas"]
    )
    
    # Format the retrieved context and extract unique sources
    context_blocks = []
    unique_sources = set()
    
    for i in range(len(search_results['documents'][0])):
        doc = search_results['documents'][0][i]
        meta = search_results['metadatas'][0][i]
        
        # Build a clean block of text for the LLM to read
        context_blocks.append(f"Source: {meta['source']}\n{doc}\n")
        unique_sources.add(meta['source'])
        
    compiled_context = "\n---\n".join(context_blocks)
    
    # The Strict Grounding System Prompt
    system_prompt = f"""You are a helpful academic advisor assistant for Queens College students. 
Your ONLY job is to answer the user's question based STRICTLY on the context provided below.

Context:
{compiled_context}

RULES:
1. If the answer is not contained within the context above, you MUST explicitly say: "I don't have enough information on that based on the student reviews."
2. Do NOT use your general training knowledge to answer questions. 
3. Briefly cite the source document in your answer when making claims.
"""

    # Generate the response using Groq
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ],
        temperature=0.0 # Force deterministic, non-creative answers
    )
    
    answer = response.choices[0].message.content
    return answer, list(unique_sources)

# Gradio UI Setup
def handle_query(question):
    answer, sources = ask_assistant(question)
    # Format the sources beautifully for the UI
    source_text = "\n".join(f"• {s}" for s in sources)
    return answer, source_text

with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# QC CS Professor Review AI")
    gr.Markdown("Ask a question about CS professors, and I will search the raw latest student reviews to give you objective insight.")
    
    inp = gr.Textbox(label="Your question", placeholder="e.g., Are Kenneth Lord's exams difficult?")
    btn = gr.Button("Ask")
    
    answer_box = gr.Textbox(label="Answer", lines=8)
    sources_box = gr.Textbox(label="Retrieved from", lines=3)
    
    # Wire up the inputs
    btn.click(handle_query, inputs=inp, outputs=[answer_box, sources_box])
    inp.submit(handle_query, inputs=inp, outputs=[answer_box, sources_box])

if __name__ == "__main__":
    # Launch the web interface
    demo.launch(server_name="127.0.0.1", server_port=7860)