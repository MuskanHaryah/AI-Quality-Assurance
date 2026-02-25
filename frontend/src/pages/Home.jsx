import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Box,
  Typography,
  Button,
  Grid,
  Stack,
  Chip,
  alpha,
} from '@mui/material';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import AutoGraphIcon from '@mui/icons-material/AutoGraph';
import SecurityIcon from '@mui/icons-material/Security';
import SpeedIcon from '@mui/icons-material/Speed';
import CategoryIcon from '@mui/icons-material/Category';
import VerifiedIcon from '@mui/icons-material/Verified';
import DashboardIcon from '@mui/icons-material/Dashboard';
import { GlassCard } from '../components/common/GlassCard';
import { PURPLE, TEAL, PINK } from '../theme/theme';
import { checkHealth } from '../api/services';

const features = [
  {
    icon: <UploadFileIcon sx={{ fontSize: 36 }} />,
    title: 'Upload Documents',
    description: 'Drag & drop PDF or DOCX files with your software requirements.',
    color: PURPLE,
  },
  {
    icon: <AutoGraphIcon sx={{ fontSize: 36 }} />,
    title: 'ML Classification',
    description: 'Requirements auto-classified into 7 ISO/IEC 9126 quality categories.',
    color: TEAL,
  },
  {
    icon: <SpeedIcon sx={{ fontSize: 36 }} />,
    title: 'Quality Scoring',
    description: 'Overall quality score with risk assessment and gap analysis.',
    color: '#10b981',
  },
  {
    icon: <SecurityIcon sx={{ fontSize: 36 }} />,
    title: 'Security Analysis',
    description: 'Identify missing security, reliability, and portability requirements.',
    color: '#ef4444',
  },
  {
    icon: <CategoryIcon sx={{ fontSize: 36 }} />,
    title: 'Category Coverage',
    description: 'See which quality areas are strong and where gaps exist.',
    color: '#f59e0b',
  },
  {
    icon: <VerifiedIcon sx={{ fontSize: 36 }} />,
    title: 'Actionable Insights',
    description: 'Get recommendations to improve your requirements document.',
    color: PINK,
  },
];

export default function Home() {
  const navigate = useNavigate();
  const [modelInfo, setModelInfo] = useState(null);

  useEffect(() => {
    checkHealth()
      .then((data) => setModelInfo(data))
      .catch(() => {});
  }, []);

  return (
    <Container maxWidth="lg">
      {/* Hero */}
      <Box sx={{ pt: { xs: 6, md: 10 }, pb: { xs: 4, md: 6 }, textAlign: 'center' }}>
        <Box
          sx={{
            display: 'inline-flex',
            p: 2,
            borderRadius: '50%',
            background: `linear-gradient(135deg, ${alpha(PURPLE, 0.12)}, ${alpha(TEAL, 0.12)})`,
            mb: 3,
          }}
        >
          <AutoGraphIcon sx={{ fontSize: 48, color: PURPLE }} />
        </Box>

        <Typography
          variant="h1"
          sx={{
            background: `linear-gradient(135deg, ${PURPLE}, ${TEAL})`,
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            mb: 2,
          }}
        >
          QualityMapAI
        </Typography>

        <Typography
          variant="h5"
          color="text.secondary"
          sx={{
            maxWidth: 600,
            mx: 'auto',
            mb: 4,
            fontWeight: 400,
            lineHeight: 1.6,
          }}
        >
          Automated requirements quality analysis powered by machine learning and ISO/IEC 9126
        </Typography>

        <Stack
          direction={{ xs: 'column', sm: 'row' }}
          spacing={2}
          justifyContent="center"
          sx={{ mb: 2 }}
        >
          <Button
            variant="contained"
            size="large"
            startIcon={<UploadFileIcon />}
            onClick={() => navigate('/upload')}
            sx={{ px: 4, py: 1.5 }}
          >
            Analyze Document
          </Button>
          <Button
            variant="outlined"
            size="large"
            startIcon={<DashboardIcon />}
            onClick={() => navigate('/dashboard')}
            sx={{ px: 4, py: 1.5 }}
          >
            View Dashboard
          </Button>
        </Stack>

        {modelInfo && (
          <Stack direction="row" spacing={1} justifyContent="center" sx={{ mt: 2 }}>
            <Chip
              label={`Model: ${modelInfo.model}`}
              size="small"
              variant="outlined"
              sx={{ fontSize: '0.75rem' }}
            />
            <Chip
              label={`Accuracy: ${(modelInfo.accuracy * 100).toFixed(1)}%`}
              size="small"
              color="success"
              variant="outlined"
              sx={{ fontSize: '0.75rem' }}
            />
          </Stack>
        )}
      </Box>

      {/* Features Grid */}
      <Box sx={{ pb: 10 }}>
        <Grid container spacing={3}>
          {features.map((feature, idx) => (
            <Grid size={{ xs: 12, sm: 6, md: 4 }} key={idx}>
              <GlassCard
                sx={{
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'flex-start',
                  cursor: 'default',
                }}
              >
                <Box
                  sx={{
                    p: 1.5,
                    borderRadius: 3,
                    background: alpha(feature.color, 0.1),
                    color: feature.color,
                    mb: 2,
                    display: 'flex',
                  }}
                >
                  {feature.icon}
                </Box>
                <Typography variant="h6" fontWeight={700} sx={{ mb: 1 }}>
                  {feature.title}
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.6 }}>
                  {feature.description}
                </Typography>
              </GlassCard>
            </Grid>
          ))}
        </Grid>
      </Box>
    </Container>
  );
}
