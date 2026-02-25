# Contributing to QualityMapAI

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

---

## Getting Started

1. **Fork** the repository
2. **Clone** your fork: `git clone <your-fork-url>`
3. **Set up** the development environment (see [docs/DEVELOPMENT.md](DEVELOPMENT.md))
4. **Create a branch** for your feature: `git checkout -b feature/your-feature-name`
5. **Make changes**, write tests, verify everything passes
6. **Push** and open a Pull Request

---

## Development Workflow

### Branch Naming

| Type      | Format                        | Example                       |
|-----------|-------------------------------|-------------------------------|
| Feature   | `feature/short-description`   | `feature/batch-upload`        |
| Bug fix   | `fix/short-description`       | `fix/upload-validation`       |
| Docs      | `docs/short-description`      | `docs/api-examples`           |
| Refactor  | `refactor/short-description`  | `refactor/scorer-cleanup`     |

### Commit Messages

Use clear, descriptive commit messages:

```
feat: add batch file upload endpoint
fix: handle empty DOCX files in document processor
test: add E2E tests for error scenarios
docs: update API documentation with rate limit info
refactor: extract scoring logic into separate module
```

---

## Code Standards

### Python (Backend)

- Follow **PEP 8** style guidelines
- Maximum line length: **100 characters**
- Use **type hints** on all function signatures
- Write **Google-style docstrings** for public functions
- Use `app_logger` for logging (never `print()`)
- Raise `AppError` subclasses for expected errors

### JavaScript/JSX (Frontend)

- Follow **ESLint** rules (`npm run lint`)
- Use **functional components** with hooks
- Use **MUI `sx` prop** for styling (no separate CSS files)
- Keep components focused — one responsibility per component

---

## Testing Requirements

### Before Submitting a PR

```bash
# Run ALL tests (must pass with 0 failures)
cd backend
python -m pytest tests/ -v

# Run frontend lint
cd frontend
npm run lint

# Build frontend (must succeed)
npm run build
```

### Writing Tests

- Every new endpoint needs integration tests in `tests/test_api.py`
- Every new service function needs unit tests in the appropriate test file
- Test both **success** and **error** paths
- Use the existing `conftest.py` fixtures (`app`, `client`)

---

## Pull Request Checklist

- [ ] Code follows the style guidelines above
- [ ] All existing tests pass (`118+` tests, 0 failures)
- [ ] New tests added for new functionality
- [ ] Documentation updated (API.md, README, etc.) if applicable
- [ ] No hardcoded values — use `Config` class
- [ ] Error handling uses the established patterns
- [ ] Commit messages are clear and descriptive

---

## Project Structure Rules

| Directory           | What goes here                              |
|---------------------|---------------------------------------------|
| `backend/routes/`   | API endpoint blueprints only                |
| `backend/services/` | Business logic (ML, scoring, extraction)    |
| `backend/database/` | DB schema, queries, connection management   |
| `backend/utils/`    | Shared utilities (logging, validation, etc.)|
| `backend/tests/`    | All test files (`test_*.py`)                |
| `frontend/src/pages/`      | Page-level components                |
| `frontend/src/components/` | Reusable UI components               |
| `frontend/src/api/`        | API client and service methods       |
| `docs/`             | All documentation                           |

---

## Reporting Issues

When reporting a bug, please include:

1. **Steps to reproduce** the issue
2. **Expected behaviour** vs **actual behaviour**
3. **Error messages** or screenshots
4. **Environment** (OS, Python version, Node version, browser)

---

## Questions?

Open an issue with the `question` label, or refer to:
- [Development Guide](DEVELOPMENT.md) — setup and common tasks
- [API Documentation](API.md) — endpoint reference
- [Architecture](ARCHITECTURE.md) — system design overview
