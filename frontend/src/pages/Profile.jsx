import React, { useState, useEffect } from 'react';
import { User, Mail, Lock, Save, ArrowLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { getCookie } from '../utils/csrf';
const Profile = () => {
    const navigate = useNavigate();
    const [user, setUser] = useState({ username: '', email: '' });
    const [passwords, setPasswords] = useState({ new: '' });
    const [loading, setLoading] = useState(true);
    const [message, setMessage] = useState('');

    useEffect(() => {
        // Fetch current user details
        fetch('http://127.0.0.1:8000/api/user/profile/', {
            method:'GET',
            credentials:'include',
        })
            .then(res => {
                if (res.status === 403) {
                    navigate('/login'); // Redirect if not logged in
                    return null;
                }
                return res.json();
            })
            .then(data => {
                if (data) {
                    setUser(data);
                    setLoading(false);
                }
            })
            .catch(err => console.error(err));
    }, [navigate]);

    const handleSave = async () => {
        const payload = { email: user.email };
        if (passwords.new) payload.new_password = passwords.new;

        const res = await fetch('http://127.0.0.1:8000/api/user/profile/', {
            method: 'PUT',
            headers: { 
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie('csrftoken')
            },
            credentials:'include',
            body: JSON.stringify(payload)
        });
        
        if (res.ok) {
            setMessage("✅ Settings Saved!");
            setPasswords({ new: '' }); // Clear password field
            setTimeout(() => setMessage(""), 3000);
        } else {
            setMessage("❌ Error saving settings");
        }
    };

    if (loading) return <div className="min-h-screen bg-black text-white flex items-center justify-center">Loading...</div>;

    return (
        <div className="min-h-screen bg-black text-white p-6 pb-24 font-sans">
            <div className="max-w-md mx-auto animate-in fade-in slide-in-from-bottom-4 duration-700">
                
                {/* Header */}
                <div className="flex items-center gap-4 mb-8">
                    <button onClick={() => navigate(-1)} className="p-2 bg-white/5 rounded-full hover:bg-white/10 transition-colors">
                        <ArrowLeft size={20} />
                    </button>
                    <h1 className="text-2xl font-bold">Account Settings</h1>
                </div>

                {/* Avatar Card */}
                <div className="flex flex-col items-center gap-3 p-8 bg-gray-900/50 rounded-2xl border border-white/10 mb-8 backdrop-blur-md">
                    <div className="h-24 w-24 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white shadow-xl shadow-indigo-500/20">
                        <User size={40} />
                    </div>
                    <div className="text-center">
                        <h2 className="text-xl font-bold text-white">{user.username}</h2>
                        <p className="text-sm text-gray-400">Member since {user.date_joined}</p>
                    </div>
                </div>

                {/* Form Fields */}
                <div className="space-y-6">
                    
                    {/* Email */}
                    <div className="space-y-2">
                        <label className="text-xs font-bold text-gray-500 uppercase tracking-wider ml-1">Email Address</label>
                        <div className="flex items-center gap-3 bg-white/5 border border-white/10 p-4 rounded-xl focus-within:border-indigo-500/50 transition-colors">
                            <Mail className="text-gray-400" size={20} />
                            <input 
                                type="email" 
                                value={user.email} 
                                onChange={(e) => setUser({...user, email: e.target.value})}
                                placeholder="Add your email"
                                className="bg-transparent w-full outline-none font-medium text-white placeholder-gray-600"
                            />
                        </div>
                    </div>

                    {/* Password */}
                    <div className="space-y-2">
                        <label className="text-xs font-bold text-gray-500 uppercase tracking-wider ml-1">New Password</label>
                        <div className="flex items-center gap-3 bg-white/5 border border-white/10 p-4 rounded-xl focus-within:border-indigo-500/50 transition-colors">
                            <Lock className="text-gray-400" size={20} />
                            <input 
                                type="password" 
                                value={passwords.new} 
                                onChange={(e) => setPasswords({...passwords, new: e.target.value})}
                                placeholder="Set new password (optional)"
                                className="bg-transparent w-full outline-none font-medium text-white placeholder-gray-600"
                            />
                        </div>
                    </div>

                    {/* Save Button */}
                    <button 
                        onClick={handleSave}
                        className="w-full mt-8 py-4 bg-white text-black font-bold rounded-xl flex items-center justify-center gap-2 hover:bg-gray-200 transition-all active:scale-95 shadow-lg hover:shadow-white/10"
                    >
                        <Save size={20} /> Save Changes
                    </button>

                    {message && (
                        <div className={`text-center font-bold p-3 rounded-lg animate-pulse ${message.includes('Error') ? 'text-red-400' : 'text-green-400'}`}>
                            {message}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default Profile;