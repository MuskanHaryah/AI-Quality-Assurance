import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  IconButton,
  Box,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  useMediaQuery,
  useTheme,
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import HomeIcon from '@mui/icons-material/Home';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import DashboardIcon from '@mui/icons-material/Dashboard';
import AutoGraphIcon from '@mui/icons-material/AutoGraph';
import { glassTokens, PURPLE, TEAL } from '../../theme/theme';

const navItems = [
  { label: 'Home', path: '/', icon: <HomeIcon /> },
  { label: 'Upload', path: '/upload', icon: <UploadFileIcon /> },
  { label: 'Dashboard', path: '/dashboard', icon: <DashboardIcon /> },
];

export default function Navigation() {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const handleNavigate = (path) => {
    navigate(path);
    setDrawerOpen(false);
  };

  const isActive = (path) => location.pathname === path;

  return (
    <>
      <AppBar position="fixed">
        <Toolbar sx={{ justifyContent: 'space-between' }}>
          {/* Logo */}
          <Box
            sx={{ display: 'flex', alignItems: 'center', cursor: 'pointer', gap: 1 }}
            onClick={() => handleNavigate('/')}
          >
            <AutoGraphIcon
              sx={{
                fontSize: 28,
                background: `linear-gradient(135deg, ${PURPLE}, ${TEAL})`,
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}
            />
            <Typography
              variant="h6"
              sx={{
                fontWeight: 800,
                background: `linear-gradient(135deg, ${PURPLE}, ${TEAL})`,
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                letterSpacing: '-0.02em',
              }}
            >
              QualityMapAI
            </Typography>
          </Box>

          {/* Desktop Nav */}
          {!isMobile && (
            <Box sx={{ display: 'flex', gap: 1 }}>
              {navItems.map((item) => (
                <Button
                  key={item.path}
                  onClick={() => handleNavigate(item.path)}
                  startIcon={item.icon}
                  sx={{
                    color: isActive(item.path) ? PURPLE : 'text.secondary',
                    fontWeight: isActive(item.path) ? 700 : 500,
                    position: 'relative',
                    '&::after': isActive(item.path)
                      ? {
                          content: '""',
                          position: 'absolute',
                          bottom: 4,
                          left: '20%',
                          right: '20%',
                          height: 3,
                          borderRadius: 2,
                          background: `linear-gradient(90deg, ${PURPLE}, ${TEAL})`,
                        }
                      : {},
                    '&:hover': {
                      color: PURPLE,
                      backgroundColor: 'rgba(124, 58, 237, 0.04)',
                    },
                  }}
                >
                  {item.label}
                </Button>
              ))}
            </Box>
          )}

          {/* Mobile Hamburger */}
          {isMobile && (
            <IconButton
              edge="end"
              onClick={() => setDrawerOpen(true)}
              sx={{ color: 'text.primary' }}
              aria-label="open navigation menu"
            >
              <MenuIcon />
            </IconButton>
          )}
        </Toolbar>
      </AppBar>

      {/* Mobile Drawer */}
      <Drawer
        anchor="right"
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        PaperProps={{
          sx: {
            width: 260,
            background: glassTokens.bgSurface,
            backdropFilter: glassTokens.blurHeavy,
            WebkitBackdropFilter: glassTokens.blurHeavy,
            borderLeft: `1px solid ${glassTokens.border}`,
          },
        }}
      >
        <Box sx={{ pt: 2 }}>
          <Typography
            variant="h6"
            sx={{
              px: 2,
              pb: 2,
              fontWeight: 800,
              background: `linear-gradient(135deg, ${PURPLE}, ${TEAL})`,
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            QualityMapAI
          </Typography>
          <List>
            {navItems.map((item) => (
              <ListItem key={item.path} disablePadding>
                <ListItemButton
                  onClick={() => handleNavigate(item.path)}
                  selected={isActive(item.path)}
                  sx={{
                    mx: 1,
                    borderRadius: 2,
                    '&.Mui-selected': {
                      background: `linear-gradient(135deg, rgba(124,58,237,0.1), rgba(6,182,212,0.1))`,
                      '&:hover': {
                        background: `linear-gradient(135deg, rgba(124,58,237,0.15), rgba(6,182,212,0.15))`,
                      },
                    },
                  }}
                >
                  <ListItemIcon sx={{ color: isActive(item.path) ? PURPLE : 'text.secondary', minWidth: 40 }}>
                    {item.icon}
                  </ListItemIcon>
                  <ListItemText
                    primary={item.label}
                    primaryTypographyProps={{
                      fontWeight: isActive(item.path) ? 700 : 500,
                      color: isActive(item.path) ? PURPLE : 'text.primary',
                    }}
                  />
                </ListItemButton>
              </ListItem>
            ))}
          </List>
        </Box>
      </Drawer>
    </>
  );
}
