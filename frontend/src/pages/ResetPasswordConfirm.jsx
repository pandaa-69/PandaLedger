import React, { useState } from 'react';
import { Lock, ArrowLeft, CheckCircle } from 'lucide-react';
import { useNavigate, useParams } from 'react-router-dom';

const ResetPasswordConfirm = () => {
    const navigate = useNavigate();
    const { uid, token } = useParams(); // Capture the secure codes from the URL
    const [password, setPassword] = useState('');
    const [message, setMessage] = useState('');
    const [loading, setLoading] = useState(false);
    const [success, setSuccess] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        
        try {
            const res = await fetch('http://127.0.0.1:8000/api/auth/reset-password-confirm/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ uid, token, new_password: password })
            });
            const data = await res.json();
            
            if (res.ok) {
                setSuccess(true);
                setMessage("✅ Password reset successful! Redirecting...");
                setTimeout(() => navigate('/login'), 3000);
            } else {
                setMessage("❌ " + (data.error || "Invalid link or expired token."));
            }
        } catch (error) {
            setMessage("❌ Network error");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-black text-white flex items-center justify-center p-4">
            <div className="w-full max-w-md space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
                
                <div className="text-center space-y-2">
                    <h1 className="text-3xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">New Password</h1>
                    <p className="text-gray-400">Create a secure password for your account.</p>
                </div>

                <div className="bg-gray-900/50 p-8 rounded-2xl border border-white/10 backdrop-blur-md">
                    {!success ? (
                        <div className="space-y-4">
                            <div className="space-y-2">
                                <label className="text-xs font-bold text-gray-500 uppercase tracking-wider ml-1">New Password</label>
                                <div className="flex items-center gap-3 bg-white/5 border border-white/10 p-4 rounded-xl focus-within:border-cyan-500/50 transition-colors">
                                    <Lock className="text-gray-400" size={20} />
                                    <input 
                                        type="password" 
                                        value={password} 
                                        onChange={(e) => setPassword(e.target.value)}
                                        placeholder="••••••••"
                                        className="bg-transparent w-full outline-none font-medium text-white placeholder-gray-600"
                                    />
                                </div>
                            </div>

                            <button 
                                onClick={handleSubmit}
                                disabled={loading || password.length < 4}
                                className="w-full py-4 bg-white text-black font-bold rounded-xl flex items-center justify-center gap-2 hover:bg-gray-200 transition-all active:scale-95 disabled:opacity-50"
                            >
                                {loading ? "Updating..." : "Reset Password"}
                            </button>
                            
                            {message && <div className="text-center font-bold text-red-400">{message}</div>}
                        </div>
                    ) : (
                        <div className="flex flex-col items-center gap-4 py-8">
                            <CheckCircle size={64} className="text-green-400 animate-bounce" />
                            <h2 className="text-xl font-bold text-white">All Done!</h2>
                            <p className="text-gray-400 text-center">{message}</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default ResetPasswordConfirm;