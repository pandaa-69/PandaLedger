import React, { useState } from "react";
import MarketDashboard from "../components/MarketDashboard";
import { Link } from "react-router-dom";
import { ArrowRight, Wallet, AlertTriangle, Edit2, Check } from "lucide-react";
import WealthCalculator from "../components/WealthCalculator";

// --- COMPONENT: BUDGET BAR (Keep this here for Logged In users) ---
const BudgetProgressBar = ({ monthlySpend }) => {
    const [budget, setBudget] = useState(() => {
        return localStorage.getItem("userBudget") || 20000;
    });
    const [isEditing, setIsEditing] = useState(false);
    const [tempBudget, setTempBudget] = useState(budget);

    const saveBudget = () => {
        localStorage.setItem("userBudget", tempBudget);
        setBudget(tempBudget);
        setIsEditing(false);
    };

    const percentage = Math.min(Math.round((monthlySpend / budget) * 100), 100);
    
    let color = "bg-green-500";
    if (percentage > 50) color = "bg-yellow-500";
    if (percentage > 85) color = "bg-red-500";

    return (
        <div className="rounded-xl border border-white/10 bg-black/40 p-5 backdrop-blur-sm">
            <div className="mb-4 flex items-center justify-between">
                <div className="flex items-center gap-2 text-gray-400">
                    <AlertTriangle size={16} />
                    <span className="text-xs font-bold uppercase tracking-widest">Monthly Limit</span>
                </div>
                
                {isEditing ? (
                    <div className="flex items-center gap-2">
                        <input 
                            type="number" 
                            value={tempBudget}
                            onChange={(e) => setTempBudget(e.target.value)}
                            className="w-20 rounded bg-white/10 px-2 py-1 text-right text-sm font-bold text-white focus:outline-none focus:ring-1 focus:ring-cyan-500"
                            autoFocus
                        />
                        <button onClick={saveBudget} className="rounded-full bg-cyan-500/20 p-1 text-cyan-400 hover:bg-cyan-500/30">
                            <Check size={14} />
                        </button>
                    </div>
                ) : (
                    <button onClick={() => setIsEditing(true)} className="flex items-center gap-1 text-sm font-bold text-white hover:text-cyan-400">
                        ₹{parseInt(budget).toLocaleString()} <Edit2 size={12} className="opacity-50" />
                    </button>
                )}
            </div>

            <div className="relative h-4 w-full overflow-hidden rounded-full bg-white/10">
                <div 
                    className={`h-full transition-all duration-1000 ease-out ${color}`} 
                    style={{ width: `${percentage}%` }}
                ></div>
            </div>
            
            <div className="mt-2 flex justify-between text-xs font-medium">
                <span className={percentage > 85 ? "text-red-400" : "text-gray-400"}>
                    {percentage}% Used
                </span>
                <span className="text-gray-500">
                    Remaining: <span className="text-white">₹{(budget - monthlySpend).toLocaleString()}</span>
                </span>
            </div>
        </div>
    );
};


function Home({ expenses }) {
  const user = localStorage.getItem('user')?.replace(/"/g, '');

  let monthlySpend = 0;
  let txCount = 0;
  if (expenses) {
    const currentMonth = new Date().getMonth();
    expenses.forEach(tx => {
        if (new Date(tx.date).getMonth() === currentMonth) {
            monthlySpend += parseFloat(tx.amount);
            txCount++;
        }
    });
  }

  return (
    <div className="mx-auto w-full max-w-6xl">
      
      {/* 1. WELCOME / HERO SECTION */}
      <div className="mb-8">
        
        {/* LOGGED IN VIEW */}
        {user ? (
            <>
                <h1 className="text-3xl md:text-4xl font-extrabold text-white mb-6 px-1">
                    Welcome back, <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500">{user}</span>.
                </h1>
                
                <div className="grid gap-4 md:grid-cols-3 mb-8">
                    {/* Monthly Spend */}
                    <Link to="/ledger" className="group rounded-xl border border-white/10 bg-gradient-to-br from-cyan-900/20 to-black p-5 backdrop-blur-sm transition-all hover:border-cyan-500/50">
                        <div className="flex items-center gap-2 text-cyan-400 mb-2">
                            <Wallet size={16} />
                            <span className="text-xs font-bold uppercase tracking-widest group-hover:text-cyan-300">This Month</span>
                        </div>
                        <div className="text-2xl md:text-3xl font-bold text-white">
                            ₹{monthlySpend.toLocaleString()}
                        </div>
                        <p className="text-xs text-gray-500 mt-1">{txCount} transactions</p>
                    </Link>

                    {/* Budget Bar */}
                    <div className="md:col-span-2">
                        <BudgetProgressBar monthlySpend={monthlySpend} />
                    </div>
                </div>
            </>
        ) : (
            // LOGGED OUT VIEW (HERO ONLY)
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
        )}
      </div>

      {/* 2. MARKET DASHBOARD (Now back at the top!) */}
      <MarketDashboard />

      {/* 3. WEALTH CALCULATOR (Bottom Filler for Logged Out Users) */}
      {!user && (
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