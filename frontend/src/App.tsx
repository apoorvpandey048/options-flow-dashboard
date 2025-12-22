import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, Navigate, useNavigate } from 'react-router-dom';
import { Activity, TrendingUp, LogOut } from 'lucide-react';
import OptionsFlowMonitor from './components/OptionsFlowMonitor';
import StrategyBacktester from './components/StrategyBacktester';
import Home from './components/Home';
import Login from './components/Login';
import { apiService } from './services/api';

// Protected Route Component
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);

  useEffect(() => {
    const verifyAuth = async () => {
      const token = localStorage.getItem('token');
      if (!token) {
        setIsAuthenticated(false);
        return;
      }

      const result = await apiService.verifyToken();
      setIsAuthenticated(!!result);
    };

    verifyAuth();
  }, []);

  if (isAuthenticated === null) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-gray-900">
        <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-blue-500 mb-4"></div>
        <p className="text-gray-400">Verifying authentication...</p>
      </div>
    );
  }

  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />;
};

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);

  useEffect(() => {
    const token = localStorage.getItem('token');
    setIsAuthenticated(!!token);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    setIsAuthenticated(false);
    // Force reload to clear all state
    window.location.href = '/login';
  };

  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black text-white">
        {/* Navigation */}
        {isAuthenticated && (
          <nav className="bg-gray-900 bg-opacity-80 backdrop-blur-lg border-b border-gray-700">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex items-center justify-between h-16">
                <div className="flex items-center">
                  <Link to="/" className="flex items-center gap-2 text-xl font-bold">
                    <Activity className="w-6 h-6 text-blue-400" />
                    <span>Options Flow Pro</span>
                  </Link>
                </div>
                <div className="flex gap-4">
                  <Link
                    to="/monitor"
                    className="px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors flex items-center gap-2"
                  >
                    <Activity className="w-4 h-4" />
                    Monitor
                  </Link>
                  <Link
                    to="/backtest"
                    className="px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors flex items-center gap-2"
                  >
                    <TrendingUp className="w-4 h-4" />
                    Backtest
                  </Link>
                  <button
                    onClick={handleLogout}
                    className="px-4 py-2 rounded-lg hover:bg-red-600 transition-colors flex items-center gap-2"
                  >
                    <LogOut className="w-4 h-4" />
                    Logout
                  </button>
                </div>
              </div>
            </div>
          </nav>
        )}

        {/* Routes */}
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Home />
              </ProtectedRoute>
            }
          />
          <Route
            path="/monitor"
            element={
              <ProtectedRoute>
                <OptionsFlowMonitor />
              </ProtectedRoute>
            }
          />
          <Route
            path="/backtest"
            element={
              <ProtectedRoute>
                <StrategyBacktester />
              </ProtectedRoute>
            }
          />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
