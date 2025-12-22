import React, { useEffect, useState } from "react";
import { X, Calendar, Trash2, Plus } from "lucide-react"; 
import { getCookie } from "../utils/csrf";
import API_URL from './config';

const AssetDetailModal = ({ asset, onClose, onAddMore, onUpdate }) => { 
  const [details, setDetails] = useState(null);
  const [loading, setLoading] = useState(true);

  // FETCH DETAILS
  const fetchDetails = () => {
    setLoading(true);
    fetch(`${API_URL}/api/portfolio/holdings/${asset.id}/`, {
      credentials: "include",
    })
      .then((res) => {
        // 👇 CRITICAL FIX: If asset is gone (404), close modal and refresh parent
        if (res.status === 404) {
            onClose(); 
            if (onUpdate) onUpdate();
            return null;
        }
        return res.json();
      })
      .then((data) => {
        if (data) {
            setDetails(data);
            setLoading(false);
        }
      })
      .catch(() => {
          setLoading(false);
      });
  };

  useEffect(() => {
    fetchDetails();
  }, [asset]);

  // DELETE HANDLER 🗑️
  const handleDelete = async (txId) => {
    if (!confirm("Are you sure you want to delete this transaction?")) return;

    try {
        const res = await fetch(`${API_URL}/api/portfolio/transaction/delete/${txId}/`, {
            method: "DELETE",
            headers: { 
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie('csrftoken')
      },
            credentials: "include",
        });

        if (res.ok) {
            // Refresh parent immediately so Net Worth updates
            if (onUpdate) onUpdate();
            // Check if holding still exists (if not, 404 logic above handles it)
            fetchDetails(); 
        } else {
            alert("Error deleting transaction");
        }
    } catch (error) {
        console.error("Delete failed", error);
    }
  };

  if (!asset) return null;

  // 👇 SAFETY CHECK: If details is null (due to loading or error), don't render content yet
  // This prevents the "Black Screen" crash!
  if (!details && !loading) return null; 

  // Optional chaining (?.) ensures we don't crash if data is missing
  const currentVal = details?.current_value || 0;
  const avgPrice = details?.avg_price || 0;
  const totalQty = details?.total_qty || 0;
  
  const profit = currentVal - (avgPrice * totalQty);
  const isProfit = profit >= 0;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 animate-in fade-in duration-200">
      <div className="w-full max-w-lg rounded-2xl bg-gray-900 border border-white/10 shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        
        {/* HEADER */}
        <div className="flex items-center justify-between border-b border-white/10 p-5 bg-gray-900">
          <div>
            <h2 className="text-xl font-bold text-white">{asset.name}</h2>
            <span className="text-sm text-gray-400">{asset.symbol}</span>
          </div>
          
          <div className="flex gap-2">
              {/* 👇 THE BUTTON YOU WANTED */}
              <button 
                onClick={() => onAddMore(asset)}
                className="flex items-center gap-2 bg-cyan-500/10 text-cyan-400 px-3 py-1.5 rounded-full text-xs font-bold hover:bg-cyan-500/20 transition-all border border-cyan-500/20"
              >
                 <Plus size={14} /> Add / Sell
              </button>
              
              <button onClick={onClose} className="rounded-full p-2 bg-white/5 hover:bg-white/20 transition-all">
                <X size={20} />
              </button>
          </div>
        </div>

        {loading || !details ? (
          <div className="p-10 text-center text-gray-500">Loading history...</div>
        ) : (
          <div className="overflow-y-auto p-5">
            
            {/* SUMMARY CARD */}
            <div className={`rounded-xl p-5 mb-6 border ${isProfit ? 'bg-green-500/10 border-green-500/20' : 'bg-red-500/10 border-red-500/20'}`}>
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div>
                    <div className="text-xs text-gray-400 uppercase tracking-widest">Current Value</div>
                    <div className="text-2xl font-bold text-white">₹{currentVal.toLocaleString()}</div>
                </div>
                <div className="text-right">
                    <div className="text-xs text-gray-400 uppercase tracking-widest">Total Returns</div>
                    <div className={`text-2xl font-bold ${isProfit ? 'text-green-400' : 'text-red-400'}`}>
                        {isProfit ? '+' : ''}₹{profit.toLocaleString(undefined, {maximumFractionDigits: 2})}
                    </div>
                </div>
              </div>
              <div className="flex justify-between text-sm pt-4 border-t border-white/10 opacity-80">
                <span>Avg Price: <span className="text-white font-bold">₹{avgPrice.toLocaleString()}</span></span>
                <span>Qty: <span className="text-white font-bold">{totalQty}</span></span>
              </div>
            </div>

            {/* TRANSACTION HISTORY LIST */}
            <h3 className="font-bold text-white mb-3 flex items-center gap-2">
                <Calendar size={16} className="text-cyan-400"/> History
            </h3>
            
            {details.transactions.length === 0 ? (
                <div className="text-center py-4 text-gray-500 text-sm">No transactions found.</div>
            ) : (
                <div className="space-y-3">
                    {details.transactions.map((tx) => (
                        <div key={tx.id} className="flex items-center justify-between bg-black p-3 rounded-lg border border-white/10 group">
                            <div className="flex items-center gap-3">
                                <div className={`px-2 py-1 rounded text-xs font-bold ${tx.type === 'BUY' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                                    {tx.type}
                                </div>
                                <div>
                                    <div className="text-sm font-bold text-white">₹{tx.price}</div>
                                    <div className="text-xs text-gray-500">{tx.date}</div>
                                </div>
                            </div>
                            
                            <div className="flex items-center gap-4">
                                <div className="text-right">
                                    <div className="text-sm font-bold text-white">{tx.qty} units</div>
                                    <div className="text-xs text-gray-500">Total: ₹{tx.total.toLocaleString()}</div>
                                </div>
                                
                                <button 
                                    onClick={() => handleDelete(tx.id)}
                                    className="text-gray-600 hover:text-red-500 transition-colors opacity-0 group-hover:opacity-100 p-1"
                                    title="Delete Transaction"
                                >
                                    <Trash2 size={16} />
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default AssetDetailModal;