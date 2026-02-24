import { Box, Typography, Stack, Chip, alpha } from '@mui/material';
import { GlassCard } from '../common/GlassCard';
import { categoryColors } from '../../utils/helpers';

/**
 * Displays category scores as horizontal glass-style bars.
 * categoryScores: { Functionality: { score, count, ... }, ... }
 */
export default function CategoryChart({ categoryScores }) {
  if (!categoryScores || Object.keys(categoryScores).length === 0) {
    return (
      <GlassCard>
        <Typography color="text.secondary">No category data available.</Typography>
      </GlassCard>
    );
  }

  const entries = Object.entries(categoryScores).sort(
    ([, a], [, b]) => (b.score ?? b) - (a.score ?? a)
  );

  return (
    <Stack spacing={2}>
      {entries.map(([category, data]) => {
        const score = typeof data === 'number' ? data : data.score ?? 0;
        const count = typeof data === 'object' ? data.count ?? 0 : null;
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
              </Stack>
              <Stack direction="row" alignItems="center" spacing={1}>
                {count !== null && (
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
                )}
                <Typography variant="body2" fontWeight={700} sx={{ minWidth: 36, textAlign: 'right' }}>
                  {score.toFixed(1)}
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
                  width: `${Math.min(score, 100)}%`,
                  borderRadius: 5,
                  background: `linear-gradient(90deg, ${color}, ${alpha(color, 0.7)})`,
                  transition: 'width 0.8s ease',
                }}
              />
            </Box>
          </Box>
        );
      })}
    </Stack>
  );
}
