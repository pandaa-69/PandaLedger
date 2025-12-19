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

  const isActive = (path) =>
    location.pathname === path
      ? "text-purple-400 bg-purple-500/10"
      : "text-gray-400 hover:text-white hover:bg-white/5";

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 border-b border-white/10 bg-black/60 backdrop-blur-xl">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6">
        {/* LOGO */}
        <Link to="/" className="flex items-center gap-2 group">
          <span className="text-2xl transition-transform group-hover:scale-110">
            🐼
          </span>
          <span className="brand-font text-xl font-bold tracking-tight bg-gradient-to-r from-purple-400 to-green-400 bg-clip-text text-transparent">
            PandaLedger
          </span>
        </Link>

        {/* DESKTOP LINKS (Hidden on Mobile) */}
        {user && (
          <div className="hidden md:flex items-center gap-2 rounded-full border border-white/10 bg-black/20 p-1 backdrop-blur-md">
            <Link
              to="/"
              className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-all ${isActive(
                "/"
              )}`}
            >
              <LayoutDashboard size={16} /> Dashboard
            </Link>
            <Link
              to="/ledger"
              className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-all ${isActive(
                "/ledger"
              )}`}
            >
              <Wallet size={16} /> Ledger
            </Link>
            <Link
              to="/portfolio"
              className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-all ${isActive(
                "/portfolio"
              )}`}
            >
              <PieChart size={16} /> Portfolio
            </Link>
          </div>
        )}

        {/* RIGHT SIDE */}
        <div className="flex items-center gap-6">
          {user ? (
            <div className="flex items-center gap-4">
              {/* Removed "Cmdr". Just showing Name now. */}
              <span className="hidden text-sm font-medium text-gray-300 sm:block">
                Hi, <span className="text-white font-bold">{user}</span>
              </span>

              <button
                onClick={handleLogout}
                className="flex items-center gap-2 rounded-lg bg-red-500/10 px-3 py-2 text-xs font-bold text-red-500 transition-all hover:bg-red-500/20 active:scale-95"
              >
                <LogOut size={16} />
                <span className="hidden sm:inline">Exit</span>
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-4">
              <Link
                to="/login"
                className="text-sm font-medium text-gray-400 hover:text-white"
              >
                Log in
              </Link>
              <Link
                to="/signup"
                className="rounded-full bg-white px-5 py-2 text-sm font-bold text-black transition-transform hover:scale-105 active:scale-95"
              >
                Get Started
              </Link>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
