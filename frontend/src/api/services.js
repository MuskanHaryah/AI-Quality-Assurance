import apiClient from './client';

/**
 * Upload a PDF or DOCX file.
 * @param {File} file
 * @param {function} onProgress  – receives 0-100 percent
 * @returns {{ success, file_id, filename, file_type, size_bytes, size_mb, status, message }}
 */
export const uploadFile = async (file, onProgress) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await apiClient.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 60000,
    onUploadProgress: (progressEvent) => {
      if (onProgress && progressEvent.total) {
        const pct = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        onProgress(pct);
      }
    },
  });
  return response.data;
};

/**
 * Run the full analysis pipeline on an uploaded file.
 * @param {string} fileId
 * @returns full analysis result object
 */
export const analyzeFile = async (fileId) => {
  const response = await apiClient.post('/analyze', { file_id: fileId });
  return response.data;
};

/**
 * Quick-classify one requirement text.
 * @param {string} text
 */
export const predictRequirement = async (text) => {
  const response = await apiClient.post('/predict', { text });
  return response.data;
};

/**
 * Quick-classify multiple requirement texts.
 * @param {string[]} texts
 */
export const predictBatch = async (texts) => {
  const response = await apiClient.post('/predict', { texts });
  return response.data;
};

/**
 * Get a full analysis report by ID.
 * @param {string} analysisId
 */
export const getReport = async (analysisId) => {
  const response = await apiClient.get(`/report/${analysisId}`);
  return response.data;
};

/**
 * Get the 20 most recent analyses (dashboard).
 */
export const getRecentAnalyses = async () => {
  const response = await apiClient.get('/analyses');
  return response.data;
};

/**
 * Health check – is the backend alive?
 */
export const checkHealth = async () => {
  const response = await apiClient.get('/health');
  return response.data;
};
