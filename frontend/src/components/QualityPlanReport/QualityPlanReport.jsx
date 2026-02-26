import {
  Box,
  Typography,
  Grid,
  Stack,
  Chip,
  Divider,
  LinearProgress,
  Tooltip,
  Collapse,
  IconButton,
  Button,
  alpha,
  Alert,
} from '@mui/material';
import { useState } from 'react';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import TipsAndUpdatesIcon from '@mui/icons-material/TipsAndUpdates';
import VerifiedIcon from '@mui/icons-material/Verified';
import ShieldIcon from '@mui/icons-material/Shield';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import { GlassCard, SectionHeader } from '../common/GlassCard';
import { categoryColors } from '../../utils/helpers';
import { PURPLE, TEAL } from '../../theme/theme';

/** Strength → colour mapping */
const strengthConfig = {
  Strong:   { color: '#10b981', label: 'Strong Plan' },
  Moderate: { color: '#f59e0b', label: 'Moderate Plan' },
  Weak:     { color: '#ef4444', label: 'Weak Plan' },
};

/** Priority → colour mapping for suggestions */
const sugPriorityColor = {
  critical: '#dc2626',
  high:     '#ef4444',
  medium:   '#f59e0b',
  info:     '#3b82f6',
};

export default function QualityPlanReport({ planData }) {
  if (!planData) return null;

  const {
    overall_coverage,
    achievable_quality,
    plan_strength,
    category_coverage,
    suggestions,
    summary,
    domain_match,
    document_type_warning,
  } = planData;

  const strengthCfg = strengthConfig[plan_strength] || strengthConfig.Weak;
  const domainMismatch = domain_match && !domain_match.matches;

  return (
    <Box>
      <SectionHeader
        title="Quality Plan Analysis"
        subtitle="How well does your quality plan cover the SRS requirements?"
        chip={{ label: strengthCfg.label, color: plan_strength === 'Strong' ? 'success' : plan_strength === 'Moderate' ? 'warning' : 'error' }}
      />

      {/* Document Type Warning - uploaded wrong document type */}
      {document_type_warning && (
        <Alert
          severity="error"
          icon={<WarningAmberIcon />}
          sx={{ mb: 3 }}
        >
          <Typography variant="subtitle2" fontWeight={600} gutterBottom>
            Wrong Document Type Detected
            <Chip 
              label="AI" 
              size="small" 
              sx={{ ml: 1, height: 18, fontSize: '0.65rem', bgcolor: 'rgba(139, 92, 246, 0.2)', color: '#8b5cf6' }} 
            />
          </Typography>
          <Typography variant="body2" sx={{ mb: 1 }}>
            This document appears to be a <strong>{document_type_warning.detected_type}</strong> rather than a Quality Plan.
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {document_type_warning.reasoning}
          </Typography>
          <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 1 }}>
            Confidence: {Math.round((document_type_warning.confidence || 0) * 100)}% | Please upload an actual Quality Plan document.
          </Typography>
        </Alert>
      )}

      {/* Domain Mismatch Warning */}
      {domainMismatch && (
        <Alert
          severity="warning"
          icon={<WarningAmberIcon />}
          sx={{ mb: 3 }}
        >
          <Typography variant="subtitle2" fontWeight={600} gutterBottom>
            Domain Mismatch Detected
          </Typography>
          <Typography variant="body2">
            This Quality Plan appears to be for a <strong>{domain_match.qp_domain}</strong> system,
            but the SRS is for a <strong>{domain_match.srs_domain}</strong> system.
            Please verify you&apos;ve uploaded the correct Quality Plan document.
          </Typography>
        </Alert>
      )}

      {/* Top metrics row */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {/* Coverage Score */}
        <Grid size={{ xs: 12, sm: 6, md: 4 }}>
          <GlassCard sx={{ textAlign: 'center', py: 3, height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
            <ShieldIcon sx={{ fontSize: 40, color: TEAL, mb: 1 }} />
            <Typography variant="h3" fontWeight={800} sx={{ color: TEAL }}>
              {Math.round(overall_coverage)}%
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Plan Coverage
            </Typography>
            <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 0.5 }}>
              How much of your SRS quality factors the plan addresses
            </Typography>
          </GlassCard>
        </Grid>

        {/* Achievable Quality */}
        <Grid size={{ xs: 12, sm: 6, md: 4 }}>
          <GlassCard sx={{ textAlign: 'center', py: 3, height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
            <VerifiedIcon sx={{ fontSize: 40, color: PURPLE, mb: 1 }} />
            <Typography variant="h3" fontWeight={800} sx={{ color: PURPLE }}>
              {Math.round(achievable_quality)}%
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Achievable Quality
            </Typography>
            <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 0.5 }}>
              Predicted quality if the plan is fully executed
            </Typography>
          </GlassCard>
        </Grid>

        {/* Plan Strength */}
        <Grid size={{ xs: 12, sm: 6, md: 4 }}>
          <GlassCard sx={{ textAlign: 'center', py: 3, height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
            <Box
              sx={{
                width: 56,
                height: 56,
                borderRadius: '50%',
                background: alpha(strengthCfg.color, 0.1),
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                mx: 'auto',
                mb: 1,
              }}
            >
              <Typography variant="h5" fontWeight={800} sx={{ color: strengthCfg.color }}>
                {plan_strength === 'Strong' ? 'A' : plan_strength === 'Moderate' ? 'B' : 'C'}
              </Typography>
            </Box>
            <Typography variant="h6" fontWeight={700} sx={{ color: strengthCfg.color }}>
              {strengthCfg.label}
            </Typography>
            <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 0.5 }}>
              Overall plan quality grade
            </Typography>
          </GlassCard>
        </Grid>
      </Grid>

      {/* Summary */}
      {summary && (
        <GlassCard sx={{ mb: 4, borderLeft: `4px solid ${TEAL}` }}>
          <Typography variant="body1" color="text.secondary" sx={{ lineHeight: 1.7 }}>
            {summary}
          </Typography>
        </GlassCard>
      )}

      {/* Per-category coverage */}
      <GlassCard sx={{ mb: 4 }}>
        <Typography variant="h6" fontWeight={700} sx={{ mb: 2 }}>
          Category Coverage Breakdown
        </Typography>
        <Stack spacing={2}>
          {Object.entries(category_coverage || {}).map(([cat, data]) => (
            <CategoryCoverageRow key={cat} category={cat} data={data} />
          ))}
        </Stack>
      </GlassCard>

      {/* Suggestions */}
      {suggestions?.length > 0 && (
        <Box sx={{ mb: 4 }}>
          <SectionHeader
            title="Improvement Suggestions"
            subtitle="Actions to strengthen your quality plan"
          />
          <Stack spacing={2}>
            {suggestions.map((sug, idx) => (
              <SuggestionCard key={idx} suggestion={sug} />
            ))}
          </Stack>
        </Box>
      )}
    </Box>
  );
}

/** Single category coverage row with expandable evidence */
function CategoryCoverageRow({ category, data }) {
  const [expanded, setExpanded] = useState(false);
  const [showAll, setShowAll] = useState(false);
  const color = categoryColors[category] || '#64748b';
  const covered = data?.covered;
  const evidenceCount = data?.evidence_count || 0;
  const snippets = data?.evidence_snippets || [];
  const inSrs = data?.in_srs;
  const srsCount = data?.srs_requirement_count || 0;

  return (
    <Box>
      <Stack direction="row" alignItems="center" spacing={2}>
        {/* Status icon */}
        {covered ? (
          <CheckCircleIcon sx={{ color: '#10b981', fontSize: 22 }} />
        ) : (
          <CancelIcon sx={{ color: '#ef4444', fontSize: 22 }} />
        )}

        {/* Category name */}
        <Box sx={{ minWidth: 130 }}>
          <Typography variant="subtitle2" fontWeight={600} sx={{ color }}>
            {category}
          </Typography>
        </Box>

        {/* Progress bar showing coverage */}
        <Box sx={{ flex: 1 }}>
          <LinearProgress
            variant="determinate"
            value={covered ? 100 : 0}
            sx={{
              height: 8,
              borderRadius: 4,
              backgroundColor: alpha(color, 0.1),
              '& .MuiLinearProgress-bar': {
                backgroundColor: covered ? color : 'transparent',
                borderRadius: 4,
              },
            }}
          />
        </Box>

        {/* Tags */}
        <Stack direction="row" spacing={0.5}>
          {inSrs && (
            <Tooltip title={`${srsCount} requirement(s) in SRS`}>
              <Chip label={`SRS: ${srsCount}`} size="small" sx={{ fontSize: '0.7rem', height: 22 }} />
            </Tooltip>
          )}
          {!inSrs && (
            <Chip label="Not in SRS" size="small" variant="outlined" sx={{ fontSize: '0.7rem', height: 22 }} />
          )}
          <Chip
            label={covered ? `${evidenceCount} evidence` : 'Not covered'}
            size="small"
            sx={{
              backgroundColor: alpha(covered ? '#10b981' : '#ef4444', 0.1),
              color: covered ? '#10b981' : '#ef4444',
              fontSize: '0.7rem',
              fontWeight: 600,
              height: 22,
            }}
          />
        </Stack>

        {/* Expand button for evidence */}
        {snippets.length > 0 && (
          <IconButton size="small" onClick={() => setExpanded(!expanded)}>
            {expanded ? <ExpandLessIcon fontSize="small" /> : <ExpandMoreIcon fontSize="small" />}
          </IconButton>
        )}
      </Stack>

      {/* Expandable evidence snippets */}
      <Collapse in={expanded}>
        <Box sx={{ ml: 6, mt: 1.5, mb: 1 }}>
          <Typography variant="caption" color="text.secondary" fontWeight={600} sx={{ mb: 1, display: 'block' }}>
            Evidence found in your Quality Plan:
          </Typography>
          <Stack spacing={1}>
            {(showAll ? snippets : snippets.slice(0, 3)).map((snippet, idx) => (
              <Box
                key={idx}
                sx={{
                  p: 1.5,
                  borderRadius: 1.5,
                  backgroundColor: alpha(color, 0.04),
                  borderLeft: `3px solid ${alpha(color, 0.4)}`,
                }}
              >
                <Typography
                  variant="body2"
                  sx={{
                    color: 'text.secondary',
                    lineHeight: 1.6,
                    fontSize: '0.8rem',
                  }}
                >
                  &ldquo;{snippet.trim()}&rdquo;
                </Typography>
              </Box>
            ))}
          </Stack>
          {snippets.length > 3 && !showAll && (
            <Button
              size="small"
              onClick={() => setShowAll(true)}
              sx={{ mt: 1.5, textTransform: 'none', fontWeight: 600, fontSize: '0.75rem' }}
            >
              View More ({snippets.length - 3} more)
            </Button>
          )}
          {showAll && snippets.length > 3 && (
            <Button
              size="small"
              onClick={() => setShowAll(false)}
              sx={{ mt: 1.5, textTransform: 'none', fontWeight: 600, fontSize: '0.75rem' }}
            >
              Show Less
            </Button>
          )}
        </Box>
      </Collapse>

      <Divider sx={{ mt: 1.5 }} />
    </Box>
  );
}

/** Single suggestion card */
function SuggestionCard({ suggestion }) {
  const { category, priority, message, type } = suggestion;
  const color = sugPriorityColor[priority] || '#64748b';

  const typeLabel = {
    uncovered: 'Not Covered',
    both_missing: 'Missing Everywhere',
    proactive: 'Proactive Coverage',
    low_coverage: 'Low Coverage',
    error: 'Error',
  };

  return (
    <GlassCard sx={{ borderLeft: `4px solid ${color}` }}>
      <Stack direction="row" justifyContent="space-between" alignItems="flex-start" spacing={2}>
        <Stack spacing={0.5} sx={{ flex: 1 }}>
          <Stack direction="row" alignItems="center" spacing={1}>
            <TipsAndUpdatesIcon sx={{ color, fontSize: 18 }} />
            <Typography variant="subtitle2" fontWeight={700}>
              {category}
            </Typography>
            <Chip
              label={priority}
              size="small"
              sx={{
                backgroundColor: alpha(color, 0.1),
                color,
                fontWeight: 600,
                fontSize: '0.65rem',
                height: 20,
                textTransform: 'capitalize',
              }}
            />
            {type && (
              <Chip
                label={typeLabel[type] || type}
                size="small"
                variant="outlined"
                sx={{ fontSize: '0.65rem', height: 20 }}
              />
            )}
          </Stack>
          <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.6 }}>
            {message}
          </Typography>
        </Stack>
      </Stack>
    </GlassCard>
  );
}
