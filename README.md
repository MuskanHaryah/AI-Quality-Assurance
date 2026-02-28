<div align="center">

# 🎯 QualityMapAI

### AI-Powered Software Quality Assurance Analyzer

*Intelligent requirement analysis and quality prediction using machine learning*

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-000000.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

[Features](#-features) • [Quick Start](#-quick-start) • [Tech Stack](#-tech-stack) • [Demo](#-demo)

</div>

---

## 🚀 What is QualityMapAI?

QualityMapAI automatically analyzes Software Requirements Specifications (SRS) and predicts quality metrics using AI. Upload your documents, get instant insights on requirement coverage, quality gaps, and risk assessments—**before testing even begins**.

## ✨ Features

🤖 **AI-Powered Classification** - Automatically categorizes requirements into 7 quality attributes (ISO/IEC 9126)  
📊 **Quality Prediction** - Predict project quality before development with 80%+ accuracy  
🔍 **Gap Analysis** - Identify missing test coverage and requirement gaps instantly  
📈 **Interactive Dashboard** - Beautiful charts, gauges, and real-time analytics  
📄 **Smart Reports** - Generate professional PDF/HTML reports with actionable insights  
⚡ **Fast & Lightweight** - No GPU required, runs on standard laptops  

## 🛠️ Tech Stack

**Frontend:** React 18 • Material-UI • Recharts • Vite  
**Backend:** Flask • scikit-learn • NLTK • SQLite  
**ML Model:** Logistic Regression with TF-IDF vectorization  

## 📦 Quick Start

### Prerequisites
- Python 3.8+ and Node.js 16+

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/QualityMapAI.git
cd QualityMapAI

# Backend setup
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
python app.py

# Frontend setup (new terminal)
cd frontend
npm install
npm run dev
```

Visit **http://localhost:3000** 🎉

## 📸 Demo

```
📂 Upload SRS Document → 🤖 AI Analysis → 📊 Quality Score: 78.5%

✅ 85% Functional Requirements Met
⚠️  45% Security Coverage (Action Needed!)
✅ 90% Usability Score
```

## 🎯 Use Cases

- **QA Teams**: Verify requirement coverage and test completeness
- **Project Managers**: Early quality prediction for better planning
- **Developers**: Identify quality gaps before coding starts

## 📁 Project Structure

```
├── backend/          # Flask API + ML models
├── frontend/         # React dashboard
├── ml-training/      # Model training scripts
└── README.md
```

## 🤝 Contributing

Contributions welcome! This is an academic project open for educational improvements.

## 📄 License

MIT License - Free for educational and commercial use

---

<div align="center">

**Built with ❤️ by Muskan Haryah and Team**

⭐ Star this repo if it helps your project!

</div>
