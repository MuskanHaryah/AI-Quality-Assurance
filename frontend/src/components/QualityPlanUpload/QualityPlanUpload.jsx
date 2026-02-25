import { useState, useCallback } from 'react';
import {
  Box,
  Typography,
  Button,
  LinearProgress,
  Stack,
  Chip,
  alpha,
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import InsertDriveFileIcon from '@mui/icons-material/InsertDriveFile';
import FactCheckIcon from '@mui/icons-material/FactCheck';
import { glassTokens, PURPLE, TEAL } from '../../theme/theme';
import { GlassCard } from '../common/GlassCard';
import { formatFileSize } from '../../utils/helpers';

const VALID_TYPES = [
  'application/pdf',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
];
const MAX_SIZE = 10 * 1024 * 1024;

export default function QualityPlanUpload({ onUpload, uploading, progress }) {
  const [dragActive, setDragActive] = useState(false);
  const [file, setFile] = useState(null);
  const [error, setError] = useState(null);

  const validate = (f) => {
    if (!VALID_TYPES.includes(f.type)) {
      setError('Only PDF and DOCX files are accepted.');
      return false;
    }
    if (f.size > MAX_SIZE) {
      setError('File must be less than 10 MB.');
      return false;
    }
    return true;
  };

  const handleFile = useCallback((selectedFile) => {
    setError(null);
    if (!validate(selectedFile)) return;
    setFile(selectedFile);
  }, []);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(e.type === 'dragenter' || e.type === 'dragover');
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files?.[0]) handleFile(e.dataTransfer.files[0]);
  };

  const handleChange = (e) => {
    if (e.target.files?.[0]) handleFile(e.target.files[0]);
  };

  const handleSubmit = () => {
    if (file && onUpload) {
      onUpload(file);
    }
  };

  return (
    <GlassCard>
      <Stack spacing={2}>
        <Stack direction="row" alignItems="center" spacing={1.5}>
          <FactCheckIcon sx={{ color: PURPLE, fontSize: 28 }} />
          <Box>
            <Typography variant="h6" fontWeight={700}>
              Check Your Quality Plan
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Upload your Quality Plan (PDF or DOCX) to see how well it covers the quality
              factors identified in your SRS analysis.
            </Typography>
          </Box>
        </Stack>

        {/* Drop zone */}
        <Box
          component="label"
          htmlFor="qp-file-upload"
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            p: { xs: 3, sm: 4 },
            minHeight: 140,
            borderRadius: `${glassTokens.radiusSmall}px`,
            border: `2px dashed ${dragActive ? TEAL : 'rgba(100, 116, 139, 0.3)'}`,
            background: dragActive
              ? `linear-gradient(135deg, rgba(6,182,212,0.06), rgba(124,58,237,0.06))`
              : 'rgba(255,255,255,0.3)',
            cursor: uploading ? 'wait' : 'pointer',
            transition: 'all 0.25s ease',
            '&:hover': {
              borderColor: TEAL,
              background: `linear-gradient(135deg, rgba(6,182,212,0.04), rgba(124,58,237,0.04))`,
            },
          }}
        >
          <input
            id="qp-file-upload"
            type="file"
            accept=".pdf,.docx"
            onChange={handleChange}
            hidden
            disabled={uploading}
          />

          {file ? (
            <Stack alignItems="center" spacing={1}>
              <InsertDriveFileIcon sx={{ fontSize: 36, color: TEAL }} />
              <Typography variant="subtitle2" fontWeight={600}>
                {file.name}
              </Typography>
              <Chip label={formatFileSize(file.size)} size="small" />
            </Stack>
          ) : (
            <Stack alignItems="center" spacing={1}>
              <CloudUploadIcon sx={{ fontSize: 36, color: 'text.secondary' }} />
              <Typography variant="body2" color="text.secondary">
                Drop your Quality Plan here or click to browse
              </Typography>
              <Typography variant="caption" color="text.secondary">
                PDF or DOCX, max 10 MB
              </Typography>
            </Stack>
          )}
        </Box>

        {/* Progress */}
        {uploading && (
          <Box>
            <LinearProgress
              variant="determinate"
              value={progress}
              sx={{
                height: 6,
                borderRadius: 3,
                backgroundColor: alpha(TEAL, 0.1),
                '& .MuiLinearProgress-bar': {
                  background: `linear-gradient(90deg, ${TEAL}, ${PURPLE})`,
                  borderRadius: 3,
                },
              }}
            />
            <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5 }}>
              Analyzing quality plan… {progress}%
            </Typography>
          </Box>
        )}

        {/* Error */}
        {error && (
          <Typography variant="body2" color="error">
            {error}
          </Typography>
        )}

        {/* Submit button */}
        <Button
          variant="contained"
          onClick={handleSubmit}
          disabled={!file || uploading}
          startIcon={<FactCheckIcon />}
          sx={{
            alignSelf: 'flex-start',
            background: `linear-gradient(135deg, ${TEAL}, ${PURPLE})`,
            '&:hover': {
              background: `linear-gradient(135deg, ${PURPLE}, ${TEAL})`,
            },
          }}
        >
          {uploading ? 'Analyzing…' : 'Analyze Quality Plan'}
        </Button>
      </Stack>
    </GlassCard>
  );
}
