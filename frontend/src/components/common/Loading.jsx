import { Box, CircularProgress, Typography } from '@mui/material';
import { glassTokens } from '../../theme/theme';

export default function Loading({ message = 'Loading...', fullPage = false }) {
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 2,
        py: fullPage ? 0 : 8,
        minHeight: fullPage ? '60vh' : 'auto',
      }}
    >
      <Box
        sx={{
          p: 3,
          borderRadius: '50%',
          background: glassTokens.bgCard,
          backdropFilter: glassTokens.blur,
          boxShadow: glassTokens.shadowMedium,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <CircularProgress
          size={40}
          thickness={4}
          sx={{
            color: 'primary.main',
          }}
        />
      </Box>
      <Typography variant="body1" color="text.secondary" fontWeight={500}>
        {message}
      </Typography>
    </Box>
  );
}
