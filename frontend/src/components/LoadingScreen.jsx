import React from "react";
import { Loader2 } from "lucide-react";

const LoadingScreen = () => {
  return (
    <div className="fixed inset-0 z-[100] flex flex-col items-center justify-center bg-black text-white">
      {/* 1. Glowing Background Blob for ambiance */}
      <div className="absolute top-1/2 left-1/2 h-64 w-64 -translate-x-1/2 -translate-y-1/2 rounded-full bg-purple-600/20 blur-[100px]"></div>

      {/* 2. The Logo Animation */}
      <div className="relative z-10 flex flex-col items-center gap-4">
        <h1 className="animate-pulse text-5xl font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-green-400">
          🐼
        </h1>

        {/* 3. The Spinner */}
        <Loader2 className="h-8 w-8 animate-spin text-purple-500" />

        <p className="text-xs font-medium uppercase tracking-widest text-gray-500">
          Loading Ledger...
        </p>
      </div>
    </div>
  );
};

export default LoadingScreen;
