<div align="center">

# Cable Design Validation System

**Advanced AI-powered validation for wires and cables design.**

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white" alt="LangChain">
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
  <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
  <img src="https://img.shields.io/badge/LangSmith-FF4B4B?style=for-the-badge&logo=LangSmith&logoColor=white" alt="LangSmith">
</p>

</div>
<br>

The **Cable Design Validation System** is a sophisticated backend engine that automates the 
verification of cable technical specifications against Indian standards (IS). By combining 
**Structured RAG** with a **Multi-Stage Automated Workflow**, it transforms unstructured technical 
descriptions into validated, compliant designs with high precision.
<br>
<br>
<hr style="border: none; border-top: 1px solid #343333ff;" />

## 🛠️ How It Works

The system follows a rigorous 4-stage pipeline orchestrated for maximum accuracy:

- **Extraction**: [Groq](https://groq.com/) processes raw text to identify key parameters (CSA, Voltage, Materials).
- **Database Validation**: Checks parameters against technical tables in `conductors.db`.
- **Contextual Logic**: Aggregates database proofs and standard references.
- **Self-Correction**: [Google Gemini](https://ai.google.dev/) performs a final cross-reference audit.
<hr style="border: none; border-top: 1px solid #343333ff;" />

## 🚀 Key Features

- 🧠 **Multi-Model Intelligence**: Leverages Groq for speed and Gemini for deep analysis.
- 📐 **IEC Compliance**: Automated checks for insulation thickness and conductor class.
- 🔍 **LangSmith Tracing**: Full observability of the AI decision-making process.
- 📦 **Modern Stack**: Built with `uv` for lightning-fast dependency resolution.
- 🛡️ **Pydantic Validation**: Strong typing ensures data integrity from API to Database.

<hr style="border: none; border-top: 1px solid #343333ff;" />

## 📂 Architecture at a Glance

```text
src/backend/
├── orchestrator/   # 🎮 Main pipeline controller
├── providers/      # 🔌 LLM Client wrappers (Groq/Gemini)
├── validators/     # ⚖️ Rule-based & SQL engines
├── schemas/        # 📑 Pydantic data models
└── prompt_library/ # 📜 Prompt engineering templates
```

---

## 📥 Getting Started

### 1. Prerequisites

Ensure you have [uv](https://github.com/astral-sh/uv) installed:

```bash

pip install uv

```

### 2. Quick Setup

```bash
# Clone and enter
git clone <repo-url>
cd Innovites-cable-design-validation-system

# Sync dependencies
uv sync
```

### 3. Environment variables

Create a `.env` file with your credentials:

```env
GROQ_API_KEY=gsk_...
GOOGLE_API_KEY=AIza...
DATABASE_URL=sqlite:///./conductors.db
LANGSMITH_TRACING_V2=true
```

### 4. Launch Service

```bash
uv run main.py
```

🌐 **API Docs:** `http://localhost:8000/docs`

---

## 📝 License

Licensed under the [MIT License](/LICENSE).

<div align="center">
  Built with ❤️ for Cable Engineering Excellence
</div>