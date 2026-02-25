# Deployment Guide

This guide covers deploying QualityMapAI in development, Docker, and production environments.

---

## Prerequisites

| Tool       | Version  | Purpose                   |
|------------|----------|---------------------------|
| Python     | 3.11+    | Backend runtime           |
| Node.js    | 18+      | Frontend build toolchain  |
| npm        | 9+       | Frontend package manager  |
| Git        | 2.40+    | Version control           |

---

## 1. Local Development Setup

### Backend

```bash
# Clone the repository
git clone <repo-url>
cd AI-Quality-Assurance

# Create and activate virtual environment
python -m venv .venv

# Windows
.venv\Scripts\Activate.ps1

# macOS/Linux
source .venv/bin/activate

# Install dependencies
cd backend
pip install -r requirements.txt

# Start the backend server
python app.py
# → Server runs on http://localhost:5000
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start dev server (proxies /api → localhost:5000)
npm run dev
# → Dev server on http://localhost:5173
```

### Verify

- Backend health: `curl http://localhost:5000/api/health`
- Frontend: Open `http://localhost:5173` in your browser

---

## 2. Environment Variables

Create a `.env` file in the project root (or set system environment variables):

| Variable         | Default                  | Description                      |
|------------------|--------------------------|----------------------------------|
| `SECRET_KEY`     | `dev-secret-key-...`     | Flask secret key (change in prod)|
| `VITE_API_URL`   | `/api`                   | Frontend API base URL            |

---

## 3. Production Build

### Frontend

```bash
cd frontend
npm run build
# Output: frontend/dist/
```

The `dist/` folder contains static files ready to be served by any web server (Nginx, Apache, etc.).

### Backend (Production WSGI)

Do **not** use `python app.py` in production. Use a WSGI server:

```bash
# Install gunicorn (Linux/macOS)
pip install gunicorn

# Run with gunicorn
cd backend
gunicorn "app:create_app()" --bind 0.0.0.0:5000 --workers 4

# On Windows, use waitress instead:
pip install waitress
python -c "from waitress import serve; from app import create_app; serve(create_app(), host='0.0.0.0', port=5000)"
```

---

## 4. Docker Deployment

### Dockerfile (Backend)

```dockerfile
FROM python:3.13-slim

WORKDIR /app

# Copy and install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy application code
COPY backend/ .

# Copy ML models
COPY backend/models/ ./models/

EXPOSE 5000

CMD ["gunicorn", "app:create_app()", "--bind", "0.0.0.0:5000", "--workers", "4"]
```

### Dockerfile (Frontend)

```dockerfile
FROM node:18-alpine AS build

WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY docs/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
```

### docker-compose.yml

```yaml
version: "3.8"

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "5000:5000"
    volumes:
      - upload-data:/app/uploads
      - db-data:/app/data
    environment:
      - SECRET_KEY=your-production-secret-key
    restart: unless-stopped

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  upload-data:
  db-data:
```

### Nginx Config

```nginx
server {
    listen 80;
    server_name localhost;

    root /usr/share/nginx/html;
    index index.html;

    # SPA routing — serve index.html for all non-file routes
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Proxy API requests to backend
    location /api/ {
        proxy_pass http://backend:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        client_max_body_size 10M;
    }
}
```

### Run with Docker Compose

```bash
docker-compose up --build -d
# Frontend: http://localhost
# Backend:  http://localhost:5000/api/health
```

---

## 5. Database

QualityMapAI uses **SQLite** with WAL mode. The database file is created automatically on first launch at:

```
backend/data/quality_assurance.db
```

### Backup

```bash
# Simple file copy (while app is stopped or using WAL checkpoint)
cp backend/data/quality_assurance.db backup/quality_assurance_$(date +%Y%m%d).db
```

### Reset

```bash
rm backend/data/quality_assurance.db
# The database is recreated on next app startup
```

---

## 6. ML Model Files

The following files must be present in `backend/models/`:

| File                     | Description                |
|--------------------------|----------------------------|
| `classifier_model.pkl`   | Trained SVM model          |
| `tfidf_vectorizer.pkl`   | TF-IDF vectorizer          |
| `model_info.json`        | Model metadata (accuracy)  |

These are generated by the training scripts in `ml-training/` and should be version-controlled or stored in artifact storage.

---

## 7. Checklist

- [ ] Set a strong `SECRET_KEY` in production
- [ ] Use a WSGI server (gunicorn / waitress), not `python app.py`
- [ ] Serve frontend via Nginx or CDN, not Vite dev server
- [ ] Set up regular database backups
- [ ] Configure CORS origins to your domain (not `*`)
- [ ] Enable HTTPS (TLS/SSL certificate)
- [ ] Set up monitoring and logging (Sentry, ELK, etc.)
- [ ] Review rate limit settings for production load
