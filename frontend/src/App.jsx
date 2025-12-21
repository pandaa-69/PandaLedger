import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";

// Components
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import LoadingScreen from "./components/LoadingScreen";
import MobileNav from "./components/MobileNav";

// Pages
import Home from "./pages/Home";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Ledger from "./pages/Ledger";
import Portfolio from "./pages/Portfolio";
import NotFound from "./pages/NotFound";
import Profile from './pages/Profile';

function App() {
  const [expenses, setExpenses] = useState(null);
  const [loading, setLoading] = useState(true);

  // Keep your existing fetch logic!
  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/expenses/", {
      method: "GET",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
    })
      .then((response) => {
        if (response.status === 401 || response.status === 403) {
          setExpenses(null);
          return null;
        }
        return response.json();
      })
      .then((data) => {
        if (data) setExpenses(data.results || data);
      })
      .catch((error) => console.error("Error fetching data:", error))
      .finally(() => setTimeout(() => setLoading(false), 800));
  }, []);

  if (loading) return <LoadingScreen />;

  return (
    <Router>
      <div className="flex min-h-screen flex-col bg-black text-white antialiased selection:bg-cyan-500/30">
        <Navbar />

        <main className="flex-1 w-full mx-auto max-w-[95%] px-4 pt-28 pb-24">
          <Routes>
            <Route path="/" element={<Home expenses={expenses} />} />
            
            <Route
              path="/ledger"
              element={expenses ? <Ledger expenses={expenses} /> : <Navigate to="/login" />}
            />

            <Route
              path="/portfolio"
              element={expenses ? <Portfolio /> : <Navigate to="/login" />}
            />

            {/* 👇 PROTECTED PROFILE ROUTE */}
            <Route 
              path="/profile" 
              element={expenses ? <Profile /> : <Navigate to="/login" />} 
            />

            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </main>

        {expenses && <MobileNav />}
        <Footer />
      </div>
    </Router>
  );
}

export default App;