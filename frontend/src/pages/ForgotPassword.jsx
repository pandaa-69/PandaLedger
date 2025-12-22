import React, { useState } from 'react';
import { Mail, ArrowLeft, Send } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { getCookie } from '../utils/csrf';
import API_URL from './config';


const ForgotPassword = () => {
    const navigate = useNavigate();
    const [email, setEmail] = useState('');
    const [message, setMessage] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        
        try {
            const res = await fetch(`${API_URL}/api/auth/reset-password/`, {
                method: 'POST',
                headers: { 
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie('csrftoken')
                },
                body: JSON.stringify({ email }),
                credentials:'include'
            });
            const data = await res.json();
            
            if (res.ok) {
                setMessage("✅ Check your email for the link!");
            } else {
                setMessage("❌ " + data.error);
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
                
                {/* Header */}
                <div className="text-center space-y-2">
                    <button onClick={() => navigate('/login')} className="absolute top-8 left-8 p-2 bg-white/5 rounded-full hover:bg-white/10 transition-colors">
                        <ArrowLeft size={20} />
                    </button>
                    <h1 className="text-3xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">Reset Password</h1>
                    <p className="text-gray-400">Enter your email to receive a recovery link.</p>
                </div>

                {/* Form */}
                <div className="bg-gray-900/50 p-8 rounded-2xl border border-white/10 backdrop-blur-md">
                    <div className="space-y-4">
                        <div className="space-y-2">
                            <label className="text-xs font-bold text-gray-500 uppercase tracking-wider ml-1">Email Address</label>
                            <div className="flex items-center gap-3 bg-white/5 border border-white/10 p-4 rounded-xl focus-within:border-cyan-500/50 transition-colors">
                                <Mail className="text-gray-400" size={20} />
                                <input 
                                    type="email" 
                                    value={email} 
                                    onChange={(e) => setEmail(e.target.value)}
                                    placeholder="your@email.com"
                                    className="bg-transparent w-full outline-none font-medium text-white placeholder-gray-600"
                                />
                            </div>
                        </div>

                        <button 
                            onClick={handleSubmit}
                            disabled={loading}
                            className="w-full py-4 bg-white text-black font-bold rounded-xl flex items-center justify-center gap-2 hover:bg-gray-200 transition-all active:scale-95 disabled:opacity-50"
                        >
                            {loading ? "Sending..." : <><Send size={18} /> Send Link</>}
                        </button>
                    </div>

                    {message && (
                        <div className={`mt-6 text-center font-bold p-3 rounded-lg animate-pulse ${message.includes('Error') || message.includes('❌') ? 'text-red-400' : 'text-green-400'}`}>
                            {message}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default ForgotPassword;