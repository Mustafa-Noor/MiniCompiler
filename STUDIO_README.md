# Mini Pascal Compiler Studio

Full-stack web IDE for the Mini Pascal Compiler.

## Architecture

```
frontend/          React + Vite + TailwindCSS dashboard
backend/           FastAPI REST API wrapping compiler modules
backend/compiler/  Lexer, parsers, symbol table, error handler
```

## Prerequisites

- Python 3.8+
- Node.js 20+

## Backend Setup

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

API docs: http://127.0.0.1:8000/docs

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Open: http://localhost:5173

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/upload` | Upload `.pas` file |
| POST | `/source` | Save editor source |
| GET | `/source` | Get current source |
| POST | `/run/lexer` | Run lexical analyzer |
| POST | `/run/rd` | Run recursive descent parser |
| POST | `/run/ll1` | Run LL(1) predictive parser |
| POST | `/run/lr` | Run SLR parser |
| GET | `/symbol-table` | Get symbol table entries |
| GET | `/errors` | Get compilation errors |
| GET | `/reports` | Get report download links |
| GET | `/status` | Dashboard statistics |
| GET | `/reports/download/{filename}` | Download report file |

## Sample API Responses

### POST /run/lexer

```json
{
  "success": true,
  "tokens": [
    {"token_type": "KEYWORD_PROGRAM", "lexeme": "program", "line": 1, "column": 1}
  ],
  "statistics": {
    "keywords": 12,
    "identifiers": 8,
    "numbers": 2,
    "operators": 5,
    "total": 45
  }
}
```

### POST /run/rd

```json
{
  "accepted": true,
  "trace": ["→ parse_program", "  match KEYWORD_PROGRAM", "..."]
}
```

### POST /run/ll1

```json
{
  "accepted": true,
  "first_sets": {"program": ["KEYWORD_program"]},
  "follow_sets": {"program": ["EOF"]},
  "parsing_table": {"M[program, KEYWORD_program]": "KEYWORD_program ID ..."},
  "trace": ["Step 1: EXPAND program → ..."]
}
```

### POST /run/lr

```json
{
  "accepted": true,
  "action_table": {"[0, KEYWORD_program]": "shift:1"},
  "goto_table": {"[0, program]": "2"},
  "trace": ["Step 1: SHIFT → state 1"]
}
```

## Workflow

1. Start backend and frontend
2. Open Dashboard — edit Pascal source or upload a file
3. Click **Run Lexer**, **RD**, **LL1**, or **LR** from the editor toolbar
4. Navigate sidebar pages to inspect tokens, traces, tables, errors
5. Download reports from the Reports page

## Course Info

Compiler Construction Lab · CS-471L · Spring 2026 · UET Lahore
