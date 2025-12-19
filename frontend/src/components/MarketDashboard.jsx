import React, { useEffect, useState } from 'react';
import { 
    TrendingUp, TrendingDown, Newspaper, RefreshCw, Clock, 
    Coins, Bitcoin, Globe, ChevronDown, MapPin, Zap
} from 'lucide-react';
import { AreaChart, Area, ResponsiveContainer, YAxis, Tooltip } from 'recharts';

// --- CONFIG ---
const MARKET_DETAILS = {
    "New York": { exchange: "NYSE", local: "09:30 - 16:00 ET", ist: "20:00 - 02:30 IST", status: "Impacts IT Sector" },
    "London": { exchange: "LSE", local: "08:00 - 16:30 GMT", ist: "13:30 - 22:00 IST", status: "Banking & Metals" },
    "Mumbai": { exchange: "NSE", local: "09:15 - 15:30 IST", ist: "09:15 - 15:30 IST", status: "Home Market" },
    "Tokyo": { exchange: "TSE", local: "09:00 - 15:00 JST", ist: "05:30 - 11:30 IST", status: "Asian Trend Setter" }
};

const getMarketStatus = () => {
    const now = new Date();
    const day = now.getDay(); 
    const hour = now.getHours();
    const minute = now.getMinutes();

    if (day === 0 || day === 6) return { isOpen: false, text: "Closed", color: "text-red-400" };
    const timeInMinutes = hour * 60 + minute;
    if (timeInMinutes < 555) return { isOpen: false, text: "Pre-Market", color: "text-yellow-400" };
    else if (timeInMinutes > 930) return { isOpen: false, text: "Closed", color: "text-gray-400" };
    else return { isOpen: true, text: "Open", color: "text-green-400" };
};

// --- COMPONENT: TICKER TAPE (The Scrolling Bar) ---
const TickerTape = ({ items }) => {
    // Duplicate items for infinite loop
    const tickerItems = [...items, ...items]; 

    return (
        // 🛠️ FIXED POSITIONING: 
        // top-16 (64px) accounts for the Navbar height.
        // z-40 ensures it floats above everything else.
        <div className="fixed top-16 left-0 right-0 z-40 flex w-full overflow-hidden border-y border-white/5 bg-black/80 backdrop-blur-md shadow-lg">
            
            {/* Left Fade Overlay */}
            <div className="absolute left-0 top-0 z-10 h-full w-16 bg-gradient-to-r from-black to-transparent"></div>
            
            {/* The Moving Track */}
            <div className="flex animate-scroll whitespace-nowrap py-2">
                {tickerItems.map((item, index) => {
                    const isPositive = parseFloat(item.change) >= 0;
                    return (
                        <div key={`${item.id}-${index}`} className="mx-6 flex items-center gap-2 text-xs font-bold uppercase tracking-widest">
                            <span className="text-gray-400">{item.id}</span>
                            <span className="text-white">
                                {["nifty", "sensex", "gold", "silver", "usd_inr"].includes(item.id) ? "₹" : "$"}
                                {item.price.toLocaleString()}
                            </span>
                            <span className={`flex items-center ${isPositive ? "text-green-400" : "text-red-400"}`}>
                                {isPositive ? <TrendingUp size={12} className="mr-1"/> : <TrendingDown size={12} className="mr-1"/>}
                                {item.change}%
                            </span>
                        </div>
                    );
                })}
            </div>

            {/* Right Fade Overlay */}
            <div className="absolute right-0 top-0 z-10 h-full w-16 bg-gradient-to-l from-black to-transparent"></div>
        </div>
    );
};

// --- COMPONENT: Compact Clock ---
const CompactClock = ({ city, timeZone, isActive, onClick }) => {
    const [time, setTime] = useState("");
    useEffect(() => {
        const update = () => setTime(new Date().toLocaleTimeString("en-US", { timeZone, hour: '2-digit', minute: '2-digit', hour12: false }));
        update();
        const i = setInterval(update, 1000 * 60);
        return () => clearInterval(i);
    }, [timeZone]);

    return (
        <button 
            onClick={onClick}
            className={`flex items-center gap-2 rounded-full border px-3 py-1.5 text-xs font-bold transition-all active:scale-95 ${
                isActive 
                ? "border-cyan-500 bg-cyan-500/10 text-white shadow-[0_0_10px_rgba(6,182,212,0.2)]" 
                : "border-white/5 bg-white/5 text-gray-400 hover:bg-white/10 hover:border-white/10"
            }`}
        >
            <span className="uppercase tracking-wider text-[10px]">{city}</span>
            <span className={`font-mono ${isActive ? "text-cyan-400" : "text-gray-500"}`}>{time}</span>
        </button>
    );
};

const SafeNewsImage = ({ src, alt }) => {
    const [hasError, setHasError] = useState(false);
    if (hasError || !src) return null; 
    return (
        <img 
            src={src} 
            alt={alt} 
            onError={() => setHasError(true)}
            className="h-14 w-14 sm:h-16 sm:w-16 rounded-lg object-cover opacity-80" 
        />
    );
};

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

const MarketDashboard = () => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const [activeCity, setActiveCity] = useState(null); 
    const marketStatus = getMarketStatus();

    const fetchData = () => {
        setRefreshing(true);
        fetch('http://127.0.0.1:8000/api/dashboard/live/')
            .then(res => res.ok ? res.json() : Promise.reject("Failed"))
            .then(data => { 
                setData(data); 
                setLoading(false); 
                setRefreshing(false); 
            })
            .catch(err => { console.error(err); setLoading(false); setRefreshing(false); });
    };

    useEffect(() => { fetchData(); }, []);

    if (loading) return <DashboardSkeleton />;
    if (!data) return <div className="text-center text-red-500 py-10">Data Unavailable</div>;

    return (
        <div className="mb-10 animate-in fade-in duration-700">
            
            {/* HEADER with Controls */}
            <div className="mb-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4 px-1">
                <div className="flex items-center gap-3">
                    <h2 className="text-lg font-bold text-white">Market Pulse</h2>
                    <span className={`flex items-center gap-1 text-[10px] font-bold uppercase tracking-wider ${marketStatus.color}`}>
                        <div className={`h-1.5 w-1.5 rounded-full ${marketStatus.isOpen ? "bg-green-400 animate-pulse" : "bg-red-400"}`}></div>
                        {marketStatus.text}
                    </span>
                </div>
                
                <button 
                    onClick={fetchData} 
                    className="flex w-fit items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-1.5 text-xs font-bold text-gray-300 transition-all hover:bg-white/10 active:scale-95"
                >
                    <RefreshCw size={12} className={refreshing ? "animate-spin" : ""} />
                    {refreshing ? "Updating..." : "Refresh Prices"}
                </button>
            </div>

            {/* 🆕 NEW TICKER TAPE (Uses real data) */}
            <TickerTape items={data.market_summary} />

            {/* 1. ASSET GRAPHS */}
            <div className="grid grid-cols-2 gap-3 sm:gap-4 lg:grid-cols-4 mb-6">
                {data.market_summary.map((item) => {
                    const isPositive = parseFloat(item.change) >= 0;
                    const graphData = item.graph_data ? item.graph_data.map((val, i) => ({ i, val })) : [];
                    const symbol = ["nifty", "sensex", "gold", "silver", "usd_inr"].includes(item.id) ? "₹" : "$";
                    
                    let color = isPositive ? '#4ade80' : '#ef4444';
                    let Icon = isPositive ? TrendingUp : TrendingDown;
                    let iconColor = isPositive ? 'text-green-400' : 'text-red-400';
                    let bgBadge = isPositive ? 'bg-green-500/10 border-green-500/20' : 'bg-red-500/10 border-red-500/20';

                    if (item.id === 'gold') { color = '#fbbf24'; Icon = Coins; iconColor = 'text-yellow-400'; bgBadge = 'bg-yellow-500/10 border-yellow-500/20'; }
                    if (item.id === 'silver') { color = '#94a3b8'; Icon = Coins; iconColor = 'text-slate-400'; bgBadge = 'bg-slate-500/10 border-slate-500/20'; }
                    if (item.id === 'bitcoin') { color = '#f97316'; Icon = Bitcoin; iconColor = 'text-orange-400'; bgBadge = 'bg-orange-500/10 border-orange-500/20'; }

                    return (
                        <div key={item.id} className="group relative min-w-0 flex flex-col justify-between overflow-hidden rounded-xl border border-white/10 bg-white/5 p-3 sm:p-5 backdrop-blur-sm transition-all hover:border-white/20 hover:shadow-lg">
                            <div className="z-10 flex flex-col gap-1 pointer-events-none">
                                <div className="flex justify-between items-start">
                                    <h4 className="flex items-center gap-1.5 text-[10px] sm:text-xs font-bold uppercase tracking-widest text-gray-400 truncate">
                                        <Icon size={12} className={iconColor} />
                                        {item.id}
                                    </h4>
                                    <div className={`flex items-center gap-0.5 rounded px-1.5 py-0.5 text-[10px] font-bold border ${bgBadge} ${iconColor}`}>
                                        <Icon size={10} />
                                        {item.change}%
                                    </div>
                                </div>
                                <div className="text-lg sm:text-2xl font-bold text-white tracking-tight">
                                    {symbol}{item.price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                                </div>
                            </div>
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
                })}
            </div>

            {/* 2. COMPACT GLOBAL CLOCKS */}
            <div className="mb-8">
                <div className="flex flex-wrap gap-2 justify-center sm:justify-start">
                    <div className="flex items-center gap-2 rounded-full bg-black/40 px-3 py-2 text-[10px] font-bold uppercase tracking-widest text-gray-500">
                        <Globe size={12} /> Global Hours
                    </div>
                    {["New York", "London", "Mumbai", "Tokyo"].map((city) => {
                         const tz = city === "New York" ? "America/New_York" : city === "London" ? "Europe/London" : city === "Mumbai" ? "Asia/Kolkata" : "Asia/Tokyo";
                         return (
                            <CompactClock 
                                key={city}
                                city={city}
                                timeZone={tz}
                                isActive={activeCity === city}
                                onClick={() => setActiveCity(activeCity === city ? null : city)}
                            />
                         )
                    })}
                </div>

                {activeCity && (
                    <div className="mt-3 animate-in fade-in slide-in-from-top-1 duration-200">
                        <div className="flex items-center justify-between rounded-lg border border-cyan-500/30 bg-cyan-900/10 p-4 backdrop-blur-md">
                            <div className="flex items-center gap-3">
                                <MapPin size={18} className="text-cyan-400" />
                                <div>
                                    <span className="block text-sm font-bold text-white">{activeCity} <span className="text-gray-400 text-xs font-normal">({MARKET_DETAILS[activeCity].exchange})</span></span>
                                    <div className="flex items-center gap-1 mt-1 text-xs text-gray-300">
                                        <Zap size={10} className="text-cyan-400" />
                                        {MARKET_DETAILS[activeCity].status}
                                    </div>
                                </div>
                            </div>
                            <div className="text-right">
                                <span className="block text-[10px] uppercase text-gray-500">Your Time (India)</span>
                                <span className="block font-mono text-sm font-bold text-cyan-400">{MARKET_DETAILS[activeCity].ist}</span>
                            </div>
                        </div>
                    </div>
                )}
            </div>

            {/* 3. NEWS */}
            <h3 className="mt-8 mb-4 flex items-center gap-2 text-base md:text-lg font-bold text-gray-200 px-1">
                <Newspaper size={18} className="text-cyan-400" /> 
                Market News
            </h3>
            
            <div className="flex gap-3 overflow-x-auto pb-4 md:grid md:grid-cols-2 lg:grid-cols-3 md:overflow-visible">
                {data.news.map((newsItem, index) => (
                    <a key={index} href={newsItem.link} target="_blank" rel="noreferrer" className="min-w-[280px] md:min-w-0 flex gap-3 rounded-xl border border-white/5 bg-white/5 p-3 transition-all hover:border-cyan-500/30 hover:bg-white/10">
                        <div className="flex flex-1 flex-col justify-between">
                            <div>
                                <div className="mb-1 flex items-center gap-2 text-[9px] sm:text-[10px] font-bold uppercase tracking-wider text-gray-500">
                                    <span className="text-cyan-400">{newsItem.tag}</span>
                                    <span>•</span>
                                    <span>{newsItem.publisher}</span>
                                </div>
                                <h4 className="line-clamp-2 text-xs sm:text-sm font-medium leading-relaxed text-gray-200">
                                    {newsItem.title}
                                </h4>
                            </div>
                        </div>
                        <SafeNewsImage src={newsItem.image} alt="news" />
                    </a>
                ))}
            </div>
        </div>
    );
};

const DashboardSkeleton = () => (
    <div className="mb-10 animate-pulse px-2">
        <div className="mb-6 h-8 w-48 rounded bg-white/10"></div>
        <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
            {[1,2,3,4].map(i => <div key={i} className="h-32 rounded-xl border border-white/5 bg-white/5"></div>)}
        </div>
    </div>
);

export default MarketDashboard;