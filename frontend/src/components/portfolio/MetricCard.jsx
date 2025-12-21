import React from 'react';

const MetricCard = ({ title, value, subtitle, icon }) => (
  <div className="bg-gray-900 border border-white/5 p-6 rounded-3xl hover:border-white/10 transition-colors">
    <div className="flex items-center gap-3 text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-4">
      {icon} {title}
    </div>
    <div className="text-3xl font-black text-white">{value}</div>
    <p className="text-[10px] text-gray-500 mt-1 italic">{subtitle}</p>
  </div>
);

export default MetricCard;