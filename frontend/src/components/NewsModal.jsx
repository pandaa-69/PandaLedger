import React from 'react';
import { X, ExternalLink, Search, Newspaper } from 'lucide-react'; // 👈 Import Newspaper icon

const NewsModal = ({ article, onClose }) => {
    if (!article) return null;

    const isBadLink = !article.link || article.link === "#";
    
    const handleReadClick = () => {
        let finalUrl = article.link;
        
        if (isBadLink) {
            const query = encodeURIComponent(`${article.title} ${article.publisher} news`);
            finalUrl = `https://www.google.com/search?q=${query}&tbm=nws`;
        }
        
        window.open(finalUrl, "_blank", "noopener,noreferrer");
    };

    return (
        <div className="fixed inset-0 z-50 flex items-start pt-20 sm:pt-0 sm:items-center justify-center p-4">
            {/* Backdrop Blur */}
            <div 
                className="absolute inset-0 bg-black/80 backdrop-blur-sm transition-opacity animate-in fade-in duration-300"
                onClick={onClose}
            ></div>

            {/* Modal Content */}
            <div className="relative w-full max-w-lg overflow-hidden rounded-2xl border border-white/10 bg-gray-950 shadow-2xl animate-in zoom-in-95 slide-in-from-bottom-8 duration-300">
                
                {/* Image Header with NEW Fallback */}
                <div className="relative h-56 w-full bg-black">
                    {article.image ? (
                        <img 
                            src={article.image} 
                            alt="News" 
                            className="h-full w-full object-cover opacity-90"
                        />
                    ) : (
                        // 👇 NEW "PIXEL GRID" FALLBACK 👇
                        <div className="h-full w-full flex flex-col items-center justify-center relative overflow-hidden">
                            {/* CSS Grid Pattern Background */}
                            <div className="absolute inset-0 opacity-20 bg-[linear-gradient(to_right,#ffffff0a_1px,transparent_1px),linear-gradient(to_bottom,#ffffff0a_1px,transparent_1px)] bg-[size:32px_32px]"></div>
                            <div className="absolute inset-0 bg-gradient-to-t from-gray-950 via-transparent to-transparent"></div>
                            
                            {/* Big Icon & Text */}
                            <div className="z-10 flex flex-col items-center gap-3 opacity-30 animate-pulse">
                                <Newspaper size={64} />
                                <span className="text-sm font-bold uppercase tracking-widest">No Image Available</span>
                            </div>
                        </div>
                    )}
                    
                    {/* Close Button */}
                    <button 
                        onClick={onClose}
                        className="absolute right-3 top-3 rounded-full bg-black/40 p-2 text-white backdrop-blur-md hover:bg-white/20 transition-all active:scale-90 z-20"
                    >
                        <X size={18} />
                    </button>

                    {/* Tag Overlay */}
                    <div className="absolute bottom-0 left-0 w-full bg-gradient-to-t from-gray-950 via-gray-950/80 to-transparent p-6 pt-16 z-10">
                        <span className="inline-block rounded-md bg-cyan-500/20 px-2 py-1 text-[10px] font-bold uppercase tracking-widest text-cyan-300 border border-cyan-500/30 shadow-[0_0_10px_rgba(6,182,212,0.2)]">
                            {article.tag}
                        </span>
                    </div>
                </div>

                {/* Body */}
                <div className="p-6 pt-2 relative z-20">
                    <div className="mb-4 flex items-center gap-2 text-xs text-gray-400">
                        <span className="font-bold text-cyan-200">{article.publisher}</span>
                        <span className="opacity-50">•</span>
                        <span className="font-mono">{new Date(article.time).toLocaleDateString()}</span>
                    </div>

                    <h3 className="mb-8 text-xl font-bold leading-relaxed text-white line-clamp-4 font-heading">
                        {article.title}
                    </h3>

                    {/* The Smart Button */}
                    <button 
                        onClick={handleReadClick}
                        className={`group flex w-full items-center justify-center gap-2 rounded-xl py-4 text-sm font-bold transition-all active:scale-95 ${
                            isBadLink 
                            ? "bg-gradient-to-r from-orange-500 to-red-500 text-white shadow-lg shadow-orange-500/20 hover:brightness-110" 
                            : "bg-white text-black hover:bg-gray-200"
                        }`}
                    >
                        {isBadLink ? (
                            <>
                                <Search size={18} /> Search on Google
                            </>
                        ) : (
                            <>
                                <ExternalLink size={18} /> Read Full Article
                            </>
                        )}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default NewsModal;