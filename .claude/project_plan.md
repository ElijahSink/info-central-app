# AI Dashboard Builder - Implementation Plan

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   AI Service    │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   (OpenAI)      │
│                 │    │                 │    │                 │
│ - Dashboard UI  │    │ - Block API     │    │ - Code Gen      │
│ - Block Cards   │    │ - AI Proxy      │    │ - Self-healing  │
│ - Layout Mgmt   │    │ - Execution     │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │
         │              ┌─────────────────┐
         └──────────────►│   SQLite DB     │
                        │                 │
                        │ - Blocks        │
                        │ - Versions      │
                        │ - Data Cache    │
                        └─────────────────┘
```

## Technology Stack

### Frontend
- **React 18** with TypeScript
- **Vite** for build tooling
- **TailwindCSS** for styling
- **shadcn/ui** for components (pre-installed)
- **Framer Motion** for animations
- **React DnD** for drag & drop layout

### Backend
- **Python 3.11+** with **FastAPI**
- **SQLite** with **SQLAlchemy**
- **uv** for package management
- **Pydantic** for data validation
- **AsyncIO** for concurrent execution

### AI Integration
- **OpenAI API** (GPT-4)
- **Structured outputs** for code generation
- **Function calling** for self-healing

## Project Structure

```
ai-dashboard/
├── frontend/                   # React application
│   ├── src/
│   │   ├── components/        # UI components
│   │   │   ├── ui/           # shadcn/ui components
│   │   │   ├── Dashboard.tsx
│   │   │   ├── BlockCard.tsx
│   │   │   └── AddBlockDialog.tsx
│   │   ├── hooks/            # Custom React hooks
│   │   ├── lib/              # Utilities
│   │   └── types/            # TypeScript types
│   ├── package.json
│   └── vite.config.ts
├── backend/                    # FastAPI application
│   ├── app/
│   │   ├── api/              # API routes
│   │   ├── core/             # Core business logic
│   │   ├── models/           # SQLAlchemy models
│   │   ├── services/         # Business services
│   │   │   ├── ai_service.py
│   │   │   ├── block_service.py
│   │   │   └── execution_service.py
│   │   └── main.py
│   ├── generated_code/         # AI-generated code storage
│   │   └── blocks/           # Organized by block_id/version
│   ├── pyproject.toml
│   └── uv.lock
├── .claude/                    # Planning documents
└── README.md
```

## Implementation Phases

### ✅ Phase 1: Core Infrastructure (COMPLETED)
1. ✅ Set up Python backend with FastAPI + SQLite
2. ✅ Set up React frontend with Vite + TypeScript
3. ✅ Basic API structure and database models
4. ✅ OpenAI integration service

### ✅ Phase 2: Block Management (COMPLETED)
1. ✅ Block CRUD operations
2. ✅ Code generation pipeline
3. ✅ Basic execution environment
4. ✅ Frontend block display
5. ✅ Improved AI prompts for real API calls

### 🚧 Phase 3: AI Dev Loop System (CRITICAL PRIORITY)
**Key Insight**: AI needs to see its code execute and iterate to improve

1. **Execute-Analyze-Iterate Loop**
   - Execute generated code immediately in sandbox
   - Capture execution results and errors
   - Feed results back to AI for improvement
   
2. **Error Analysis Intelligence**
   - Pattern recognition for common failures
   - Contextual suggestions for AI improvements
   - Fallback strategy recommendations
   
3. **Multi-Iteration Code Generation** 
   - AI attempts 2-3 approaches per block
   - Each attempt learns from previous failures
   - Success patterns stored for future use

### Phase 4: UI & Layout Enhancement
1. Dashboard layout system improvements
2. Drag & drop functionality
3. Block cards with live data display
4. Dynamic React component rendering

### Phase 5: Advanced Features
1. Auto-refresh scheduling
2. Complete self-healing system
3. Block editing with AI assistance
4. Data persistence optimization

### Phase 6: Polish & Testing
1. Error boundaries and fallbacks
2. Performance optimization
3. Documentation
4. Comprehensive testing

## Security Model

### Process Isolation
- Each block runs in a separate Python subprocess
- Subprocess has restricted file access (current directory only)
- Network access allowed but logged
- No subprocess can install packages

### File System Constraints
- Generated code stored in `backend/generated_code/`
- Block execution limited to reading files in current directory
- No write access to system directories
- Temporary files only in designated areas

### Code Generation Safety
- AI-generated code validated before execution
- Import statements restricted to pre-approved packages
- Syntax validation before storage
- Version control for all generated code

## Pre-installed Packages

### Python Backend Packages
```
# Data & APIs
requests
httpx
beautifulsoup4
pandas
numpy

# Date/Time
python-dateutil

# JSON/Data
pydantic
jmespath

# Utilities
python-dotenv
asyncio
```

### Frontend Packages (shadcn/ui components)
All shadcn/ui components will be pre-installed:
- Button, Card, Input, Label
- Dialog, Sheet, Popover
- Table, Chart components
- Form components
- Layout components

## AI Integration Strategy

### Code Generation Prompts
1. **System Prompt**: Defines available packages, constraints, coding standards
2. **Block Prompt**: User's natural language description
3. **Context Prompt**: Previous versions, error context for iterations

### Generated Code Structure
```python
# Backend Block Structure
from typing import Any, Dict
import asyncio

class BlockExecutor:
    async def fetch_data(self) -> Dict[str, Any]:
        # AI-generated data fetching logic
        pass
    
    async def process_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        # AI-generated data processing
        pass
```

```typescript
// Frontend Block Structure
interface BlockProps {
  data: any;
  refreshData: () => void;
  isLoading: boolean;
  error?: string;
}

export function GeneratedBlock({ data, refreshData, isLoading, error }: BlockProps) {
  // AI-generated React component
}
```

### Self-Healing Process
1. Monitor block execution for errors
2. Capture error context (stack trace, data, environment)
3. Send to AI with original prompt + error context
4. Generate new version with fixes
5. Test new version before deployment
6. Log healing attempts and outcomes

## Database Schema

```sql
-- Blocks table
CREATE TABLE blocks (
    id INTEGER PRIMARY KEY,
    user_prompt TEXT NOT NULL,
    title TEXT,
    current_version INTEGER DEFAULT 1,
    refresh_interval INTEGER DEFAULT 3600, -- seconds
    layout_data JSON, -- position, size
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'active' -- active, error, disabled
);

-- Block versions table
CREATE TABLE block_versions (
    id INTEGER PRIMARY KEY,
    block_id INTEGER REFERENCES blocks(id),
    version INTEGER,
    backend_code TEXT,
    frontend_code TEXT,
    ai_explanation TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'active' -- active, deprecated, failed
);

-- Block data cache
CREATE TABLE block_data (
    id INTEGER PRIMARY KEY,
    block_id INTEGER REFERENCES blocks(id),
    data JSON,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);

-- Execution logs
CREATE TABLE execution_logs (
    id INTEGER PRIMARY KEY,
    block_id INTEGER REFERENCES blocks(id),
    version INTEGER,
    execution_type TEXT, -- fetch, process, heal
    success BOOLEAN,
    error_message TEXT,
    execution_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Development Environment Setup

### Backend Setup
```bash
cd backend
uv venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
uv pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev  # Runs on port 5173
```

### Environment Variables
```bash
# .env file
OPENAI_API_KEY=your_key_here
DATABASE_URL=sqlite:///./dashboard.db
FRONTEND_URL=http://localhost:5173
BACKEND_URL=http://localhost:8000
```

## Next Steps

1. Initialize project structure
2. Set up development environment
3. Begin Phase 1 implementation
4. Test basic AI integration
5. Iterate on core functionality

## Success Metrics

- [ ] User can create blocks with natural language
- [ ] Blocks display data from external APIs  
- [ ] Blocks refresh automatically
- [ ] Failed blocks trigger self-healing
- [ ] Dashboard layout is persistent
- [ ] All data is stored locally in SQLite