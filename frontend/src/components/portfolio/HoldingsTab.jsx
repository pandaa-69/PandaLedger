import React, { useMemo } from 'react';
import { Landmark, Plus, PieChart as PieIcon, TrendingUp, Building2, Coins, Wallet } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import AssetSection from './AssetSection';

const HoldingsTab = ({ portfolio, onAddClick, onAssetClick }) => {
    
  // 📊 Calculate Asset Class Split
  const assetClassData = useMemo(() => {
    const groups = {};
    if(portfolio.holdings) {
        portfolio.holdings.forEach((h) => {
            groups[h.type] = (groups[h.type] || 0) + h.current_value;
        });
    }
    return Object.entries(groups).map(([name, value]) => ({ name, value }));
  }, [portfolio.holdings]);

  const COLORS = { STOCK: "#22d3ee", ETF: "#818cf8", REIT: "#fb923c", GOLD: "#facc15", MF: "#f472b6", CRYPTO: "#a855f7" };

  return (
    <>
      <div className="grid lg:grid-cols-3 gap-6 mb-12">
        {/* Net Worth Card */}
        <div className="lg:col-span-2 relative group">
            <div className="absolute -inset-0.5 bg-gradient-to-r from-cyan-500 to-emerald-500 rounded-3xl blur opacity-10 group-hover:opacity-20 transition duration-1000"></div>
            <div className="relative bg-gray-900 border border-white/10 rounded-3xl p-8 h-full flex flex-col justify-between overflow-hidden shadow-2xl">
            <div>
                <div className="text-gray-400 text-xs font-bold uppercase tracking-[0.2em] mb-2 flex items-center gap-2">
                <Landmark size={14} className="text-cyan-400" /> Current Net Worth
                </div>
                <div className="text-5xl md:text-6xl font-black text-white tracking-tighter mb-8">
                ₹{(portfolio.summary.total_value || 0).toLocaleString()}
                </div>
                
                <div className="grid grid-cols-2 gap-4 max-w-md">
                    {/* Invested Box */}
                    <div className="bg-white/5 rounded-2xl p-4 border border-white/5">
                        <div className="text-[10px] uppercase text-gray-500 font-bold mb-1">Invested</div>
                        <div className="text-lg font-bold text-white leading-none">₹{(portfolio.summary.total_invested || 0).toLocaleString()}</div>
                    </div>
                    
                    {/* Total P&L Box (UPDATED) */}
                    <div className="bg-white/5 rounded-2xl p-4 border border-white/5">
                        <div className="text-[10px] uppercase text-gray-500 font-bold mb-1">Total P&L</div>
                        <div className={`text-lg font-bold leading-none flex items-center gap-2 ${(portfolio.summary.total_profit || 0) >= 0 ? "text-emerald-400" : "text-red-400"}`}>
                            {/* Amount */}
                            <span>
                                {(portfolio.summary.total_profit || 0) >= 0 ? "+" : ""}₹{(portfolio.summary.total_profit || 0).toLocaleString()}
                            </span>
                            
                            {/* Percentage Pill */}
                            <span className={`text-[10px] px-1.5 py-0.5 rounded ${ (portfolio.summary.total_profit || 0) >= 0 ? "bg-emerald-500/20 text-emerald-300" : "bg-red-500/20 text-red-300" }`}>
                                {portfolio.summary.total_profit_pct}%
                            </span>
                        </div>
                    </div>
                </div>
            </div>
            
            <button onClick={onAddClick} className="mt-8 w-full md:w-fit bg-white text-black px-10 py-4 rounded-2xl font-black flex items-center justify-center gap-3 hover:bg-cyan-50 transition-all shadow-xl shadow-white/5">
                <Plus size={20} /> Add Asset
            </button>
            </div>
        </div>

        {/* Allocation Pie Chart */}
        <div className="bg-gray-900 border border-white/10 rounded-3xl p-6 relative overflow-hidden flex flex-col items-center justify-center shadow-xl">
            <div className="absolute top-6 left-6 text-gray-400 text-xs font-bold uppercase tracking-widest flex items-center gap-2">
            <PieIcon size={14} className="text-indigo-400" /> Allocation
            </div>
            {portfolio.holdings && portfolio.holdings.length > 0 ? (
            <div className="w-full h-48 mt-6">
                <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                    <Pie data={assetClassData} innerRadius={60} outerRadius={75} paddingAngle={5} dataKey="value" animationDuration={1000}>
                    {assetClassData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[entry.name] || "#ffffff"} stroke="none" />
                    ))}
                    </Pie>
                    <Tooltip formatter={(value) => `₹${value.toLocaleString()}`} contentStyle={{ backgroundColor: "#000", border: "1px solid #374151", borderRadius: "12px", fontSize: "11px", color: "#fff" }} itemStyle={{ color: "#fff" }} />
                </PieChart>
                </ResponsiveContainer>
            </div>
            ) : (
            <div className="text-gray-600 text-sm font-medium italic">No assets</div>
            )}
        </div>
      </div>

      <div className="space-y-12">
        <AssetSection title="Equity Stocks" assets={portfolio.holdings.filter((h) => h.type === "STOCK")} icon={<TrendingUp size={20} className="text-cyan-400" />} onAssetClick={onAssetClick} color="cyan" />
        <AssetSection title="Exchange Traded Funds" assets={portfolio.holdings.filter((h) => h.type === "ETF")} icon={<Landmark size={20} className="text-indigo-400" />} onAssetClick={onAssetClick} color="indigo" />
        <AssetSection title="REITs" assets={portfolio.holdings.filter((h) => h.type === "REIT")} icon={<Building2 size={20} className="text-orange-400" />} onAssetClick={onAssetClick} color="orange" />
        <AssetSection title="Gold" assets={portfolio.holdings.filter((h) => h.type === "GOLD")} icon={<Coins size={20} className="text-yellow-500" />} onAssetClick={onAssetClick} color="yellow" />
        <AssetSection title="Mutual Funds" assets={portfolio.holdings.filter((h) => h.type === "MF")} icon={<Wallet size={20} className="text-pink-400" />} onAssetClick={onAssetClick} color="pink" />
      </div>
    </>
  );
};

export default HoldingsTab;