# Mini Pascal Compiler Studio

A web-based compiler construction and visualization platform for a subset of Pascal. The system implements the full compiler front end—lexical analysis through semantic checking—and exposes every phase through an interactive React dashboard backed by a FastAPI REST API.

Built for **CS-471L Compiler Construction Lab** as a final-year project.

---

## Features

| Phase | Description |
|---|---|
| **Lexer** | Double-buffered scanner with token categorization and line/column tracking |
| **Recursive Descent** | Top-down parser with nested entry/exit trace logging |
| **LL(1) Predictor** | Table-driven parsing with automated FIRST & FOLLOW computation |
| **SLR(1) Parser** | Bottom-up shift-reduce parsing with LR(0) closures and ACTION/GOTO tables |
| **Symbol Table** | Scoped symbol management for variables, functions, and procedures |
| **Semantic Analysis** | Type checking, parameter validation, and declaration integrity |
| **AST Viewer** | Abstract syntax tree visualization |
| **Error Handler** | Panic-mode recovery with categorized diagnostic messages |
| **Reports** | Downloadable compiler listings, traces, and error logs |

---

## Tech Stack

**Backend** — Python, FastAPI, Uvicorn, Pydantic

**Frontend** — React 18, Vite, Tailwind CSS, Framer Motion, Recharts, React Router

The grammar is based on the Pascal subset described in *Compilers: Principles, Techniques, and Tools* (Dragon Book), Appendix A. See [`pascal.txt`](pascal.txt) for the reference grammar.

---

## Project Structure

```
FinalProject/
├── backend/
│   ├── main.py                  # FastAPI application entry point
│   ├── requirements.txt
│   ├── api/                     # REST route handlers
│   ├── uploads/                 # Uploaded source files (gitignored)
│   ├── outputs/                 # Generated reports (gitignored)
│   └── compiler/
│       ├── lexer/               # Scanner, tokens, double buffer
│       ├── parsers/             # RD, LL(1), FIRST/FOLLOW, parsing tables
│       ├── lr_parser/           # SLR parser
│       ├── symbol_table/        # Scoped symbol table
│       ├── error_handler/       # Diagnostic collection
│       ├── semantic_analyzer.py
│       ├── ast_builder.py
│       └── integration/         # CompilerRunner & session state
├── frontend/
│   ├── src/
│   │   ├── pages/               # Studio views (lexer, parsers, reports, …)
│   │   ├── components/          # Shared UI components
│   │   ├── context/             # Global compiler state
│   │   └── services/api.js      # Backend API client
│   └── package.json
├── pascal.txt                   # Dragon Book Pascal subset grammar
└── FINAL_YEAR_PROJECT_REPORT.md # Full academic project report
```

---

## Prerequisites

- **Python** 3.10 or newer
- **Node.js** 18 or newer
- **npm** (comes with Node.js)

---

## Getting Started

### 1. Clone the repository

```powershell
git clone <repository-url>
cd FinalProject
```

### 2. Start the backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate        # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

The API runs at **http://127.0.0.1:8000**. Interactive docs are available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

### 3. Start the frontend

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

The UI opens at **http://localhost:5173**.

### 4. Configure the API URL (optional)

The frontend defaults to `http://127.0.0.1:8000`. To override, copy the example env file:

```powershell
cp .env.example .env
```

Set `VITE_API_URL` in `frontend/.env` if the backend runs on a different host or port.

---

## Usage

1. Open **http://localhost:5173** and click **Enter Studio**.
2. Upload a `.pas` or `.txt` source file, or type code directly in the editor.
3. Run individual compiler phases from the sidebar, or use **Run All** on the dashboard to execute the full pipeline.
4. Inspect tokens, parser traces, FIRST/FOLLOW sets, parsing tables, the symbol table, errors, and AST from their respective pages.
5. Download generated reports from the Reports page.

### Sample program

```pascal
program GCD(input, output);
var
    x, y: integer;
    result: integer;

function gcd(a, b: integer): integer;
begin
    if b = 0 then
        gcd := a
    else
        gcd := gcd(b, a mod b)
end;

begin
    read(x, y);
    result := gcd(x, y);
    write(result)
end.
```

### Supported language constructs

- Program declarations with `input` / `output` file parameters
- Global and local variable declarations (`integer`, `real`, arrays)
- Functions and procedures with parameters passed by reference
- Compound statements, assignments, `if`/`else`, `while` loops
- Arithmetic, relational, and logical expressions
- Built-in `read` and `write` procedures

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/upload` | Upload a Pascal source file (`.pas` or `.txt`) |
| `POST` | `/source` | Save source code from the editor |
| `GET` | `/source` | Retrieve the current source |
| `POST` | `/run/lexer` | Run lexical analysis |
| `POST` | `/run/rd` | Run recursive descent parser |
| `POST` | `/run/ll1` | Run LL(1) predictive parser |
| `POST` | `/run/lr` | Run SLR parser |
| `POST` | `/run/all` | Run the full compilation pipeline |
| `POST` | `/run/ast` | Build and return the AST |
| `GET` | `/symbol-table` | Get the current symbol table |
| `GET` | `/errors` | Get collected errors |
| `GET` | `/reports` | List generated report files |
| `GET` | `/status` | Get compilation session status |
| `GET` | `/health` | Health check |

---

## Production Build

```powershell
# Frontend
cd frontend
npm run build
npm run preview

# Backend (no build step — run with Uvicorn)
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

Serve the `frontend/dist` folder with any static file server, or configure your deployment to proxy API requests to the backend.

---

## Documentation

The full academic report—including system design, methodology, test cases, and results—is in [`FINAL_YEAR_PROJECT_REPORT.md`](FINAL_YEAR_PROJECT_REPORT.md).

---

## License

Academic project — see course and institution guidelines for usage and distribution.
