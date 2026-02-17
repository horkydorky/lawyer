# backend/main.py
import os
import re
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import List, Dict
import chromadb
from google import genai
from fastapi.middleware.cors import CORSMiddleware

# ---- Environment and setup ----
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("❌ Missing GEMINI_API_KEY in .env")

client = genai.Client(api_key=API_KEY)

BASE_DIR = Path(__file__).resolve().parent
VECTORSTORE_DIR = BASE_DIR.parent / "chroma_db"
COLLECTION_NAME = "legal_docs"

app = FastAPI(
    title="MyPocketLawyer - Legal Assistant (Stateless)",
    description="Gemini-powered stateless legal assistant using Chroma for retrieval.",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Request model ----------
class ChatRequest(BaseModel):
    query: str
    k: int = 8


# ---------- Embedding helper ----------
# Lazy-load embedding model to reduce startup memory usage
embedding_model = None

def get_embedding_model():
    """Lazy-load the embedding model only when needed"""
    global embedding_model
    if embedding_model is None:
        print("🔄 Loading embedding model on CPU...")
        from langchain_huggingface import HuggingFaceEmbeddings
        embedding_model = HuggingFaceEmbeddings(
            model_name="BAAI/bge-large-en-v1.5",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
    return embedding_model

def get_query_embedding(text: str):
    # Use the local model to get query embedding
    model = get_embedding_model()
    return model.embed_query(text)


# ---------- Small-talk guard ----------
SMALL_TALK = {
    "hi", "hello", "hey", "yo", "sup",
    "good morning", "good afternoon", "good evening",
    "thanks", "thank you", "how are you", "test", "ping"
}

def is_small_talk(query: str) -> bool:
    q = query.strip().lower()
    return q in SMALL_TALK or len(q) <= 2


# ---------- Classification & Query Rewriting ----------
def classify_and_rewrite_query(query: str) -> (bool, str):
    prompt = f"""
You are a legal query processing agent for a Nepali law RAG system. Perform TWO tasks:

**TASK 1: DOMAIN CLASSIFICATION**
Determine if the user query relates to Nepali legal topics.
LEGAL TOPICS INCLUDE: Constitution, acts, courts, government bodies, rights, duties,
citizenship, crimes, labor law, property law, family law, constitutional structure.
NON-LEGAL: General knowledge, weather, sports, entertainment, technical issues.

**TASK 2: QUERY REWRITING** (Only if legal)
Rewrite the query into a concise legal search query for vector retrieval.
Include: jurisdiction (Nepal), legal topic, and core intent.

**OUTPUT FORMAT:**
IS_LEGAL: [YES/NO]
REWRITTEN_QUERY: [rewritten query or "N/A" if non-legal]

**USER QUERY:**
{query}

**YOUR RESPONSE:**
"""
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        result_text = (response.text or "").strip()

        is_legal = False
        rewritten_query = ""

        for line in result_text.splitlines():
            line = line.strip()
            if line.startswith("IS_LEGAL:"):
                legal_part = line.replace("IS_LEGAL:", "").strip().upper()
                is_legal = "LEGAL" in legal_part or legal_part in ["YES", "TRUE"]
            elif line.startswith("REWRITTEN_QUERY:"):
                rewritten_part = line.replace("REWRITTEN_QUERY:", "").strip()
                if rewritten_part != "N/A":
                    rewritten_query = rewritten_part

        if not rewritten_query and is_legal:
            rewritten_query = query

        return is_legal, rewritten_query

    except Exception as e:
        print(f"Classification/Rewriting error: {e}")
        return True, query


# ---------- Retrieval ----------
def retrieve_top_k(rewritten_query: str, k: int = 4):
    client_chroma = chromadb.PersistentClient(path=str(VECTORSTORE_DIR))
    try:
        collection = client_chroma.get_collection(name=COLLECTION_NAME)
    except Exception:
        raise HTTPException(status_code=404, detail=f"Collection '{COLLECTION_NAME}' not found.")

    query_emb = get_query_embedding(rewritten_query)

    results = collection.query(
        query_embeddings=[query_emb],
        n_results=k
    )

    output = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        output.append({
            "text": doc,
            "document_title": meta.get("document_title", "Unknown"),
            "part_number": meta.get("part_number", ""),
            "part_title": meta.get("part_title", ""),
            "article_number": meta.get("article_number", ""),
            "article_title": meta.get("article_title", ""),
            "clause_index": meta.get("clause_index", "")
        })
    return output


# ---------- Answer Generation ----------
def generate_legal_answer(query: str, sources: list):
    context_text = "\n\n".join([
        f"📘 Document: {src['document_title']}\n"
        f"Part {src['part_number']} – {src['part_title']}\n"
        f"Article {src['article_number']}: {src['article_title']}\n"
        f"Clause {src['clause_index']}\n"
        f"Text: {src['text']}"
        for src in sources
    ])

    prompt = f"""
You are MyPocketLawyer — an AI legal assistant specialized in Nepali law.

Use the retrieved context to answer the user's question as accurately as possible.
- Prioritize information from the retrieved context and cite document title, part, article, and clause if available.
- Do NOT invent laws, clauses, or articles that are not in the retrieved context.
- If the context does not fully answer the question, provide **logical reasoning** based on the information in context, general legal principles, or common practices, but clearly distinguish reasoning from documented law.
- Clearly indicate if something is your logical inference rather than an explicit provision in law.

Instructions:
- Be concise and neutral.
- Adapt your response to the question type:
    * **Factual/definitional questions**: summarize context.
    * **Action/procedure questions**: provide practical steps only if supported by context, or suggest reasonable actions using logical reasoning.
- If context is insufficient to answer, clearly state: "Based on the retrieved legal documents, there is no information directly answering this question, but logically…"

Question:
{query}

Retrieved Context:
{context_text}

Answer format:
- **Short Answer**: summary from retrieved context
- **What the Law Says**: cite relevant context; omit if not available
- **Logical Reasoning / Practical Steps**: clearly indicate if based on reasoning rather than context
"""

    try:
        # Primary model (Pro)
        response = client.models.generate_content(
            model="gemini-2.5-pro",
            contents=prompt
        )
        return response.text

    except Exception as e:
        print(f"⚠️ gemini-2.5-pro failed: {e}")
        try:
            # Fallback to Flash
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            return response.text
        except Exception as e2:
            print(f"❌ Both models failed: {e2}")
            return "⚠️ Sorry, the AI legal assistant is temporarily unavailable. Please try again shortly."

# ---------- Routes ----------
@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "MyPocketLawyer backend is live."}

# Mount static files (JS, CSS, images)
# We mount them at the root or /assets depending on how Vite builds.
# Usually Vite puts assets in dist/assets. 
# We'll serve the entire 'dist' folder as static, but we need to handle the index.html fallback for SPA.

FRONTEND_DIST = BASE_DIR.parent / "frontend" / "dist"

if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="assets")
    
    # Catch-all for SPA: serve index.html for any path not matching an API route or file
    @app.get("/{full_path:path}")
    async def serve_spa_or_static(full_path: str):
        # Check if file exists in dist (e.g. favicon.ico, robot.txt)
        file_path = FRONTEND_DIST / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        
        # Otherwise, serve index.html
        return FileResponse(FRONTEND_DIST / "index.html")
else:
    print(f"⚠️ Frontend build not found at {FRONTEND_DIST}. Serving API only.")
    @app.get("/")
    def root():
        return {"message": "Backend live. Frontend build not found. Run 'npm run build' in frontend/."}


@app.post("/chat")
def chat_endpoint(req: ChatRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query text cannot be empty.")
    try:
        if is_small_talk(req.query):
            generic_reply = "I'm designed to help with Nepali law. Please ask a legal question (e.g., rights, acts, courts)."
            return {"query": req.query, "rewritten_query": None, "answer": generic_reply, "sources": []}

        is_legal, rewritten_query = classify_and_rewrite_query(req.query)

        if not is_legal:
            generic_reply = "I'm designed to assist only with Nepali law-related questions. Please ask about rights, duties, or constitutional matters."
            return {"query": req.query, "rewritten_query": None, "answer": generic_reply, "sources": []}

        sources = retrieve_top_k(rewritten_query, req.k)
        answer = generate_legal_answer(req.query, sources)

        return {"query": req.query, "rewritten_query": rewritten_query, "answer": answer, "sources": sources}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
