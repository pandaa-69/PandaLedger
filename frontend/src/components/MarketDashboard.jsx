import React, { useEffect, useState } from 'react';
import { 
    TrendingUp, TrendingDown, Newspaper, RefreshCw, Clock, Globe, 
    ChevronDown, MapPin, Zap
} from 'lucide-react';
import MarketCard from './MarketCard';
import NewsModal from './NewsModal'; // 👈 1. Import the Modal
import API_URL from './config';
// --- INTERNAL COMPONENTS ---
// 1. Live Clock
const LiveClock = ({ city, timeZone, isActive, onClick }) => {
    const [time, setTime] = useState("");
    useEffect(() => {
        const update = () => {
             const t = new Intl.DateTimeFormat('en-US', {
                timeZone, hour: '2-digit', minute: '2-digit', hour12: false
            }).format(new Date());
            setTime(t);
        };
        update();
        const i = setInterval(update, 1000);
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

// 2. Ticker Tape
const TickerTape = ({ items }) => {
    const tickerItems = [...items, ...items]; 
    return (
        <div className="fixed top-16 left-0 right-0 z-40 flex w-full overflow-hidden border-y border-white/5 bg-black/80 backdrop-blur-md shadow-lg pointer-events-none">
            <div className="absolute left-0 top-0 z-10 h-full w-16 bg-gradient-to-r from-black to-transparent"></div>
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
            <div className="absolute right-0 top-0 z-10 h-full w-16 bg-gradient-to-l from-black to-transparent"></div>
        </div>
    );
};

// 3. Helper for News Images
const SafeNewsImage = ({ src, alt }) => {
    const [hasError, setHasError] = useState(false);
    if (hasError || !src) return null; 
    return (
        <img src={src} alt={alt} onError={() => setHasError(true)} className="h-14 w-14 sm:h-16 sm:w-16 rounded-lg object-cover opacity-80" />
    );
};

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

const DashboardSkeleton = () => (
    <div className="mb-10 animate-pulse px-2">
        <div className="mb-6 h-8 w-48 rounded bg-white/10"></div>
        <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
            {[1,2,3,4].map(i => <div key={i} className="h-32 rounded-xl border border-white/5 bg-white/5"></div>)}
        </div>
    </div>
);

// --- MAIN COMPONENT ---
const MarketDashboard = () => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const [activeCity, setActiveCity] = useState(null); 
    const [selectedArticle, setSelectedArticle] = useState(null); // 👈 2. State for Modal

    const marketStatus = getMarketStatus();

    const fetchData = (isAutoRefresh = false) => {
        if (!isAutoRefresh) setRefreshing(true); 
        
        fetch(`${API_URL}/api/dashboard/live/`)
            .then(res => res.ok ? res.json() : Promise.reject("Failed"))
            .then(newData => { 
                setData(newData); 
                setLoading(false); 
                setRefreshing(false); 
            })
            .catch(err => { 
                console.error(err); 
                setLoading(false); 
                setRefreshing(false); 
            });
    };

    useEffect(() => { 
        fetchData(); 
        const interval = setInterval(() => {
            fetchData(true); 
        }, 30000); 
        return () => clearInterval(interval);
    }, []);

    if (loading) return <DashboardSkeleton />;
    if (!data) return <div className="text-center text-red-500 py-10">Data Unavailable</div>;

    return (
        <div className="mb-10 animate-in fade-in duration-700">
            
            {/* Header */}
            <div className="mb-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4 px-1">
                <div className="flex items-center gap-3">
                    <h2 className="text-lg font-bold text-white">Market Pulse</h2>
                    <span className={`flex items-center gap-1 text-[10px] font-bold uppercase tracking-wider ${marketStatus.color}`}>
                        <div className={`h-1.5 w-1.5 rounded-full ${marketStatus.isOpen ? "bg-green-400 animate-pulse" : "bg-red-400"}`}></div>
                        {marketStatus.text}
                    </span>
                </div>
                
                <button 
                    onClick={() => fetchData(false)} 
                    className="flex w-fit items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-1.5 text-xs font-bold text-gray-300 transition-all hover:bg-white/10 active:scale-95"
                >
                    <RefreshCw size={12} className={refreshing ? "animate-spin" : ""} />
                    {refreshing ? "Updating..." : "Refresh Prices"}
                </button>
            </div>

            {/* Ticker Tape */}
            <TickerTape items={data.market_summary} />

            {/* 1. ASSET GRAPHS */}
            <div className="grid grid-cols-2 gap-3 sm:gap-4 lg:grid-cols-4 mb-6">
                {data.market_summary.map((item) => (
                    <MarketCard key={item.id} item={item} />
                ))}
            </div>

            {/* 2. GLOBAL CLOCKS */}
            <div className="mb-8">
                <div className="flex flex-wrap gap-2 justify-center sm:justify-start">
                    <div className="flex items-center gap-2 rounded-full bg-black/40 px-3 py-2 text-[10px] font-bold uppercase tracking-widest text-gray-500">
                        <Globe size={12} /> Global Hours
                    </div>
                    {["New York", "London", "Mumbai", "Tokyo"].map((city) => {
                         const tz = city === "New York" ? "America/New_York" : city === "London" ? "Europe/London" : city === "Mumbai" ? "Asia/Kolkata" : "Asia/Tokyo";
                         return (
                            <LiveClock 
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

            {/* 3. NEWS (Now opens Modal!) */}
            <h3 className="mt-8 mb-4 flex items-center gap-2 text-base md:text-lg font-bold text-gray-200 px-1">
                <Newspaper size={18} className="text-cyan-400" /> 
                Market News
            </h3>
            
            <div className="flex gap-3 overflow-x-auto pb-4 md:grid md:grid-cols-2 lg:grid-cols-3 md:overflow-visible">
                {data.news.map((newsItem, index) => (
                    <div 
                        key={index} 
                        onClick={() => setSelectedArticle(newsItem)} // 👈 Open Modal
                        className="cursor-pointer min-w-[280px] md:min-w-0 flex gap-3 rounded-xl border border-white/5 bg-white/5 p-3 transition-all hover:border-cyan-500/30 hover:bg-white/10"
                    >
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
                    </div>
                ))}
            </div>

            {/* 4. RENDER MODAL */}
            {selectedArticle && (
                <NewsModal 
                    article={selectedArticle} 
                    onClose={() => setSelectedArticle(null)} 
                />
            )}
        </div>
    );
};

export default MarketDashboard;