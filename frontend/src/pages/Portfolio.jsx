import React, { useState, useEffect } from "react";
import { BarChart3, Calculator } from "lucide-react";

// 👇 The new modular imports
import WealthCalculator from "../components/WealthCalculator";
import AddTransactionModal from "../components/AddTransactionModal";
import AssetDetailModal from "../components/AssetDetailModal";
import HoldingsTab from "../components/portfolio/HoldingsTab";
import AnalyticsTab from "../components/portfolio/AnalyticsTab";
import API_URL from './config';

const Portfolio = () => {
  const [portfolio, setPortfolio] = useState({ holdings: [], summary: {} });
  const [analytics, setAnalytics] = useState({ metrics: {}, sectors: [], performance_graph: [] });
  const [activeTab, setActiveTab] = useState("holdings");
  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedAssetForDetail, setSelectedAssetForDetail] = useState(null);
  const [prefillAsset, setPrefillAsset] = useState(null);

  const fetchPortfolio = () => {
    fetch(`${API_URL}/api/portfolio/holdings/`, { credentials: "include" })
      .then((res) => res.json())
      .then((data) => setPortfolio(data))
      .catch((err) => console.error(err));
  };

  const fetchAnalytics = () => {
    fetch(`${API_URL}/api/analytics/dashboard/`, { credentials: "include" })
      .then((res) => res.json())
      .then((data) => setAnalytics(data))
      .catch((err) => console.error(err));
  };

  useEffect(() => {
    fetchPortfolio();
    fetchAnalytics();
  }, []);

  const handleAddMore = (asset) => {
    setPrefillAsset(asset);
    setSelectedAssetForDetail(null);
    setShowAddModal(true);
  };

  const refreshData = () => {
    fetchPortfolio();
    fetchAnalytics();
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-20 animate-in fade-in duration-700">
      
      {/* Minimalist Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center py-8 gap-4">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-white flex items-center gap-3">
            PandaVault <span className="text-xs bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 px-2 py-1 rounded-md uppercase tracking-widest font-bold">Pro</span>
          </h1>
        </div>
        <div className="flex bg-gray-900/50 backdrop-blur-md p-1 rounded-xl border border-white/10 shadow-inner">
          <button onClick={() => setActiveTab("holdings")} className={`px-5 py-2 rounded-lg text-sm font-bold transition-all ${activeTab === "holdings" ? "bg-cyan-500 text-black shadow-lg shadow-cyan-500/20" : "text-gray-400 hover:text-white"}`}>Holdings</button>
          <button onClick={() => setActiveTab("analytics")} className={`px-5 py-2 rounded-lg text-sm font-bold transition-all flex items-center gap-2 ${activeTab === "analytics" ? "bg-indigo-600 text-white shadow-lg shadow-indigo-500/20" : "text-gray-400 hover:text-white"}`}><BarChart3 size={16} /> Analytics</button>
          <button onClick={() => setActiveTab("calculator")} className={`px-5 py-2 rounded-lg text-sm font-bold transition-all flex items-center gap-2 ${activeTab === "calculator" ? "bg-purple-600 text-white shadow-lg shadow-purple-500/20" : "text-gray-400 hover:text-white"}`}><Calculator size={16} /> Simulator</button>
        </div>
      </div>

      {/* 🚀 Modular Tabs */}
      {activeTab === "holdings" && (
        <HoldingsTab portfolio={portfolio} onAddClick={() => setShowAddModal(true)} onAssetClick={setSelectedAssetForDetail} />
      )}

      {activeTab === "analytics" && (
        <AnalyticsTab analytics={analytics} />
      )}

      {activeTab === "calculator" && (
        <div className="max-w-4xl mx-auto py-10 animate-in slide-in-from-bottom-4">
          <WealthCalculator />
        </div>
      )}

      {/* Modals */}
      {showAddModal && <AddTransactionModal onClose={() => { setShowAddModal(false); setPrefillAsset(null); }} onSuccess={refreshData} prefillAsset={prefillAsset} />}
      {selectedAssetForDetail && <AssetDetailModal asset={selectedAssetForDetail} onClose={() => setSelectedAssetForDetail(null)} onAddMore={handleAddMore} onUpdate={refreshData} />}
    </div>
  );
};

export default Portfolio;