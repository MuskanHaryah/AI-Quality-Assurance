# System Architecture

## Overview

QualityMapAI is a full-stack web application that uses machine learning to analyse software requirements documents against the ISO/IEC 9126 quality standard.

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React 19)                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────────────┐  │
│  │   Home   │ │  Upload  │ │ Results  │ │    Dashboard      │  │
│  └──────────┘ └──────────┘ └──────────┘ └───────────────────┘  │
│                         │                                       │
│  ┌──────────────────────┴──────────────────────────────────┐   │
│  │  API Layer (axios) — services.js / client.js            │   │
│  └─────────────────────────┬───────────────────────────────┘   │
│                Vite Dev Proxy │ /api → :5000                    │
└────────────────────────────┼────────────────────────────────────┘
                             │ HTTP/JSON
┌────────────────────────────┼────────────────────────────────────┐
│                    BACKEND (Flask)                               │
│                             │                                   │
│  ┌─────────────────────────┴───────────────────────────────┐   │
│  │  Routes (Blueprints)                                    │   │
│  │  ┌────────┐ ┌─────────┐ ┌─────────┐ ┌────────────────┐ │   │
│  │  │ upload │ │ analyze │ │ predict │ │ report/health  │ │   │
│  │  └───┬────┘ └────┬────┘ └────┬────┘ └───────┬────────┘ │   │
│  └──────┼───────────┼───────────┼───────────────┼──────────┘   │
│         │           │           │               │               │
│  ┌──────┴───────────┴───────────┴───────────────┴──────────┐   │
│  │  Services (Business Logic)                              │   │
│  │  ┌──────────────────┐  ┌─────────────────────────────┐  │   │
│  │  │ document_processor│  │ requirement_extractor       │  │   │
│  │  │ (PDF/DOCX → text)│  │ (text → requirement list)   │  │   │
│  │  └──────────────────┘  └─────────────────────────────┘  │   │
│  │  ┌──────────────────┐  ┌─────────────────────────────┐  │   │
│  │  │ classifier       │  │ quality_scorer              │  │   │
│  │  │ (TF-IDF + SVM)   │  │ (scores, risks, gaps)      │  │   │
│  │  └──────────────────┘  └─────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────┘   │
│         │                                                       │
│  ┌──────┴──────────────────────────────────────────────────┐   │
│  │  Database (SQLite + WAL)                                │   │
│  │  ┌─────────┐  ┌──────────┐  ┌──────────────────────┐   │   │
│  │  │ uploads │  │ analyses │  │ requirements          │   │   │
│  │  └─────────┘  └──────────┘  └──────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────┘   │
│         │                                                       │
│  ┌──────┴──────────────────────────────────────────────────┐   │
│  │  Utilities                                              │   │
│  │  logger · validators · file_handler · error_handler     │   │
│  │  rate_limiter (flask-limiter)                           │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Analysis Pipeline

The core `/api/analyze` endpoint runs an 8-step pipeline:

```
   ┌──────────────┐
   │ 1. Validate  │  Check file_id exists in request
   │    Request   │
   └──────┬───────┘
          │
   ┌──────▼───────┐
   │ 2. Load File │  Fetch file path from uploads table
   │    Metadata  │
   └──────┬───────┘
          │
   ┌──────▼───────┐
   │ 3. Extract   │  pdfplumber (PDF) or python-docx (DOCX)
   │    Text      │  → raw text + word count + page count
   └──────┬───────┘
          │
   ┌──────▼───────┐
   │ 4. Extract   │  Split by sentences/lists/newlines
   │ Requirements │  Filter by keywords (shall/must/should/will)
   │              │  Filter by length and quality rules
   └──────┬───────┘
          │
   ┌──────▼───────┐
   │ 5. Classify  │  TF-IDF vectorisation → SVM prediction
   │    (ML)      │  → category + confidence for each requirement
   └──────┬───────┘
          │
   ┌──────▼───────┐
   │ 6. Score &   │  Coverage, balance, confidence → overall score
   │    Analyse   │  Gap analysis, risk level, recommendations
   └──────┬───────┘
          │
   ┌──────▼───────┐
   │ 7. Save to   │  Atomic transaction: analysis + requirements
   │    Database  │  + upload status update (all or nothing)
   └──────┬───────┘
          │
   ┌──────▼───────┐
   │ 8. Return    │  Full JSON with scores, requirements,
   │    Response  │  recommendations, gap analysis, timing
   └──────────────┘
```

---

## Data Model

```
┌──────────────┐       ┌──────────────┐       ┌──────────────────┐
│   uploads    │       │   analyses   │       │  requirements    │
├──────────────┤       ├──────────────┤       ├──────────────────┤
│ id (PK)      │──────▶│ upload_id(FK)│       │ analysis_id (FK) │
│ filename     │       │ id (PK)      │──────▶│ id (PK, auto)    │
│ original_name│       │ total_reqs   │       │ requirement_text │
│ file_path    │       │ overall_score│       │ category         │
│ file_type    │       │ risk_level   │       │ confidence       │
│ size_bytes   │       │ cat_present  │       │ keyword_strength │
│ status       │       │ cat_missing  │       │ source_index     │
│ uploaded_at  │       │ cat_scores   │       └──────────────────┘
└──────────────┘       │ recommend.   │
                       │ gap_analysis │
                       │ created_at   │
                       └──────────────┘

Relationships:
  uploads 1──────M analyses  (one upload → one analysis typically)
  analyses 1─────M requirements (one analysis → many requirements)
  CASCADE DELETE: deleting an upload removes its analyses & requirements
```

---

## ML Model

| Component               | Detail                                        |
|--------------------------|-----------------------------------------------|
| **Algorithm**            | TF-IDF vectorisation + Linear SVM classifier  |
| **Training Data**        | ~2000 labelled requirement sentences           |
| **Accuracy**             | 84.38% (test set)                             |
| **Categories (7)**       | Efficiency, Functionality, Maintainability, Portability, Reliability, Security, Usability |
| **Standard**             | ISO/IEC 9126 Software Quality Characteristics |
| **Inference**            | Singleton pattern — model loaded once at startup |
| **Batch Support**        | Single `transform()` + `predict()` call for batch |

---

## Frontend Architecture

```
App.jsx (Router + Suspense)
├── Navigation (glass AppBar + responsive drawer)
├── Home       (hero, features, health check)
├── Upload     (stepper: select → upload → analyse)
├── Results    (gauge, chart, table, recommendations, gaps)
└── Dashboard  (stats cards, recent analyses table)

State Management:
├── AppContext  → global notifications, analysis data
└── Local state → forms, search, pagination

API Layer:
├── client.js   → axios instance, interceptors, error handling
└── services.js → uploadFile, analyzeFile, predictRequirement,
                   predictBatch, getReport, getRecentAnalyses, checkHealth
```

---

## Technology Stack

| Layer      | Technology                                    |
|------------|-----------------------------------------------|
| Frontend   | React 19, Vite 6, Material-UI 7, Emotion     |
| Backend    | Flask 3.0, Python 3.13                        |
| ML         | scikit-learn 1.3 (TF-IDF + SVM)              |
| Database   | SQLite 3 (WAL mode)                           |
| Doc Parser | pdfplumber (PDF), python-docx (DOCX)          |
| Styling    | Liquid Glass theme (glass-morphism + gradients)|
| Rate Limit | Flask-Limiter (200/min, 50/sec)               |
| Testing    | pytest (118 tests), unittest                  |
