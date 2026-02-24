# Frontend Development Roadmap
**Phase 2: React Frontend Implementation**

Status: Ready to Start | Backend: ✅ Complete (88 tests passing)

---

## PHASE 2.1: React Setup with Material-UI (Day 1-2)

### Step 1: Initialize React Project
```bash
# Choose ONE approach:

# Option A: Vite (Recommended - faster, modern)
cd AI-Quality-Assurance
npm create vite@latest frontend -- --template react
cd frontend
npm install

# Option B: Create React App (Traditional)
cd AI-Quality-Assurance
npx create-react-app frontend
cd frontend
```

### Step 2: Install Core Dependencies
```bash
# Material-UI and styling
npm install @mui/material @emotion/react @emotion/styled
npm install @mui/icons-material
npm install @mui/x-charts  # For charts

# Routing
npm install react-router-dom

# API & Utils
npm install axios
npm install date-fns  # Date formatting
```

### Step 3: Project Structure Setup
Create this folder structure:
```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── api/
│   │   └── client.js          (axios instance)
│   ├── components/
│   │   ├── common/            (shared components)
│   │   ├── FileUpload/
│   │   ├── ScoreGauge/
│   │   ├── CategoryChart/
│   │   ├── RequirementsTable/
│   │   ├── RecommendationCard/
│   │   └── Navigation/
│   ├── pages/
│   │   ├── Home.jsx
│   │   ├── Upload.jsx
│   │   ├── Results.jsx
│   │   └── Dashboard.jsx
│   ├── context/
│   │   └── AppContext.jsx     (global state)
│   ├── theme/
│   │   └── theme.js           (MUI theme config)
│   ├── utils/
│   │   └── helpers.js
│   ├── App.jsx
│   └── main.jsx
├── package.json
└── vite.config.js / package.json
```

### Step 4: Create Theme Configuration
**File: `src/theme/theme.js`**
```javascript
import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
      light: '#42a5f5',
      dark: '#1565c0',
    },
    secondary: {
      main: '#9c27b0',
    },
    success: { main: '#2e7d32' },   // Low risk
    warning: { main: '#ed6c02' },   // Medium risk
    error: { main: '#d32f2f' },     // High risk
    info: { main: '#0288d1' },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: { fontSize: '2.5rem', fontWeight: 700 },
    h2: { fontSize: '2rem', fontWeight: 600 },
    h3: { fontSize: '1.75rem', fontWeight: 600 },
    h4: { fontSize: '1.5rem', fontWeight: 500 },
    h5: { fontSize: '1.25rem', fontWeight: 500 },
    h6: { fontSize: '1rem', fontWeight: 500 },
  },
  shape: {
    borderRadius: 8,
  },
  spacing: 8,
});

export default theme;
```

### Step 5: Setup Layout Wrapper
**File: `src/App.jsx`**
```javascript
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import theme from './theme/theme';
import Navigation from './components/Navigation/Navigation';
import Home from './pages/Home';
import Upload from './pages/Upload';
import Results from './pages/Results';
import Dashboard from './pages/Dashboard';

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <BrowserRouter>
        <Navigation />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/upload" element={<Upload />} />
          <Route path="/results/:id" element={<Results />} />
          <Route path="/dashboard" element={<Dashboard />} />
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  );
}

export default App;
```

**✅ Checkpoint: Run `npm run dev` - You should see a blank app with routing**

---

## PHASE 2.2: API Integration (Day 3)

### Step 1: Create Axios Instance
**File: `src/api/client.js`**
```javascript
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized
      localStorage.removeItem('authToken');
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

### Step 2: Create API Methods
**File: `src/api/services.js`**
```javascript
import apiClient from './client';

export const uploadFile = async (file, onProgress) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await apiClient.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (progressEvent) => {
      const percentCompleted = Math.round(
        (progressEvent.loaded * 100) / progressEvent.total
      );
      if (onProgress) onProgress(percentCompleted);
    },
  });

  return response.data;
};

export const analyzeFile = async (fileId) => {
  const response = await apiClient.post('/analyze', { file_id: fileId });
  return response.data;
};

export const predictRequirement = async (text) => {
  const response = await apiClient.post('/predict', { text });
  return response.data;
};

export const getReport = async (analysisId) => {
  const response = await apiClient.get(`/report/${analysisId}`);
  return response.data;
};

export const getRecentAnalyses = async () => {
  const response = await apiClient.get('/analyses');
  return response.data;
};

export const checkHealth = async () => {
  const response = await apiClient.get('/health');
  return response.data;
};
```

**✅ Checkpoint: Test API connectivity with health check**

---

## PHASE 2.3: Pages Implementation (Day 4-6)

### Step 1: Home Page
**File: `src/pages/Home.jsx`**
```javascript
import { Box, Container, Typography, Button, Grid, Card, CardContent } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import AssessmentIcon from '@mui/icons-material/Assessment';
import SecurityIcon from '@mui/icons-material/Security';

export default function Home() {
  const navigate = useNavigate();

  const features = [
    { icon: <UploadFileIcon />, title: 'Upload Documents', desc: 'PDF & DOCX support' },
    { icon: <AssessmentIcon />, title: 'ML Analysis', desc: 'ISO/IEC 9126 classification' },
    { icon: <SecurityIcon />, title: 'Quality Scoring', desc: '7 category assessment' },
  ];

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 8 }}>
        <Typography variant="h1" align="center" gutterBottom>
          QualityMapAI
        </Typography>
        <Typography variant="h5" align="center" color="text.secondary" sx={{ mb: 4 }}>
          Automated Requirements Quality Analysis using ML
        </Typography>
        
        <Box sx={{ textAlign: 'center', mb: 6 }}>
          <Button 
            variant="contained" 
            size="large" 
            onClick={() => navigate('/upload')}
            startIcon={<UploadFileIcon />}
          >
            Get Started
          </Button>
        </Box>

        <Grid container spacing={4}>
          {features.map((feature, idx) => (
            <Grid item xs={12} md={4} key={idx}>
              <Card>
                <CardContent sx={{ textAlign: 'center', py: 4 }}>
                  <Box sx={{ fontSize: 48, color: 'primary.main', mb: 2 }}>
                    {feature.icon}
                  </Box>
                  <Typography variant="h5" gutterBottom>{feature.title}</Typography>
                  <Typography color="text.secondary">{feature.desc}</Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>
    </Container>
  );
}
```

### Step 2: Upload Page
**File: `src/pages/Upload.jsx`**
```javascript
import { useState } from 'react';
import { Container, Box, Typography, Button, Alert } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import FileUpload from '../components/FileUpload/FileUpload';
import { uploadFile, analyzeFile } from '../api/services';

export default function Upload() {
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);

  const handleFileSelect = (selectedFile) => {
    setFile(selectedFile);
    setError(null);
  };

  const handleAnalyze = async () => {
    if (!file) return;

    setError(null);
    setUploading(true);

    try {
      // Step 1: Upload
      const uploadResult = await uploadFile(file, setUploadProgress);
      const fileId = uploadResult.file_id;

      // Step 2: Analyze
      setUploading(false);
      setAnalyzing(true);
      const analysisResult = await analyzeFile(fileId);

      // Step 3: Navigate to results
      navigate(`/results/${fileId}`);
    } catch (err) {
      setError(err.response?.data?.error || 'Upload failed. Please try again.');
      setUploading(false);
      setAnalyzing(false);
    }
  };

  return (
    <Container maxWidth="md">
      <Box sx={{ py: 6 }}>
        <Typography variant="h3" gutterBottom>
          Upload Requirements Document
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
          Upload a PDF or DOCX file containing software requirements (max 10 MB)
        </Typography>

        <FileUpload 
          onFileSelect={handleFileSelect}
          uploading={uploading}
          progress={uploadProgress}
        />

        {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}

        <Box sx={{ mt: 4, textAlign: 'center' }}>
          <Button
            variant="contained"
            size="large"
            onClick={handleAnalyze}
            disabled={!file || uploading || analyzing}
          >
            {uploading ? `Uploading... ${uploadProgress}%` : 
             analyzing ? 'Analyzing...' : 
             'Analyze Document'}
          </Button>
        </Box>
      </Box>
    </Container>
  );
}
```

### Step 3: Results Page (continued in components)
### Step 4: Dashboard Page (continued in components)

**✅ Checkpoint: Basic page routing works**

---

## PHASE 2.4: Components Implementation (Day 7-9)

### Component 1: FileUpload
**File: `src/components/FileUpload/FileUpload.jsx`**
```javascript
import { useState } from 'react';
import { Box, Typography, Paper, LinearProgress } from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';

export default function FileUpload({ onFileSelect, uploading, progress }) {
  const [dragActive, setDragActive] = useState(false);
  const [file, setFile] = useState(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = (selectedFile) => {
    // Validate file type
    const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    if (!validTypes.includes(selectedFile.type)) {
      alert('Please upload a PDF or DOCX file');
      return;
    }

    // Validate file size (10 MB)
    if (selectedFile.size > 10 * 1024 * 1024) {
      alert('File size must be less than 10 MB');
      return;
    }

    setFile(selectedFile);
    onFileSelect(selectedFile);
  };

  return (
    <Paper
      sx={{
        p: 4,
        textAlign: 'center',
        border: dragActive ? '2px dashed primary.main' : '2px dashed',
        borderColor: dragActive ? 'primary.main' : 'divider',
        backgroundColor: dragActive ? 'action.hover' : 'background.paper',
        cursor: 'pointer',
      }}
      onDragEnter={handleDrag}
      onDragLeave={handleDrag}
      onDragOver={handleDrag}
      onDrop={handleDrop}
    >
      <input
        type="file"
        id="file-upload"
        accept=".pdf,.docx"
        style={{ display: 'none' }}
        onChange={handleChange}
      />
      <label htmlFor="file-upload">
        <CloudUploadIcon sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
        <Typography variant="h6" gutterBottom>
          {file ? file.name : 'Drag & drop file here'}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          or click to browse (PDF, DOCX - max 10 MB)
        </Typography>
      </label>

      {uploading && (
        <Box sx={{ mt: 2 }}>
          <LinearProgress variant="determinate" value={progress} />
          <Typography variant="body2" sx={{ mt: 1 }}>{progress}% uploaded</Typography>
        </Box>
      )}
    </Paper>
  );
}
```

### Component 2: ScoreGauge
**File: `src/components/ScoreGauge/ScoreGauge.jsx`**
```javascript
import { Box, Typography } from '@mui/material';

export default function ScoreGauge({ score, riskLevel }) {
  const getColor = (level) => {
    const colors = {
      Low: '#2e7d32',
      Medium: '#ed6c02',
      High: '#d32f2f',
      Critical: '#b71c1c',
    };
    return colors[level] || '#757575';
  };

  const color = getColor(riskLevel);
  const circumference = 2 * Math.PI * 45;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  return (
    <Box sx={{ position: 'relative', display: 'inline-flex' }}>
      <svg width="120" height="120">
        {/* Background circle */}
        <circle
          cx="60"
          cy="60"
          r="45"
          fill="none"
          stroke="#e0e0e0"
          strokeWidth="10"
        />
        {/* Progress circle */}
        <circle
          cx="60"
          cy="60"
          r="45"
          fill="none"
          stroke={color}
          strokeWidth="10"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          transform="rotate(-90 60 60)"
        />
      </svg>
      <Box
        sx={{
          position: 'absolute',
          top: 0,
          left: 0,
          bottom: 0,
          right: 0,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <Typography variant="h4" component="div" sx={{ fontWeight: 700 }}>
          {score.toFixed(1)}
        </Typography>
        <Typography variant="caption" color="text.secondary">
          {riskLevel}
        </Typography>
      </Box>
    </Box>
  );
}
```

### Component 3: CategoryChart (basic bar chart)
### Component 4: RequirementsTable (MUI DataGrid)
### Component 5: RecommendationCard (card with priority badge)
### Component 6: Navigation (AppBar with links)

**✅ Checkpoint: All components render correctly**

---

## PHASE 2.5: Styling & Responsiveness (Day 10)

- [ ] Test on mobile breakpoints (xs, sm, md, lg, xl)
- [ ] Add responsive Grid layouts to all pages
- [ ] Ensure MUI breakpoints work: `sx={{ xs: 12, md: 6 }}`
- [ ] Test dark mode toggle (useTheme, useMediaQuery)
- [ ] Check color contrast for accessibility (WCAG AA)
- [ ] Add focus states for keyboard navigation
- [ ] Test print stylesheet (for PDF exports)

---

## PHASE 2.6: State Management (Day 11)

**File: `src/context/AppContext.jsx`**
```javascript
import { createContext, useContext, useState, useEffect } from 'react';

const AppContext = createContext();

export const AppProvider = ({ children }) => {
  const [theme, setTheme] = useState('light');
  const [analyses, setAnalyses] = useState([]);
  const [notifications, setNotifications] = useState([]);

  // Load theme from localStorage
  useEffect(() => {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) setTheme(savedTheme);
  }, []);

  // Save theme to localStorage
  useEffect(() => {
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'light' ? 'dark' : 'light'));
  };

  const addNotification = (message, type = 'info') => {
    const id = Date.now();
    setNotifications((prev) => [...prev, { id, message, type }]);
    setTimeout(() => {
      setNotifications((prev) => prev.filter((n) => n.id !== id));
    }, 5000);
  };

  return (
    <AppContext.Provider value={{ 
      theme, toggleTheme, 
      analyses, setAnalyses,
      notifications, addNotification 
    }}>
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => useContext(AppContext);
```

---

## PHASE 3: INTEGRATION & TESTING

### Week 1: E2E Workflow Testing
- [ ] **Day 1-2: Upload to Report Flow**
  - [ ] Upload PDF → verify success
  - [ ] Upload DOCX → verify success
  - [ ] Analyze → wait for completion
  - [ ] View report → all sections load
  - [ ] Navigate back to dashboard

- [ ] **Day 3: Stress Testing**
  - [ ] Upload 9.9 MB file (near limit)
  - [ ] Upload multiple files sequentially
  - [ ] Test slow network (throttle to 3G)
  - [ ] Test timeout handling (30s+)

- [ ] **Day 4: Browser Compatibility**
  - [ ] Chrome (latest)
  - [ ] Firefox (latest)
  - [ ] Safari (latest)
  - [ ] Edge (latest)
  - [ ] Mobile Safari (iOS)
  - [ ] Chrome Mobile (Android)

### Week 2: Error Scenarios
- [ ] **Day 1: Upload Failures**
  - [ ] Network timeout → show retry
  - [ ] Server 500 error → show error message
  - [ ] Invalid file type → show validation error
  - [ ] File too large → show size error

- [ ] **Day 2: Analysis Failures**
  - [ ] Malformed PDF → handle extraction error
  - [ ] Empty document → show "no requirements" message
  - [ ] Corrupted DOCX → handle gracefully

- [ ] **Day 3: Backend Integration**
  - [ ] Backend offline → show connection error
  - [ ] DB connection lost → show try again later
  - [ ] ML model error → fallback message

### Week 3: Performance Testing
- [ ] **Day 1: Frontend Performance**
  - [ ] Run Lighthouse audit (target >90)
  - [ ] Check bundle size (target <500 KB)
  - [ ] Code splitting (lazy load routes)
  - [ ] Image optimization
  - [ ] Tree shaking

- [ ] **Day 2: API Performance**
  - [ ] Measure /upload response time (<2s)
  - [ ] Measure /analyze response time (<5s)
  - [ ] Measure /report response time (<1s)
  - [ ] Test concurrent uploads (5+ users)

- [ ] **Day 3: Optimization**
  - [ ] React.memo for expensive components
  - [ ] useMemo for heavy calculations
  - [ ] useCallback for event handlers
  - [ ] Debounce search/filter inputs

### Week 4: Documentation
- [ ] **Day 1: API Documentation**
  - [ ] Create OpenAPI/Swagger spec
  - [ ] Document all endpoints (request/response)
  - [ ] Add example cURL commands
  - [ ] Document error codes

- [ ] **Day 2: Component Documentation**
  - [ ] Setup Storybook
  - [ ] Document all reusable components
  - [ ] Add prop types & examples
  - [ ] Interactive component playground

- [ ] **Day 3: Deployment Guide**
  - [ ] Backend deployment steps (Docker)
  - [ ] Frontend build & deployment (Vercel/Netlify)
  - [ ] Environment variable setup
  - [ ] Domain & SSL configuration

- [ ] **Day 4: Handoff**
  - [ ] Architecture diagram
  - [ ] Known issues list
  - [ ] Future enhancement ideas
  - [ ] Contributor guidelines

---

## QUICK REFERENCE COMMANDS

### Development
```bash
# Backend
cd backend
python app.py                    # Start Flask server (port 5000)
python -m pytest tests/ -v       # Run tests

# Frontend
cd frontend
npm run dev                      # Start dev server (Vite port 5173)
npm run build                    # Production build
npm run preview                  # Preview production build
```

### Git Workflow
```bash
git add .
git commit -m "feat(frontend): Add upload page"
git push origin main
```

### Common Issues
- **CORS error**: Check Flask CORS config in backend/app.py
- **API not found**: Verify backend is running on port 5000
- **Module not found**: Run `npm install` in frontend/
- **Build fails**: Clear node_modules, reinstall dependencies

---

## ESTIMATED TIMELINE

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| 2.1 React Setup | 2 days | Working React app with routing |
| 2.2 API Integration | 1 day | All API calls working |
| 2.3 Pages | 3 days | All 4 pages functional |
| 2.4 Components | 3 days | All 6+ components complete |
| 2.5 Styling | 1 day | Responsive & accessible |
| 2.6 State | 1 day | Context & persistence working |
| **Phase 2 Total** | **11 days** | **Production-ready frontend** |
| 3.1 E2E Testing | 4 days | Full workflow verified |
| 3.2 Error Testing | 3 days | Edge cases handled |
| 3.3 Performance | 3 days | Optimized & fast |
| 3.4 Documentation | 4 days | Fully documented |
| **Phase 3 Total** | **14 days** | **Tested & documented** |
| **Grand Total** | **25 days** | **Complete application** |

---

**Next Action**: Start with Phase 2.1 Step 1 (Create React app)
