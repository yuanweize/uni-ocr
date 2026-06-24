import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import OcrConsole from './pages/OcrConsole';
import Settings from './pages/Settings';
import ApiDocs from './pages/ApiDocs';
import Layout from './components/Layout';
import { useEffect, useState } from 'react';
import axios from 'axios';



// Protected Route Wrapper
const ProtectedRoute = ({ children, isPublic, requiresAuth = false }: { children: React.ReactNode, isPublic?: boolean, requiresAuth?: boolean }) => {
  const token = localStorage.getItem('token');
  if (requiresAuth && !token) return <Navigate to="/login" replace />;
  if (isPublic === false && !token) return <Navigate to="/login" replace />;
  return <>{children}</>;
};

function App() {
  const [isPublic, setIsPublic] = useState<boolean | null>(null);

  useEffect(() => {
    axios.get('/api/config').then(res => {
      setIsPublic(res.data.is_ocr_public);
    }).catch(() => {
      setIsPublic(true); // default fallback
    });
  }, []);

  if (isPublic === null) return <div className="min-h-screen flex items-center justify-center text-white">Loading...</div>;

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        
        <Route element={<Layout />}>
          <Route path="/" element={
            <ProtectedRoute isPublic={isPublic}><OcrConsole isPublic={isPublic!} /></ProtectedRoute>
          } />
          <Route path="/docs-ui" element={
            <ProtectedRoute isPublic={isPublic}><ApiDocs /></ProtectedRoute>
          } />
          <Route path="/settings" element={
            <ProtectedRoute requiresAuth><Settings /></ProtectedRoute>
          } />
        </Route>
        
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
