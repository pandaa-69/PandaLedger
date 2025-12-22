import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Loader2, LogIn, Eye, EyeOff } from "lucide-react";
import { getCookie } from '../utils/csrf';
import API_URL from './config';

function Login() {
  const [formData, setFormData] = useState({ username: "", password: "" });
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    setLoading(true);

    fetch(`${API_URL}/api/auth/login/`, {
      method: "POST",
      headers: { 
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie('csrftoken')
      },
      body: JSON.stringify(formData),
      credentials: "include",
    })
      .then((res) => {
        if (!res.ok) throw new Error("Login failed");
        return res.json();
      })
      .then((data) => {
        localStorage.setItem("user", JSON.stringify(data.username));
        window.location.href = "/"; 
      })
      .catch((err) => {
        alert("Invalid Credentials!");
        setLoading(false);
      });
  };

  return (
    <div className="flex min-h-[80vh] items-center justify-center px-4">
      <div className="w-full max-w-md rounded-2xl border border-white/10 bg-black/40 p-8 shadow-2xl backdrop-blur-xl animate-in fade-in slide-in-from-bottom-4 duration-700">
        
        {/* Header */}
        <div className="mb-8 text-center">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-cyan-500/20 text-cyan-400">
            <LogIn size={24} />
          </div>
          <h2 className="text-2xl font-bold text-white">Welcome Back</h2>
          <p className="text-sm text-gray-400">
            Enter credentials to access your wealth.
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1">
            <label className="text-xs font-bold uppercase tracking-wider text-gray-500">
              Username
            </label>
            <input
              type="text"
              placeholder="e.g. panda_master"
              className="w-full rounded-lg border border-white/10 bg-white/5 px-4 py-3 text-white outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/50 transition-all placeholder-gray-600"
              onChange={(e) =>
                setFormData({ ...formData, username: e.target.value })
              }
            />
          </div>

          <div className="space-y-1">
            {/* 👇 Flex container for Label + Forgot Link */}
            <div className="flex justify-between items-center">
                <label className="text-xs font-bold uppercase tracking-wider text-gray-500">
                Password
                </label>
                <Link to="/forgot-password" class="text-xs font-bold text-cyan-500 hover:text-cyan-400 hover:underline transition-colors">
                    Forgot Password?
                </Link>
            </div>
            
            <div className="relative">
                <input
                type={showPassword ? "text" : "password"}
                placeholder="••••••••"
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
            {loading ? <Loader2 className="mx-auto animate-spin" /> : "Sign In"}
          </button>
        </form>

        <div className="mt-6 text-center text-sm text-gray-500">
          Don't have an account?{" "}
          <Link
            to="/signup"
            className="font-bold text-cyan-400 hover:underline hover:text-cyan-300"
          >
            Create one
          </Link>
        </div>
      </div>
    </div>
  );
}

export default Login;