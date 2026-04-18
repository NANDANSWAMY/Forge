# Forge POC

**AI-powered endpoint compliance automation**

Drop an installer → Get a signed, policy-ready package.

## Quick Start

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set environment variables
cp .env.example .env
# Edit .env with your Azure OpenAI credentials

# 4. Initialize the knowledge base
python -m forge.knowledge_base.init_db

# 5. Run the backend API
uvicorn forge.api.main:app --reload --port 8000

# 6. Run the Streamlit frontend (new terminal)
streamlit run forge/ui/app.py
```

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Upload    │────▶│  AI Analyze │────▶│   Package   │
│  Installer  │     │  (Azure OAI)│     │  + Policy   │
└─────────────┘     └──────┬──────┘     └─────────────┘
                          │
                    ┌─────▼─────┐
                    │ Knowledge │
                    │   Base    │
                    │ (ChromaDB)│
                    └───────────┘
```

## Project Structure

```
forge-poc/
├── forge/
│   ├── api/              # FastAPI backend
│   ├── services/         # Core business logic
│   ├── knowledge_base/   # RAG + ChromaDB
│   ├── models/           # Pydantic schemas
│   └── ui/               # Streamlit frontend
├── data/
│   ├── uploads/          # Uploaded installers
│   ├── packages/         # Generated packages
│   └── policies/         # WDAC policies
├── tests/
├── .env.example
├── requirements.txt
└── README.md
```

## Features (POC Scope)

- [x] Upload MSI/EXE installers
- [x] AI-powered silent switch discovery
- [x] Knowledge base with RAG for past packages
- [x] Basic WDAC policy generation
- [x] Mock sandbox execution
- [ ] Real sandbox execution (future)
- [ ] CA signing integration (future)
