# AI-Driven Quality Assurance Analyzer
## Complete Project Specification Document

**Project Name:** **QualityMapAI** (RequireVerify as alternative)

**Project Type:** Web-based AI System for Software Quality Assessment

**Date:** February 22, 2026

---

## 📋 Table of Contents

1. [Tech Stack](#tech-stack)
2. [Complete Features](#complete-features)
3. [AI Training Approach](#ai-training-approach)
4. [System Requirements](#system-requirements)
5. [System Architecture](#system-architecture)
6. [Data Flow](#data-flow)

---

# 1. TECH STACK

## Frontend Stack

### React 18+ 
**Why chosen:**
- ✓ You have experience with React
- ✓ Component reusability (upload form, result cards, charts)
- ✓ Fast virtual DOM for dynamic UI updates
- ✓ Better state management for complex workflows
- ✓ Easy to integrate charts and visualizations
- ✓ Professional look for demo/presentation

### UI Library: Material-UI (MUI) v5
**Why chosen:**
- ✓ Pre-built professional components (cards, tables, buttons)
- ✓ Consistent design system out-of-the-box
- ✓ Responsive by default
- ✓ Good documentation
- ✓ Less CSS code needed
- ✓ Icons included (for quality metrics)

**Alternative:** Ant Design (equally good)

### Axios
**Why chosen:**
- ✓ Easy HTTP requests to Flask backend
- ✓ File upload support
- ✓ Better error handling than fetch
- ✓ Cleaner syntax

### Recharts or Chart.js
**Why chosen:**
- ✓ Visualize quality scores (pie charts, bar graphs)
- ✓ Easy integration with React
- ✓ Interactive and professional

---

## Backend Stack

### Flask 3.x (Python)
**Why chosen:**
- ✓ Lightweight and simple
- ✓ Perfect integration with Python ML models
- ✓ Easy to build REST APIs
- ✓ Less boilerplate than Django
- ✓ Quick to learn and implement
- ✓ Ideal for semester projects

**Alternatives considered:**
- Django: Too heavyweight for this project
- FastAPI: Good but Flask is more standard for academic projects
- Node.js: Would require separate Python service for AI

### Flask-CORS
**Why chosen:**
- ✓ Handle Cross-Origin requests from React
- ✓ Required for React development server

### Flask-RESTful (optional)
**Why chosen:**
- ✓ Cleaner REST API structure
- ✓ Better error handling

---

## AI/ML Stack

### scikit-learn 1.3+
**Why chosen:**
- ✓ Industry-standard for text classification
- ✓ Simple to train and deploy
- ✓ TF-IDF vectorization included
- ✓ Multiple algorithms available (Logistic Regression, Naive Bayes, SVM)
- ✓ No GPU needed (unlike deep learning)
- ✓ Fast inference
- ✓ Good for small-medium datasets

### pandas 2.x
**Why chosen:**
- ✓ Data manipulation and CSV handling
- ✓ Easy dataset creation
- ✓ Data analysis and statistics

### NLTK or spaCy
**Why chosen:**
- ✓ Text preprocessing (tokenization, stopword removal)
- ✓ Sentence splitting for requirement extraction
- ✓ Part-of-speech tagging (optional)

**Recommendation:** Start with NLTK (simpler), upgrade to spaCy if needed

### joblib
**Why chosen:**
- ✓ Save/load trained models efficiently
- ✓ Built-in with scikit-learn
- ✓ Fast serialization

---

## Document Processing Stack

### PyPDF2 or pdfplumber
**Why chosen:**
- ✓ Extract text from PDF files (SRS, test reports)
- ✓ Simple API
- ✓ No external dependencies

**Recommendation:** Use pdfplumber (better text extraction quality)

### python-docx (optional)
**Why chosen:**
- ✓ Support Word documents (.docx)
- ✓ Many projects use Word for documentation

---

## Database Stack

### SQLite 3
**Why chosen:**
- ✓ No separate server needed
- ✓ File-based database
- ✓ Good for project history tracking
- ✓ Easy to demo
- ✓ Can upgrade to PostgreSQL later

**What to store:**
- Upload history
- Analysis results
- User sessions (if multi-user)
- Cached predictions

**Alternative:** No database initially (process and display only)

---

## Development Tools

### Python Virtual Environment (venv)
**Why:**
- ✓ Isolate project dependencies
- ✓ Avoid version conflicts

### npm/yarn
**Why:**
- ✓ React package management

### Git
**Why:**
- ✓ Version control
- ✓ Team collaboration
- ✓ GitHub for backup

---

# 2. COMPLETE FEATURES

## Module 1: Document Upload & Management

### Feature 1.1: Multi-File Upload
**How it works:**
- User can upload multiple files:
  - SRS (PDF/DOCX)
  - Quality Plan (PDF/DOCX)
  - Test Report (PDF/DOCX)
- File validation (size, type)
- Progress indicator during upload
- File preview (filename, size, type)

**Technical implementation:**
- React: File input with drag-and-drop (Dropzone.js)
- Backend: Flask receives files via POST
- Storage: Save temporarily in `/uploads` folder

---

### Feature 1.2: Document Type Detection
**How it works:**
- System automatically identifies document type
- Uses filename patterns + content analysis
- User can override if wrong

**Technical implementation:**
- Keyword matching ("requirement", "test", "quality")
- Rule-based classification

---

## Module 2: Text Extraction & Preprocessing

### Feature 2.1: PDF/DOCX Text Extraction
**How it works:**
- Extract raw text from uploaded documents
- Preserve structure (headings, sections)
- Handle multi-page documents

**Technical implementation:**
```python
import pdfplumber
text = pdfplumber.open(file).extract_text()
```

---

### Feature 2.2: Text Cleaning
**How it works:**
- Remove special characters
- Normalize whitespace
- Handle tables and lists
- Split into sentences

**Technical implementation:**
```python
import nltk
sentences = nltk.sent_tokenize(text)
```

---

## Module 3: AI-Powered Requirement Classification

### Feature 3.1: Requirement Extraction
**How it works:**
- Identify requirement statements from SRS
- Filter out non-requirement text (introductions, references)
- Detect "shall", "must", "should" keywords

**Technical implementation:**
- Pattern matching + ML classification
- Extract sentences containing requirement indicators

---

### Feature 3.2: Quality Attribute Classification
**How it works:**
- Classify each requirement into quality categories:
  - **Functional** (login, register, process order)
  - **Performance** (response time, throughput)
  - **Security** (authentication, encryption)
  - **Usability** (UI, user experience)
  - **Reliability** (uptime, error handling)
  - **Maintainability** (code quality, documentation)
  - **Portability** (platform support)

**Technical implementation:**
- Trained ML model (scikit-learn)
- TF-IDF vectorization
- Multi-class classification

**Example:**
```
Input: "System shall respond within 2 seconds"
Output: Efficiency (ISO/IEC 9126 - Time Behavior) (95% confidence)
```

---

## Module 4: Evidence Mapping & Gap Analysis

### Feature 4.1: Test Evidence Extraction
**How it works:**
- Extract test results from test reports
- Parse test cases, pass/fail status
- Extract performance metrics (response times, etc.)

**Technical implementation:**
- Keyword extraction from test report
- Pattern matching for numbers and units
- Table extraction from PDF

---

### Feature 4.2: Requirement-Evidence Matching
**How it works:**
- Match each requirement with corresponding test evidence
- Check if requirement is verified
- Identify gaps (requirements without evidence)

**Technical implementation:**
- Semantic similarity matching
- Keyword overlap
- Quality attribute matching

**Example:**
```
Requirement: "Response time < 2 seconds" (Performance)
Test Evidence: "Avg response: 1.8 seconds" ✓ MATCHED
```

---

### Feature 4.3: Gap Detection
**How it works:**
- List requirements without test evidence
- Highlight missing quality attributes
- Risk scoring

**Output example:**
```
GAPS FOUND:
- Security requirement #3 not tested
- No performance tests found
- 5 functional requirements lack evidence
```

---

## Module 5: Quality Scoring & Assessment

### Feature 5.1: Overall Quality Score
**How it works:**
- Calculate percentage of requirements satisfied
- Weighted scoring by quality attribute
- Visual score display (gauge, percentage)

**Formula:**
```
Quality Score = (Requirements Satisfied / Total Requirements) × 100
```

**Technical implementation:**
- Count matched vs total requirements
- Apply weights (security = 15%, performance = 15%, etc.)

---

### Feature 5.2: Category-wise Breakdown
**How it works:**
- Show quality score per category
- Bar chart visualization
- Detailed metrics

**Example output:**
```
Functionality:   85% ████████▌
Efficiency:      60% ██████
Security:        40% ████
Usability:       90% █████████
```

---

### Feature 5.3: Risk Highlighting
**How it works:**
- Identify high-risk areas
- Color-coded warnings (red/yellow/green)
- Prioritized action items

**Risk levels:**
- 🔴 Critical: Security/Performance gaps
- 🟡 Medium: Usability/Reliability gaps
- 🟢 Low: Documentation gaps

---

## Module 6: Early Quality Prediction (AI-Powered)

### Feature 6.1: Quality Forecast
**How it works:**
- Analyze SRS + Quality Plan (before testing)
- Predict final achievable quality %
- Estimate risk level

**Prediction factors:**
1. **Requirement Clarity Score** (40%)
   - Ambiguous words detected
   - Completeness check
   - Measurability of requirements

2. **Quality Attribute Coverage** (30%)
   - Number of non-functional requirements
   - Security requirements presence
   - Performance criteria defined

3. **Testing Plan Strength** (30%)
   - Test types mentioned (unit, integration, performance)
   - Code review planned
   - Automation mentioned

**Formula:**
```
Predicted Quality = 0.4 × Clarity + 0.3 × Coverage + 0.3 × Testing Strength
```

**Example output:**
```
PREDICTED QUALITY: 72% (Medium)

Current State:
✓ Good requirement clarity (80%)
⚠ Missing security requirements (60%)
✓ Strong testing plan (70%)

Risks:
- No security testing planned
- Performance benchmarks undefined
```

---

### Feature 6.2: Improvement Suggestions
**How it works:**
- AI generates actionable recommendations
- Prioritized by impact
- Specific to detected gaps

**Example:**
```
RECOMMENDATIONS:
1. Add security requirements (encryption, authentication)
2. Define performance benchmarks (response time thresholds)
3. Include unit testing in quality plan
```

---

## Module 7: Report Generation

### Feature 7.1: Quality Assessment Report
**How it works:**
- Generate PDF/HTML report
- Include all metrics, charts, gaps
- Professional formatting

**Report sections:**
1. Executive Summary
2. Requirements Overview
3. Quality Score (overall + category-wise)
4. Gap Analysis
5. Recommendations

---

### Feature 7.2: Comparison Report
**How it works:**
- Compare multiple uploads
- Track quality improvement over time
- Show trends

---

## Module 8: Dashboard & Visualization

### Feature 8.1: Interactive Dashboard
**Components:**
- Overall quality gauge
- Category breakdown (bar chart)
- Gap summary (list with icons)
- Recent uploads (table)

---

### Feature 8.2: Drill-down View
**How it works:**
- Click on category to see details
- View individual requirements
- See evidence matches

---

## Module 9: Admin Features (Optional)

### Feature 9.1: Model Retraining
**How it works:**
- Upload new training data
- Retrain classifier
- Update model version

---

### Feature 9.2: System Settings
**How it works:**
- Configure quality weights
- Set thresholds (pass/fail)
- Customize categories

---

# 3. AI TRAINING APPROACH

## Phase 1: Dataset Creation

### Step 1: Collect Sample Data
**Sources:**
1. **Public datasets:**
   - GitHub: Search "SRS sample", "software requirements"
   - Kaggle: Requirements engineering datasets
   - IEEE: Sample SRS documents

2. **Create your own:**
   - Extract from existing projects
   - Write synthetic requirements
   - Use online SRS templates

**Target size:** 500-1000 requirement statements

---

### Step 2: Label the Data
**Create CSV file: `requirements_dataset.csv`**

| ID | Requirement Text | Quality_Attribute | Sub_Category |
|----|-----------------|-------------------|--------------|
| 1 | User shall login with email and password | Functional | Authentication |
| 2 | System shall respond within 2 seconds | Performance | Response_Time |
| 3 | Password must be encrypted using AES-256 | Security | Encryption |
| 4 | UI should be intuitive and easy to use | Usability | User_Experience |
| 5 | System shall have 99.9% uptime | Reliability | Availability |
| 6 | Code should follow PEP-8 standards | Maintainability | Code_Quality |
| 7 | System must run on Windows and Linux | Portability | Platform |

**Labeling guidelines:**
- Be consistent with categories
- Include variations (different phrasings)
- Balance classes (similar number per category)

---

### Step 3: Data Preprocessing
**Code example:**
```python
import pandas as pd
import nltk
from sklearn.model_selection import train_test_split

# Load data
df = pd.read_csv('requirements_dataset.csv')

# Clean text
df['text_clean'] = df['Requirement Text'].str.lower()
df['text_clean'] = df['text_clean'].str.replace(r'[^\w\s]', '', regex=True)

# Split dataset
X = df['text_clean']
y = df['Quality_Attribute']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
```

---

## Phase 2: Feature Engineering

### TF-IDF Vectorization
**Why TF-IDF:**
- Converts text to numerical features
- Captures word importance
- Industry standard for text classification

**Code:**
```python
from sklearn.feature_extraction.text import TfidfVectorizer

vectorizer = TfidfVectorizer(
    max_features=500,      # Top 500 words
    ngram_range=(1, 2),    # Unigrams and bigrams
    min_df=2,              # Ignore rare words
    stop_words='english'   # Remove common words
)

X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)
```

---

## Phase 3: Model Training

### Algorithm Selection
**Try multiple algorithms:**

1. **Logistic Regression** (Recommended)
   - Fast training
   - Good with text data
   - Interpretable

2. **Naive Bayes**
   - Fast inference
   - Works well with small data

3. **SVM (Support Vector Machine)**
   - High accuracy
   - Good with high-dimensional data

4. **Random Forest**
   - Handles complex patterns
   - Less prone to overfitting

### Training Code
```python
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.metrics import accuracy_score, classification_report

# Train Logistic Regression
model = LogisticRegression(max_iter=1000, random_state=42)
model.fit(X_train_tfidf, y_train)

# Evaluate
y_pred = model.predict(X_test_tfidf)
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy * 100:.2f}%")
print(classification_report(y_test, y_pred))
```

---

## Phase 4: Model Evaluation

### Metrics to Check
1. **Accuracy:** Overall correctness
2. **Precision:** How many predicted positives are correct
3. **Recall:** How many actual positives are found
4. **F1-Score:** Harmonic mean of precision and recall

**Target performance:**
- Accuracy > 80% (good for semester project)
- Balanced precision/recall across categories

---

## Phase 5: Model Saving & Deployment

### Save Model
```python
import joblib

# Save model and vectorizer
joblib.dump(model, 'models/classifier_model.pkl')
joblib.dump(vectorizer, 'models/tfidf_vectorizer.pkl')
```

### Load Model in Flask
```python
import joblib

# Load once at startup
model = joblib.load('models/classifier_model.pkl')
vectorizer = joblib.load('models/tfidf_vectorizer.pkl')

def classify_requirement(text):
    text_tfidf = vectorizer.transform([text])
    prediction = model.predict(text_tfidf)[0]
    confidence = model.predict_proba(text_tfidf).max()
    return prediction, confidence
```

---

## Phase 6: Continuous Improvement

### Model Retraining
- Collect user feedback on predictions
- Add misclassified examples to dataset
- Retrain periodically
- Version control models

---

# 4. SYSTEM REQUIREMENTS

## 4.1 Functional Requirements

### FR-1: Document Upload
**Description:** System shall allow users to upload SRS, Quality Plan, and Test Report documents.

**Input:** PDF or DOCX files (max 10MB each)

**Output:** Upload confirmation with file details

**Priority:** Critical

---

### FR-2: Text Extraction
**Description:** System shall extract text content from uploaded documents.

**Input:** Uploaded document

**Output:** Plain text representation

**Priority:** Critical

---

### FR-3: Requirement Classification
**Description:** System shall classify requirements into quality attribute categories.

**Input:** Requirement text

**Output:** Quality attribute label + confidence score

**Categories (ISO/IEC 9126):**
- Functionality
- Security (elevated from sub-characteristic)
- Reliability
- Usability
- Efficiency
- Maintainability
- Portability

**Priority:** Critical

---

### FR-4: Evidence Extraction
**Description:** System shall extract test evidence from test reports.

**Input:** Test report document

**Output:** List of test cases with results

**Priority:** High

---

### FR-5: Gap Analysis
**Description:** System shall identify requirements without corresponding test evidence.

**Input:** Requirements list + Test evidence

**Output:** Gap report with missing items

**Priority:** High

---

### FR-6: Quality Score Calculation
**Description:** System shall calculate overall quality score.

**Formula:** (Satisfied Requirements / Total Requirements) × 100

**Output:** Percentage score + category breakdown

**Priority:** Critical

---

### FR-7: Quality Prediction
**Description:** System shall predict expected quality based on SRS and Quality Plan analysis.

**Input:** SRS + Quality Plan (pre-testing phase)

**Output:** Predicted quality score + risk assessment

**Prediction factors:**
- Requirement clarity (40%)
- Quality attribute coverage (30%)
- Testing plan strength (30%)

**Priority:** High

---

### FR-8: Report Generation
**Description:** System shall generate quality assessment reports.

**Output format:** PDF or HTML

**Sections:**
- Executive summary
- Quality scores
- Gap analysis
- Recommendations

**Priority:** Medium

---

### FR-9: Visualization
**Description:** System shall display quality metrics through charts and graphs.

**Visualizations:**
- Overall quality gauge
- Category-wise bar chart
- Gap summary
- Trend analysis (if multiple uploads)

**Priority:** High

---

### FR-10: Search & Filter
**Description:** System shall allow searching and filtering requirements.

**Search by:**
- Keyword
- Quality attribute
- Evidence status (verified/unverified)

**Priority:** Low

---

## 4.2 Non-Functional Requirements

### NFR-1: Performance
**PER-1:** System shall process uploaded documents within 30 seconds for files up to 10MB.

**PER-2:** AI classification shall complete within 100ms per requirement.

**PER-3:** Dashboard shall load within 2 seconds.

**PER-4:** System shall support concurrent uploads from up to 10 users.

---

### NFR-2: Accuracy
**ACC-1:** Requirement classification accuracy shall be ≥ 80%.

**ACC-2:** Quality score calculation shall have ≤ 5% error margin.

**ACC-3:** Evidence matching shall have ≥ 75% precision.

---

### NFR-3: Usability
**USA-1:** UI shall be intuitive with minimal training required.

**USA-2:** Error messages shall be clear and actionable.

**USA-3:** Upload process shall have progress indicators.

**USA-4:** Dashboard shall be responsive (mobile/tablet/desktop).

**USA-5:** System shall support drag-and-drop file upload.

---

### NFR-4: Security
**SEC-1:** Uploaded files shall be stored securely with access control.

**SEC-2:** File type validation shall prevent malicious uploads.

**SEC-3:** System shall sanitize extracted text to prevent injection attacks.

**SEC-4:** API endpoints shall have rate limiting.

---

### NFR-5: Reliability
**REL-1:** System shall have 99% uptime during demo period.

**REL-2:** Failed uploads shall not crash the system.

**REL-3:** System shall gracefully handle corrupted files.

**REL-4:** Model predictions shall fallback to rule-based if AI fails.

---

### NFR-6: Maintainability
**MNT-1:** Code shall follow PEP-8 (Python) and ESLint standards (JavaScript).

**MNT-2:** All functions shall have docstrings/comments.

**MNT-3:** System shall have modular architecture for easy updates.

**MNT-4:** ML model shall be versioned for retraining.

---

### NFR-7: Scalability
**SCA-1:** System shall handle documents up to 100 pages.

**SCA-2:** System shall support up to 1000 requirements per document.

**SCA-3:** Database shall support at least 100 analysis records.

---

### NFR-8: Compatibility
**CMP-1:** Frontend shall work on Chrome, Firefox, Edge (latest versions).

**CMP-2:** System shall support PDF versions 1.4 to 1.7.

**CMP-3:** System shall accept DOCX (Office 2007+).

**CMP-4:** Backend shall run on Python 3.8+.

---

### NFR-9: Portability
**PRT-1:** System shall run on Windows, Linux, macOS.

**PRT-2:** Deployment shall use Docker for consistency.

**PRT-3:** Database shall be portable (SQLite file-based).

---

### NFR-10: Documentation
**DOC-1:** API endpoints shall be documented (Swagger/OpenAPI).

**DOC-2:** User manual shall be provided.

**DOC-3:** Installation guide shall be included.

**DOC-4:** Code repository shall have README.md.

---

## 4.3 System Constraints

### CONS-1: Technology Stack
System must use Python (backend), React (frontend), scikit-learn (AI).

### CONS-2: Budget
Zero budget (use free/open-source tools only).

### CONS-3: Timeline
Complete within one semester (12-14 weeks).

### CONS-4: Team Size
Designed for 2-4 person team.

### CONS-5: Hardware
Run on standard student laptop (no GPU required).

---

## 4.4 Business Rules

### BR-1: File Size Limit
Maximum upload size: 10MB per file.

### BR-2: Supported Formats
Only PDF and DOCX accepted.

### BR-3: Quality Score Calculation
Must use weighted scoring: Security (15%), Performance (15%), Functional (40%), Others (30%).

### BR-4: Gap Threshold
If quality score < 70%, system shall flag as "High Risk".

### BR-5: Prediction Confidence
AI predictions below 60% confidence shall be marked as "Uncertain".

---

## 4.5 User Requirements

### User Roles

**Role 1: Quality Analyst** (Primary user)
- Upload documents
- View quality reports
- Analyze gaps
- Export reports

**Role 2: Project Manager** (Secondary)
- View quality predictions
- Track quality trends
- Access recommendations

**Role 3: Admin** (Optional)
- Manage system settings
- Retrain models
- View system logs

---

## 4.6 Data Requirements

### Input Data
1. **SRS Document:** Text-based requirements specification
2. **Quality Plan:** Testing and quality strategies
3. **Test Report:** Test cases and execution results

### Output Data
1. **Quality Score:** Numerical (0-100%)
2. **Classification Results:** Category labels + confidence
3. **Gap Analysis:** List of unverified requirements
4. **Prediction Report:** Expected quality + risks

### Storage Requirements
- Upload storage: 1GB (local filesystem)
- Database: 100MB (SQLite)
- Model files: 50MB

---

# 5. SYSTEM ARCHITECTURE

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                        │
│                    (React + Material-UI)                      │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Upload Page  │  │  Dashboard   │  │ Report View  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP/REST API (Axios)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      FLASK BACKEND                            │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ File Upload  │  │ Text Extract │  │  AI Service  │      │
│  │   Handler    │  │   Service    │  │  (Classify)  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Evidence    │  │   Quality    │  │  Prediction  │      │
│  │   Matcher    │  │   Scorer     │  │   Engine     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
         ┌──────────────────────────────────────┐
         │     DATA LAYER                       │
         │                                      │
         │  ┌─────────────┐  ┌─────────────┐  │
         │  │   SQLite    │  │ File System │  │
         │  │  Database   │  │  (Uploads)  │  │
         │  └─────────────┘  └─────────────┘  │
         │                                      │
         │  ┌─────────────┐                    │
         │  │  ML Models  │                    │
         │  │   (.pkl)    │                    │
         │  └─────────────┘                    │
         └──────────────────────────────────────┘
```

---

## Component Breakdown

### Frontend Components (React)

```
src/
├── components/
│   ├── UploadForm.jsx         // File upload with drag-drop
│   ├── FileList.jsx           // Display uploaded files
│   ├── Dashboard.jsx          // Main dashboard
│   ├── QualityGauge.jsx       // Circular quality score
│   ├── CategoryChart.jsx      // Bar chart for categories
│   ├── GapList.jsx            // List of gaps
│   ├── PredictionPanel.jsx    // Quality prediction display
│   ├── ReportViewer.jsx       // View detailed report
│   └── LoadingSpinner.jsx     // Loading indicator
│
├── services/
│   └── api.js                 // Axios API calls
│
├── utils/
│   ├── fileValidation.js      // Validate file type/size
│   └── formatters.js          // Format data for display
│
├── App.jsx                    // Main app component
└── index.jsx                  // Entry point
```

---

### Backend Structure (Flask)

```
backend/
├── app.py                     // Flask app entry point
│
├── routes/
│   ├── upload.py              // File upload endpoints
│   ├── analyze.py             // Analysis endpoints
│   └── report.py              // Report generation endpoints
│
├── services/
│   ├── document_processor.py  // PDF/DOCX extraction
│   ├── requirement_extractor.py  // Extract requirements
│   ├── classifier.py          // AI classification
│   ├── evidence_matcher.py    // Match requirements to tests
│   ├── quality_scorer.py      // Calculate quality score
│   └── predictor.py           // Quality prediction logic
│
├── models/
│   ├── classifier_model.pkl   // Trained ML model
│   └── tfidf_vectorizer.pkl   // TF-IDF vectorizer
│
├── utils/
│   ├── text_cleaner.py        // Text preprocessing
│   └── validators.py          // Input validation
│
├── database/
│   ├── db.py                  // Database connection
│   └── models.py              // SQLite models
│
└── uploads/                   // Temporary file storage
```

---

## Database Schema

### Table: uploads
```sql
CREATE TABLE uploads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NOT NULL,  -- 'SRS', 'QualityPlan', 'TestReport'
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    file_path VARCHAR(500) NOT NULL,
    status VARCHAR(50) DEFAULT 'uploaded'  -- 'uploaded', 'processed', 'failed'
);
```

### Table: analysis_results
```sql
CREATE TABLE analysis_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    upload_id INTEGER NOT NULL,
    overall_quality_score REAL,
    functional_score REAL,
    performance_score REAL,
    security_score REAL,
    usability_score REAL,
    reliability_score REAL,
    maintainability_score REAL,
    total_requirements INTEGER,
    satisfied_requirements INTEGER,
    gaps_count INTEGER,
    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (upload_id) REFERENCES uploads(id)
);
```

### Table: requirements
```sql
CREATE TABLE requirements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    upload_id INTEGER NOT NULL,
    requirement_text TEXT NOT NULL,
    quality_attribute VARCHAR(50),
    confidence_score REAL,
    has_evidence BOOLEAN DEFAULT 0,
    FOREIGN KEY (upload_id) REFERENCES uploads(id)
);
```

### Table: predictions
```sql
CREATE TABLE predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    upload_id INTEGER NOT NULL,
    predicted_quality REAL,
    clarity_score REAL,
    coverage_score REAL,
    testing_strength REAL,
    risk_level VARCHAR(50),  -- 'Low', 'Medium', 'High'
    prediction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (upload_id) REFERENCES uploads(id)
);
```

---

# 6. DATA FLOW

## Flow 1: Quality Assessment (Main Flow)

```
1. USER ACTION
   └─> User uploads SRS + Test Report

2. FRONTEND
   └─> Validate files (size, type)
   └─> POST /api/upload (multipart/form-data)

3. BACKEND: File Upload Handler
   └─> Save files to /uploads/
   └─> Store metadata in database
   └─> Return upload_id

4. FRONTEND
   └─> Call POST /api/analyze/{upload_id}

5. BACKEND: Analysis Service
   
   Step 5.1: Text Extraction
   └─> Extract text from SRS using pdfplumber
   └─> Extract text from Test Report
   
   Step 5.2: Requirement Extraction
   └─> Split SRS into sentences
   └─> Filter requirement sentences (contains "shall", "must", etc.)
   
   Step 5.3: AI Classification
   └─> For each requirement:
       └─> Clean text
       └─> Vectorize with TF-IDF
       └─> Predict quality attribute
       └─> Get confidence score
       └─> Store in database
   
   Step 5.4: Evidence Extraction
   └─> Parse test report for test cases
   └─> Extract pass/fail status
   └─> Extract metrics (response times, etc.)
   
   Step 5.5: Evidence Matching
   └─> For each requirement:
       └─> Find related test evidence
       └─> Check if satisfied
       └─> Mark as verified/unverified
   
   Step 5.6: Gap Analysis
   └─> Identify unverified requirements
   └─> Group by quality attribute
   └─> Calculate gap count
   
   Step 5.7: Quality Scoring
   └─> Calculate overall score
   └─> Calculate category-wise scores
   └─> Store results in database
   
   └─> Return JSON response

6. FRONTEND
   └─> Render dashboard with results
   └─> Show charts and visualizations
```

---

## Flow 2: Quality Prediction (Early Assessment)

```
1. USER ACTION
   └─> User uploads SRS + Quality Plan

2. FRONTEND
   └─> POST /api/predict

3. BACKEND: Prediction Service
   
   Step 3.1: Text Extraction
   └─> Extract from SRS
   └─> Extract from Quality Plan
   
   Step 3.2: Requirement Analysis
   └─> Classify all requirements (using AI model)
   └─> Count requirements per category
   └─> Calculate coverage score
   
   Step 3.3: Clarity Analysis
   └─> Detect ambiguous words ("fast", "user-friendly")
   └─> Check requirement measurability
   └─> Calculate clarity score
   
   Step 3.4: Testing Plan Analysis
   └─> Keyword search for test types
   └─> Check for automation mentions
   └─> Check for code review mentions
   └─> Calculate testing strength score
   
   Step 3.5: Prediction Calculation
   └─> Predicted Quality = 0.4×Clarity + 0.3×Coverage + 0.3×Testing
   └─> Determine risk level
   └─> Generate recommendations
   
   └─> Store prediction in database
   └─> Return JSON response

4. FRONTEND
   └─> Display prediction with visualizations
   └─> Show risk warnings
   └─> Display recommendations
```

---

## API Endpoints Specification

### POST /api/upload
**Description:** Upload documents

**Request:**
```
Content-Type: multipart/form-data

srs_file: [File]
quality_plan: [File] (optional)
test_report: [File] (optional)
```

**Response:**
```json
{
  "status": "success",
  "upload_id": 123,
  "files": [
    {"name": "srs.pdf", "type": "SRS", "size": 245632},
    {"name": "tests.pdf", "type": "TestReport", "size": 189234}
  ]
}
```

---

### POST /api/analyze/{upload_id}
**Description:** Analyze uploaded documents for quality assessment

**Response:**
```json
{
  "status": "success",
  "results": {
    "overall_quality_score": 78.5,
    "category_scores": {
      "Functional": 85.0,
      "Performance": 60.0,
      "Security": 45.0,
      "Usability": 90.0,
      "Reliability": 75.0,
      "Maintainability": 80.0
    },
    "total_requirements": 50,
    "satisfied_requirements": 39,
    "gaps": [
      {
        "requirement": "Password must be encrypted",
        "category": "Security",
        "status": "Not verified"
      }
    ],
    "risk_level": "Medium"
  }
}
```

---

### POST /api/predict
**Description:** Predict quality before testing phase

**Request:**
```json
{
  "upload_id": 123
}
```

**Response:**
```json
{
  "status": "success",
  "prediction": {
    "predicted_quality": 72.0,
    "clarity_score": 80.0,
    "coverage_score": 60.0,
    "testing_strength": 70.0,
    "risk_level": "Medium",
    "risks": [
      "No security requirements defined",
      "Performance criteria missing"
    ],
    "recommendations": [
      "Add security requirements (authentication, encryption)",
      "Define performance benchmarks",
      "Include unit testing plan"
    ]
  }
}
```

---

### GET /api/report/{upload_id}
**Description:** Generate quality report

**Response:** PDF or HTML report

---

# SUMMARY

## What You're Building

**QualityMapAI** is an intelligent web system that:

1. **Accepts** software documentation (SRS, quality plans, test reports)
2. **Extracts** requirements using NLP
3. **Classifies** requirements into quality attributes using AI
4. **Matches** requirements with test evidence
5. **Calculates** quality scores and identifies gaps
6. **Predicts** expected quality before testing phase
7. **Generates** actionable reports and recommendations

---

## Tech Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | React + Material-UI | User interface |
| **Backend** | Flask (Python) | REST API server |
| **AI/ML** | scikit-learn + NLTK | Requirement classification |
| **Document** | pdfplumber | PDF text extraction |
| **Database** | SQLite | Store analysis history |
| **Visualization** | Recharts | Charts and graphs |

---

## Project Timeline (12 Weeks)

| Week | Task |
|------|------|
| 1-2 | Dataset creation + AI model training |
| 3-4 | Flask backend + API development |
| 5-6 | React frontend + UI components |
| 7-8 | Integration + testing |
| 9-10 | Quality prediction feature |
| 11 | Report generation + polish |
| 12 | Documentation + demo prep |

---

## Success Criteria

✅ AI classification accuracy ≥ 80%  
✅ Process documents in < 30 seconds  
✅ Clear, professional UI  
✅ Working quality prediction  
✅ Complete gap analysis  
✅ Exportable reports  

---

**This specification gives you a crystal-clear roadmap for your semester project.**

Ready to start implementation? Let me know which module to build first! 🚀
