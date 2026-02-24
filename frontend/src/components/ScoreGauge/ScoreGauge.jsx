import { Box, Typography } from '@mui/material';
import { riskHex, clampScore } from '../../utils/helpers';
import { glassTokens, PURPLE, TEAL } from '../../theme/theme';

export default function ScoreGauge({ score, riskLevel, size = 160 }) {
  const safeScore = clampScore(score);
  const color = riskHex(riskLevel);
  const center = size / 2;
  const radius = (size - 24) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (safeScore / 100) * circumference;

  return (
    <Box
      sx={{
        position: 'relative',
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        p: 2,
        borderRadius: '50%',
        background: glassTokens.bgCard,
        backdropFilter: glassTokens.blur,
        boxShadow: glassTokens.shadowMedium,
      }}
    >
      <svg width={size} height={size} style={{ transform: 'rotate(-90deg)' }}>
        {/* Background track */}
        <circle
          cx={center}
          cy={center}
          r={radius}
          fill="none"
          stroke="rgba(0,0,0,0.06)"
          strokeWidth="12"
        />
        {/* Gradient definition */}
        <defs>
          <linearGradient id="scoreGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor={PURPLE} />
            <stop offset="100%" stopColor={color} />
          </linearGradient>
        </defs>
        {/* Progress arc */}
        <circle
          cx={center}
          cy={center}
          r={radius}
          fill="none"
          stroke="url(#scoreGradient)"
          strokeWidth="12"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          style={{ transition: 'stroke-dashoffset 0.8s ease' }}
        />
      </svg>

      {/* Center label */}
      <Box
        sx={{
          position: 'absolute',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <Typography
          variant="h3"
          sx={{ fontWeight: 800, color: 'text.primary', lineHeight: 1 }}
        >
          {safeScore.toFixed(1)}
        </Typography>
        <Typography
          variant="caption"
          sx={{
            fontWeight: 600,
            color,
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
            mt: 0.5,
          }}
        >
          {riskLevel} Risk
        </Typography>
      </Box>
    </Box>
  );
}
