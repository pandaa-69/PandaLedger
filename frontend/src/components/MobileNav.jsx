import React from "react";
import { Link, useLocation } from "react-router-dom";
import { LayoutDashboard, Wallet, PieChart } from "lucide-react";

const MobileNav = () => {
  const location = useLocation();

  // Only show if user is logged in (we check this by seeing if the routes match)
  // Or we can rely on the parent to hide/show it.
  // For visual styling:
  const isActive = (path) =>
    location.pathname === path
      ? "text-purple-400"
      : "text-gray-500 hover:text-gray-300";

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 border-t border-white/10 bg-black/80 backdrop-blur-xl md:hidden pb-safe">
      <div className="flex items-center justify-around p-3">
        <Link
          to="/"
          className={`flex flex-col items-center gap-1 ${isActive("/")}`}
        >
          <LayoutDashboard size={24} />
          <span className="text-[10px] font-medium">Market</span>
        </Link>

        <Link
          to="/ledger"
          className={`flex flex-col items-center gap-1 ${isActive("/ledger")}`}
        >
          <Wallet size={24} />
          <span className="text-[10px] font-medium">Ledger</span>
        </Link>

        <Link
          to="/portfolio"
          className={`flex flex-col items-center gap-1 ${isActive(
            "/portfolio"
          )}`}
        >
          <PieChart size={24} />
          <span className="text-[10px] font-medium">Wealth</span>
        </Link>
      </div>
    </div>
  );
};

export default MobileNav;
