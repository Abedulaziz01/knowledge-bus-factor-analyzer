from dotenv import load_dotenv
import os

load_dotenv()

# Groq API key — used in Phase 7 (LLM narrative generation).
# Free tier at console.groq.com/keys — no credit card needed.
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Model to use — Groq's free tier gives access to Llama 3.3 70B,
# same model you used in the PubMed assistant project.
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# Path where DuckDB stores the local database file.
DUCKDB_PATH = os.getenv("DUCKDB_PATH", "./data/processed/kbfa.duckdb")

# Risk scoring thresholds.
# HIGH risk = one person owns more than this % of a file's lines.
# MEDIUM risk = one person owns more than this % but less than HIGH.
RISK_THRESHOLD_HIGH = int(os.getenv("RISK_THRESHOLD_HIGH", 80))
RISK_THRESHOLD_MEDIUM = int(os.getenv("RISK_THRESHOLD_MEDIUM", 50))