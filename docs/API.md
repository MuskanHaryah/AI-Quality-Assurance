# QualityMapAI API Documentation

**Base URL:** `http://localhost:5000/api`  
**Version:** 1.0.0  
**Content-Type:** `application/json` (unless noted otherwise)

---

## Table of Contents

1. [Health Check](#1-health-check)
2. [Upload File](#2-upload-file)
3. [Analyze File](#3-analyze-file)
4. [Predict (Classify)](#4-predict-classify)
5. [Get Report](#5-get-report)
6. [List Analyses (Dashboard)](#6-list-analyses-dashboard)
7. [Error Format](#7-error-format)
8. [Rate Limiting](#8-rate-limiting)

---

## 1. Health Check

Check if the backend is running and the ML model is loaded.

```
GET /api/health
```

### Response `200 OK`

```json
{
  "status": "ok",
  "message": "QualityMapAI backend running",
  "model": "tfidf_svm_classifier",
  "accuracy": 0.8438
}
```

---

## 2. Upload File

Upload a PDF or DOCX file for analysis.

```
POST /api/upload
Content-Type: multipart/form-data
```

### Request

| Field  | Type   | Required | Description                       |
|--------|--------|----------|-----------------------------------|
| `file` | File   | Yes      | PDF or DOCX file (max 10 MB)      |

### Response `200 OK`

```json
{
  "success": true,
  "file_id": "20260223_152312_cf11b406",
  "filename": "requirements.pdf",
  "file_type": "pdf",
  "size_bytes": 204800,
  "size_mb": 0.20,
  "status": "uploaded",
  "message": "File uploaded successfully. Use /api/analyze to process it."
}
```

### Error Responses

| Code | Condition                          |
|------|------------------------------------|
| 400  | No file provided                   |
| 400  | File has no name                   |
| 400  | Unsupported file type (not PDF/DOCX) |
| 400  | File exceeds 10 MB size limit      |
| 500  | Could not save file to disk        |
| 500  | Could not save file metadata to DB |

---

## 3. Analyze File

Run the full analysis pipeline on a previously uploaded file.

**Pipeline:** Extract text → Extract requirements → Classify with ML → Calculate quality scores → Save to DB

```
POST /api/analyze
Content-Type: application/json
```

### Request Body

```json
{
  "file_id": "20260223_152312_cf11b406"
}
```

| Field     | Type   | Required | Description                   |
|-----------|--------|----------|-------------------------------|
| `file_id` | string | Yes      | ID returned from `/api/upload` |

### Response `200 OK`

```json
{
  "success": true,
  "analysis_id": "20260223_152312_cf11b406",
  "total_requirements": 12,
  "overall_score": 74.3,
  "risk": {
    "level": "Medium",
    "colour": "orange"
  },
  "category_scores": {
    "Functionality": { "count": 3, "percentage": 25.0, "score": 85.0 },
    "Security": { "count": 2, "percentage": 16.7, "score": 70.0 },
    "Reliability": { "count": 2, "percentage": 16.7, "score": 70.0 },
    "Efficiency": { "count": 1, "percentage": 8.3, "score": 50.0 },
    "Usability": { "count": 2, "percentage": 16.7, "score": 70.0 },
    "Maintainability": { "count": 1, "percentage": 8.3, "score": 50.0 },
    "Portability": { "count": 1, "percentage": 8.3, "score": 50.0 }
  },
  "requirements": [
    {
      "text": "The system shall authenticate all users.",
      "category": "Security",
      "confidence": 0.87,
      "keyword_strength": "strong"
    }
  ],
  "recommendations": [
    {
      "category": "Efficiency",
      "priority": "high",
      "message": "Add more efficiency requirements..."
    }
  ],
  "gap_analysis": [
    {
      "category": "Maintainability",
      "gap_type": "insufficient",
      "shortage": 1
    }
  ],
  "categories_present": ["Functionality", "Security", "Reliability"],
  "categories_missing": ["Maintainability"],
  "document_info": {
    "word_count": 450,
    "page_count": 2,
    "file_type": "pdf"
  },
  "extraction_stats": {
    "total_candidates": 20,
    "total_found": 12,
    "strong_count": 8,
    "weak_count": 4,
    "filtered_count": 8
  },
  "processing_time_s": 2.41
}
```

### Error Responses

| Code | Condition                              |
|------|----------------------------------------|
| 400  | Missing JSON body or `file_id`         |
| 400  | Empty `file_id`                        |
| 404  | No upload found for the given `file_id`|
| 422  | Text extraction failed                 |
| 422  | No requirement statements found        |
| 500  | Failed to save analysis results to DB  |

---

## 4. Predict (Classify)

Classify one or more plain-text requirement sentences on the fly — no file upload needed.

```
POST /api/predict
Content-Type: application/json
```

### Request Body (single)

```json
{
  "text": "The system shall encrypt all passwords using AES-256."
}
```

### Request Body (batch)

```json
{
  "texts": [
    "The system must respond in under 2 seconds.",
    "Users shall be able to reset their password.",
    "All data must be backed up every 24 hours."
  ]
}
```

| Field   | Type           | Required | Description                          |
|---------|----------------|----------|--------------------------------------|
| `text`  | string         | One of   | Single requirement text              |
| `texts` | array[string]  | One of   | Batch of requirement texts           |

### Response `200 OK`

```json
{
  "success": true,
  "count": 3,
  "results": [
    {
      "text": "The system must respond in under 2 seconds.",
      "category": "Efficiency",
      "confidence": 92.5,
      "probabilities": {
        "Efficiency": 92.5,
        "Reliability": 3.2,
        "Functionality": 1.8,
        "Security": 1.0,
        "Usability": 0.8,
        "Maintainability": 0.4,
        "Portability": 0.3
      }
    }
  ]
}
```

### Error Responses

| Code | Condition                                |
|------|------------------------------------------|
| 400  | Missing JSON body                        |
| 400  | Neither `text` nor `texts` provided      |
| 400  | `texts` is not a non-empty list          |
| 400  | Text entry is empty or not a string      |
| 500  | Classification failed                    |

---

## 5. Get Report

Retrieve the full analysis report for a given analysis ID.

```
GET /api/report/<analysis_id>
```

### URL Parameters

| Parameter      | Type   | Description                        |
|----------------|--------|------------------------------------|
| `analysis_id`  | string | The analysis ID from `/api/analyze`|

### Response `200 OK`

```json
{
  "success": true,
  "analysis_id": "20260223_152312_cf11b406",
  "summary": {
    "overall_score": 74.3,
    "risk": { "level": "Medium" },
    "total_requirements": 12,
    "categories_present": ["Functionality", "Security"],
    "categories_missing": ["Maintainability"],
    "created_at": "2026-02-23 15:23:12",
    "filename": "requirements.pdf",
    "file_type": "pdf"
  },
  "category_scores": { "...": "..." },
  "requirements": [
    {
      "id": 1,
      "text": "The system shall authenticate all users.",
      "category": "Security",
      "confidence": 0.87,
      "keyword_strength": "strong"
    }
  ],
  "recommendations": [ "..." ],
  "gap_analysis": [ "..." ],
  "categories_present": ["Functionality", "Security"],
  "categories_missing": ["Maintainability"]
}
```

### Error Responses

| Code | Condition                       |
|------|---------------------------------|
| 400  | Empty `analysis_id`             |
| 404  | No analysis found for given ID  |

---

## 6. List Analyses (Dashboard)

Get the 20 most recent analyses for the dashboard view.

```
GET /api/analyses
```

### Response `200 OK`

```json
{
  "success": true,
  "count": 5,
  "analyses": [
    {
      "analysis_id": "20260223_152312_cf11b406",
      "filename": "requirements.pdf",
      "file_type": "pdf",
      "overall_score": 74.3,
      "risk_level": "Medium",
      "total_requirements": 12,
      "created_at": "2026-02-23 15:23:12"
    }
  ]
}
```

---

## 7. Error Format

All error responses follow this consistent format:

```json
{
  "success": false,
  "error": "Human-readable error message"
}
```

Some errors include additional detail:

```json
{
  "success": false,
  "error": "Validation failed",
  "details": { "field": "file_id", "reason": "required" }
}
```

### Standard HTTP Error Codes

| Code | Meaning                                    |
|------|--------------------------------------------|
| 400  | Bad request / validation error             |
| 404  | Resource not found                         |
| 405  | HTTP method not allowed                    |
| 413  | File too large (> 10 MB)                   |
| 422  | Unprocessable – extraction or scoring failed|
| 429  | Rate limit exceeded                        |
| 500  | Internal server error                      |

---

## 8. Rate Limiting

All endpoints are rate-limited to prevent abuse:

| Scope      | Limit             |
|------------|-------------------|
| Global     | 200 requests/min  |
| Global     | 50 requests/sec   |

When the limit is exceeded a `429 Too Many Requests` response is returned:

```json
{
  "success": false,
  "error": "Rate limit exceeded. Please slow down."
}
```

---

## ML Model Details

| Property   | Value                                                            |
|------------|------------------------------------------------------------------|
| Algorithm  | TF-IDF + SVM (Support Vector Machine)                            |
| Accuracy   | 84.38%                                                           |
| Categories | Efficiency, Functionality, Maintainability, Portability, Reliability, Security, Usability |
| Standard   | ISO/IEC 9126 Software Quality Characteristics                    |

---

## OpenAPI 3.0 Specification

A machine-readable OpenAPI spec is available at [`docs/openapi.yaml`](openapi.yaml).
