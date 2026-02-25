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
  TablePagination,
  alpha,
  IconButton,
  Tooltip,
} from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import VisibilityIcon from '@mui/icons-material/Visibility';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import AssessmentIcon from '@mui/icons-material/Assessment';
import CategoryIcon from '@mui/icons-material/Category';
import InsertDriveFileIcon from '@mui/icons-material/InsertDriveFile';
import { GlassCard, SectionHeader } from '../components/common/GlassCard';
import Loading from '../components/common/Loading';
import ErrorDisplay from '../components/common/ErrorDisplay';
import { getRecentAnalyses, checkHealth } from '../api/services';
import { formatRelative } from '../utils/helpers';
import { PURPLE, TEAL } from '../theme/theme';

export default function Dashboard() {
  const navigate = useNavigate();
  const [analyses, setAnalyses] = useState([]);
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

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
      let msg = err.friendlyMessage || 'Failed to load dashboard data.';
      if (err.code === 'ECONNREFUSED' || err.code === 'ERR_NETWORK' || msg.includes('Network Error')) {
        msg = 'Cannot connect to the backend server. Please make sure the server is running (python app.py).';
      }
      setError(msg);
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

  // Parse categories_present (stored as JSON string or array)
  const parseCats = (raw) => {
    if (Array.isArray(raw)) return raw;
    if (typeof raw === 'string') {
      try { return JSON.parse(raw); } catch { return []; }
    }
    return [];
  };

  const avgCategories =
    totalAnalyses > 0
      ? (analyses.reduce((sum, a) => sum + parseCats(a.categories_present).length, 0) / totalAnalyses).toFixed(1)
      : '—';

  const stats = [
    { label: 'Total Analyses', value: totalAnalyses, icon: <AssessmentIcon />, color: PURPLE },
    { label: 'Requirements Processed', value: totalRequirements, icon: <InsertDriveFileIcon />, color: TEAL },
    { label: 'Avg Categories', value: `${avgCategories}/7`, icon: <CategoryIcon />, color: '#10b981' },
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
            subtitle={`${totalAnalyses} ${totalAnalyses === 1 ? 'analysis' : 'analyses'} found`}
          />

          {analyses.length === 0 ? (
            <Box sx={{ py: 8, textAlign: 'center' }}>
              <Box
                sx={{
                  width: 80,
                  height: 80,
                  borderRadius: '50%',
                  background: alpha(PURPLE, 0.1),
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  mx: 'auto',
                  mb: 3,
                }}
              >
                <UploadFileIcon sx={{ fontSize: 40, color: PURPLE }} />
              </Box>
              <Typography variant="h5" fontWeight={700} gutterBottom>
                Welcome to QualityMapAI
              </Typography>
              <Typography variant="body1" color="text.secondary" sx={{ mb: 1, maxWidth: 420, mx: 'auto' }}>
                Upload your SRS document to analyze requirements quality.
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 4, maxWidth: 420, mx: 'auto' }}>
                We&apos;ll classify requirements into ISO/IEC 9126 categories, detect your system domain, and provide tailored recommendations.
              </Typography>
              <Button
                variant="contained"
                size="large"
                startIcon={<UploadFileIcon />}
                onClick={() => navigate('/upload')}
                sx={{ px: 4 }}
              >
                Upload Your First Document
              </Button>
            </Box>
          ) : (
            <>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell sx={{ fontWeight: 700 }}>File</TableCell>
                      <TableCell sx={{ fontWeight: 700 }}>Type</TableCell>
                      <TableCell sx={{ fontWeight: 700 }} align="right">Categories</TableCell>
                      <TableCell sx={{ fontWeight: 700 }} align="right">Reqs</TableCell>
                      <TableCell sx={{ fontWeight: 700 }}>When</TableCell>
                      <TableCell sx={{ fontWeight: 700 }} align="center">Action</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {analyses
                      .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                      .map((a) => {
                        const cats = parseCats(a.categories_present);
                        return (
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
                                {cats.length}/7
                              </Typography>
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
                        );
                      })}
                  </TableBody>
                </Table>
              </TableContainer>
              <TablePagination
                component="div"
                count={analyses.length}
                page={page}
                onPageChange={(_, newPage) => setPage(newPage)}
                rowsPerPage={rowsPerPage}
                onRowsPerPageChange={(e) => {
                  setRowsPerPage(parseInt(e.target.value, 10));
                  setPage(0);
                }}
                rowsPerPageOptions={[10, 25, 50]}
              />
            </>
          )}
        </GlassCard>
      </Box>
    </Container>
  );
}
