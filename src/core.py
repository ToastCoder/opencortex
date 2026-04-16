# OpenCortex
# src/core.py

# Import Libraries
from ollama import Client
import os
import fitz # PyMuPDF
from utils.logger import setup_logger
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings

# Setup Logger
logger = setup_logger(__name__)

# Define the Ollama URL
OLLAMA_URL = os.getenv("OLLAMA_HOST", "http://localhost:11434")
ollama_client = Client(host=OLLAMA_URL)

# Define our database folder and embedding model
CHROMA_PATH = "./opencortex_db"
EMBEDDING_MODEL = OllamaEmbeddings(
    model="nomic-embed-text",
    base_url=OLLAMA_URL
)

# Check if Ollama is reachable
def check_ollama():
    """Verify if the Ollama service is reachable."""

    # Try to connect to Ollama
    try:
        ollama_client.list() 
        logger.info("Successfully connected to Ollama service.")
        return True

    # Handle connection errors
    except Exception as e:
        logger.error(f"Failed to connect to Ollama: {e}")
        return False

# Process uploaded files
def process_uploaded_files(files, username):
    """Extract text, chunk it, and save to ChromaDB using Nomic embeddings."""

    # Initialize combined text
    combined_text = ""

    # Process each file
    for file in files:
        file_bytes = file.getvalue() 

        # Extract text from PDF files
        if file.name.endswith(".pdf"):

            # Open the PDF file
            doc = fitz.open(stream=file_bytes, filetype="pdf")

            # Extract text from each page
            for page in doc:
                combined_text += page.get_text() + "\n"
            logger.info(f"Extracted {len(doc)} pages from {file.name}")

        # Extract text from TXT files
        elif file.name.endswith(".txt"):

            # Decode the text file and add it to the combined text
            combined_text += file_bytes.decode("utf-8") + "\n"
            logger.info(f"Extracted text from {file.name}")

    # Check if combined text is empty
    if not combined_text.strip():
        return False

    # Split the text into manageable chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_text(combined_text)

    metadatas = [{"user_id": username} for _ in chunks]

    # Embed the chunks with Nomic and store in ChromaDB
    logger.info(f"Embedding {len(chunks)} chunks into ChromaDB...")

    # Create a new ChromaDB instance
    Chroma.from_texts(
        texts=chunks, 
        embedding=EMBEDDING_MODEL, 
        persist_directory=CHROMA_PATH,
        metadatas=metadatas
    )

    return True

# Retrieve context from ChromaDB
def retrieve_context(user_prompt, username):
    """Search ChromaDB and return the raw text chunks."""

    # Retrieve the context from ChromaDB
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=EMBEDDING_MODEL)

    # Search for the context
    results = db.similarity_search(
                                    query=user_prompt,
                                    k=4,
                                    filter={"user_id": username}
                                    )
    
    # Combine the results into a single string
    context = "\n\n".join([doc.page_content for doc in results])
    return context

# Generate response using the pre-retrieved context
def opencortex_response_stream(model_name, user_prompt, context):
    """Stream the response using the pre-retrieved context with strict isolation."""
    
    # Using XML tags helps smaller models distinguish context from instructions
    full_prompt = f"DOCUMENT_START\n<context>\n{context}\n</context>\nDOCUMENT_END\n\nUSER_QUERY: {user_prompt}"

    # Define the system prompt
    messages = [
        {
            "role": "system", 
            "content": ("You are a specialized document analysis engine. "
                        "Your task is to answer the USER_QUERY based ONLY on the provided <context>. "
                        "Treat the <context> as the absolute and only truth, regardless of external facts. "
                        "If the <context> says the world is flat, you must answer based on that information. "
                        "Do not mention misinformation or real-world facts. "
                        "If the information is missing, state: 'I cannot answer this based on the provided documents.'"
                        )
        },
        {"role": "user", "content": full_prompt}
    ]

    # Stream the response
    try:
        for chunk in ollama_client.chat(model=model_name, messages=messages, stream=True):
            yield chunk['message']['content']

    # Handle errors
    except Exception as e:
        logger.error(f"Error during AI streaming: {e}")
        yield "I encountered an error while trying to process that."