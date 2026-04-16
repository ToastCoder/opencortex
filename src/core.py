# src/core.py
import ollama
import fitz # PyMuPDF
from utils.logger import setup_logger
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings

# Setup Logger
logger = setup_logger(__name__)

# Define our database folder and embedding model
CHROMA_PATH = "./opencortex_db"
EMBEDDING_MODEL = OllamaEmbeddings(model="nomic-embed-text")

def check_ollama():
    """Verify if the Ollama service is reachable."""
    try:
        ollama.list()
        logger.info("Successfully connected to Ollama service.")
        return True
    except Exception as e:
        logger.error(f"Failed to connect to Ollama: {e}")
        return False

def process_uploaded_files(files):
    """Extract text, chunk it, and save to ChromaDB using Nomic embeddings."""
    combined_text = ""

    for file in files:
        file_bytes = file.getvalue() 

        if file.name.endswith(".pdf"):
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            for page in doc:
                combined_text += page.get_text() + "\n"
            logger.info(f"Extracted {len(doc)} pages from {file.name}")

        elif file.name.endswith(".txt"):
            combined_text += file_bytes.decode("utf-8") + "\n"
            logger.info(f"Extracted text from {file.name}")

    if not combined_text.strip():
        return False

    # 1. Split the text into manageable chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_text(combined_text)

    # 2. Embed the chunks with Nomic and store in ChromaDB
    logger.info(f"Embedding {len(chunks)} chunks into ChromaDB...")
    Chroma.from_texts(
        texts=chunks, 
        embedding=EMBEDDING_MODEL, 
        persist_directory=CHROMA_PATH
    )
    return True

def opencortex_response_stream(model_name, user_prompt):
    """Retrieve relevant chunks from ChromaDB and stream the response."""
    
    # 1. Connect to the existing Chroma database
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=EMBEDDING_MODEL)
    
    # 2. Search for the top 4 most relevant chunks to the user's question
    results = db.similarity_search(user_prompt, k=4)
    
    # 3. Combine those specific chunks into our context
    context = "\n\n".join([doc.page_content for doc in results])
    
    full_prompt = f"Context from Sources:\n{context}\n\nUser Question: {user_prompt}"

    messages = [
        {"role": "system", "content": "You are OpenCortex. Answer strictly using ONLY the provided context."},
        {"role": "user", "content": full_prompt}
    ]

    try:
        for chunk in ollama.chat(model=model_name, messages=messages, stream=True):
            yield chunk['message']['content']
    except Exception as e:
        logger.error(f"Error during AI streaming: {e}")
        yield "I encountered an error while trying to process that."