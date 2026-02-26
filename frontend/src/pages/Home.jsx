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
  Divider,
  alpha,
} from '@mui/material';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import AutoGraphIcon from '@mui/icons-material/AutoGraph';
import SecurityIcon from '@mui/icons-material/Security';
import CategoryIcon from '@mui/icons-material/Category';
import VerifiedIcon from '@mui/icons-material/Verified';
import DashboardIcon from '@mui/icons-material/Dashboard';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import LanguageIcon from '@mui/icons-material/Language';
import FactCheckIcon from '@mui/icons-material/FactCheck';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import GppGoodIcon from '@mui/icons-material/GppGood';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import { GlassCard } from '../components/common/GlassCard';
import { PURPLE, TEAL, PINK } from '../theme/theme';
import { checkHealth } from '../api/services';

const features = [
  {
    icon: <UploadFileIcon sx={{ fontSize: 36 }} />,
    title: 'Smart Document Upload',
    description: 'Upload PDF or DOCX files. AI verifies the document is actually an SRS — warns you immediately if you upload the wrong file type.',
    color: PURPLE,
    badge: 'AI-Powered',
  },
  {
    icon: <AutoGraphIcon sx={{ fontSize: 36 }} />,
    title: 'ML Requirement Classification',
    description: 'Requirements auto-extracted and classified into 7 ISO/IEC 9126 quality categories using a trained TF-IDF + SVM model with 84.4% accuracy.',
    color: TEAL,
    badge: 'ML Model',
  },
  {
    icon: <LanguageIcon sx={{ fontSize: 36 }} />,
    title: 'AI Domain Detection',
    description: 'Gemini AI identifies your system domain across 15+ domains (Banking, Healthcare, Zoo/Wildlife, E-commerce, etc.) with confidence score and reasoning.',
    color: '#8b5cf6',
    badge: 'Gemini AI',
  },
  {
    icon: <SecurityIcon sx={{ fontSize: 36 }} />,
    title: 'Domain-Critical Analysis',
    description: 'Highlights critical quality factors for your specific domain. A Banking SRS flags Security; a Library SRS flags Usability — tailored to your project.',
    color: '#ef4444',
    badge: null,
  },
  {
    icon: <FactCheckIcon sx={{ fontSize: 36 }} />,
    title: 'Quality Plan Comparison',
    description: 'Upload your Quality Plan and compare it against your SRS. Get category coverage scores, achievable quality %, and plan strength rating.',
    color: '#10b981',
    badge: 'AI-Enhanced',
  },
  {
    icon: <CategoryIcon sx={{ fontSize: 36 }} />,
    title: 'Gap Analysis',
    description: 'Identify missing or under-represented quality categories. See exactly which ISO/IEC 9126 areas need more requirements coverage.',
    color: '#f59e0b',
    badge: null,
  },
  {
    icon: <VerifiedIcon sx={{ fontSize: 36 }} />,
    title: 'AI Recommendations',
    description: 'Gemini AI generates actionable, domain-specific suggestions. Critical categories with too few requirements trigger high-priority alerts.',
    color: PINK,
    badge: 'Gemini AI',
  },
  {
    icon: <WarningAmberIcon sx={{ fontSize: 36 }} />,
    title: 'Wrong Document Detection',
    description: 'AI detects if you upload a User Manual, Design Document, Resume, or any non-SRS/non-QP file and clearly explains what the document actually is.',
    color: '#f97316',
    badge: 'AI-Powered',
  },
  {
    icon: <GppGoodIcon sx={{ fontSize: 36 }} />,
    title: 'Requirements Dashboard',
    description: 'View all past analyses, track improvements over time, explore per-requirement confidence scores, and monitor your SRS quality history.',
    color: '#06b6d4',
    badge: null,
  },
];

const workflow = [
  {
    step: '01',
    title: 'Upload Your SRS',
    description: 'Upload a PDF or DOCX Software Requirements Specification. AI validates it is the right document type.',
    color: PURPLE,
  },
  {
    step: '02',
    title: 'Get SRS Analysis',
    description: 'ML model classifies all requirements. AI detects your domain and highlights critical categories for your project type.',
    color: TEAL,
  },
  {
    step: '03',
    title: 'Upload Quality Plan',
    description: 'Upload your Quality Plan document. AI validates it and compares it category-by-category against your SRS.',
    color: '#10b981',
  },
  {
    step: '04',
    title: 'Review Results',
    description: 'Get coverage scores, achievable quality %, AI recommendations, and gap analysis to improve your documentation.',
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
          sx={{ maxWidth: 640, mx: 'auto', mb: 2, fontWeight: 400, lineHeight: 1.6 }}
        >
          AI-powered SRS quality analysis and Quality Plan comparison — built on machine learning, ISO/IEC 9126, and Google Gemini
        </Typography>

        {/* AI badge row */}
        <Stack direction="row" spacing={1} justifyContent="center" flexWrap="wrap" sx={{ mb: 4, gap: 1 }}>
          <Chip
            icon={<AutoAwesomeIcon sx={{ fontSize: '14px !important' }} />}
            label="Gemini AI"
            size="small"
            sx={{ bgcolor: alpha('#8b5cf6', 0.12), color: '#8b5cf6', fontWeight: 600 }}
          />
          <Chip label="TF-IDF + SVM" size="small" variant="outlined" sx={{ fontSize: '0.75rem' }} />
          <Chip label="ISO/IEC 9126" size="small" variant="outlined" sx={{ fontSize: '0.75rem' }} />
          <Chip label="15+ Domains" size="small" variant="outlined" sx={{ fontSize: '0.75rem' }} />
          <Chip label="PDF & DOCX" size="small" variant="outlined" sx={{ fontSize: '0.75rem' }} />
        </Stack>

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

      {/* How It Works */}
      <Box sx={{ pb: 6 }}>
        <Typography variant="h4" fontWeight={700} textAlign="center" sx={{ mb: 1 }}>
          How It Works
        </Typography>
        <Typography variant="body1" color="text.secondary" textAlign="center" sx={{ mb: 4 }}>
          A two-document workflow to fully assess your software requirements quality
        </Typography>
        <Grid container spacing={2} alignItems="stretch">
          {workflow.map((step, idx) => (
            <Grid size={{ xs: 12, sm: 6, md: 3 }} key={idx}>
              <GlassCard sx={{ height: '100%', position: 'relative', overflow: 'visible' }}>
                {/* Step number */}
                <Box
                  sx={{
                    width: 40, height: 40,
                    borderRadius: '50%',
                    background: `linear-gradient(135deg, ${step.color}, ${alpha(step.color, 0.6)})`,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    mb: 2,
                  }}
                >
                  <Typography variant="caption" fontWeight={800} sx={{ color: '#fff', fontSize: '0.8rem' }}>
                    {step.step}
                  </Typography>
                </Box>
                <Typography variant="subtitle1" fontWeight={700} sx={{ mb: 0.5 }}>
                  {step.title}
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.6 }}>
                  {step.description}
                </Typography>
                {/* Arrow connector (not on last item) */}
                {idx < workflow.length - 1 && (
                  <Box sx={{
                    display: { xs: 'none', md: 'flex' },
                    position: 'absolute', right: -16, top: '50%',
                    transform: 'translateY(-50%)', zIndex: 10,
                    bgcolor: 'background.paper', borderRadius: '50%',
                    boxShadow: 1, p: 0.3,
                  }}>
                    <ArrowForwardIcon sx={{ fontSize: 16, color: 'text.disabled' }} />
                  </Box>
                )}
              </GlassCard>
            </Grid>
          ))}
        </Grid>
      </Box>

      <Divider sx={{ mb: 6, opacity: 0.4 }} />

      {/* Features Grid */}
      <Box sx={{ pb: 10 }}>
        <Typography variant="h4" fontWeight={700} textAlign="center" sx={{ mb: 1 }}>
          Features
        </Typography>
        <Typography variant="body1" color="text.secondary" textAlign="center" sx={{ mb: 4 }}>
          Everything you need to evaluate and improve software requirements quality
        </Typography>
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
                <Stack direction="row" justifyContent="space-between" alignItems="flex-start" sx={{ width: '100%', mb: 2 }}>
                  <Box
                    sx={{
                      p: 1.5,
                      borderRadius: 3,
                      background: alpha(feature.color, 0.1),
                      color: feature.color,
                      display: 'flex',
                    }}
                  >
                    {feature.icon}
                  </Box>
                  {feature.badge && (
                    <Chip
                      icon={feature.badge.includes('Gemini') || feature.badge.includes('AI') ? <AutoAwesomeIcon sx={{ fontSize: '12px !important' }} /> : undefined}
                      label={feature.badge}
                      size="small"
                      sx={{
                        height: 22,
                        fontSize: '0.65rem',
                        fontWeight: 600,
                        bgcolor: alpha(feature.color, 0.1),
                        color: feature.color,
                      }}
                    />
                  )}
                </Stack>
                <Typography variant="h6" fontWeight={700} sx={{ mb: 1 }}>
                  {feature.title}
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.7 }}>
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
