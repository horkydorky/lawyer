import os
import sys
import json
import uuid
from pathlib import Path
from typing import List, Dict, Optional
from tqdm import tqdm
from dotenv import load_dotenv

# Ensure we can import from config (if it exists)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

# Attempt to import necessary libraries, handle missing ones gracefully
try:
    import fitz  # PyMuPDF
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain_chroma import Chroma
    import chromadb
    from google import genai
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("Please ensure you have installed the requirements from 'requirements_deploy.txt'.")
    sys.exit(1)

# Configuration from paths or defaults
try:
    from config.paths import DATA_DIR, PROCESSED_DIR, VECTORSTORE_DIR
except ImportError:
    # Fallback default paths if config module not found
    DATA_DIR = PROJECT_ROOT / "data"
    PROCESSED_DIR = DATA_DIR / "processed"
    VECTORSTORE_DIR = PROJECT_ROOT / "chroma_db"

EMBEDDING_MODEL = "BAAI/bge-large-en-v1.5"
COLLECTION_NAME = "legal_docs"

# Load environment variables
load_dotenv(PROJECT_ROOT / ".env")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("⚠️  Warning: GEMINI_API_KEY not found in environment variables.")
    # Proceed anyway, but some features (like re-extraction) might fail if needed.
    # For ingestion from pre-processed JSONs, we might not need it if embeddings are local (HuggingFace).
    # But wait, the notebook uses Gemini for embeddings? 
    # Let's check: get_embeddings uses client.models.embed_content?
    # Ah, the notebook uses standard HuggingFaceEmbeddings for Chroma, but also has a `get_embeddings` function using Gemini.
    # The `create_vector_store` function uses `HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)`.
    # So we don't strictly need Gemini API key for the vector store if we use the local model.
    pass

def load_json_files(folder: Path) -> List[tuple]:
    """Load all JSON files from folder."""
    if not folder.exists():
        print(f"⚠️  Processed data directory not found: {folder}")
        return []
    
    json_files = list(folder.glob("*.json"))
    data = []
    for f in json_files:
        try:
            with open(f, "r", encoding="utf-8") as jf:
                data.append((f.stem, json.load(jf)))
        except Exception as e:
            print(f"⚠️  Failed to load {f.name}: {e}")
    return data

def flatten_legal_json(doc_title: str, js: Dict) -> List[Dict]:
    """
    Flatten legal JSON structure into distinct chunks for vector search.
    """
    entries = []

    # Preamble
    if js.get("preamble"):
        entries.append({
            "text": js["preamble"].strip(),
            "metadata": {
                "document_title": doc_title,
                "section": "Preamble"
            }
        })

    # Parts and Articles
    for part in js.get("parts", []):
        pnum = part.get("part_number", "")
        ptitle = part.get("part_title", "")
        for article in part.get("articles", []):
            anum = article.get("article_number", "")
            atitle = article.get("article_title", "")
            clauses = article.get("clauses", [])

            for idx, clause in enumerate(clauses, start=1):
                entries.append({
                    "text": clause.strip(),
                    "metadata": {
                        "document_title": doc_title,
                        "part_number": pnum,
                        "part_title": ptitle,
                        "article_number": anum,
                        "article_title": atitle,
                        "clause_index": idx,
                        "section": "Clause"
                    }
                })
    return entries

def create_vector_store(persist_dir: Path):
    """Rebuild the ChromaDB vector store from processed JSON data."""
    print("📚 Loading processed JSONs from:", PROCESSED_DIR)
    data = load_json_files(PROCESSED_DIR)

    if not data:
        print("❌ No data found to ingest. Ensure 'data/processed' contains valid JSON files.")
        return

    all_entries = []
    for doc_name, js in tqdm(data, desc="Flattening documents"):
        all_entries.extend(flatten_legal_json(doc_name, js))

    print(f"🧩 Total {len(all_entries)} text entries to embed")

    # Initialize ChromaDB Client
    # Note: Using langchain-chroma wrapper for easier integration with standard embeddings
    
    print(f"🔄 Initializing Vector Store at {persist_dir}...")
    
    # We use HuggingFace embeddings as per notebook configuration
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )

    try:
        # Check if directory exists and clean it if you want strict rebuild, 
        # but Chroma handles persistence. 
        # We can just create execution using from_texts.
        
        # Extract texts and metadatas
        texts = [e["text"] for e in all_entries]
        metadatas = [e["metadata"] for e in all_entries]
        
        # Batch processing might be needed for large datasets, 
        # but langchain Chroma wrapper handles batching usually. 
        # If dataset is huge, consider manual batching.
        
        vectordb = Chroma.from_texts(
            texts=texts,
            embedding=embeddings,
            metadatas=metadatas,
            persist_directory=str(persist_dir),
            collection_name=COLLECTION_NAME
        )
        
        print(f"✅ Vector store successfully created at: {persist_dir}")
        print(f"📊 Collection '{COLLECTION_NAME}' is ready.")
        
    except Exception as e:
        print(f"❌ Failed to create vector store: {e}")

if __name__ == "__main__":
    create_vector_store(VECTORSTORE_DIR)
