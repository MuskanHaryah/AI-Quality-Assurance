import { useState, useCallback } from 'react';
import { Box, Typography, LinearProgress, Chip, Stack } from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import InsertDriveFileIcon from '@mui/icons-material/InsertDriveFile';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import { glassTokens, PURPLE, TEAL } from '../../theme/theme';
import { formatFileSize } from '../../utils/helpers';

const VALID_TYPES = [
  'application/pdf',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
];
const MAX_SIZE = 10 * 1024 * 1024; // 10 MB

export default function FileUpload({ onFileSelect, uploading, progress }) {
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

  const handleFile = useCallback(
    (selectedFile) => {
      setError(null);
      if (!validate(selectedFile)) return;
      setFile(selectedFile);
      onFileSelect(selectedFile);
    },
    [onFileSelect]
  );

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

  return (
    <Box>
      <Box
        component="label"
        htmlFor="file-upload"
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          p: { xs: 4, sm: 6 },
          minHeight: 200,
          borderRadius: `${glassTokens.radius}px`,
          border: `2px dashed ${dragActive ? PURPLE : 'rgba(100, 116, 139, 0.3)'}`,
          background: dragActive
            ? `linear-gradient(135deg, rgba(124,58,237,0.06), rgba(6,182,212,0.06))`
            : glassTokens.bgCard,
          backdropFilter: glassTokens.blur,
          WebkitBackdropFilter: glassTokens.blur,
          boxShadow: dragActive ? glassTokens.shadowMedium : glassTokens.shadowSoft,
          cursor: uploading ? 'default' : 'pointer',
          transition: 'all 0.25s ease',
          '&:hover': uploading
            ? {}
            : {
                borderColor: PURPLE,
                boxShadow: glassTokens.shadowMedium,
                background: `linear-gradient(135deg, rgba(124,58,237,0.04), rgba(6,182,212,0.04))`,
              },
        }}
      >
        <input
          id="file-upload"
          type="file"
          accept=".pdf,.docx"
          style={{ display: 'none' }}
          onChange={handleChange}
          disabled={uploading}
        />

        {file ? (
          <Stack alignItems="center" spacing={1.5}>
            <Box
              sx={{
                p: 2,
                borderRadius: '50%',
                background: `linear-gradient(135deg, rgba(124,58,237,0.1), rgba(6,182,212,0.1))`,
                display: 'flex',
              }}
            >
              <InsertDriveFileIcon sx={{ fontSize: 40, color: PURPLE }} />
            </Box>
            <Stack alignItems="center" spacing={0.5}>
              <Stack direction="row" alignItems="center" spacing={1}>
                <Typography variant="subtitle1" fontWeight={600}>
                  {file.name}
                </Typography>
                <CheckCircleIcon sx={{ fontSize: 18, color: 'success.main' }} />
              </Stack>
              <Chip
                label={formatFileSize(file.size)}
                size="small"
                variant="outlined"
                sx={{ borderColor: 'divider' }}
              />
            </Stack>
            {!uploading && (
              <Typography variant="body2" color="text.secondary">
                Click or drop to replace
              </Typography>
            )}
          </Stack>
        ) : (
          <Stack alignItems="center" spacing={1.5}>
            <Box
              sx={{
                p: 2,
                borderRadius: '50%',
                background: `linear-gradient(135deg, rgba(124,58,237,0.1), rgba(6,182,212,0.1))`,
                display: 'flex',
              }}
            >
              <CloudUploadIcon sx={{ fontSize: 48, color: PURPLE }} />
            </Box>
            <Typography variant="h6" fontWeight={600}>
              Drag & drop your file here
            </Typography>
            <Typography variant="body2" color="text.secondary">
              or click to browse — PDF, DOCX up to 10 MB
            </Typography>
          </Stack>
        )}
      </Box>

      {/* Upload progress */}
      {uploading && (
        <Box sx={{ mt: 2 }}>
          <LinearProgress variant="determinate" value={progress} />
          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5, textAlign: 'center' }}>
            Uploading… {progress}%
          </Typography>
        </Box>
      )}

      {/* Validation error */}
      {error && (
        <Typography variant="body2" color="error" sx={{ mt: 1.5, textAlign: 'center' }}>
          {error}
        </Typography>
      )}
    </Box>
  );
}
