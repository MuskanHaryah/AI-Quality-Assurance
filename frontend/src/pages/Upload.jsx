import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Box,
  Typography,
  Button,
  Stack,
  Stepper,
  Step,
  StepLabel,
} from '@mui/material';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import AnalyticsIcon from '@mui/icons-material/Analytics';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import FileUpload from '../components/FileUpload/FileUpload';
import Loading from '../components/common/Loading';
import ErrorDisplay from '../components/common/ErrorDisplay';
import { GlassCard } from '../components/common/GlassCard';
import { uploadFile, analyzeFile } from '../api/services';
import { useApp } from '../context/AppContext';
import { PURPLE } from '../theme/theme';

const steps = ['Select File', 'Upload & Analyze', 'View Results'];

export default function Upload() {
  const navigate = useNavigate();
  const { addNotification } = useApp();

  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState(null);
  const [activeStep, setActiveStep] = useState(0);

  const handleFileSelect = (selectedFile) => {
    setFile(selectedFile);
    setError(null);
    setActiveStep(0);
  };

  const handleAnalyze = async () => {
    if (!file) return;
    setError(null);

    try {
      // Step 1: Upload
      setUploading(true);
      setActiveStep(1);
      const uploadResult = await uploadFile(file, setUploadProgress);
      const fileId = uploadResult.file_id;
      setUploading(false);

      // Step 2: Analyze
      setAnalyzing(true);
      await analyzeFile(fileId);
      setAnalyzing(false);

      // Step 3: Navigate
      setActiveStep(2);
      addNotification('Analysis complete!', 'success');

      // Small delay so user sees the success state
      setTimeout(() => {
        navigate(`/results/${fileId}`);
      }, 600);
    } catch (err) {
      let message = err.friendlyMessage || err.message || 'Something went wrong.';
      // Make connection errors more user-friendly
      if (err.code === 'ECONNREFUSED' || err.code === 'ERR_NETWORK' || message.includes('Network Error')) {
        message = 'Cannot connect to the backend server. Please make sure the server is running (python app.py).';
      } else if (message.includes('status code 500')) {
        message = 'Server error. Please restart the backend server and try again.';
      }
      setError(message);
      setUploading(false);
      setAnalyzing(false);
      setActiveStep(0);
      addNotification(message, 'error');
    }
  };

  return (
    <Container maxWidth="md">
      <Box sx={{ py: { xs: 4, md: 6 } }}>
        <Typography variant="h3" fontWeight={800} gutterBottom>
          Upload Document
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 4, maxWidth: 520 }}>
          Upload a PDF or DOCX containing software requirements. Our ML model will
          classify each requirement and score the overall quality.
        </Typography>

        {/* Stepper */}
        <GlassCard sx={{ mb: 4 }}>
          <Stepper
            activeStep={activeStep}
            alternativeLabel
            sx={{
              '& .MuiStepIcon-root.Mui-active': { color: PURPLE },
              '& .MuiStepIcon-root.Mui-completed': { color: PURPLE },
            }}
          >
            {steps.map((label) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
              </Step>
            ))}
          </Stepper>
        </GlassCard>

        {/* Upload Area */}
        {!analyzing && (
          <FileUpload
            onFileSelect={handleFileSelect}
            uploading={uploading}
            progress={uploadProgress}
          />
        )}

        {/* Analyzing spinner */}
        {analyzing && (
          <GlassCard sx={{ py: 6 }}>
            <Loading message="Analyzing your requirements…" />
          </GlassCard>
        )}

        {/* Error */}
        {error && (
          <Box sx={{ mt: 3 }}>
            <ErrorDisplay message={error} onRetry={() => setError(null)} />
          </Box>
        )}

        {/* Action Button */}
        {!analyzing && (
          <Stack alignItems="center" sx={{ mt: 4 }}>
            <Button
              variant="contained"
              size="large"
              onClick={handleAnalyze}
              disabled={!file || uploading || analyzing}
              startIcon={
                uploading ? null : analyzing ? null : <AnalyticsIcon />
              }
              sx={{ px: 5, py: 1.5 }}
            >
              {uploading
                ? `Uploading… ${uploadProgress}%`
                : 'Analyze Document'}
            </Button>
          </Stack>
        )}
      </Box>
    </Container>
  );
}
