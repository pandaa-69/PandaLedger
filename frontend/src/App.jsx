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
import Profile from "./pages/Profile";
import ForgotPassword from "./pages/ForgotPassword";
import ResetPasswordConfirm from "./pages/ResetPasswordConfirm";

import API_URL from "./config";

function App() {
  const [expenses, setExpenses] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // 1️⃣ Fetch CSRF cookie ONCE
    fetch(`${API_URL}/api/auth/csrf/`, {
      credentials: "include",
    }).catch((err) => console.log("CSRF error:", err));

    // 2️⃣ Check auth state using a protected endpoint
    fetch(`${API_URL}/api/expenses/`, {
      method: "GET",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
    })
      .then((res) => {
        if (res.status === 401 || res.status === 403) {
          setExpenses(null);
          return null;
        }
        return res.json();
      })
      .then((data) => {
        if (data) setExpenses(data.results || data);
      })
      .catch(() => setExpenses(null))
      .finally(() => setTimeout(() => setLoading(false), 500));
  }, []);

  if (loading) return <LoadingScreen />;

  return (
    <Router>
      <div className="flex min-h-screen flex-col bg-black text-white antialiased">
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

            <Route
              path="/profile"
              element={expenses ? <Profile /> : <Navigate to="/login" />}
            />

            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />
            <Route path="/reset-password/:uid/:token" element={<ResetPasswordConfirm />} />
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
