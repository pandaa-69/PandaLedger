import React, { useState, useMemo } from 'react';
import { Activity, ShieldCheck, TrendingUp, Zap, PieChart as PieIcon } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, Cell } from 'recharts';
import MetricCard from './MetricCard';

const AnalyticsTab = ({ analytics }) => {
  const [timeRange, setTimeRange] = useState('MAX'); // '1M', '6M', '1Y', 'MAX'

  const COLORS = { STOCK: "#22d3ee", ETF: "#818cf8", REIT: "#fb923c", GOLD: "#facc15", MF: "#f472b6", CRYPTO: "#a855f7" };

  // 🕒 1. Smart Data Downsampling (The "Zoom" Logic)
  const chartData = useMemo(() => {
    if (!analytics.performance_graph || analytics.performance_graph.length === 0) return [];

    const now = new Date();
    let cutoff = new Date();

    // Set Cutoff Date
    if (timeRange === '1M') cutoff.setMonth(now.getMonth() - 1);
    if (timeRange === '6M') cutoff.setMonth(now.getMonth() - 6);
    if (timeRange === '1Y') cutoff.setFullYear(now.getFullYear() - 1);
    if (timeRange === 'MAX') cutoff = new Date('2000-01-01'); 

    // Filter Data by Date
    const timeFiltered = analytics.performance_graph.filter(d => new Date(d.date) >= cutoff);

    // Downsample for Performance (Prevent lag, but keep enough detail)
    if (timeRange === '1M') {
        return timeFiltered; // Keep ALL points (Daily precision)
    }
    if (timeRange === '6M') {
        return timeFiltered.filter((_, i) => i % 2 === 0 || i === timeFiltered.length - 1); // Every 2nd day
    }
    if (timeRange === '1Y') {
        return timeFiltered.filter((_, i) => i % 5 === 0 || i === timeFiltered.length - 1); // Weekly-ish
    }
    if (timeRange === 'MAX') {
        return timeFiltered.filter((_, i) => i % 14 === 0 || i === timeFiltered.length - 1); // Bi-Weekly
    }
    return timeFiltered;
  }, [analytics.performance_graph, timeRange]);


  // 📅 2. Dynamic X-Axis Labels (The Fix for "Which Date is this?")
  const formatXAxis = (dateStr) => {
      const date = new Date(dateStr);
      if (timeRange === '1M') {
          return date.toLocaleDateString('en-US', { day: 'numeric', month: 'short' }); // "15 Dec"
      }
      if (timeRange === '6M' || timeRange === '1Y') {
          return date.toLocaleDateString('en-US', { month: 'short', year: '2-digit' }); // "Dec '25"
      }
      return date.getFullYear(); // "2025" (For MAX)
  };

  return (
    <div className="animate-in slide-in-from-right-4 duration-500 space-y-8">
      {/* Top Row: Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <MetricCard title="Actual XIRR" value={`${analytics.metrics.xirr}%`} subtitle="Annualized Speed" icon={<Activity className="text-emerald-400" />} />
        <MetricCard title="Volatility" value={analytics.metrics.volatility} subtitle="Portfolio Risk Rating" icon={<ShieldCheck className="text-cyan-400" />} />
        <MetricCard title="Market Beta" value={analytics.metrics.beta} subtitle="Sensitivity to Nifty" icon={<TrendingUp className="text-purple-400" />} />
        <MetricCard title="Health Score" value={`${analytics.metrics.health_score}/100`} subtitle="Diversification Quality" icon={<Zap className="text-yellow-400" />} />
      </div>

      {/* Performance Graph Row */}
      <div className="grid lg:grid-cols-2 gap-8">
        <div className="bg-gray-900 border border-white/5 p-8 rounded-[2rem]">
            
          <div className="flex justify-between items-center mb-8">
            <h3 className="text-white font-bold text-lg flex items-center gap-3">
                <Activity size={20} className="text-cyan-400" /> Performance
            </h3>
            
            {/* Time Selectors */}
            <div className="flex bg-white/5 p-1 rounded-lg">
                {['1M', '6M', '1Y', 'MAX'].map(range => (
                    <button 
                        key={range}
                        onClick={() => setTimeRange(range)}
                        className={`px-3 py-1 text-[10px] font-bold rounded-md transition-all ${timeRange === range ? 'bg-cyan-500 text-black' : 'text-gray-400 hover:text-white'}`}
                    >
                        {range}
                    </button>
                ))}
            </div>
          </div>

          <div className="w-full h-80">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="colorPort" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#22d3ee" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#22d3ee" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#ffffff05" vertical={false} />
                
                {/* 👇 The Fixed X-Axis Logic */}
                <XAxis 
                    dataKey="date" // Use the full date string as key
                    tickFormatter={formatXAxis} // Apply the smart formatting function
                    stroke="#9ca3af" 
                    fontSize={10} 
                    tickLine={false} 
                    axisLine={false} 
                    minTickGap={30} // Prevents overlapping text
                />
                
                <YAxis hide />
                <Tooltip
                    contentStyle={{ backgroundColor: '#111827', border: 'none', borderRadius: '12px', boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.5)' }}
                    itemStyle={{ fontSize: '12px', fontWeight: 'bold', color: '#e5e7eb' }}
                    labelStyle={{ color: '#9ca3af', marginBottom: '0.5rem', fontSize: '11px' }}
                    formatter={(value) => `₹${value.toLocaleString()}`}
                    labelFormatter={(label) => {
                        // Ensure tooltip shows full readable date
                        return new Date(label).toLocaleDateString('en-US', { weekday: 'short', year: 'numeric', month: 'long', day: 'numeric' });
                    }}
                />
                <Area type="monotone" dataKey="portfolio" stroke="#22d3ee" strokeWidth={3} fillOpacity={1} fill="url(#colorPort)" activeDot={{ r: 6, strokeWidth: 0 }} />
                <Area type="stepAfter" dataKey="invested" stroke="#6b7280" strokeWidth={2} fill="transparent" strokeDasharray="4 4" activeDot={false} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Sector Allocation */}
        <div className="bg-gray-900 border border-white/5 p-8 rounded-[2rem]">
          <h3 className="text-white font-bold text-lg mb-8 flex items-center gap-3">
            <PieIcon size={20} className="text-indigo-400" /> Sector Allocation
          </h3>
          <div className="w-full h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={analytics.sectors} layout="vertical" margin={{ left: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#ffffff05" horizontal={false} />
                <XAxis type="number" hide />
                <YAxis dataKey="name" type="category" stroke="#9ca3af" fontSize={12} tickLine={false} axisLine={false} />
                <Tooltip cursor={{ fill: "#ffffff05" }} contentStyle={{ backgroundColor: "#111827", border: "1px solid #374151", borderRadius: "12px" }} itemStyle={{ color: '#e5e7eb', fontWeight: 'bold' }} labelStyle={{ color: '#9ca3af' }} />
                <Bar dataKey="value" radius={[0, 8, 8, 0]} barSize={24}>
                  {analytics.sectors.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[entry.name] || "#6366f1"} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsTab;