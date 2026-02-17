from pathlib import Path

# Detect project root (the folder containing config/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"
PROCESSED_DIR = PROJECT_ROOT / "processeddata"
VECTORSTORE_DIR = PROJECT_ROOT / "chroma_db"
VECTORSTORE1_DIR = PROJECT_ROOT / "chroma_db1"
VECTORSTORE2_DIR = PROJECT_ROOT / "chroma_db2"
EVAL_PATH = DATA_DIR / "evaluation" / "Evaluation_dataset.json"
# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
PROCESSED_DIR.mkdir(exist_ok=True)
VECTORSTORE_DIR.mkdir(exist_ok=True)
