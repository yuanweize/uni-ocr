import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import axios from 'axios'

// Global Axios Config
axios.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  // Only attach token to internal API requests
  if (token && (config.url?.startsWith('/api') || config.url?.startsWith(window.location.origin))) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

axios.interceptors.response.use(
  (response) => response,
  (error) => {
    // Only handle 401 for internal API requests
    const isInternalRequest = error.config?.url?.startsWith('/api') || error.config?.url?.startsWith(window.location.origin);
    if (isInternalRequest && error.response?.status === 401) {
      localStorage.removeItem('token');
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
