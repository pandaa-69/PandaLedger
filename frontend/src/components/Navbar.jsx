import React, { useState, useEffect } from "react";
import { Link, useLocation } from "react-router-dom";
import { LayoutDashboard, Wallet, PieChart, LogOut } from "lucide-react";

function Navbar() {
  const [user, setUser] = useState(null);
  const location = useLocation();

  useEffect(() => {
    const loggedInUser = localStorage.getItem("user");
    if (loggedInUser) setUser(loggedInUser.replace(/"/g, ""));
  }, []);

  const handleLogout = () => {
    fetch("http://127.0.0.1:8000/api/auth/logout/", {
      method: "POST",
      credentials: "include",
    }).then(() => {
      localStorage.removeItem("user");
      window.location.href = "/login";
    });
  };

  // Helper for active link styling
  const isActive = (path) =>
    location.pathname === path
      ? "text-cyan-400 bg-cyan-500/10 border-cyan-500/20" // Active style
      : "text-gray-400 hover:text-white hover:bg-white/5 border-transparent";

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 border-b border-white/10 bg-black/80 backdrop-blur-xl">
      <div className="mx-auto flex h-16 max-w-[95%] items-center justify-between px-4">
        
        {/* LOGO */}
        <Link to="/" className="flex items-center gap-2 group">
          <span className="text-2xl transition-transform group-hover:scale-110">🐼</span>
          <span className="brand-font text-xl font-bold tracking-tight bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
            PandaLedger
          </span>
        </Link>

        {/* DESKTOP LINKS */}
        {user && (
          <div className="hidden md:flex items-center gap-2 rounded-full border border-white/10 bg-black/40 p-1">
            <Link to="/" className={`flex items-center gap-2 px-4 py-1.5 rounded-full text-sm font-bold border transition-all ${isActive("/")}`}>
              <LayoutDashboard size={16} /> Dashboard
            </Link>
            <Link to="/ledger" className={`flex items-center gap-2 px-4 py-1.5 rounded-full text-sm font-bold border transition-all ${isActive("/ledger")}`}>
              <Wallet size={16} /> Ledger
            </Link>
            {/* 👇 HERE IS THE LINK */}
            <Link to="/portfolio" className={`flex items-center gap-2 px-4 py-1.5 rounded-full text-sm font-bold border transition-all ${isActive("/portfolio")}`}>
              <PieChart size={16} /> Portfolio
            </Link>
          </div>
        )}

        {/* RIGHT SIDE (User / Login) */}
        <div className="flex items-center gap-4">
          {user ? (
            <div className="flex items-center gap-4">
              <span className="hidden text-sm font-medium text-gray-300 sm:block">
                Hi, <span className="text-white font-bold">{user}</span>
              </span>
              <button onClick={handleLogout} className="group flex items-center gap-2 rounded-lg bg-red-500/10 px-3 py-2 text-xs font-bold text-red-500 transition-all hover:bg-red-500/20 active:scale-95">
                <LogOut size={16} className="group-hover:-translate-x-0.5 transition-transform"/>
                <span className="hidden sm:inline">Exit</span>
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-4">
              <Link to="/login" className="text-sm font-bold text-gray-400 hover:text-white">Log in</Link>
              <Link to="/signup" className="rounded-full bg-white px-5 py-2 text-sm font-bold text-black hover:scale-105 transition-transform">Get Started</Link>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}

export default Navbar;