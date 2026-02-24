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
import CategoryIcon from '@mui/icons-material/Category';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';
import { GlassCard, SectionHeader } from '../components/common/GlassCard';
import Loading from '../components/common/Loading';
import ErrorDisplay from '../components/common/ErrorDisplay';
import ScoreGauge from '../components/ScoreGauge/ScoreGauge';
import CategoryChart from '../components/CategoryChart/CategoryChart';
import RequirementsTable from '../components/RequirementsTable/RequirementsTable';
import RecommendationCard, { GapAnalysisCard } from '../components/RecommendationCard/RecommendationCard';
import { getReport } from '../api/services';
import { formatDate, riskColor, categoryColors } from '../utils/helpers';
import { glassTokens, PURPLE, TEAL } from '../theme/theme';

export default function Results() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchReport = () => {
    setLoading(true);
    setError(null);
    getReport(id)
      .then((data) => setReport(data))
      .catch((err) => setError(err.friendlyMessage || 'Failed to load report.'))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchReport();
  }, [id]);

  if (loading) return <Loading message="Loading analysis report…" fullPage />;
  if (error) return <Container maxWidth="md" sx={{ py: 8 }}><ErrorDisplay message={error} onRetry={fetchReport} fullPage /></Container>;
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
