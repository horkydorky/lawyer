# MyPocketLawyer ⚖️ — AI-Powered Legal Aid Assistant (Nepali Law)

A stateless Retrieval-Augmented Generation (RAG) assistant for Nepali law. It uses:
- Google Gemini for embeddings and generation
- ChromaDB for vector search
- FastAPI for the backend
- Vite/React and Shadcn/UI for the modern frontend user interface

This bot answers only from the ingested legal documents:
- Constitution of Nepal 2072
- The Criminal Offences Act 2074
- The Labour Act 2074
- The National Civil Act 2074
- The National Penal Act 2074
- Bank and Financial Institution Act 2073
- Banking Offence and Punishment Act 2064
- Electronic Commerce Act 2081
- International Financial Transactions Act 2054
- The Income Tax Act 2058

---

## ✨ Features

- Small-talk guard and domain classification (Nepali law only)
- Query rewriting to improve retrieval quality
- ChromaDB retrieval with metadata-rich source display
- Gemini 2.5 Pro/Flash for grounded answer generation
- Streamlit chat UI with collapsible sources and search query display
- Adaptive answer format:
  - Short Answer
  - What the Law Says (cites articles/clauses)
  - Practical Steps (only for action/procedure queries)
  - Disclaimer

---

## 🗂️ Repository Structure

```
.
├─ backend/
│  ├─ main.py                         # FastAPI stateless RAG pipeline
│
├─ chroma_db/                         # ChromaDB persistent directory (auto-generated)
│
├─ config/
│  ├─ __init__.py
│  └─ paths.py                        # Project path utilities (optional)
│
├─ data/
│  ├─ raw/                            # Raw legal documents (if building vectors)
│  ├─ processed/                       # Converted & cleaned JSON docs
│  └─ evaluation/                      # Test sets, metrics, prompts
│
├─ documentation/
│  ├─ LiteratureReview.pdf
│  └─ Proposal.pdf
│
├─ frontend/
│  ├─ index.html
│  ├─ package.json
│  ├─ vite.config.ts
│  ├─ tailwind.config.ts
│  ├─ postcss.config.js
│  ├─ public/
│  └─ src/
│     ├─ main.tsx                      # React entry point
│     ├─ App.tsx                       # Root wrapper component
│     ├─ App.css                       # Global component styling
│     ├─ index.css                     # Tailwind + base styles
│     │
│     ├─ pages/
│     │  ├─ Index.tsx                  # Landing page (hero + CTA)
│     │  └─ NotFound.tsx               # 404 handler
│     │
│     ├─ components/
│     │  ├─ Hero.tsx                   # Homepage hero UI
│     │  ├─ NavLink.tsx                # Navbar interactive link component
│     │  ├─ LegalAssistant.tsx         # Main chat screen
│     │  └─ ui/                        # shadcn component library
│     │
│     ├─ hooks/
│     │  ├─ use-mobile.tsx
│     │  └─ use-toast.ts
│     │
│     └─ lib/
│        └─ utils.ts                   # Shared helpers (stream UI, formatting)
│
├─ notebooks/
│  ├─ baseline_data_ingestion_pipeline.ipynb
│  ├─ baseline_retrieval_pipeline.ipynb
│  ├─ data_ingestion_multimodel.ipynb
│  ├─ final_data_ingestion_pipeline.ipynb
│  ├─ final_retreval_pipeline.ipynb
│  ├─ final_retriever_evaluation.ipynb
│  ├─ generator_evaluation.ipynb
│  ├─ multimodel_evaluation.ipynb
│  ├─ multimodel_split_evaluation.ipynb
│  └─ retriever_evaluation.ipynb
│
├─ .env                                # GEMINI_API_KEY
├─ .gitignore
├─ generator_evaluation_results.csv
├─ generator_evaluation_results.json
├─ requirements.txt
├─ run.py                              # Optional pipeline runner
└─ README.md

```

---

## 🧱 Tech Stack

- Backend: FastAPI, Pydantic, Uvicorn
- Vector Store: ChromaDB (persistent)
- LLM + Embeddings: Google Gemini (via `google-genai`)
  - Generation: gemini-2.5-pro (fallback: gemini-2.5-flash)
  - Embeddings: models/text-embedding-004
- Frontend: Frontend — Vite + React + TypeScript + Tailwind + Shadcn/UI

---

## 🚀 Quickstart

### 1) Prerequisites
- Python 3.10+
- A Google Gemini API key (from Google AI Studio)
- macOS, Linux, or Windows

### 2) Environment

Create a `.env` in the repo root:
```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3) Install dependencies

Create a virtual environment and install:
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
```

### 4) Build or provide the vector store

- If `./backend/chroma_db/` already contains a collection named `legal_docs`, you’re set.
- Otherwise, build it using your ingestion notebooks:
  - Recommended: `notebooks/final_data_ingestion_pipeline.ipynb`
- Place raw text/markdown under `data/raw/` (or what your notebook expects).
- Output should be a persistent Chroma collection at `./backend/../chroma_db` (repo root `./chroma_db`).

> The backend looks for a Chroma collection named `legal_docs` at repo-root `./chroma_db`.

### 5) Run the backend

From repo root:
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```
You should see: “✅ MyPocketLawyer backend (completely stateless) is live.”

### 6) Run the frontend 🌐

In a separate terminal, follow these steps to launch the React application:

# 1. Navigate to the frontend directory
```bash
cd frontend
```
# 2. Install Node.js dependencies (only needed the first time)
```bash
npm install
```
# 3. Start the development server
```bash
npm run dev
```
### Optional: run.py
If `run.py` orchestrates both backend and frontend on your machine, run:
```bash
python run.py
```
(If not implemented to launch both, use the separate commands above.)

### 7) Deployment 🐳
For Docker deployment instructions, please refer to [DEPLOY.md](DEPLOY.md).

---

## 🧪 Example Queries

- What are the three organs of the Government under the Constitution of Nepal?
- What is the overtime pay in Nepali like?
- What happens if someone is found planting explosives?


## 📊 Evaluation Figures
## Retriever Evaluation (Full-Chunk Splitting)
<img width="635" height="401" alt="Screen Shot 2025-11-27 at 09 20 31" src="https://github.com/user-attachments/assets/39bfd950-8011-4b53-8069-d068f806fcb3" />


## Retriever Evaluation (Article-wise Splitting)
<img width="639" height="416" alt="Screen Shot 2025-11-27 at 09 20 01" src="https://github.com/user-attachments/assets/7f285203-78d3-43b0-b643-84375eb7411f" />


## Generator Evaluation
## Quality & Efficiency Scores
<img width="313" height="293" alt="Screen Shot 2025-11-27 at 09 22 24" src="https://github.com/user-attachments/assets/c2a06898-056c-40cd-ac01-8e621940dc44" />

## Response Time & Cost Distribution
 <img width="297" height="297" alt="Screen Shot 2025-11-27 at 09 23 05" src="https://github.com/user-attachments/assets/2be73b56-d5a6-4f4d-a154-0c863841bd5d" />

 ## Quality Metrics Comparison
 <img width="309" height="297" alt="Screen Shot 2025-11-27 at 09 24 29" src="https://github.com/user-attachments/assets/8c0ed852-16b9-4716-85a9-f103467fd013" />

## Performance by Legal Sources
<img width="320" height="304" alt="Screen Shot 2025-11-27 at 09 25 10" src="https://github.com/user-attachments/assets/ec218a5c-8a16-4c41-934d-4f17a8f3b5c0" />








