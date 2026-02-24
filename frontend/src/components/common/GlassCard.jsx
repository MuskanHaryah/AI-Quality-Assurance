import { Box, Typography, Stack, Chip, Alert } from '@mui/material';
import { glassTokens } from '../../theme/theme';

/**
 * A glass-style card wrapper for consistent section styling.
 */
export function GlassCard({ children, sx = {}, ...props }) {
  return (
    <Box
      sx={{
        background: glassTokens.bgCard,
        backdropFilter: glassTokens.blur,
        WebkitBackdropFilter: glassTokens.blur,
        border: `1px solid ${glassTokens.border}`,
        borderRadius: `${glassTokens.radius}px`,
        boxShadow: glassTokens.shadowSoft,
        p: 3,
        transition: 'all 0.25s ease',
        '&:hover': {
          boxShadow: glassTokens.shadowMedium,
        },
        ...sx,
      }}
      {...props}
    >
      {children}
    </Box>
  );
}

/**
 * Section header for pages.
 */
export function SectionHeader({ title, subtitle, action, chip }) {
  return (
    <Stack direction="row" justifyContent="space-between" alignItems="flex-start" sx={{ mb: 3 }}>
      <Box>
        <Stack direction="row" alignItems="center" gap={1.5}>
          <Typography variant="h4" fontWeight={700}>
            {title}
          </Typography>
          {chip && (
            <Chip
              label={chip.label}
              color={chip.color || 'primary'}
              size="small"
              variant="filled"
            />
          )}
        </Stack>
        {subtitle && (
          <Typography variant="body1" color="text.secondary" sx={{ mt: 0.5 }}>
            {subtitle}
          </Typography>
        )}
      </Box>
      {action && <Box>{action}</Box>}
    </Stack>
  );
}

/**
 * An inline notification toast (used with the global context).
 */
export function NotificationToast({ notification, onClose }) {
  return (
    <Alert
      severity={notification.severity}
      onClose={onClose}
      sx={{
        mb: 1,
        background: glassTokens.bgSurface,
        backdropFilter: glassTokens.blur,
        border: `1px solid ${glassTokens.border}`,
      }}
    >
      {notification.message}
    </Alert>
  );
}
