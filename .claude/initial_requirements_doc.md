# AI-Powered Dashboard Builder — V1 Requirements Document

## 1. Purpose & Scope
The goal of this app is to provide a **personal, AI-augmented dashboard builder**. Users can create customizable blocks on a single-page dashboard by describing what they want in natural language. The AI interprets prompts, generates functional code (frontend + backend), and manages block lifecycle including fetching, processing, displaying, and refreshing data. While designed for personal use first (running locally), the system should allow for future scalability into a hosted public service.

---

## 2. Architecture Overview
- **Frontend:** Web app (React + Tailwind + shadcn/ui). Blocks rendered as resizable, rearrangeable cards.
- **Backend:** Local server (Python + FastAPI). Responsible for:
  - Running AI-assisted code generation.
  - Hosting APIs for generated blocks.
  - Managing persistence and scheduling.
- **Persistence:** SQLite (or equivalent) for:
  - Block metadata (layout, refresh interval, prompt history, versions).
  - Data storage for blocks requiring historical context.
- **AI Role:**
  - Generate both backend (data fetching/processing) and frontend (UI components) code.
  - Attempt automated debugging/self-healing when blocks fail.
  - Write code autonomously; generated code is treated as user data, not core app source.
- **Execution:** Generated backend code runs in **separate processes** with basic isolation to prevent crashes. Future versions may add CPU, memory, and time limits.

---

## 3. User Workflow
1. **Add Block**
   - User clicks “Add Block.”
   - User submits natural language prompt.
   - AI generates block code (frontend + backend), schedules refresh cycle, and hot-loads block into dashboard.

2. **Iterate**
   - User can refine block via chat-style iteration (e.g. “make chart bars blue”).
   - Original prompt is preserved alongside iteration history.

3. **View / Refresh**
   - Blocks refresh automatically per their schedule.
   - User can trigger manual refresh.

4. **Failure & Debugging**
   - If a block fails, AI attempts automated fixes.
   - Fixes result in a **new version** of the block (with logged explanation).
   - If unsuccessful, user is notified.

---

## 4. Block Requirements
- **UI**
  - Uniform card-style layout consistent with UI framework.
  - Support resizing and rearranging.
  - Theming support is not required in V1 but architecture should not preclude it.

- **Data Fetching**
  - AI may use:
    - Public APIs
    - HTTP/HTML parsing
    - Headless browser automation (e.g. Playwright)
  - User can optionally specify method.

- **Persistence**
  - Each block may optionally persist data (for historical queries).
  - Block metadata and code versions must be persisted.

- **Scheduling**
  - Configurable refresh interval per block.
  - Backend handles execution (global scheduler vs. per-block timers is an implementation detail).

- **Isolation & Safety**
  - Backend block code runs in separate processes.
  - Exception handling prevents frontend crashes.
  - Lightweight sandboxing (basic file/network access restrictions) should be considered in MVP.

---

## 5. AI Responsibilities
- Generate code to:
  - Fetch and process data.
  - Define persistence models where needed.
  - Render UI components.
- Self-heal when blocks fail (new version + explanation).
- Log actions taken for debugging and traceability.

---

## 6. Persistence Model
- **Database (SQLite or similar):**
  - Blocks table: ID, prompt, current version, refresh interval, layout, status.
  - Versions table: block ID, version, generated code refs, AI explanations.
  - Optional: Data storage per block (for historical queries).
- **Filesystem:**
  - Store AI-generated code as user data, organized by block ID and version.

---

## 7. Non-Goals for V1
- Multi-page dashboards.
- User accounts or authentication.
- Theming system.
- Strong sandboxing with CPU/memory/time constraints (only lightweight isolation for now).

---

## 8. Future Considerations
- Multi-dashboard support.
- Multi-user system for public deployment.
- Robust sandboxing with resource limits.
- Richer theming and block styling.
- Centralized marketplace or sharing system for blocks.

---

## 9. Tech Stack (Recommended)
- **Frontend:** React, TailwindCSS, shadcn/ui, Framer Motion (for animations).
- **Backend:** Python, FastAPI.
- **Database:** SQLite (upgradeable to PostgreSQL for scalability).
- **AI Integration:** Local or API-based LLM for code generation and debugging.
- **Sandboxing/Isolation:** Separate backend processes, with potential future use of Docker/Firecracker.

---

## 10. MVP Success Criteria
- User can create, edit, and delete blocks via natural language prompts.
- Blocks render in dashboard, can be rearranged/resized.
- Blocks fetch and display live data.
- Blocks refresh automatically and manually.
- Failed blocks trigger AI self-healing attempts and log explanations.
- All block data, versions, and metadata are persisted locally.

