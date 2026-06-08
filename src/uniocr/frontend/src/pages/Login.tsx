import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { ScanText, Lock, KeyRound, Loader2, AlertTriangle } from 'lucide-react';

export default function Login() {
  const [password, setPassword] = useState('');
  const [totpCode, setTotpCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [needsPasswordChange, setNeedsPasswordChange] = useState(false);
  const [newPassword, setNewPassword] = useState('');
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      const res = await axios.post('/api/auth/login', {
        password,
        totp_code: totpCode || null
      });
      localStorage.setItem('token', res.data.access_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${res.data.access_token}`;
      
      if (res.data.requires_password_change) {
        setNeedsPasswordChange(true);
      } else {
        navigate('/');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      await axios.post('/api/config', { new_password: newPassword });
      // After changing password, they must login again or we can just let them in.
      // Let's force them to login again with the new password.
      localStorage.removeItem('token');
      delete axios.defaults.headers.common['Authorization'];
      setNeedsPasswordChange(false);
      setPassword('');
      setNewPassword('');
      setError('Password updated. Please log in with your new password.');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center relative z-10 p-4">
      <div className="glass-panel w-full max-w-md p-8 flex flex-col items-center relative overflow-hidden">
        
        {needsPasswordChange && (
          <div className="absolute inset-0 bg-black/80 backdrop-blur-md z-20 flex flex-col items-center justify-center p-8 text-center animate-in fade-in zoom-in duration-300">
            <AlertTriangle className="text-yellow-500 mb-4" size={48} />
            <h2 className="text-xl font-bold text-white mb-2">Security Alert</h2>
            <p className="text-white/70 text-sm mb-6">You are using the default admin password. For your security, you must set a new password before continuing.</p>
            
            <form onSubmit={handlePasswordChange} className="w-full flex flex-col gap-4">
              <input 
                type="password" 
                placeholder="New strong password" 
                className="glass-input w-full"
                value={newPassword}
                onChange={e => setNewPassword(e.target.value)}
                required
                minLength={6}
              />
              <button 
                type="submit" 
                disabled={loading}
                className="glass-button-primary w-full flex justify-center items-center h-10"
              >
                {loading ? <Loader2 className="animate-spin" /> : 'Update & Re-login'}
              </button>
            </form>
          </div>
        )}

        <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-primary to-purple-500 flex items-center justify-center shadow-xl mb-6">
          <ScanText className="text-white" size={32} />
        </div>
        <h1 className="text-3xl font-bold text-white mb-2">UniOCR</h1>
        <p className="text-white/50 mb-8 text-center">Secure console access</p>
        
        {error && (
          <div className={`w-full p-3 rounded-lg mb-6 text-sm text-center border ${error.includes('updated') ? 'bg-green-500/10 border-green-500/20 text-green-400' : 'bg-red-500/10 border-red-500/20 text-red-400'}`}>
            {error}
          </div>
        )}

        <form onSubmit={handleLogin} className="w-full flex flex-col gap-4">
          <div className="relative">
            <Lock className="absolute left-3 top-1/2 -translate-y-1/2 text-white/40" size={20} />
            <input
              type="password"
              placeholder="Admin Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="glass-input w-full pl-10"
              required
            />
          </div>
          
          <div className="relative">
            <KeyRound className="absolute left-3 top-1/2 -translate-y-1/2 text-white/40" size={20} />
            <input
              type="text"
              placeholder="2FA Code (If enabled)"
              value={totpCode}
              onChange={(e) => setTotpCode(e.target.value)}
              className="glass-input w-full pl-10"
            />
          </div>
          
          <button 
            type="submit" 
            disabled={loading || needsPasswordChange}
            className="glass-button-primary w-full mt-4 flex items-center justify-center gap-2"
          >
            {loading && !needsPasswordChange ? <Loader2 className="animate-spin" size={20} /> : 'Authenticate'}
          </button>
        </form>
      </div>
    </div>
  );
}
