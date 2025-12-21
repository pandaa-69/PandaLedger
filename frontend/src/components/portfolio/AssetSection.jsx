import React from 'react';
import { ChevronRight } from 'lucide-react';

const AssetSection = ({ title, assets, icon, onAssetClick, color }) => {
  if (!assets || assets.length === 0) return null;
  const total = assets.reduce((sum, a) => sum + a.current_value, 0);
  
  return (
    <div className="animate-in slide-in-from-bottom-4 duration-700">
      <div className="flex items-center justify-between mb-4 px-2">
        <h3 className="flex items-center gap-3 font-black text-lg text-white">
          <span className="p-2 bg-white/5 rounded-lg">{icon}</span>
          {title}
        </h3>
        <div className="text-[10px] font-bold text-gray-500 bg-white/5 px-3 py-1 rounded-full border border-white/5 uppercase tracking-widest">
          Sub-total: <span className="text-gray-300">₹{total.toLocaleString()}</span>
        </div>
      </div>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {assets.map((asset, idx) => (
          <button
            key={idx}
            onClick={() => onAssetClick(asset)}
            className="group relative text-left bg-gray-900/40 hover:bg-gray-800/60 border border-white/5 hover:border-cyan-500/30 p-5 rounded-2xl transition-all duration-300 active:scale-[0.98]"
          >
            <div className="flex justify-between items-start">
              <div className="max-w-[65%]">
                <div className="font-bold text-white truncate text-base group-hover:text-cyan-400 transition-colors">
                  {asset.name}
                </div>
                <div className="text-[10px] font-bold text-gray-500 mt-1 uppercase tracking-widest">
                  {asset.symbol.split(".")[0]} • {Number(asset.qty).toFixed(2)} qty
                </div>
              </div>
              <div className="text-right">
                <div className="font-bold text-white text-lg tracking-tight">
                  ₹{asset.current_value.toLocaleString()}
                </div>
                <div className={`text-[11px] font-black mt-1 flex items-center justify-end gap-1 px-2 py-0.5 rounded-full ${asset.profit >= 0 ? 'text-emerald-400 bg-emerald-400/10' : 'text-red-400 bg-red-400/10'}`}>
                  {asset.profit >= 0 ? "+" : ""}
                  {asset.profit.toLocaleString(undefined, { maximumFractionDigits: 0 })} ({asset.profit_pct}%)
                </div>
              </div>
            </div>
            <div className="absolute right-2 bottom-2 text-white/0 group-hover:text-white/20 transition-all">
              <ChevronRight size={14} />
            </div>
          </button>
        ))}
      </div>
    </div>
  );
};

export default AssetSection;