import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Box,
  Typography,
  Grid,
  Stack,
  Chip,
  Button,
  Divider,
  alpha,
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import DescriptionIcon from '@mui/icons-material/Description';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';
import FactCheckIcon from '@mui/icons-material/FactCheck';
import { GlassCard, SectionHeader } from '../components/common/GlassCard';
import Loading from '../components/common/Loading';
import ErrorDisplay from '../components/common/ErrorDisplay';
import ScoreGauge from '../components/ScoreGauge/ScoreGauge';
import CategoryChart from '../components/CategoryChart/CategoryChart';
import RequirementsTable from '../components/RequirementsTable/RequirementsTable';
import RecommendationCard, { GapAnalysisCard } from '../components/RecommendationCard/RecommendationCard';
import QualityPlanUpload from '../components/QualityPlanUpload/QualityPlanUpload';
import QualityPlanReport from '../components/QualityPlanReport/QualityPlanReport';
import { getReport, uploadQualityPlan, getQualityPlan } from '../api/services';
import { formatDate, riskColor, categoryColors } from '../utils/helpers';
import { PURPLE, TEAL } from '../theme/theme';

export default function Results() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Quality Plan state
  const [showQPUpload, setShowQPUpload] = useState(false);
  const [qpUploading, setQpUploading] = useState(false);
  const [qpProgress, setQpProgress] = useState(0);
  const [qpResult, setQpResult] = useState(null);
  const [qpError, setQpError] = useState(null);

  useEffect(() => {
    const fetchReport = () => {
      setLoading(true);
      setError(null);
      getReport(id)
        .then((data) => {
          setReport(data);
          // Also check if a quality plan already exists
          getQualityPlan(id)
            .then((qp) => {
              if (qp?.has_plan) setQpResult(qp);
            })
            .catch(() => { /* no plan yet — that's fine */ });
        })
        .catch((err) => setError(err.friendlyMessage || 'Failed to load report.'))
        .finally(() => setLoading(false));
    };
    fetchReport();
  }, [id]);

  const handleRetry = () => {
    setLoading(true);
    setError(null);
    getReport(id)
      .then((data) => setReport(data))
      .catch((err) => setError(err.friendlyMessage || 'Failed to load report.'))
      .finally(() => setLoading(false));
  };

  const handleQPUpload = async (file) => {
    setQpError(null);
    setQpUploading(true);
    setQpProgress(0);
    try {
      const result = await uploadQualityPlan(id, file, setQpProgress);
      setQpResult(result);
      setShowQPUpload(false);
    } catch (err) {
      setQpError(err.friendlyMessage || 'Failed to analyze quality plan.');
    } finally {
      setQpUploading(false);
    }
  };

  if (loading) return <Loading message="Loading analysis report…" fullPage />;
  if (error) return <Container maxWidth="md" sx={{ py: 8 }}><ErrorDisplay message={error} onRetry={handleRetry} fullPage /></Container>;
  if (!report) return null;

  const { summary, category_scores, requirements, recommendations, gap_analysis, categories_present, categories_missing } = report;

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: { xs: 3, md: 5 } }}>
        {/* Header */}
        <Stack direction="row" alignItems="center" spacing={2} sx={{ mb: 4 }}>
          <Button
            startIcon={<ArrowBackIcon />}
            onClick={() => navigate(-1)}
            sx={{ color: 'text.secondary' }}
          >
            Back
          </Button>
          <Divider orientation="vertical" flexItem />
          <Stack>
            <Typography variant="h4" fontWeight={800}>
              Analysis Report
            </Typography>
            <Stack direction="row" spacing={1} alignItems="center" sx={{ mt: 0.5 }}>
              <DescriptionIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
              <Typography variant="body2" color="text.secondary">
                {summary?.filename} • {formatDate(summary?.created_at)}
              </Typography>
            </Stack>
          </Stack>
        </Stack>

        {/* Top Row: Score + Overview */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          {/* Score Card */}
          <Grid size={{ xs: 12, md: 4 }}>
            <GlassCard sx={{ textAlign: 'center', py: 4 }}>
              <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 2 }}>
                Overall Quality Score
              </Typography>
              <ScoreGauge
                score={summary?.overall_score ?? 0}
                riskLevel={summary?.risk?.level ?? 'Low'}
              />
            </GlassCard>
          </Grid>

          {/* Quick Stats */}
          <Grid size={{ xs: 12, md: 8 }}>
            <GlassCard sx={{ height: '100%' }}>
              <Typography variant="h6" fontWeight={700} sx={{ mb: 2 }}>
                Summary
              </Typography>
              <Grid container spacing={2}>
                <Grid size={{ xs: 6, sm: 3 }}>
                  <StatItem
                    label="Requirements"
                    value={summary?.total_requirements ?? 0}
                  />
                </Grid>
                <Grid size={{ xs: 6, sm: 3 }}>
                  <StatItem
                    label="Risk Level"
                    value={summary?.risk?.level ?? '—'}
                    chipColor={riskColor(summary?.risk?.level)}
                  />
                </Grid>
                <Grid size={{ xs: 6, sm: 3 }}>
                  <StatItem
                    label="Categories Found"
                    value={categories_present?.length ?? 0}
                    total={7}
                  />
                </Grid>
                <Grid size={{ xs: 6, sm: 3 }}>
                  <StatItem
                    label="Missing"
                    value={categories_missing?.length ?? 0}
                  />
                </Grid>
              </Grid>

              {/* Category tags */}
              <Divider sx={{ my: 2 }} />
              <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>
                Categories Present
              </Typography>
              <Stack direction="row" flexWrap="wrap" gap={1}>
                {categories_present?.map((cat) => (
                  <Chip
                    key={cat}
                    icon={<CheckCircleIcon />}
                    label={cat}
                    size="small"
                    sx={{
                      backgroundColor: alpha(categoryColors[cat] || '#64748b', 0.1),
                      color: categoryColors[cat] || '#64748b',
                      fontWeight: 600,
                      '& .MuiChip-icon': { color: categoryColors[cat] || '#64748b', fontSize: 16 },
                    }}
                  />
                ))}
                {categories_missing?.map((cat) => (
                  <Chip
                    key={cat}
                    icon={<CancelIcon />}
                    label={cat}
                    size="small"
                    variant="outlined"
                    sx={{
                      borderColor: alpha('#ef4444', 0.3),
                      color: '#ef4444',
                      fontWeight: 500,
                      '& .MuiChip-icon': { color: '#ef4444', fontSize: 16 },
                    }}
                  />
                ))}
              </Stack>
            </GlassCard>
          </Grid>
        </Grid>

        {/* Category Scores */}
        <GlassCard sx={{ mb: 4 }}>
          <SectionHeader
            title="Category Scores"
            subtitle="Quality distribution across ISO/IEC 9126 categories"
          />
          <CategoryChart categoryScores={category_scores} />
        </GlassCard>

        {/* Requirements Table */}
        <GlassCard sx={{ mb: 4 }}>
          <SectionHeader
            title="Requirements"
            subtitle={`${requirements?.length ?? 0} requirements extracted and classified`}
          />
          <RequirementsTable requirements={requirements ?? []} />
        </GlassCard>

        {/* Recommendations */}
        {recommendations?.length > 0 && (
          <Box sx={{ mb: 4 }}>
            <SectionHeader
              title="Recommendations"
              subtitle="Actionable suggestions to improve your requirements"
            />
            <Stack spacing={2}>
              {recommendations.map((rec, idx) => (
                <RecommendationCard key={idx} recommendation={rec} />
              ))}
            </Stack>
          </Box>
        )}

        {/* Gap Analysis */}
        {gap_analysis?.length > 0 && (
          <Box sx={{ mb: 4 }}>
            <SectionHeader
              title="Gap Analysis"
              subtitle="Coverage gaps detected in your requirements"
            />
            <Grid container spacing={2}>
              {gap_analysis.map((gap, idx) => (
                <Grid size={{ xs: 12, sm: 6 }} key={idx}>
                  <GapAnalysisCard gap={gap} />
                </Grid>
              ))}
            </Grid>
          </Box>
        )}

        <Divider sx={{ my: 5 }} />

        {/* ── Quality Plan Section ─────────────────────────────────── */}
        {qpResult ? (
          /* Show quality plan results if we have them */
          <Box sx={{ mb: 4 }}>
            <QualityPlanReport planData={qpResult} />
          </Box>
        ) : (
          /* Ask user if they want to check their quality plan */
          <Box sx={{ mb: 4 }}>
            {!showQPUpload ? (
              <GlassCard
                sx={{
                  textAlign: 'center',
                  py: 5,
                  background: 'linear-gradient(135deg, rgba(6,182,212,0.04), rgba(124,58,237,0.04))',
                  border: `1px dashed rgba(124,58,237,0.3)`,
                }}
              >
                <FactCheckIcon sx={{ fontSize: 48, color: TEAL, mb: 2 }} />
                <Typography variant="h5" fontWeight={700} sx={{ mb: 1 }}>
                  Want to check your Quality Plan?
                </Typography>
                <Typography variant="body1" color="text.secondary" sx={{ mb: 3, maxWidth: 500, mx: 'auto' }}>
                  Upload your Quality Plan document and we&apos;ll analyze how well it covers
                  the {summary?.total_requirements ?? 0} quality factors identified above.
                  You&apos;ll see coverage scores, achievable quality, and improvement suggestions.
                </Typography>
                <Button
                  variant="contained"
                  size="large"
                  startIcon={<FactCheckIcon />}
                  onClick={() => setShowQPUpload(true)}
                  sx={{
                    px: 4,
                    py: 1.5,
                    background: `linear-gradient(135deg, ${TEAL}, ${PURPLE})`,
                    '&:hover': { background: `linear-gradient(135deg, ${PURPLE}, ${TEAL})` },
                  }}
                >
                  Yes, Check My Quality Plan
                </Button>
              </GlassCard>
            ) : (
              <Box>
                <QualityPlanUpload
                  onUpload={handleQPUpload}
                  uploading={qpUploading}
                  progress={qpProgress}
                />
                {qpError && (
                  <Box sx={{ mt: 2 }}>
                    <ErrorDisplay message={qpError} onRetry={() => setQpError(null)} />
                  </Box>
                )}
              </Box>
            )}
          </Box>
        )}

        {/* Footer actions */}
        <Stack direction="row" spacing={2} justifyContent="center" sx={{ py: 4 }}>
          <Button
            variant="contained"
            startIcon={<UploadFileIcon />}
            onClick={() => navigate('/upload')}
          >
            Analyze Another Document
          </Button>
          <Button
            variant="outlined"
            onClick={() => navigate('/dashboard')}
          >
            View Dashboard
          </Button>
        </Stack>
      </Box>
    </Container>
  );
}

/** Small stat display card */
function StatItem({ label, value, chipColor, total }) {
  return (
    <Box sx={{ textAlign: 'center' }}>
      {chipColor ? (
        <Chip
          label={value}
          color={chipColor}
          sx={{ fontWeight: 700, fontSize: '1rem', mb: 0.5 }}
        />
      ) : (
        <Typography variant="h4" fontWeight={800} color="text.primary">
          {value}{total ? <Typography component="span" variant="h6" color="text.secondary">/{total}</Typography> : null}
        </Typography>
      )}
      <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 0.5 }}>
        {label}
      </Typography>
    </Box>
  );
}
