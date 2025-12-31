
# ⚡ AI-Driven Cable Design Validation System

AI-powered validation system for IEC 60502-1 low-voltage cable designs using LLM reasoning instead of deterministic rule engines.


## 📋 overview

This system validates cable design specifications against IEC standards using AI reasoning to:

Extract design attributes from structured or free-text input
Validate compliance using engineering judgment
Return PASS/WARN/FAIL results with confidence scores and explanations

Key Principle: No hardcoded IEC rules or lookup tables — validation is performed entirely through AI reasoning.
## Architecture

┌─────────────┐
│   Streamlit │  ← User Interface
│   Frontend  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   FastAPI   │  ← REST API
│   Backend   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  LangChain  │  ← AI Integration
│  + Gemini   │
└─────────────┘
## 🚀 Quick Start

#### Prerequisites

- Python 3.11+
- UV package manager
- Gemini API key
- LangSmith Api key

### 1. Clone Repository

```bash
git clone <repository-url>
cd cable-design-validator
```
### 2. Install UV (if not installed)
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```
```bash
# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```
### 3. Setup Environment
```bash
# Create virtual environment and install dependencies
uv sync
```
### Install dependencies
```bash
uv pip install -r requirements.txt
```
### 4. Configure API Key
Create .env file in project root:
```bash
GOOGLE_API_KEY = your_api_key_here
LANGSMITH_API_KEY = your_api_key_here

GEMINI_MODEL_NAME = "gemini-2.5-flash"

LANGSMITH_TRACING_V2 = "true"
LANGSMITH_PROJECT = "cable-design-validation"
LANGSMITH_ENDPOINT = "https://api.smith.langchain.com"
```
### 5. Run Backend
```bash
# Start FastAPI server
uv run main.py
```
Backend will run at http://localhost:8000

### 6. Run Frontend
In a new terminal:
```bash
# Activate environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### Start Streamlit
```bash
uv run python -m streamlit run src/frontend/app.py
```
Frontend will open at http://localhost:8501
