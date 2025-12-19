import React from "react";
import { Link } from "react-router-dom";
import { Home } from "lucide-react";

const NotFound = () => {
  return (
    <div className="flex h-[80vh] flex-col items-center justify-center text-center">
      <h1 className="text-9xl font-black text-gray-800">404</h1>
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 rounded-full bg-cyan-500/20 blur-[100px] h-64 w-64"></div>

      <p className="z-10 mt-4 text-2xl font-bold text-white">
        Lost in the Void?
      </p>
      <p className="z-10 mt-2 max-w-md text-gray-400">
        The page you are looking for does not exist. It might have been moved or
        deleted.
      </p>

      <Link
        to="/"
        className="z-10 mt-8 flex items-center gap-2 rounded-full bg-white px-6 py-3 text-sm font-bold text-black transition-transform hover:scale-105"
      >
        <Home size={18} /> Return Home
      </Link>
    </div>
  );
};

export default NotFound;
