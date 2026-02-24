import { Typography, Chip, Stack, alpha } from '@mui/material';
import PriorityHighIcon from '@mui/icons-material/PriorityHigh';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import { GlassCard } from '../common/GlassCard';

const priorityConfig = {
  high: { icon: <PriorityHighIcon fontSize="small" />, color: '#ef4444', label: 'High' },
  medium: { icon: <WarningAmberIcon fontSize="small" />, color: '#f59e0b', label: 'Medium' },
  low: { icon: <InfoOutlinedIcon fontSize="small" />, color: '#3b82f6', label: 'Low' },
};

export default function RecommendationCard({ recommendation }) {
  const { category, priority, message } = recommendation;
  const config = priorityConfig[priority?.toLowerCase()] || priorityConfig.low;

  return (
    <GlassCard
      sx={{
        borderLeft: `4px solid ${config.color}`,
        '&:hover': {
          transform: 'translateY(-2px)',
        },
      }}
    >
      <Stack direction="row" justifyContent="space-between" alignItems="flex-start" spacing={2}>
        <Stack spacing={1} sx={{ flex: 1 }}>
          <Stack direction="row" alignItems="center" spacing={1}>
            <Typography variant="subtitle1" fontWeight={700}>
              {category}
            </Typography>
            <Chip
              icon={config.icon}
              label={config.label}
              size="small"
              sx={{
                backgroundColor: alpha(config.color, 0.1),
                color: config.color,
                fontWeight: 600,
                fontSize: '0.7rem',
                height: 24,
                '& .MuiChip-icon': { color: config.color },
              }}
            />
          </Stack>
          <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.6 }}>
            {message}
          </Typography>
        </Stack>
      </Stack>
    </GlassCard>
  );
}

/**
 * Display gap analysis entries.
 */
export function GapAnalysisCard({ gap }) {
  return (
    <GlassCard
      sx={{
        borderLeft: `4px solid #f59e0b`,
      }}
    >
      <Stack spacing={0.5}>
        <Typography variant="subtitle2" fontWeight={700}>
          {gap.category}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {gap.gap_type}: {gap.shortage || gap.message || '—'}
        </Typography>
      </Stack>
    </GlassCard>
  );
}
