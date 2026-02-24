import { createContext, useContext, useState, useCallback } from 'react';

const AppContext = createContext();

export const AppProvider = ({ children }) => {
  const [currentAnalysis, setCurrentAnalysis] = useState(null);
  const [recentAnalyses, setRecentAnalyses] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(false);

  const addNotification = useCallback((message, severity = 'info') => {
    const id = Date.now();
    setNotifications((prev) => [...prev, { id, message, severity }]);
    setTimeout(() => {
      setNotifications((prev) => prev.filter((n) => n.id !== id));
    }, 5000);
  }, []);

  const removeNotification = useCallback((id) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id));
  }, []);

  const value = {
    currentAnalysis,
    setCurrentAnalysis,
    recentAnalyses,
    setRecentAnalyses,
    notifications,
    addNotification,
    removeNotification,
    loading,
    setLoading,
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
};

export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
};

export default AppContext;
