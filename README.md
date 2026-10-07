# Multi-Provider AI Chatbot (OpenAI / Claude / Gemini)

A unified, production-ready AI Chatbot platform capable of dynamically switching between **OpenAI**, **Anthropic Claude**, and **Google Gemini** with real-time **Server-Sent Events (SSE) Streaming** and persistent **Redis Memory** (Sliding Window Context & TTL).

---

## Key Features

- **Multi-Provider Unified Gateway**: Seamlessly switch between OpenAI (GPT-4o, GPT-4o-mini, o3-mini), Anthropic Claude (Claude 3.5 Sonnet, Claude 3.5 Haiku), and Google Gemini (Gemini 2.5 Flash, Gemini 2.5 Pro).
- **Real-time SSE Streaming**: Low-latency token streaming powered by `sse-starlette` on the backend and native `ReadableStream` / `TextDecoder` on the frontend.
- **Intelligent Redis Memory**:
  - **Sliding Window Context**: Dynamically retrieves the last $N$ messages to manage token consumption effectively.
  - **Auto-Expiration (TTL)**: Configurable 24-hour Time-to-Live on conversations to prevent memory leaks.
  - **Interruption-Safe Persistence**: Saves the complete assistant response into Redis automatically upon stream completion.
- **Provider Request Normalization**: Normalizes disparate payload schemas (OpenAI messages list, Claude separate system parameters, and Gemini `contents`/`model` role structure) behind a clean abstraction.
- **Modern Glassmorphic UI**:
  - Cyberpunk-inspired dark theme with responsive layout and smooth micro-animations.
  - Full Markdown rendering with syntax-highlighted code blocks and one-click copy buttons.
  - Live streaming cursor animation and on-demand "Stop Generation" control.
  - Session manager for creating new conversations, switching histories, and clearing context.

---

## Project Architecture

```
Multi-Provider AI Chatbot/
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore rules (protects API keys)
├── README.md                   # Complete documentation & setup guide
├── docker-compose.yml          # Container configuration for Redis & Backend
│
├── backend/                    # Python FastAPI Core Backend
│   ├── Dockerfile              # Production Dockerfile
│   ├── requirements.txt        # Dependencies: fastapi, sse-starlette, redis, openai, anthropic, google-genai
│   ├── .env                    # Local environment variables & API keys
│   └── app/
│       ├── __init__.py
│       ├── main.py             # FastAPI entrypoint, SSE endpoint, CORS & routes
│       ├── config.py           # Pydantic Settings configuration loader
│       ├── schemas.py          # Data models (ChatRequest, Message, Stream)
│       ├── services/
│       │   ├── __init__.py
│       │   ├── llm_factory.py  # Provider Factory & dynamic routing
│       │   ├── redis_service.py # Async Redis Sliding Window & TTL management
│       │   └── providers/
│       │       ├── __init__.py
│       │       ├── base.py     # Base LLM Provider abstract interface
│       │       ├── openai_provider.py
│       │       ├── claude_provider.py
│       │       └── gemini_provider.py
│       └── utils/
│           ├── __init__.py
│           └── normalization.py # Request/Role normalization per LLM specification
│
└── frontend/                   # React + Vite Web Client
    ├── Dockerfile              # Multi-stage Nginx Dockerfile
    ├── package.json
    ├── vite.config.js
    ├── index.html
    └── src/
        ├── main.jsx            # React root mount
        ├── App.jsx             # Main application layout & session state
        ├── index.css           # Glassmorphic cyber design system
        ├── components/
        │   ├── Header.jsx      # Title & provider status badge
        │   ├── Sidebar.jsx     # Session history management
        │   ├── ChatWindow.jsx  # Markdown messages & code blocks with copy
        │   ├── ChatInput.jsx   # Input textarea & stop generation button
        │   └── ModelSelector.jsx # Dynamic provider & model dropdowns
        ├── hooks/
        │   └── useSSEChat.js   # Custom ReadableStream SSE consumption hook
        └── services/
            └── api.js          # REST client for models & session history
```

---

## Quick Start

### 1. Configure Environment Variables
Copy `.env.example` to `backend/.env` (if not already created) and fill in your API keys:
```env
# Backend Settings
HOST=0.0.0.0
PORT=8000
DEBUG=True

# LLM API Keys (Only configure the ones you have)
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
GEMINI_API_KEY=your_gemini_key_here

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
REDIS_TTL_HOURS=24
SLIDING_WINDOW_SIZE=20
```

> **Note**: You do not need keys for all three providers. The backend automatically detects which keys are present and enables the corresponding providers accordingly.

---

### 2. Option A: One-Click Launch with PowerShell (Windows - Recommended)

If you are on Windows, you can start all services (Redis, FastAPI backend, and React frontend) and automatically open the application in your browser with a single command:

```powershell
.\run.ps1
```

To stop all running containers when you are done:
```powershell
.\stop.ps1
```

---

### 3. Option B: Run with Docker Compose (Cross-Platform)

Start all services (Redis, Backend, and Frontend) in detached mode:
```bash
docker compose up -d
```

Once started, open your browser and go to: **`http://localhost:5173`**

To stop all services:
```bash
docker compose down
```

---

### 4. Option C: Run Manually / Locally on Host

#### Start Redis:
Ensure Redis is running locally on port `6379`, or run a quick Redis container:
```bash
docker run -d -p 6379:6379 --name redis-chat redis:7-alpine
```

#### Run the FastAPI Backend:
```bash
cd backend
python -m venv venv

# Windows (PowerShell):
.\venv\Scripts\activate

# Linux / macOS:
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

#### Run the React Frontend:
```bash
cd frontend
npm install
npm run dev
```

Open your browser and navigate to: **`http://localhost:5173`**

---

## API Reference

### `GET /api/models`
Returns the catalog of all supported providers and models along with their availability status based on configured API keys.

### `POST /api/chat`
Streams real-time response tokens via Server-Sent Events (SSE).
- **Payload:**
  ```json
  {
    "session_id": "session-12345",
    "provider": "openai",
    "model": "gpt-4o-mini",
    "messages": [
      { "role": "user", "content": "Explain Server-Sent Events" }
    ],
    "system_prompt": "You are a helpful coding assistant.",
    "temperature": 0.7
  }
  ```
- **SSE Stream Events:**
  ```
  data: {"token": "Server", "done": false, "error": null}
  data: {"token": "-Sent", "done": false, "error": null}
  ...
  data: {"token": "", "done": true, "error": null}
  ```

### `GET /api/chat/{session_id}/history`
Fetches the saved conversation history for a given session from Redis.

### `DELETE /api/chat/{session_id}`
Clears conversation memory and session context in Redis.

---
