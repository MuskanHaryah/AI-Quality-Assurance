# Changelog

All notable changes to QualityMapAI are documented here.

## [1.0.0] — 2026-02-25

### Phase 3: Integration & Testing
- **E2E Tests:** Added 30 end-to-end workflow tests covering upload→analyze→report pipeline, stress tests (50 & 100 requirements), error scenarios, and edge cases
- **Rate Limiting:** Integrated Flask-Limiter (200 req/min, 50 req/sec) with 429 error handling
- **Database Indices:** Added 6 performance indices on uploads, analyses, and requirements tables
- **API Documentation:** Full API reference (docs/API.md) + OpenAPI 3.0 spec (docs/openapi.yaml)
- **Deployment Guide:** Docker, WSGI, Nginx configuration documentation
- **Development Guide:** Setup, common tasks, code conventions, troubleshooting
- **Architecture Docs:** System diagrams, pipeline flow, data model, tech stack overview
- **Total Tests:** 118 (all passing)

### Phase 2: React Frontend (2026-02-24)
- **Pages:** Home, Upload, Results, Dashboard — all with Liquid Glass theme
- **Components:** 11 reusable components (FileUpload, ScoreGauge, CategoryChart, RequirementsTable, RecommendationCard, GlassCard, Loading, ErrorDisplay, Navigation, SectionHeader, GapAnalysisCard)
- **API Integration:** Axios client with interceptors, 7 service methods, upload progress tracking
- **State Management:** React Context for global state, notifications, async handling
- **Responsive:** Mobile-first design with MUI breakpoints, glass-morphism styling
- **Build:** Production optimised with code splitting (vendor, MUI, charts, pages)

### Phase 1: Flask Backend (2026-02-23)
- **API:** 4 core endpoints (upload, analyze, predict, report) + health + dashboard
- **ML Pipeline:** TF-IDF + SVM classifier, 84.38% accuracy, 7 ISO/IEC 9126 categories
- **Document Processing:** PDF (pdfplumber) and DOCX (python-docx) text extraction
- **Requirement Extraction:** Keyword-based detection (shall/must/should/will), length and quality filtering
- **Quality Scoring:** Coverage, balance, confidence metrics; risk levels; recommendations; gap analysis
- **Database:** SQLite with WAL mode, atomic transactions, cascading deletes
- **Error Handling:** Custom exception hierarchy, consistent JSON error responses, route decorator
- **Testing:** 88 unit + integration tests (all passing)
- **Logging:** Structured logging with file output

---

# Known Issues & Limitations

## Current Limitations

| #  | Area          | Description                                                         | Severity |
|----|---------------|---------------------------------------------------------------------|----------|
| 1  | ML Model      | 84.38% accuracy — some requirements may be misclassified            | Medium   |
| 2  | File Types    | Only PDF and DOCX are supported (no TXT, CSV, or Excel)            | Low      |
| 3  | Language       | English-only requirement detection (keyword-based)                  | Medium   |
| 4  | Database      | SQLite — not suitable for high-concurrency production deployments    | Medium   |
| 5  | Auth          | No user authentication or access control                            | High     |
| 6  | File Storage  | Uploaded files stored on local disk (not cloud storage)             | Low      |
| 7  | Encoding      | Windows cp1252 logging may fail on Unicode arrow characters (→)     | Low      |
| 8  | Batch Size    | No hard limit on document size beyond 10 MB — very large docs may be slow | Low |
| 9  | Re-analysis   | Re-analysing a file overwrites previous results (no version history)| Low      |
| 10 | Categories    | Fixed 7 ISO/IEC 9126 categories — not customisable per project      | Low      |

## Known Workarounds

- **Issue 7 (Encoding):** The arrow character in log messages triggers a `UnicodeEncodeError` on Windows terminals using cp1252. This is cosmetic only and does not affect functionality. Log files in UTF-8 are unaffected.
- **Issue 5 (Auth):** For local development/demo use only. Add authentication before any public deployment.
- **Issue 4 (SQLite):** For production with multiple concurrent users, consider migrating to PostgreSQL.

## Future Improvements

See `TODO.md` → "Optional Enhancements" section for planned features including authentication, batch analysis, WebSocket real-time processing, Docker containerisation, and CI/CD pipelines.
