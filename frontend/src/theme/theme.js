import { createTheme, alpha } from '@mui/material/styles';

// ── Liquid Glass Design Tokens ──────────────────────────────────────
const PURPLE = '#7c3aed';
const TEAL   = '#06b6d4';
const PINK   = '#ec4899';

const glassTokens = {
  blur: 'blur(16px)',
  blurHeavy: 'blur(24px)',
  bgSurface: 'rgba(255, 255, 255, 0.55)',
  bgSurfaceHover: 'rgba(255, 255, 255, 0.7)',
  bgCard: 'rgba(255, 255, 255, 0.45)',
  bgNavbar: 'rgba(255, 255, 255, 0.65)',
  border: 'rgba(255, 255, 255, 0.5)',
  borderSubtle: 'rgba(255, 255, 255, 0.25)',
  shadowSoft: '0 4px 24px rgba(0, 0, 0, 0.06), 0 1px 2px rgba(0, 0, 0, 0.04)',
  shadowMedium: '0 8px 32px rgba(0, 0, 0, 0.08), 0 2px 8px rgba(0, 0, 0, 0.04)',
  shadowElevated: '0 16px 48px rgba(0, 0, 0, 0.10), 0 4px 16px rgba(0, 0, 0, 0.06)',
  gradientPrimary: `linear-gradient(135deg, ${PURPLE}, ${TEAL})`,
  gradientAccent: `linear-gradient(135deg, ${PURPLE}, ${PINK})`,
  gradientSubtle: `linear-gradient(135deg, ${alpha(PURPLE, 0.08)}, ${alpha(TEAL, 0.08)})`,
  radius: 16,
  radiusSmall: 12,
  radiusLarge: 24,
};

// ── MUI Theme ───────────────────────────────────────────────────────
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: PURPLE,
      light: '#a78bfa',
      dark: '#5b21b6',
      contrastText: '#ffffff',
    },
    secondary: {
      main: TEAL,
      light: '#67e8f9',
      dark: '#0891b2',
      contrastText: '#ffffff',
    },
    success: { main: '#10b981', light: '#6ee7b7', dark: '#059669' },
    warning: { main: '#f59e0b', light: '#fcd34d', dark: '#d97706' },
    error:   { main: '#ef4444', light: '#fca5a5', dark: '#dc2626' },
    info:    { main: '#3b82f6', light: '#93c5fd', dark: '#2563eb' },
    background: {
      default: '#f0f2f5',
      paper: '#ffffff',
    },
    text: {
      primary: '#1e293b',
      secondary: '#64748b',
    },
    divider: 'rgba(0, 0, 0, 0.08)',
  },

  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica Neue", Arial, sans-serif',
    h1: { fontSize: '2.75rem', fontWeight: 800, letterSpacing: '-0.02em', lineHeight: 1.15 },
    h2: { fontSize: '2rem', fontWeight: 700, letterSpacing: '-0.01em', lineHeight: 1.2 },
    h3: { fontSize: '1.625rem', fontWeight: 700, letterSpacing: '-0.01em', lineHeight: 1.3 },
    h4: { fontSize: '1.375rem', fontWeight: 600, lineHeight: 1.35 },
    h5: { fontSize: '1.125rem', fontWeight: 600, lineHeight: 1.4 },
    h6: { fontSize: '1rem', fontWeight: 600, lineHeight: 1.5 },
    subtitle1: { fontWeight: 500, lineHeight: 1.5 },
    subtitle2: { fontWeight: 500, fontSize: '0.875rem', lineHeight: 1.5 },
    body1: { lineHeight: 1.6 },
    body2: { lineHeight: 1.6, fontSize: '0.875rem' },
    button: { textTransform: 'none', fontWeight: 600, letterSpacing: '0.01em' },
  },

  shape: { borderRadius: 12 },
  spacing: 8,

  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          background: 'linear-gradient(135deg, #ede9fe 0%, #e0f2fe 50%, #fce7f3 100%)',
          backgroundAttachment: 'fixed',
          minHeight: '100vh',
        },
      },
    },

    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: glassTokens.radiusSmall,
          padding: '10px 24px',
          fontWeight: 600,
          transition: 'all 0.2s ease',
        },
        contained: {
          background: glassTokens.gradientPrimary,
          boxShadow: `0 4px 16px ${alpha(PURPLE, 0.3)}`,
          '&:hover': {
            background: glassTokens.gradientPrimary,
            boxShadow: `0 6px 24px ${alpha(PURPLE, 0.4)}`,
            transform: 'translateY(-1px)',
          },
        },
        outlined: {
          borderColor: alpha(PURPLE, 0.3),
          '&:hover': {
            borderColor: PURPLE,
            background: alpha(PURPLE, 0.04),
          },
        },
      },
    },

    MuiPaper: {
      defaultProps: { elevation: 0 },
      styleOverrides: {
        root: {
          backgroundImage: 'none',
        },
      },
    },

    MuiCard: {
      defaultProps: { elevation: 0 },
      styleOverrides: {
        root: {
          background: glassTokens.bgCard,
          backdropFilter: glassTokens.blur,
          WebkitBackdropFilter: glassTokens.blur,
          border: `1px solid ${glassTokens.border}`,
          borderRadius: glassTokens.radius,
          boxShadow: glassTokens.shadowSoft,
          transition: 'all 0.25s ease',
          '&:hover': {
            boxShadow: glassTokens.shadowMedium,
            transform: 'translateY(-2px)',
          },
        },
      },
    },

    MuiAppBar: {
      defaultProps: { elevation: 0 },
      styleOverrides: {
        root: {
          background: glassTokens.bgNavbar,
          backdropFilter: glassTokens.blurHeavy,
          WebkitBackdropFilter: glassTokens.blurHeavy,
          borderBottom: `1px solid ${glassTokens.borderSubtle}`,
          boxShadow: glassTokens.shadowSoft,
          color: '#1e293b',
        },
      },
    },

    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          fontWeight: 500,
        },
        filled: {
          backdropFilter: glassTokens.blur,
        },
      },
    },

    MuiTableContainer: {
      styleOverrides: {
        root: {
          background: glassTokens.bgCard,
          backdropFilter: glassTokens.blur,
          WebkitBackdropFilter: glassTokens.blur,
          border: `1px solid ${glassTokens.border}`,
          borderRadius: glassTokens.radius,
          boxShadow: glassTokens.shadowSoft,
        },
      },
    },

    MuiLinearProgress: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          height: 8,
          backgroundColor: alpha(PURPLE, 0.1),
        },
        bar: {
          borderRadius: 8,
          background: glassTokens.gradientPrimary,
        },
      },
    },

    MuiAlert: {
      styleOverrides: {
        root: {
          borderRadius: glassTokens.radiusSmall,
          backdropFilter: glassTokens.blur,
        },
      },
    },

    MuiTooltip: {
      styleOverrides: {
        tooltip: {
          borderRadius: 8,
          backdropFilter: glassTokens.blur,
          background: 'rgba(30, 41, 59, 0.9)',
          fontSize: '0.8125rem',
          padding: '8px 14px',
        },
      },
    },

    MuiDialog: {
      styleOverrides: {
        paper: {
          background: glassTokens.bgSurface,
          backdropFilter: glassTokens.blurHeavy,
          WebkitBackdropFilter: glassTokens.blurHeavy,
          border: `1px solid ${glassTokens.border}`,
          borderRadius: glassTokens.radiusLarge,
          boxShadow: glassTokens.shadowElevated,
        },
      },
    },
  },
});

// Export tokens for use in custom components
export { glassTokens, PURPLE, TEAL, PINK };
export default theme;
