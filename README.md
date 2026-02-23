# QualityMapAI
## AI-Driven Software Quality Assurance Analyzer

**An intelligent system that evaluates software quality by analyzing project documents using artificial intelligence.**

---

## 🎯 Project Overview

QualityMapAI is a web-based system that:
- Analyzes Software Requirements Specification (SRS) documents
- Extracts and classifies requirements using AI
- Maps requirements to quality metrics (Performance, Security, Usability, etc.)
- Verifies if test reports provide evidence for requirements
- **Predicts expected quality before testing phase**
- Generates comprehensive quality assessment reports

---

## ✨ Key Features

### 1. **Intelligent Requirement Classification**
- AI-powered text classification using machine learning
- Categorizes requirements into 7 quality attributes
- 80%+ accuracy with confidence scores

### 2. **Evidence-Based Quality Assessment**
- Matches requirements with test evidence
- Identifies gaps and missing verifications
- Calculates weighted quality scores

### 3. **Early Quality Prediction** ⭐
- Predicts final quality before testing begins
- Analyzes requirement clarity and coverage
- Provides risk warnings and recommendations

### 4. **Visual Dashboard**
- Interactive charts and gauges
- Category-wise breakdown
- Gap analysis with prioritization

### 5. **Automated Reports**
- PDF/HTML export
- Executive summaries
- Actionable recommendations

---

## 🛠️ Tech Stack

### Frontend
- **React 18+** - Modern UI library
- **Material-UI (MUI)** - Professional components
- **Recharts** - Data visualization
- **Axios** - API communication

### Backend
- **Flask** - Lightweight Python web framework
- **scikit-learn** - Machine learning
- **NLTK** - Natural language processing
- **pdfplumber** - PDF text extraction

### Database
- **SQLite** - Lightweight database for analysis history

---

## 📋 System Requirements

### Software
- Python 3.8+
- Node.js 16+
- npm or yarn

### Hardware
- 4GB RAM minimum
- 1GB free disk space
- Standard laptop (no GPU needed)

---

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/QualityMapAI.git
cd QualityMapAI
```

### 2. Setup Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

### 3. Setup Frontend
```bash
cd frontend
npm install
npm start
```

### 4. Access Application
Open browser: `http://localhost:3000`

---

## 📁 Project Structure

```
AI-Quality-Assurance/
│
├── backend/
│   ├── app.py                    # Flask entry point
│   ├── routes/                   # API endpoints
│   ├── services/                 # Business logic
│   ├── models/                   # ML models (.pkl files)
│   ├── utils/                    # Helper functions
│   └── requirements.txt          # Python dependencies
│
├── frontend/
│   ├── src/
│   │   ├── components/           # React components
│   │   ├── services/             # API calls
│   │   └── App.jsx               # Main app
│   ├── package.json
│   └── public/
│
├── dataset/
│   └── requirements.csv          # Training data
│
├── docs/
│   ├── PROJECT_SPECIFICATION.md  # Complete specs
│   ├── API_DOCUMENTATION.md      # API reference
│   └── USER_GUIDE.md             # How to use
│
└── README.md
```

---

## 📖 Documentation

- [Complete Project Specification](./PROJECT_SPECIFICATION.md) - Full technical details
- [API Documentation](./docs/API_DOCUMENTATION.md) - Endpoint reference
- [User Guide](./docs/USER_GUIDE.md) - How to use the system
- [Training Guide](./docs/TRAINING_GUIDE.md) - Train your own model

---

## 🎓 Academic Context

**Project Type:** Semester Project  
**Domain:** Software Engineering + Artificial Intelligence  
**Difficulty:** Medium  
**Team Size:** 2-4 students  
**Duration:** 12-14 weeks  

---

## 🔬 AI/ML Details

### Model Type
- **Algorithm:** Logistic Regression (primary)
- **Feature Engineering:** TF-IDF vectorization
- **Training Data:** 500-1000 labeled requirements
- **Accuracy Target:** 80%+

### Quality Attributes Classified (ISO/IEC 9126)
1. Functionality
2. Security (elevated from sub-characteristic)
3. Reliability
4. Usability
5. Efficiency
6. Maintainability
7. Portability

---

## 📊 Sample Output

```
QUALITY ASSESSMENT REPORT
=========================

Overall Quality Score: 78.5%

Category Breakdown:
  Functional:      85% ████████▌
  Performance:     60% ██████
  Security:        45% ████▌
  Usability:       90% █████████
  Reliability:     75% ███████▌
  Maintainability: 80% ████████

Gaps Identified: 11
  - 5 Security requirements not verified
  - 3 Performance tests missing
  - 3 Reliability requirements incomplete

Risk Level: MEDIUM

Recommendations:
  1. Add security testing (authentication, encryption)
  2. Define performance benchmarks
  3. Include error handling tests
```

---

## 🎯 Use Cases

### Use Case 1: Quality Assurance Team
Upload SRS and test reports to verify if all requirements are tested.

### Use Case 2: Project Manager
Predict quality early in project lifecycle to plan resources.

### Use Case 3: Development Team
Identify missing quality attributes before development starts.

---

## 🔮 Future Enhancements

- [ ] Support for more document formats (Excel, JSON)
- [ ] Integration with JIRA/GitHub for automatic report generation
- [ ] Deep learning models for better accuracy
- [ ] Multi-language support (non-English requirements)
- [ ] Real-time collaboration features
- [ ] Historical trend analysis

---

## 🤝 Contributing

This is an academic project. Contributions for educational purposes are welcome!

---

## 📄 License

MIT License - Free for educational use

---

## 👥 Team

**Project by:** Muskan Haryah and Team  
**Institution:** [Your University Name]  
**Semester:** [Current Semester]  
**Year:** 2026  

---

## 📞 Contact

For questions or collaboration:
- Email: [your.email@example.com]
- GitHub: [@MuskanHaryah](https://github.com/MuskanHaryah)

---

## 🙏 Acknowledgments

- scikit-learn community for ML tools
- React and Flask communities
- Open-source SRS datasets
- Academic supervisor: [Professor Name]

---

**⭐ Star this repo if it helps your project!**

**📖 Read [PROJECT_SPECIFICATION.md](./PROJECT_SPECIFICATION.md) for complete technical details.**
