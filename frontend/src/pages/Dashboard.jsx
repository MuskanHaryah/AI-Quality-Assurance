import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Box,
  Typography,
  Grid,
  Stack,
  Chip,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  alpha,
  IconButton,
  Tooltip,
} from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import VisibilityIcon from '@mui/icons-material/Visibility';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import AssessmentIcon from '@mui/icons-material/Assessment';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import InsertDriveFileIcon from '@mui/icons-material/InsertDriveFile';
import { GlassCard, SectionHeader } from '../components/common/GlassCard';
import Loading from '../components/common/Loading';
import ErrorDisplay from '../components/common/ErrorDisplay';
import { getRecentAnalyses, checkHealth } from '../api/services';
import { formatRelative, riskHex } from '../utils/helpers';
import { PURPLE, TEAL } from '../theme/theme';

export default function Dashboard() {
  const navigate = useNavigate();
  const [analyses, setAnalyses] = useState([]);
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [analysesResp, healthResp] = await Promise.all([
        getRecentAnalyses(),
        checkHealth(),
      ]);
      setAnalyses(analysesResp.analyses ?? []);
      setHealth(healthResp);
    } catch (err) {
      setError(err.friendlyMessage || 'Failed to load dashboard data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  if (loading) return <Loading message="Loading dashboard…" fullPage />;
  if (error) return <Container maxWidth="lg" sx={{ py: 8 }}><ErrorDisplay message={error} onRetry={fetchData} fullPage /></Container>;

  // Summary stats
  const totalAnalyses = analyses.length;
  const totalRequirements = analyses.reduce((sum, a) => sum + (a.total_requirements || 0), 0);
  const avgScore =
    totalAnalyses > 0
      ? (analyses.reduce((sum, a) => sum + (a.overall_score || 0), 0) / totalAnalyses).toFixed(1)
      : '—';

  const stats = [
    { label: 'Total Analyses', value: totalAnalyses, icon: <AssessmentIcon />, color: PURPLE },
    { label: 'Requirements Processed', value: totalRequirements, icon: <InsertDriveFileIcon />, color: TEAL },
    { label: 'Average Score', value: avgScore, icon: <TrendingUpIcon />, color: '#10b981' },
  ];

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: { xs: 3, md: 5 } }}>
        <SectionHeader
          title="Dashboard"
          subtitle="Overview of your requirements analyses"
          action={
            <Stack direction="row" spacing={1}>
              <Tooltip title="Refresh">
                <IconButton onClick={fetchData} sx={{ color: 'text.secondary' }}>
                  <RefreshIcon />
                </IconButton>
              </Tooltip>
              <Button
                variant="contained"
                startIcon={<UploadFileIcon />}
                onClick={() => navigate('/upload')}
                size="small"
              >
                New Analysis
              </Button>
            </Stack>
          }
        />

        {/* Stat Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          {stats.map((stat, idx) => (
            <Grid size={{ xs: 12, sm: 4 }} key={idx}>
              <GlassCard>
                <Stack direction="row" alignItems="center" spacing={2}>
                  <Box
                    sx={{
                      p: 1.5,
                      borderRadius: 3,
                      background: alpha(stat.color, 0.1),
                      color: stat.color,
                      display: 'flex',
                    }}
                  >
                    {stat.icon}
                  </Box>
                  <Box>
                    <Typography variant="h4" fontWeight={800}>
                      {stat.value}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {stat.label}
                    </Typography>
                  </Box>
                </Stack>
              </GlassCard>
            </Grid>
          ))}
        </Grid>

        {/* Backend status */}
        {health && (
          <GlassCard sx={{ mb: 4 }}>
            <Stack direction="row" alignItems="center" spacing={2} flexWrap="wrap">
              <Chip
                label={`Backend: ${health.status}`}
                color="success"
                variant="outlined"
                size="small"
              />
              <Chip
                label={`Model: ${health.model}`}
                variant="outlined"
                size="small"
              />
              <Chip
                label={`Accuracy: ${(health.accuracy * 100).toFixed(1)}%`}
                variant="outlined"
                size="small"
                color="success"
              />
            </Stack>
          </GlassCard>
        )}

        {/* Recent analyses table */}
        <GlassCard>
          <SectionHeader
            title="Recent Analyses"
            subtitle={`${totalAnalyses} analysis${totalAnalyses !== 1 ? 'es' : ''} found`}
          />

          {analyses.length === 0 ? (
            <Box sx={{ py: 6, textAlign: 'center' }}>
              <UploadFileIcon sx={{ fontSize: 56, color: 'text.disabled', mb: 2 }} />
              <Typography variant="h6" color="text.secondary" gutterBottom>
                No analyses yet
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Upload a requirements document to get started.
              </Typography>
              <Button
                variant="contained"
                startIcon={<UploadFileIcon />}
                onClick={() => navigate('/upload')}
              >
                Upload Document
              </Button>
            </Box>
          ) : (
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell sx={{ fontWeight: 700 }}>File</TableCell>
                    <TableCell sx={{ fontWeight: 700 }}>Type</TableCell>
                    <TableCell sx={{ fontWeight: 700 }} align="right">Score</TableCell>
                    <TableCell sx={{ fontWeight: 700 }}>Risk</TableCell>
                    <TableCell sx={{ fontWeight: 700 }} align="right">Reqs</TableCell>
                    <TableCell sx={{ fontWeight: 700 }}>When</TableCell>
                    <TableCell sx={{ fontWeight: 700 }} align="center">Action</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {analyses.map((a) => (
                    <TableRow
                      key={a.analysis_id}
                      hover
                      sx={{
                        cursor: 'pointer',
                        '&:last-child td': { borderBottom: 0 },
                      }}
                      onClick={() => navigate(`/results/${a.analysis_id}`)}
                    >
                      <TableCell>
                        <Typography variant="body2" fontWeight={500} noWrap sx={{ maxWidth: 260 }}>
                          {a.filename}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={a.file_type?.toUpperCase()}
                          size="small"
                          variant="outlined"
                          sx={{ fontSize: '0.7rem', height: 22 }}
                        />
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2" fontWeight={700}>
                          {a.overall_score?.toFixed(1)}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={a.risk_level}
                          size="small"
                          sx={{
                            backgroundColor: alpha(riskHex(a.risk_level), 0.1),
                            color: riskHex(a.risk_level),
                            fontWeight: 600,
                            fontSize: '0.7rem',
                            height: 22,
                          }}
                        />
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2">{a.total_requirements}</Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" color="text.secondary" noWrap>
                          {formatRelative(a.created_at)}
                        </Typography>
                      </TableCell>
                      <TableCell align="center">
                        <Tooltip title="View report">
                          <IconButton
                            size="small"
                            onClick={(e) => {
                              e.stopPropagation();
                              navigate(`/results/${a.analysis_id}`);
                            }}
                            sx={{ color: PURPLE }}
                          >
                            <VisibilityIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </GlassCard>
      </Box>
    </Container>
  );
}
