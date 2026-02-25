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
import LanguageIcon from '@mui/icons-material/Language';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import { GlassCard, SectionHeader } from '../components/common/GlassCard';
import Loading from '../components/common/Loading';
import ErrorDisplay from '../components/common/ErrorDisplay';
import CategoryChart from '../components/CategoryChart/CategoryChart';
import RequirementsTable from '../components/RequirementsTable/RequirementsTable';
import RecommendationCard, { GapAnalysisCard } from '../components/RecommendationCard/RecommendationCard';
import QualityPlanUpload from '../components/QualityPlanUpload/QualityPlanUpload';
import QualityPlanReport from '../components/QualityPlanReport/QualityPlanReport';
import { getReport, uploadQualityPlan, getQualityPlan } from '../api/services';
import { formatDate, categoryColors } from '../utils/helpers';
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
          getQualityPlan(id)
            .then((qp) => {
              if (qp?.has_plan) setQpResult(qp);
            })
            .catch(() => { /* no plan yet */ });
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
  const domain = summary?.domain || {};

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
              SRS Summary
            </Typography>
            <Stack direction="row" spacing={1} alignItems="center" sx={{ mt: 0.5 }}>
              <DescriptionIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
              <Typography variant="body2" color="text.secondary">
                {summary?.filename} • {formatDate(summary?.created_at)}
              </Typography>
            </Stack>
          </Stack>
        </Stack>

        {/* Top Row: Domain + Overview */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          {/* Domain Card */}
          <Grid size={{ xs: 12, md: 4 }}>
            <GlassCard sx={{ textAlign: 'center', py: 4, height: '100%' }}>
              <LanguageIcon sx={{ fontSize: 48, color: PURPLE, mb: 1 }} />
              <Stack direction="row" justifyContent="center" alignItems="center" spacing={0.5} sx={{ mb: 1 }}>
                <Typography variant="subtitle2" color="text.secondary">
                  Detected Domain
                </Typography>
                {domain.method === 'gemini' && (
                  <Chip
                    icon={<AutoAwesomeIcon />}
                    label="AI"
                    size="small"
                    sx={{
                      height: 20,
                      fontSize: '0.65rem',
                      backgroundColor: alpha(PURPLE, 0.15),
                      color: PURPLE,
                      '& .MuiChip-icon': { fontSize: 12, color: PURPLE },
                    }}
                  />
                )}
              </Stack>
              <Typography variant="h5" fontWeight={800} color="text.primary">
                {domain.domain || 'General'}
              </Typography>
              {domain.confidence > 0 && (
                <Typography variant="caption" color="text.secondary">
                  Confidence: {Math.round(domain.confidence * 100)}%
                </Typography>
              )}
              {domain.reasoning && (
                <Typography
                  variant="caption"
                  color="text.secondary"
                  sx={{
                    mt: 1,
                    display: 'block',
                    fontStyle: 'italic',
                    maxWidth: 280,
                    mx: 'auto',
                    lineHeight: 1.4,
                  }}
                >
                  "{domain.reasoning}"
                </Typography>
              )}
              {Object.keys(domain.critical_categories || {}).length > 0 && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 0.5 }}>
                    Critical for this domain:
                  </Typography>
                  <Stack direction="row" flexWrap="wrap" gap={0.5} justifyContent="center">
                    {Object.entries(domain.critical_categories || {}).map(([cat, level]) => (
                      <Chip
                        key={cat}
                        label={cat}
                        size="small"
                        sx={{
                          fontSize: '0.65rem',
                          height: 22,
                          backgroundColor: alpha(level === 'critical' ? '#ef4444' : '#f59e0b', 0.1),
                          color: level === 'critical' ? '#ef4444' : '#f59e0b',
                          fontWeight: 600,
                        }}
                      />
                    ))}
                  </Stack>
                </Box>
              )}
            </GlassCard>
          </Grid>

          {/* Quick Stats */}
          <Grid size={{ xs: 12, md: 8 }}>
            <GlassCard sx={{ height: '100%' }}>
              <Typography variant="h6" fontWeight={700} sx={{ mb: 2 }}>
                What&apos;s in the SRS
              </Typography>
              <Grid container spacing={2}>
                <Grid size={{ xs: 6, sm: 4 }}>
                  <StatItem label="Requirements" value={summary?.total_requirements ?? 0} />
                </Grid>
                <Grid size={{ xs: 6, sm: 4 }}>
                  <StatItem label="Categories Found" value={categories_present?.length ?? 0} total={7} />
                </Grid>
                <Grid size={{ xs: 6, sm: 4 }}>
                  <StatItem label="Missing" value={categories_missing?.length ?? 0} />
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

        {/* Category Distribution */}
        <GlassCard sx={{ mb: 4 }}>
          <SectionHeader
            title="Category Distribution"
            subtitle="How requirements map to ISO/IEC 9126 quality categories"
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
              subtitle="What to improve in your SRS based on the detected domain"
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
              subtitle="Quality categories missing or insufficiently covered in the SRS"
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
          <Box sx={{ mb: 4 }}>
            <QualityPlanReport planData={qpResult} />
          </Box>
        ) : (
          <Box sx={{ mb: 4 }}>
            {!showQPUpload ? (
              <GlassCard
                sx={{
                  textAlign: 'center',
                  py: 5,
                  background: 'linear-gradient(135deg, rgba(6,182,212,0.06), rgba(124,58,237,0.06))',
                  border: '2px dashed rgba(124,58,237,0.35)',
                }}
              >
                <FactCheckIcon sx={{ fontSize: 48, color: TEAL, mb: 2 }} />
                <Typography variant="h5" fontWeight={700} sx={{ mb: 1 }}>
                  Want to know your quality estimation?
                </Typography>
                <Typography variant="body1" color="text.secondary" sx={{ mb: 3, maxWidth: 540, mx: 'auto' }}>
                  Upload your Quality Plan document and we&apos;ll compare it against
                  the quality categories identified above. You&apos;ll see how much
                  quality your plan can achieve and what to improve.
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
                  Upload Quality Plan
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
function StatItem({ label, value, total }) {
  return (
    <Box sx={{ textAlign: 'center' }}>
      <Typography variant="h4" fontWeight={800} color="text.primary">
        {value}{total ? <Typography component="span" variant="h6" color="text.secondary">/{total}</Typography> : null}
      </Typography>
      <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 0.5 }}>
        {label}
      </Typography>
    </Box>
  );
}
