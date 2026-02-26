import { useState, useMemo } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  TableSortLabel,
  Chip,
  Typography,
  TextField,
  InputAdornment,
  Stack,
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  alpha,
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import { categoryColors } from '../../utils/helpers';

const ROWS_PER_PAGE_OPTIONS = [10, 25, 50];

export default function RequirementsTable({ requirements = [] }) {
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('All');
  const [orderBy, setOrderBy] = useState('confidence');
  const [order, setOrder] = useState('desc');

  const categories = useMemo(
    () => ['All', ...new Set(requirements.map((r) => r.category).filter(Boolean))],
    [requirements]
  );

  const filtered = useMemo(() => {
    let data = [...requirements];

    // Search
    if (search) {
      const lower = search.toLowerCase();
      data = data.filter(
        (r) =>
          r.text?.toLowerCase().includes(lower) ||
          r.category?.toLowerCase().includes(lower)
      );
    }

    // Category filter
    if (categoryFilter !== 'All') {
      data = data.filter((r) => r.category === categoryFilter);
    }

    // Sort
    data.sort((a, b) => {
      let aVal = a[orderBy] ?? '';
      let bVal = b[orderBy] ?? '';
      if (typeof aVal === 'string') {
        aVal = aVal.toLowerCase();
        bVal = bVal.toLowerCase();
      }
      if (aVal < bVal) return order === 'asc' ? -1 : 1;
      if (aVal > bVal) return order === 'asc' ? 1 : -1;
      return 0;
    });

    return data;
  }, [requirements, search, categoryFilter, orderBy, order]);

  const handleSort = (column) => {
    const isAsc = orderBy === column && order === 'asc';
    setOrder(isAsc ? 'desc' : 'asc');
    setOrderBy(column);
  };

  if (requirements.length === 0) {
    return (
      <Typography color="text.secondary" sx={{ py: 4, textAlign: 'center' }}>
        No requirements to display.
      </Typography>
    );
  }

  return (
    <Box>
      {/* Filters */}
      <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} sx={{ mb: 2 }}>
        <TextField
          size="small"
          placeholder="Search requirements…"
          value={search}
          onChange={(e) => { setSearch(e.target.value); setPage(0); }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon sx={{ color: 'text.secondary', fontSize: 20 }} />
              </InputAdornment>
            ),
          }}
          sx={{ flex: 1, maxWidth: { sm: 320 } }}
        />
        <FormControl size="small" sx={{ minWidth: 160 }}>
          <InputLabel>Category</InputLabel>
          <Select
            value={categoryFilter}
            label="Category"
            onChange={(e) => { setCategoryFilter(e.target.value); setPage(0); }}
          >
            {categories.map((c) => (
              <MenuItem key={c} value={c}>{c}</MenuItem>
            ))}
          </Select>
        </FormControl>
      </Stack>

      {/* Table */}
      <TableContainer>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell sx={{ fontWeight: 700, width: 48 }}>#</TableCell>
              <TableCell sx={{ fontWeight: 700 }}>
                <TableSortLabel
                  active={orderBy === 'text'}
                  direction={orderBy === 'text' ? order : 'asc'}
                  onClick={() => handleSort('text')}
                >
                  Requirement
                </TableSortLabel>
              </TableCell>
              <TableCell sx={{ fontWeight: 700, width: 150 }}>
                <TableSortLabel
                  active={orderBy === 'category'}
                  direction={orderBy === 'category' ? order : 'asc'}
                  onClick={() => handleSort('category')}
                >
                  Category
                </TableSortLabel>
              </TableCell>
              <TableCell sx={{ fontWeight: 700, width: 120 }} align="right">
                <TableSortLabel
                  active={orderBy === 'confidence'}
                  direction={orderBy === 'confidence' ? order : 'asc'}
                  onClick={() => handleSort('confidence')}
                >
                  Confidence
                </TableSortLabel>
              </TableCell>
              <TableCell sx={{ fontWeight: 700, width: 120 }}>Strength</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filtered
              .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
              .map((req, idx) => {
                const color = categoryColors[req.category] || '#64748b';
                // Backend sends confidence as 0-100, no need to multiply
                const conf = Math.round(req.confidence ?? 0);
                return (
                  <TableRow
                    key={req.id ?? idx}
                    hover
                    sx={{ '&:last-child td': { borderBottom: 0 } }}
                  >
                    <TableCell>
                      <Typography variant="body2" color="text.secondary">
                        {page * rowsPerPage + idx + 1}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" sx={{ lineHeight: 1.5 }}>
                        {req.text}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={req.category}
                        size="small"
                        sx={{
                          backgroundColor: alpha(color, 0.1),
                          color,
                          fontWeight: 600,
                          fontSize: '0.75rem',
                        }}
                      />
                    </TableCell>
                    <TableCell align="right">
                      <Typography
                        variant="body2"
                        fontWeight={600}
                        sx={{
                          color: conf >= 80 ? 'success.dark' : conf >= 50 ? 'warning.dark' : 'error.dark',
                        }}
                      >
                        {conf}%
                      </Typography>
                    </TableCell>
                    <TableCell>
                      {req.keyword_strength ? (
                        <Chip
                          label={req.keyword_strength}
                          size="small"
                          variant="outlined"
                          sx={{
                            textTransform: 'capitalize',
                            fontSize: '0.7rem',
                            height: 22,
                          }}
                        />
                      ) : (
                        <Typography variant="body2" color="text.secondary">—</Typography>
                      )}
                    </TableCell>
                  </TableRow>
                );
              })}
          </TableBody>
        </Table>
      </TableContainer>

      <TablePagination
        component="div"
        count={filtered.length}
        page={page}
        onPageChange={(_, newPage) => setPage(newPage)}
        rowsPerPage={rowsPerPage}
        onRowsPerPageChange={(e) => {
          setRowsPerPage(parseInt(e.target.value, 10));
          setPage(0);
        }}
        rowsPerPageOptions={ROWS_PER_PAGE_OPTIONS}
        sx={{ borderTop: '1px solid', borderColor: 'divider' }}
      />
    </Box>
  );
}
