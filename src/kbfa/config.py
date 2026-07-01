from dotenv import load_dotenv
import os

# Load variables from .env file into the environment.
# This means you don't have to manually set environment variables
# before running the project — just fill in .env once and forget it.
load_dotenv()

# Anthropic API key — only actually used in Phase 7 (LLM narrative generation).
# Safe to leave as None for now, nothing in Phase 2 touches it.
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Path where DuckDB will store the local database file.
# Defaults to ./data/processed/kbfa.duckdb if not set in .env
DUCKDB_PATH = os.getenv("DUCKDB_PATH", "./data/processed/kbfa.duckdb")

# Risk scoring thresholds — a file is HIGH risk if one person owns
# more than this % of lines. MEDIUM risk if above the medium threshold.
# These come from .env so you can tune them without touching code.
RISK_THRESHOLD_HIGH = int(os.getenv("RISK_THRESHOLD_HIGH", 80))
RISK_THRESHOLD_MEDIUM = int(os.getenv("RISK_THRESHOLD_MEDIUM", 50))