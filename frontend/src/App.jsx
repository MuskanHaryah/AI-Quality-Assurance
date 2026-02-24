import { lazy, Suspense } from 'react';
import { Routes, Route } from 'react-router-dom';
import { Box, Snackbar, Alert } from '@mui/material';
import Navigation from './components/Navigation/Navigation';
import Loading from './components/common/Loading';
import { useApp } from './context/AppContext';

// Lazy-load pages for code splitting
const Home = lazy(() => import('./pages/Home'));
const Upload = lazy(() => import('./pages/Upload'));
const Results = lazy(() => import('./pages/Results'));
const Dashboard = lazy(() => import('./pages/Dashboard'));

function App() {
  const { notifications, removeNotification } = useApp();

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Navigation />
      <Box component="main" sx={{ flexGrow: 1, pt: { xs: 8, sm: 9 } }}>
        <Suspense fallback={<Loading message="Loading page…" fullPage />}>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/upload" element={<Upload />} />
            <Route path="/results/:id" element={<Results />} />
            <Route path="/dashboard" element={<Dashboard />} />
          </Routes>
        </Suspense>
      </Box>

      {/* Global notification toasts */}
      {notifications.map((n) => (
        <Snackbar
          key={n.id}
          open
          autoHideDuration={5000}
          onClose={() => removeNotification(n.id)}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
        >
          <Alert
            onClose={() => removeNotification(n.id)}
            severity={n.severity}
            variant="filled"
            sx={{ width: '100%', borderRadius: 3 }}
          >
            {n.message}
          </Alert>
        </Snackbar>
      ))}
    </Box>
  );
}

export default App;
