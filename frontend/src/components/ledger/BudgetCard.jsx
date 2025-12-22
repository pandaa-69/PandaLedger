import React, { useState, useEffect } from 'react';
import { CreditCard, Edit2, Check, X } from 'lucide-react';
import { getCookie } from '../../utils/csrf';
import API_URL from './config';

const BudgetCard = ({ onBudgetChange }) => {
    const [stats, setStats] = useState({ total_spent: 0, monthly_budget: 0, percentage: 0 });
    const [isEditing, setIsEditing] = useState(false);
    const [newBudget, setNewBudget] = useState(0);

    const fetchStats = () => {
        // 👇 FIXED URL: Removed "ledger/"
        fetch(`${API_URL}/api/stats/`, { credentials: "include" })
            .then(res => res.json())
            .then(data => {
                setStats(data);
                setNewBudget(data.monthly_budget);
            });
    };

    useEffect(() => { fetchStats(); }, []);

    // Handle Saving New Budget
    const handleSave = () => {
        // 👇 FIXED URL: Removed "ledger/"
        fetch(`${API_URL}/api/budget/update/`, {
            method: "POST",
            headers: { 
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie('csrftoken')
            },
            credentials: "include",
            body: JSON.stringify({ budget: newBudget })
        }).then(res => {
            if (res.ok) {
                setIsEditing(false);
                fetchStats(); // Refresh bar
                if(onBudgetChange) onBudgetChange(); // Notify parent if needed
            }
        });
    };

    // Color logic based on percentage
    const getProgressColor = () => {
        if (stats.percentage < 50) return "bg-emerald-500";
        if (stats.percentage < 80) return "bg-yellow-500";
        return "bg-red-500";
    };

    return (
        <div className="bg-gray-900 border border-white/10 p-6 rounded-2xl mb-8 relative overflow-hidden group">
            {/* Background Glow */}
            <div className={`absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-white/20 to-transparent opacity-0 group-hover:opacity-100 transition-all duration-700`} />

            <div className="flex justify-between items-end mb-4">
                <div>
                    <h3 className="text-gray-400 text-xs font-bold uppercase tracking-widest flex items-center gap-2 mb-1">
                        <CreditCard size={14} className="text-purple-400"/> Monthly Budget
                    </h3>
                    
                    {isEditing ? (
                        <div className="flex items-center gap-2 mt-2">
                            <span className="text-2xl font-bold text-white">₹</span>
                            <input 
                                type="number" 
                                value={newBudget} 
                                onChange={(e) => setNewBudget(e.target.value)}
                                className="bg-black/40 border border-purple-500/50 rounded-lg px-3 py-1 text-white font-bold w-32 focus:outline-none focus:ring-2 focus:ring-purple-500"
                                autoFocus
                            />
                            <button onClick={handleSave} className="p-2 bg-emerald-500/20 text-emerald-400 rounded-lg hover:bg-emerald-500/40"><Check size={16}/></button>
                            <button onClick={() => setIsEditing(false)} className="p-2 bg-red-500/20 text-red-400 rounded-lg hover:bg-red-500/40"><X size={16}/></button>
                        </div>
                    ) : (
                        <div className="flex items-baseline gap-2">
                            <span className="text-3xl font-black text-white">₹{stats.total_spent.toLocaleString()}</span>
                            <span className="text-gray-500 font-medium">/ ₹{stats.monthly_budget.toLocaleString()}</span>
                            <button onClick={() => setIsEditing(true)} className="ml-2 text-gray-600 hover:text-white transition-colors"><Edit2 size={12}/></button>
                        </div>
                    )}
                </div>
                <div className="text-right">
                    <div className={`text-xl font-black ${stats.percentage >= 100 ? 'text-red-500' : 'text-white'}`}>
                        {stats.percentage}%
                    </div>
                    <div className="text-xs text-gray-500 font-bold uppercase">Used</div>
                </div>
            </div>

            {/* Progress Bar */}
            <div className="w-full h-3 bg-gray-800 rounded-full overflow-hidden">
                <div 
                    className={`h-full ${getProgressColor()} transition-all duration-1000 ease-out`} 
                    style={{ width: `${stats.percentage}%` }}
                />
            </div>
            
            {stats.percentage >= 100 && (
                <div className="mt-3 text-xs text-red-400 font-bold bg-red-400/10 border border-red-400/20 p-2 rounded-lg text-center animate-pulse">
                    ⚠️ You have exceeded your monthly budget!
                </div>
            )}
        </div>
    );
};

export default BudgetCard;