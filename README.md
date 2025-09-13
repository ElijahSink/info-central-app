# Info Central - AI-Powered Dashboard Builder

A personal AI-augmented dashboard builder that lets you create customizable blocks using natural language prompts.

## Features

- 🤖 **AI-Powered**: Create blocks by describing what you want in natural language
- 🔄 **Auto-Refresh**: Blocks automatically update on configurable schedules
- 🎨 **Customizable**: Drag and drop interface with resizable blocks
- 🛠️ **Self-Healing**: AI attempts to fix broken blocks automatically
- 💾 **Persistent**: All data stored locally in SQLite

## Quick Start

### Backend Setup
```bash
cd backend
uv venv
source .venv/bin/activate  # Linux/Mac
# or .venv\Scripts\activate  # Windows
uv pip install -e .
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev  # Runs on http://localhost:5173
```

### Environment Variables
Create a `.env` file in the backend directory:
```bash
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=sqlite:///./dashboard.db
FRONTEND_URL=http://localhost:5173
BACKEND_URL=http://localhost:8000
```

## Architecture

- **Frontend**: React + TypeScript + Vite + Tailwind CSS + shadcn/ui
- **Backend**: Python + FastAPI + SQLite + SQLAlchemy
- **AI**: OpenAI GPT-4 for code generation and self-healing
- **Security**: Process isolation for generated code execution

## Usage

1. Open the dashboard in your browser
2. Click "Add Block" 
3. Describe what you want in natural language
4. Watch the AI generate and deploy your block
5. Blocks refresh automatically and can be rearranged

## Development

See `.claude/project_plan.md` for detailed implementation planning and architecture decisions.