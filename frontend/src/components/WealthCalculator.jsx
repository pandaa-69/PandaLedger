import React, { useState } from 'react';
import { Calculator, ArrowRightLeft, TrendingUp, TrendingDown } from 'lucide-react';

const WealthCalculator = () => {
    const [mode, setMode] = useState("SIP"); // "SIP" or "SWP"
    
    // SIP State
    const [sipAmount, setSipAmount] = useState(5000);
    const [sipYears, setSipYears] = useState(5);
    const [sipRate, setSipRate] = useState(12);

    // SWP State
    const [swpCorpus, setSwpCorpus] = useState(1000000); // 10 Lakhs
    const [swpWithdrawal, setSwpWithdrawal] = useState(5000);
    const [swpYears, setSwpYears] = useState(5);

    // --- SIP CALCULATION (Compound Interest) ---
    // Formula: P × ({[1 + i]^n - 1} / i) × (1 + i)
    const calculateSIP = () => {
        const i = sipRate / 100 / 12;
        const n = sipYears * 12;
        const total = Math.round(sipAmount * ((Math.pow(1 + i, n) - 1) / i) * (1 + i));
        const invested = sipAmount * n;
        return { total, invested, profit: total - invested };
    };

    // --- SWP CALCULATION (Depletion) ---
    // Simple Approximation: Final = Corpus * (1+r)^t - Withdrawal * ...
    // To keep it simple for UI: We show "Remaining Balance" after N years
    const calculateSWP = () => {
        let balance = swpCorpus;
        const monthlyRate = 8 / 100 / 12; // Assume conservative 8% for SWP (Debt/Hybrid)
        let totalWithdrawn = 0;

        for (let m = 0; m < swpYears * 12; m++) {
            balance = balance * (1 + monthlyRate); // Growth
            balance = balance - swpWithdrawal; // Withdrawal
            totalWithdrawn += swpWithdrawal;
            if (balance <= 0) { balance = 0; break; }
        }
        return { balance: Math.round(balance), totalWithdrawn };
    };

    const sipData = calculateSIP();
    const swpData = calculateSWP();

    return (
        <div className="mx-auto mt-8 max-w-2xl rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-md">
            {/* HEADER & TOGGLE */}
            <div className="mb-8 flex items-center justify-between">
                <div className="flex items-center gap-2 text-white">
                    <Calculator size={20} className="text-cyan-400" />
                    <h3 className="text-lg font-bold uppercase tracking-widest">Wealth Planner</h3>
                </div>
                
                <div className="flex rounded-lg bg-black/40 p-1">
                    <button 
                        onClick={() => setMode("SIP")}
                        className={`rounded-md px-4 py-1.5 text-xs font-bold transition-all ${mode === "SIP" ? "bg-cyan-500 text-black shadow-lg" : "text-gray-500 hover:text-white"}`}
                    >
                        SIP (Invest)
                    </button>
                    <button 
                        onClick={() => setMode("SWP")}
                        className={`rounded-md px-4 py-1.5 text-xs font-bold transition-all ${mode === "SWP" ? "bg-purple-500 text-white shadow-lg" : "text-gray-500 hover:text-white"}`}
                    >
                        SWP (Withdraw)
                    </button>
                </div>
            </div>

            <div className="grid gap-8 md:grid-cols-2">
                {/* INPUTS SIDE */}
                <div className="space-y-6">
                    {mode === "SIP" ? (
                        <>
                            <div>
                                <label className="mb-2 block text-xs font-bold uppercase text-gray-500">Monthly Investment</label>
                                <div className="mb-2 text-2xl font-bold text-white">₹{sipAmount.toLocaleString()}</div>
                                <input type="range" min="500" max="100000" step="500" value={sipAmount} onChange={(e) => setSipAmount(Number(e.target.value))} className="h-2 w-full cursor-pointer appearance-none rounded-lg bg-white/10 accent-cyan-400" />
                            </div>
                            <div>
                                <label className="mb-2 block text-xs font-bold uppercase text-gray-500">Time Period</label>
                                <div className="mb-2 text-2xl font-bold text-white">{sipYears} Years</div>
                                <input type="range" min="1" max="30" step="1" value={sipYears} onChange={(e) => setSipYears(Number(e.target.value))} className="h-2 w-full cursor-pointer appearance-none rounded-lg bg-white/10 accent-cyan-400" />
                            </div>
                            <div>
                                <label className="mb-2 block text-xs font-bold uppercase text-gray-500">Exp. Return</label>
                                <div className="mb-2 text-2xl font-bold text-white">{sipRate}%</div>
                                <input type="range" min="5" max="30" step="1" value={sipRate} onChange={(e) => setSipRate(Number(e.target.value))} className="h-2 w-full cursor-pointer appearance-none rounded-lg bg-white/10 accent-cyan-400" />
                            </div>
                        </>
                    ) : (
                        <>
                            <div>
                                <label className="mb-2 block text-xs font-bold uppercase text-gray-500">Total Corpus</label>
                                <div className="mb-2 text-2xl font-bold text-white">₹{swpCorpus.toLocaleString()}</div>
                                <input type="range" min="100000" max="10000000" step="100000" value={swpCorpus} onChange={(e) => setSwpCorpus(Number(e.target.value))} className="h-2 w-full cursor-pointer appearance-none rounded-lg bg-white/10 accent-purple-500" />
                            </div>
                            <div>
                                <label className="mb-2 block text-xs font-bold uppercase text-gray-500">Monthly Withdrawal</label>
                                <div className="mb-2 text-2xl font-bold text-white">₹{swpWithdrawal.toLocaleString()}</div>
                                <input type="range" min="1000" max="100000" step="500" value={swpWithdrawal} onChange={(e) => setSwpWithdrawal(Number(e.target.value))} className="h-2 w-full cursor-pointer appearance-none rounded-lg bg-white/10 accent-purple-500" />
                            </div>
                            <div>
                                <label className="mb-2 block text-xs font-bold uppercase text-gray-500">Duration</label>
                                <div className="mb-2 text-2xl font-bold text-white">{swpYears} Years</div>
                                <input type="range" min="1" max="30" step="1" value={swpYears} onChange={(e) => setSwpYears(Number(e.target.value))} className="h-2 w-full cursor-pointer appearance-none rounded-lg bg-white/10 accent-purple-500" />
                            </div>
                        </>
                    )}
                </div>

                {/* RESULTS SIDE */}
                <div className={`flex flex-col justify-center rounded-xl p-6 text-center transition-colors ${mode === "SIP" ? "bg-cyan-900/10 border border-cyan-500/20" : "bg-purple-900/10 border border-purple-500/20"}`}>
                    {mode === "SIP" ? (
                        <>
                            <div className="mb-4 flex justify-center text-cyan-400"><TrendingUp size={32} /></div>
                            <p className="text-xs text-gray-400">Projected Value</p>
                            <div className="my-2 text-3xl font-extrabold text-white">₹{sipData.total.toLocaleString()}</div>
                            <div className="mt-4 space-y-2 border-t border-white/10 pt-4 text-xs">
                                <div className="flex justify-between"><span className="text-gray-500">Invested</span><span className="text-white">₹{sipData.invested.toLocaleString()}</span></div>
                                <div className="flex justify-between"><span className="text-gray-500">Wealth Gained</span><span className="text-green-400">+₹{sipData.profit.toLocaleString()}</span></div>
                            </div>
                        </>
                    ) : (
                        <>
                            <div className="mb-4 flex justify-center text-purple-400"><TrendingDown size={32} /></div>
                            <p className="text-xs text-gray-400">Remaining Corpus</p>
                            <div className="my-2 text-3xl font-extrabold text-white">₹{swpData.balance.toLocaleString()}</div>
                            <div className="mt-4 space-y-2 border-t border-white/10 pt-4 text-xs">
                                <div className="flex justify-between"><span className="text-gray-500">Total Withdrawn</span><span className="text-white">₹{swpData.totalWithdrawn.toLocaleString()}</span></div>
                                <div className="flex justify-between"><span className="text-gray-500">Est. Growth Rate</span><span className="text-purple-400">8% (Conservative)</span></div>
                                {swpData.balance === 0 && <div className="mt-2 text-red-400 font-bold">⚠️ Corpus Depleted!</div>}
                            </div>
                        </>
                    )}
                </div>
            </div>
        </div>
    );
};

export default WealthCalculator;