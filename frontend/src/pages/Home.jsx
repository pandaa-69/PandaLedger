import React, { useState, useEffect } from "react";
import MarketDashboard from "../components/MarketDashboard";
import { Link } from "react-router-dom";
import { ArrowRight, Wallet, TrendingUp, AlertTriangle } from "lucide-react";
import WealthCalculator from "../components/WealthCalculator";
import API_URL from './config';

function Home() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // 1. Fetch the "Command Center" Data 📡
    fetch(`${API_URL}/api/analytics/home-summary/`, {
      credentials: "include",
    })
      .then((res) => {
        if (res.ok) return res.json();
        throw new Error("Not logged in");
      })
      .then((data) => {
        setSummary(data); // ✅ We got the data!
        setLoading(false);
      })
      .catch(() => {
        setSummary(null); // ❌ Not logged in
        setLoading(false);
      });
  }, []);

  return (
    <div className="mx-auto w-full max-w-6xl animate-in fade-in slide-in-from-bottom-4 duration-700 pb-20">
      
      {/* 1. HERO SECTION */}
      <div className="mb-8 pt-8">
        {summary ? (
            // 🟢 LOGGED IN VIEW 🟢
            <>
                <h1 className="text-3xl md:text-4xl font-extrabold text-white mb-6 px-1">
                    Welcome back, <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500 capitalize">{summary.username}</span>.
                </h1>
                
                <div className="grid gap-6 md:grid-cols-2 mb-12">
                    
                    {/* Card 1: The Wallet (Ledger Link) */}
                    <Link to="/ledger" className="group relative overflow-hidden rounded-3xl border border-white/10 bg-gray-900 p-8 transition-all hover:border-purple-500/50 hover:shadow-2xl hover:shadow-purple-500/10">
                        <div className="absolute right-0 top-0 -mr-8 -mt-8 h-32 w-32 rounded-full bg-purple-500/10 blur-3xl transition-all group-hover:bg-purple-500/20"></div>
                        
                        <div className="flex items-center gap-3 text-purple-400 mb-4">
                            <div className="p-2 bg-purple-500/10 rounded-lg group-hover:scale-110 transition-transform">
                                <Wallet size={24} />
                            </div>
                            <span className="text-xs font-bold uppercase tracking-widest">Expense Tracker</span>
                        </div>

                        <div className="space-y-1">
                            <div className="text-gray-400 text-sm font-medium">This Month's Spend</div>
                            <div className="flex items-baseline gap-2">
                                <div className="text-4xl font-black text-white">₹{summary.monthly_spend.toLocaleString()}</div>
                                <div className="text-gray-500 font-bold">/ ₹{summary.monthly_budget.toLocaleString()}</div>
                            </div>
                        </div>

                        {/* Mini Progress Bar */}
                        <div className="mt-6 w-full h-1.5 bg-gray-800 rounded-full overflow-hidden">
                            <div 
                                className={`h-full rounded-full ${ summary.monthly_spend > summary.monthly_budget ? 'bg-red-500' : 'bg-purple-500'} transition-all duration-1000`} 
                                style={{ width: `${Math.min((summary.monthly_spend / summary.monthly_budget) * 100, 100)}%` }}
                            ></div>
                        </div>
                        
                        {summary.monthly_spend > summary.monthly_budget && (
                            <div className="mt-3 flex items-center gap-2 text-xs text-red-400 font-bold animate-pulse">
                                <AlertTriangle size={12} /> Over Budget!
                            </div>
                        )}
                    </Link>

                    {/* Card 2: The Vault (Portfolio Link) */}
                    <Link to="/portfolio" className="group relative overflow-hidden rounded-3xl border border-white/10 bg-gray-900 p-8 transition-all hover:border-cyan-500/50 hover:shadow-2xl hover:shadow-cyan-500/10">
                        <div className="absolute right-0 top-0 -mr-8 -mt-8 h-32 w-32 rounded-full bg-cyan-500/10 blur-3xl transition-all group-hover:bg-cyan-500/20"></div>
                        
                        <div className="flex items-center gap-3 text-cyan-400 mb-4">
                            <div className="p-2 bg-cyan-500/10 rounded-lg group-hover:scale-110 transition-transform">
                                <TrendingUp size={24} />
                            </div>
                            <span className="text-xs font-bold uppercase tracking-widest">Investment Portfolio</span>
                        </div>

                        <div className="space-y-1">
                            <div className="text-gray-400 text-sm font-medium">Total Net Worth</div>
                            <div className="text-4xl font-black text-white">₹{summary.net_worth.toLocaleString()}</div>
                        </div>

                        <div className="mt-6 flex items-center gap-2 text-xs font-bold text-gray-500 uppercase tracking-widest group-hover:text-cyan-400 transition-colors">
                            View Analytics <ArrowRight size={14} />
                        </div>
                    </Link>

                </div>
            </>
        ) : (
            // ⚪ LOGGED OUT VIEW ⚪
            !loading && (
            <div className="py-12 text-center">
                <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight text-white mb-6">
                  Master Your <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-green-400">Wealth</span>.
                </h1>
                <p className="text-lg text-gray-400 max-w-2xl mx-auto mb-8">
                  Real-time market insights combined with powerful personal expense tracking.
                </p>
                <Link to="/signup" className="inline-flex items-center gap-2 rounded-full bg-white px-8 py-4 text-base font-bold text-black transition-transform hover:scale-105 active:scale-95">
                    Start Tracking <ArrowRight size={18} />
                </Link>
            </div>
            )
        )}
      </div>

      {/* 2. MARKET DASHBOARD (Always Visible) */}
      <MarketDashboard />

      {/* 3. CALCULATOR (Only for logged OUT users as a demo) */}
      {!summary && !loading && (
        <div className="mt-16 border-t border-white/10 pt-10">
            <div className="text-center mb-6">
                <h2 className="text-2xl font-bold text-white">Plan Your Future</h2>
                <p className="text-gray-400 text-sm">See how small investments grow over time.</p>
            </div>
            <WealthCalculator />
        </div>
      )}

    </div>
  );
}

export default Home;