"""
Configuration for the LLM-Agent Demo.
Edit this file to customize topics, thresholds, and LLM settings.
"""

# ============================================
# LLM PROVIDER SETTINGS
# ============================================
# Options: "ollama", "openai", "anthropic", "google"
LLM_PROVIDER = "ollama"

# Ollama (local, free)
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3"

# OpenAI
OPENAI_API_KEY = ""
OPENAI_MODEL = "gpt-4o-mini"

# Anthropic
ANTHROPIC_API_KEY = ""
ANTHROPIC_MODEL = "claude-3-haiku-20240307"

# Google Gemini
GOOGLE_API_KEY = ""
GOOGLE_MODEL = "gemini-2.0-flash"

# ============================================
# LLM BEHAVIOR
# ============================================
TEMPERATURE = 0.1          # 0.0-1.0 (lower = more consistent)
MAX_TOKENS = 512           # Max response length
RETRY_ATTEMPTS = 3         # Retry count on failure
RETRY_DELAY_BASE = 2       # Exponential backoff base

# ============================================
# DISCOVERY SETTINGS
# ============================================
DISCOVERY_THRESHOLD = 5    # Hits needed to promote new topic
MIN_CONFIDENCE = 0.7       # Minimum confidence to accept label

# ============================================
# DATA SETTINGS
# ============================================
INPUT_FILE_PATH = "data/reviews.csv"
OUTPUT_FILE_PATH = "output/classified.csv"
SENTINEL_LOG_FILE = "output/sentinel_log.json"

# Column names (change to match your CSV)
COMMENT_COL_NAME = "review_text"
DATE_COL_NAME = "date"
ID_COL_NAME = "id"

# ============================================
# TOPIC TAXONOMY
# ============================================
# Edit this list to match your domain!
MASTER_TOPICS = [
    "Acting Performance",
    "Plot & Story",
    "Visual Effects",
    "Cinematography",
    "Soundtrack & Score",
    "Direction",
    "Dialogue",
]
