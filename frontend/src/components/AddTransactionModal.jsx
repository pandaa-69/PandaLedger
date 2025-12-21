import React, { useState, useEffect } from "react";
import { X, Search, Check, Loader, Calendar, Info } from "lucide-react"; // Import Info icon

const AddTransactionModal = ({ onClose, onSuccess, prefillAsset = null }) => {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [selectedAsset, setSelectedAsset] = useState(prefillAsset);
  const [loading, setLoading] = useState(false);
  
  const [qty, setQty] = useState("");
  const [price, setPrice] = useState(prefillAsset ? prefillAsset.current_price || prefillAsset.price : "");
  const [type, setType] = useState("BUY");
  const [date, setDate] = useState(new Date().toISOString().split("T")[0]);

  // SEARCH LOGIC
  useEffect(() => {
    if (selectedAsset) return;

    const delayDebounceFn = setTimeout(() => {
      if (query.length > 1) {
        setLoading(true);
        const safetyTimer = setTimeout(() => setLoading(false), 5000);

        fetch(`http://127.0.0.1:8000/api/portfolio/search/?q=${query}`, {
          credentials: "include",
        })
          .then((res) => res.json())
          .then((data) => {
            setResults(data);
            setLoading(false);
            clearTimeout(safetyTimer);
          })
          .catch(() => setLoading(false));
      } else {
        setResults([]);
      }
    }, 500);

    return () => clearTimeout(delayDebounceFn);
  }, [query, selectedAsset]);

  const handleSubmit = async () => {
    if (!selectedAsset || !qty || !price) return;

    const payload = {
      asset_id: selectedAsset.id,
      qty: parseFloat(qty),
      price: parseFloat(price),
      type: type,
      date: date,
    };

    try {
      const res = await fetch("http://127.0.0.1:8000/api/portfolio/transaction/add/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        onSuccess();
        onClose();
      } else {
        alert("Failed to add transaction");
      }
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 animate-in fade-in duration-200">
      <div className="w-full max-w-md rounded-2xl bg-gray-900 border border-white/10 shadow-2xl overflow-hidden">
        
        <div className="flex items-center justify-between border-b border-white/10 p-4 bg-gray-900/50">
          <h2 className="text-lg font-bold text-white">
              {prefillAsset ? `Trade ${prefillAsset.symbol}` : "Add Asset"}
          </h2>
          <button onClick={onClose} className="rounded-full p-1 text-gray-400 hover:bg-white/10 hover:text-white">
            <X size={20} />
          </button>
        </div>

        <div className="p-4">
          {!selectedAsset ? (
            <div className="relative">
              <div className="relative">
                <Search className="absolute left-3 top-3 text-gray-500" size={18} />
                <input
                  type="text"
                  placeholder="Ticker Symbol (e.g. MON100, TATAMOTORS)"
                  className="w-full rounded-xl bg-black border border-white/20 py-2.5 pl-10 pr-4 text-white focus:border-cyan-500 focus:outline-none focus:ring-1 focus:ring-cyan-500"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  autoFocus
                />
                {loading && <Loader className="absolute right-3 top-3 animate-spin text-cyan-400" size={18} />}
              </div>

              {/* 👇 SEARCH TIP: Explains why name search fails */}
              <div className="mt-3 flex gap-2 items-start bg-blue-500/10 p-3 rounded-lg border border-blue-500/20">
                  <Info size={16} className="text-blue-400 mt-0.5 flex-shrink-0" />
                  <p className="text-xs text-blue-200/80 leading-relaxed">
                      Search using the <b>Ticker Symbol</b> for best results. <br/>
                      Ex: Use <b>MON100</b> instead of "Motilal Nasdaq".
                  </p>
              </div>

              {results.length > 0 && (
                <div className="mt-2 max-h-60 overflow-y-auto rounded-xl border border-white/10 bg-black/50">
                  {results.map((asset) => (
                    <button
                      key={asset.id}
                      onClick={() => {
                        setSelectedAsset(asset);
                        setPrice(asset.price);
                        setQuery("");
                      }}
                      className="flex w-full items-center justify-between px-4 py-3 text-left hover:bg-white/10 transition-colors"
                    >
                      <div>
                        <div className="font-bold text-white">{asset.name}</div>
                        <div className="text-xs text-gray-400">{asset.symbol} • {asset.type}</div>
                      </div>
                      <div className="text-right text-sm font-medium text-cyan-400">
                        ₹{asset.price.toLocaleString()}
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <div className="space-y-4 animate-in slide-in-from-right-10 duration-300">
              
              <div className="flex items-center justify-between rounded-xl bg-cyan-900/20 border border-cyan-500/30 p-3">
                <div>
                  <div className="font-bold text-cyan-400">{selectedAsset.name}</div>
                  <div className="text-xs text-cyan-200/60">{selectedAsset.symbol}</div>
                </div>
                {!prefillAsset && (
                    <button onClick={() => setSelectedAsset(null)} className="text-xs font-bold text-gray-400 hover:text-white underline">Change</button>
                )}
              </div>

              <div className="flex rounded-lg bg-white/5 p-1">
                <button onClick={() => setType("BUY")} className={`flex-1 rounded-md py-1.5 text-sm font-bold transition-all ${type === "BUY" ? "bg-green-600 text-white shadow" : "text-gray-400 hover:text-white"}`}>Buy</button>
                <button onClick={() => setType("SELL")} className={`flex-1 rounded-md py-1.5 text-sm font-bold transition-all ${type === "SELL" ? "bg-red-600 text-white shadow" : "text-gray-400 hover:text-white"}`}>Sell</button>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="mb-1 block text-xs font-medium text-gray-400">Quantity</label>
                  <input type="number" placeholder="0" value={qty} onChange={(e) => setQty(e.target.value)} className="w-full rounded-lg bg-black border border-white/20 p-2.5 text-white focus:border-cyan-500 focus:outline-none" />
                </div>
                <div>
                  <label className="mb-1 block text-xs font-medium text-gray-400">Price (₹)</label>
                  <input type="number" value={price} onChange={(e) => setPrice(e.target.value)} className="w-full rounded-lg bg-black border border-white/20 p-2.5 text-white focus:border-cyan-500 focus:outline-none" />
                </div>
              </div>

              <div>
                  <label className="mb-1 block text-xs font-medium text-gray-400">Transaction Date</label>
                  <div className="relative">
                    <Calendar size={16} className="absolute left-3 top-3 text-gray-500 pointer-events-none"/>
                    <input 
                        type="date" 
                        value={date} 
                        onChange={(e) => setDate(e.target.value)} 
                        className="w-full rounded-lg bg-black border border-white/20 p-2.5 pl-10 text-white focus:border-cyan-500 focus:outline-none [color-scheme:dark]" 
                    />
                  </div>
              </div>

              <div className="flex justify-between border-t border-white/10 pt-4 mt-2">
                <span className="text-sm text-gray-400">Total Value</span>
                <span className="text-lg font-bold text-white">₹{((parseFloat(qty) || 0) * (parseFloat(price) || 0)).toLocaleString()}</span>
              </div>

              <button onClick={handleSubmit} className="w-full rounded-xl bg-white py-3 font-bold text-black hover:bg-gray-200 active:scale-95 transition-all flex justify-center items-center gap-2">
                <Check size={18} /> Confirm Transaction
              </button>

            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AddTransactionModal;