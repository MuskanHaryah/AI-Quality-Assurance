import { Box, Typography, Button, Alert } from '@mui/material';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';
import RefreshIcon from '@mui/icons-material/Refresh';

export default function ErrorDisplay({ message, onRetry, fullPage = false }) {
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 2,
        py: fullPage ? 0 : 6,
        minHeight: fullPage ? '60vh' : 'auto',
        textAlign: 'center',
      }}
    >
      <ErrorOutlineIcon sx={{ fontSize: 56, color: 'error.main', opacity: 0.8 }} />
      <Typography variant="h6" color="text.primary">
        Something went wrong
      </Typography>
      <Alert severity="error" sx={{ maxWidth: 480, width: '100%' }}>
        {message || 'An unexpected error occurred. Please try again.'}
      </Alert>
      {onRetry && (
        <Button
          variant="outlined"
          color="primary"
          startIcon={<RefreshIcon />}
          onClick={onRetry}
          sx={{ mt: 1 }}
        >
          Try Again
        </Button>
      )}
    </Box>
  );
}
