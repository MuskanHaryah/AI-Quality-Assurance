import { format, formatDistanceToNow } from 'date-fns';

/**
 * Map risk level to theme colour key.
 */
export const riskColor = (level) => {
  const map = {
    Low: 'success',
    Medium: 'warning',
    High: 'error',
    Critical: 'error',
  };
  return map[level] || 'info';
};

/**
 * Map risk level to hex colour for SVGs / charts.
 */
export const riskHex = (level) => {
  const map = {
    Low: '#10b981',
    Medium: '#f59e0b',
    High: '#ef4444',
    Critical: '#dc2626',
  };
  return map[level] || '#64748b';
};

/**
 * ISO 9126 category colour palette for charts.
 */
export const categoryColors = {
  Functionality: '#7c3aed',
  Reliability: '#06b6d4',
  Usability: '#10b981',
  Efficiency: '#f59e0b',
  Maintainability: '#3b82f6',
  Portability: '#ec4899',
  Security: '#ef4444',
};

/**
 * Format a file size in bytes to a human string.
 */
export const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
};

/**
 * Format ISO date string for display.
 */
export const formatDate = (isoStr) => {
  if (!isoStr) return '—';
  try {
    return format(new Date(isoStr), 'MMM d, yyyy h:mm a');
  } catch {
    return isoStr;
  }
};

/**
 * "2 hours ago" style relative date.
 */
export const formatRelative = (isoStr) => {
  if (!isoStr) return '—';
  try {
    return formatDistanceToNow(new Date(isoStr), { addSuffix: true });
  } catch {
    return isoStr;
  }
};

/**
 * Clamp a number to 0-100 for score display.
 */
export const clampScore = (n) => Math.max(0, Math.min(100, Number(n) || 0));
