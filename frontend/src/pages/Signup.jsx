import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Loader2, UserPlus, Eye, EyeOff, Mail } from "lucide-react"; // Added Mail icon
import { getCookie } from '../utils/csrf';
import API_URL from "../config";

function Signup() {
  // 1. Added 'email' to initial state
  const [formData, setFormData] = useState({ username: "", email: "", password: "" });
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    setLoading(true);

    fetch(`${API_URL}/api/auth/signup/`, {
      method: "POST",
      headers: { 
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie('csrftoken')
      },
      body: JSON.stringify(formData),
      credentials: "include"
    })
      .then((res) => {
        if (!res.ok) {
          // Try to extract the specific error message from backend
          return res.json().then(data => { throw new Error(data.error || "Signup failed") });
        }
        return res.json();
      })
      .then(() => {
        alert("Account created! Please log in.");
        navigate("/login");
      })
      .catch((err) => {
        alert(err.message); // Show the specific error (like "Email taken")
        setLoading(false);
      });
  };

  return (
    <div className="flex min-h-[80vh] items-center justify-center px-4">
      <div className="w-full max-w-md rounded-2xl border border-white/10 bg-black/40 p-8 shadow-2xl backdrop-blur-xl animate-in fade-in slide-in-from-bottom-4 duration-700">
        
        <div className="mb-8 text-center">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-cyan-500/20 text-cyan-400">
            <UserPlus size={24} />
          </div>
          <h2 className="text-2xl font-bold text-white">Create Account</h2>
          <p className="text-sm text-gray-400">Join PandaLedger today.</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          
          {/* USERNAME */}
          <div className="space-y-1">
            <label className="text-xs font-bold uppercase tracking-wider text-gray-500">
              Choose Username
            </label>
            <input
              type="text"
              placeholder="Pick a unique name"
              required
              className="w-full rounded-lg border border-white/10 bg-white/5 px-4 py-3 text-white outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/50 transition-all placeholder-gray-600"
              onChange={(e) =>
                setFormData({ ...formData, username: e.target.value })
              }
            />
          </div>

          {/* 👇 NEW: EMAIL INPUT */}
          <div className="space-y-1">
            <label className="text-xs font-bold uppercase tracking-wider text-gray-500">
              Email Address
            </label>
            <div className="relative">
                <input
                type="email"
                placeholder="you@example.com"
                required
                className="w-full rounded-lg border border-white/10 bg-white/5 px-4 py-3 text-white outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/50 transition-all placeholder-gray-600 pl-10" // added padding left for icon
                onChange={(e) =>
                    setFormData({ ...formData, email: e.target.value })
                }
                />
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" size={18} />
            </div>
          </div>

          {/* PASSWORD */}
          <div className="space-y-1">
            <label className="text-xs font-bold uppercase tracking-wider text-gray-500">
              Choose Password
            </label>
            <div className="relative">
                <input
                type={showPassword ? "text" : "password"}
                placeholder="••••••••"
                required
                className="w-full rounded-lg border border-white/10 bg-white/5 px-4 py-3 text-white outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/50 transition-all placeholder-gray-600"
                onChange={(e) =>
                    setFormData({ ...formData, password: e.target.value })
                }
                />
                <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white transition-colors p-1"
                >
                    {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="mt-6 w-full rounded-lg bg-gradient-to-r from-cyan-500 to-blue-600 py-3 font-bold text-white transition-all hover:opacity-90 active:scale-95 disabled:opacity-50 shadow-lg shadow-cyan-500/20"
          >
            {loading ? <Loader2 className="mx-auto animate-spin" /> : "Sign Up"}
          </button>
        </form>

        <div className="mt-6 text-center text-sm text-gray-500">
          Already have an account?{" "}
          <Link
            to="/login"
            className="font-bold text-cyan-400 hover:underline hover:text-cyan-300"
          >
            Log in
          </Link>
        </div>
      </div>
    </div>
  );
}

export default Signup;