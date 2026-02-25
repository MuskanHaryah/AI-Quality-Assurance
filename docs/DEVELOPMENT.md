# Development Guide

A practical guide for developers working on QualityMapAI.

---

## Project Structure

```
AI-Quality-Assurance/
├── backend/                    # Flask API + ML pipeline
│   ├── app.py                  # Application factory + routes
│   ├── config.py               # Central configuration
│   ├── routes/                 # API endpoint blueprints
│   │   ├── upload.py           # POST /api/upload
│   │   ├── analyze.py          # POST /api/analyze
│   │   ├── predict.py          # POST /api/predict
│   │   └── report.py           # GET  /api/report/<id>
│   ├── services/               # Business logic
│   │   ├── classifier.py       # ML model wrapper (singleton)
│   │   ├── document_processor.py  # PDF/DOCX text extraction
│   │   ├── requirement_extractor.py  # Requirement detection
│   │   └── quality_scorer.py   # Score calculation + reports
│   ├── database/               # SQLite persistence
│   │   ├── db.py               # Connection management + WAL
│   │   ├── models.py           # Table schemas + indices
│   │   └── queries.py          # CRUD + transactions
│   ├── utils/                  # Shared utilities
│   │   ├── logger.py           # Structured logging
│   │   ├── validators.py       # Input validation
│   │   ├── file_handler.py     # File save/cleanup
│   │   └── error_handler.py    # Exception hierarchy + handlers
│   ├── tests/                  # Test suite (118 tests)
│   │   ├── conftest.py         # Shared fixtures
│   │   ├── test_api.py         # Integration tests
│   │   ├── test_e2e_workflow.py   # E2E + stress + error tests
│   │   ├── test_classifier.py  # ML model unit tests
│   │   ├── test_document_processor.py
│   │   ├── test_requirement_extractor.py
│   │   └── test_quality_scorer.py
│   ├── models/                 # ML model artefacts (.pkl)
│   ├── uploads/                # Uploaded files (gitignored)
│   └── data/                   # SQLite DB + logs (gitignored)
├── frontend/                   # React 19 + Vite + MUI 7
│   ├── src/
│   │   ├── App.jsx             # Router + lazy loading
│   │   ├── main.jsx            # Entry point + ThemeProvider
│   │   ├── api/                # Axios client + service methods
│   │   ├── pages/              # Home, Upload, Results, Dashboard
│   │   ├── components/         # Reusable UI components
│   │   ├── context/            # React Context (global state)
│   │   ├── theme/              # Liquid Glass MUI theme
│   │   └── utils/              # Helpers, constants
│   └── vite.config.js          # Dev proxy + code splitting
├── ml-training/                # Model training scripts
│   ├── train_model.py
│   ├── process_dataset.py
│   └── dataset/                # Training data CSVs
└── docs/                       # Documentation
    ├── API.md                  # API reference
    ├── openapi.yaml            # OpenAPI 3.0 spec
    ├── DEPLOYMENT.md           # Deployment guide
    └── ARCHITECTURE.md         # System architecture
```

---

## Getting Started

### 1. Clone & Setup

```bash
git clone <repo-url>
cd AI-Quality-Assurance

# Python virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1       # Windows
source .venv/bin/activate         # macOS/Linux

# Backend dependencies
cd backend
pip install -r requirements.txt

# Frontend dependencies
cd ../frontend
npm install
```

### 2. Run Locally

**Terminal 1 — Backend:**
```bash
cd backend
python app.py
# → http://localhost:5000
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
# → http://localhost:5173 (proxies /api → :5000)
```

### 3. Run Tests

```bash
cd backend
python -m pytest tests/ -v           # All 118 tests
python -m pytest tests/ -v -k e2e    # E2E tests only
python -m pytest tests/ -v -k error  # Error scenario tests only
python -m pytest tests/ --tb=short   # Compact output
```

---

## Common Tasks

### Add a New API Endpoint

1. Create a new file in `backend/routes/` (e.g., `stats.py`)
2. Define a Blueprint and route function
3. Add `@handle_exception` decorator for error handling
4. Register the blueprint in `app.py`:
   ```python
   from routes.stats import stats_bp
   app.register_blueprint(stats_bp, url_prefix="/api")
   ```
5. Add tests in `tests/`
6. Update `docs/API.md` and `docs/openapi.yaml`

### Add a New Frontend Page

1. Create `frontend/src/pages/NewPage.jsx`
2. Add the lazy import in `App.jsx`:
   ```jsx
   const NewPage = lazy(() => import('./pages/NewPage'));
   ```
3. Add the `<Route>` in the router
4. Add navigation link in `Navigation.jsx`

### Modify the ML Model

1. Edit training data in `ml-training/dataset/`
2. Run training: `python ml-training/train_model.py`
3. Copy outputs to `backend/models/`:
   - `classifier_model.pkl`
   - `tfidf_vectorizer.pkl`
   - `model_info.json`
4. Restart the backend to load the new model

### Reset the Database

```bash
# Delete the DB file — it is recreated on next startup
rm backend/data/quality_assurance.db
python app.py
```

---

## Code Conventions

### Backend (Python)

- **Style:** PEP 8, 100-character line limit
- **Typing:** Type hints on all function signatures
- **Docstrings:** Google-style docstrings on all public functions
- **Logging:** Use `app_logger` from `utils.logger` (not `print()`)
- **Errors:** Raise `AppError` subclasses; never return bare exceptions
- **Testing:** Every new feature must have corresponding tests

### Frontend (JavaScript/JSX)

- **Style:** ESLint default rules
- **Components:** Functional components with hooks only
- **State:** React Context for global state; local state for forms
- **API calls:** Use `frontend/src/api/services.js`
- **Styling:** MUI `sx` prop; no raw CSS files

---

## Key Design Decisions

| Decision                     | Rationale                                      |
|------------------------------|------------------------------------------------|
| SQLite (not PostgreSQL)      | Zero-config, portable, sufficient for MVP       |
| Flask (not FastAPI)          | Simpler, well-established, adequate for sync ML |
| TF-IDF + SVM (not deep learning) | Fast inference, small model size, 84% accuracy |
| Singleton ML model           | Avoid reloading large model on every request    |
| Atomic transactions          | Prevent partial writes on analysis failures     |
| Code splitting (Vite)        | Faster initial page loads                       |
| Rate limiting (flask-limiter)| Prevent abuse and resource exhaustion           |

---

## Troubleshooting

| Problem                            | Solution                                         |
|------------------------------------|--------------------------------------------------|
| `ModuleNotFoundError: flask`       | Activate venv: `.venv\Scripts\Activate.ps1`      |
| `Model file not found`             | Ensure `backend/models/*.pkl` files exist         |
| `Port 5000 already in use`         | Kill the process: `netstat -ano | findstr 5000`  |
| `CORS error in browser`            | Check backend is running and Vite proxy is set   |
| `UnicodeEncodeError` in logs       | Windows cp1252 issue — non-critical, can be ignored |
| `429 Too Many Requests`            | Rate limit hit — wait and retry                  |
| Database locked                    | WAL mode handles this; increase timeout if needed|
