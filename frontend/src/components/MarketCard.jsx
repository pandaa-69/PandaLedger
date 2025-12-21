import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, Coins, Bitcoin } from 'lucide-react';
import { AreaChart, Area, ResponsiveContainer, YAxis, Tooltip } from 'recharts';

// 👇 1. Import Odometer and its CSS
import Odometer from 'react-odometerjs';
import 'odometer/themes/odometer-theme-default.css'; 

const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
        return (
            <div className="rounded-lg border border-white/10 bg-black/90 px-2 py-1 text-xs font-bold text-white shadow-xl backdrop-blur-md">
                {payload[0].value.toLocaleString(undefined, { minimumFractionDigits: 2 })}
            </div>
        );
    }
    return null;
};

const MarketCard = ({ item }) => {
    const isPositive = parseFloat(item.change) >= 0;
    const graphData = item.graph_data ? item.graph_data.map((val, i) => ({ i, val })) : [];
    const symbol = ["nifty", "sensex", "gold", "silver", "usd_inr"].includes(item.id) ? "₹" : "$";
    
    // Style Logic
    let color = isPositive ? '#4ade80' : '#ef4444';
    let Icon = isPositive ? TrendingUp : TrendingDown;
    let iconColor = isPositive ? 'text-green-400' : 'text-red-400';
    let bgBadge = isPositive ? 'bg-green-500/10 border-green-500/20' : 'bg-red-500/10 border-red-500/20';

    if (item.id === 'gold') { color = '#fbbf24'; Icon = Coins; iconColor = 'text-yellow-400'; bgBadge = 'bg-yellow-500/10 border-yellow-500/20'; }
    if (item.id === 'silver') { color = '#94a3b8'; Icon = Coins; iconColor = 'text-slate-400'; bgBadge = 'bg-slate-500/10 border-slate-500/20'; }
    if (item.id === 'bitcoin') { color = '#f97316'; Icon = Bitcoin; iconColor = 'text-orange-400'; bgBadge = 'bg-orange-500/10 border-orange-500/20'; }

    // 👇 Helper to fix Odometer hydration issues (React needs values to be loaded)
    const [price, setPrice] = useState(0);
    useEffect(() => {
        setPrice(item.price);
    }, [item.price]);

    return (
        <div className="group relative min-w-0 flex flex-col justify-between overflow-hidden rounded-xl border border-white/10 bg-white/5 p-3 sm:p-5 backdrop-blur-sm transition-all hover:border-white/20 hover:shadow-lg hover:-translate-y-1 duration-300">
            
            {/* Header Section */}
            <div className="z-10 flex flex-col gap-1 pointer-events-none">
                <div className="flex justify-between items-start">
                    <h4 className="flex items-center gap-1.5 text-[10px] sm:text-xs font-bold uppercase tracking-widest text-gray-400 truncate">
                        <Icon size={12} className={iconColor} />
                        {item.id}
                    </h4>
                    <div className={`flex items-center gap-0.5 rounded px-1.5 py-0.5 text-[10px] font-bold border ${bgBadge} ${iconColor}`}>
                        {item.change}%
                    </div>
                </div>

                {/* 👇 NEW: ODOMETER COMPONENT */}
                <div className="flex items-baseline gap-0.5 text-lg sm:text-2xl font-bold text-white tracking-tight mt-1">
                    <span>{symbol}</span>
                    <Odometer 
                        value={price} 
                        format="(,ddd).dd" 
                        theme="default"
                    />
                </div>
            </div>

            {/* Graph Section */}
            <div className="mt-2 sm:mt-4 h-12 sm:h-16 w-full opacity-60 transition-opacity group-hover:opacity-100 relative">
                <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={graphData}>
                        <defs>
                            <linearGradient id={`color${item.id}`} x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor={color} stopOpacity={0.3}/>
                                <stop offset="95%" stopColor={color} stopOpacity={0}/>
                            </linearGradient>
                        </defs>
                        <Tooltip content={<CustomTooltip />} cursor={{ stroke: 'rgba(255,255,255,0.2)', strokeWidth: 1 }} />
                        <Area type="monotone" dataKey="val" stroke={color} strokeWidth={2} fillOpacity={1} fill={`url(#color${item.id})`} isAnimationActive={false} />
                        <YAxis domain={['dataMin', 'dataMax']} hide={true} />
                    </AreaChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
};

export default MarketCard;