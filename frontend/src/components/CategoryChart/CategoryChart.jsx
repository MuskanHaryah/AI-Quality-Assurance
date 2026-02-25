import { Box, Typography, Stack, Chip, alpha } from '@mui/material';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';
import { categoryColors } from '../../utils/helpers';

/**
 * Displays category distribution as horizontal bars.
 * categoryScores: { Functionality: { count, percentage, meets_minimum, ... }, ... }
 */
export default function CategoryChart({ categoryScores }) {
  if (!categoryScores || Object.keys(categoryScores).length === 0) {
    return (
      <Box sx={{ py: 3, textAlign: 'center' }}>
        <Typography color="text.secondary">No category data available.</Typography>
      </Box>
    );
  }

  // Sort by count (most requirements first)
  const entries = Object.entries(categoryScores).sort(
    ([, a], [, b]) => (b.count ?? 0) - (a.count ?? 0)
  );

  const maxCount = Math.max(...entries.map(([, d]) => d.count ?? 0), 1);

  return (
    <Stack spacing={2.5}>
      {entries.map(([category, data]) => {
        const count = data.count ?? 0;
        const pct = data.percentage ?? 0;
        const meetsMin = data.meets_minimum ?? false;
        const minRec = data.min_recommended ?? 1;
        const barWidth = maxCount > 0 ? (count / maxCount) * 100 : 0;
        const color = categoryColors[category] || '#64748b';

        return (
          <Box key={category}>
            <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 0.75 }}>
              <Stack direction="row" alignItems="center" spacing={1}>
                <Box
                  sx={{
                    width: 10,
                    height: 10,
                    borderRadius: '50%',
                    backgroundColor: color,
                  }}
                />
                <Typography variant="body2" fontWeight={600}>
                  {category}
                </Typography>
                {meetsMin ? (
                  <CheckCircleOutlineIcon sx={{ fontSize: 16, color: '#10b981' }} />
                ) : (
                  <ErrorOutlineIcon sx={{ fontSize: 16, color: count === 0 ? '#ef4444' : '#f59e0b' }} />
                )}
              </Stack>
              <Stack direction="row" alignItems="center" spacing={1}>
                <Chip
                  label={`${count} req${count !== 1 ? 's' : ''}`}
                  size="small"
                  sx={{
                    height: 22,
                    fontSize: '0.7rem',
                    backgroundColor: alpha(color, 0.1),
                    color,
                    fontWeight: 600,
                  }}
                />
                <Typography variant="caption" color="text.secondary" sx={{ minWidth: 40, textAlign: 'right' }}>
                  {pct.toFixed(0)}%
                </Typography>
              </Stack>
            </Stack>

            {/* Bar track */}
            <Box
              sx={{
                height: 10,
                borderRadius: 5,
                backgroundColor: alpha(color, 0.1),
                overflow: 'hidden',
              }}
            >
              <Box
                sx={{
                  height: '100%',
                  width: `${Math.min(barWidth, 100)}%`,
                  borderRadius: 5,
                  background: `linear-gradient(90deg, ${color}, ${alpha(color, 0.7)})`,
                  transition: 'width 0.8s ease',
                  minWidth: count > 0 ? 8 : 0,
                }}
              />
            </Box>

            {/* Min recommended label */}
            {!meetsMin && (
              <Typography variant="caption" color="text.secondary" sx={{ mt: 0.25, display: 'block' }}>
                {count === 0 ? 'Not covered' : `${count}/${minRec} recommended`}
              </Typography>
            )}
          </Box>
        );
      })}
    </Stack>
  );
}
