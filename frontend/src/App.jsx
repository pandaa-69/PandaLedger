import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';


// Import Components
import Navbar from './components/Navbar';
import Footer from './components/Footer';

// Import Pages
import Home from './pages/Home';
import Login from './pages/Login';
import Signup from './pages/Signup';

function App() {
  // 1. The "Memory" (useState)
  // We create a variable 'expenses' to hold our data.
  // Initially, it is an empty list [].
  const [expenses, setExpenses] = useState([])

  // 2. The "Trigger" (useEffect)
  // This runs ONE time when the page loads.
  useEffect(() => {
    // The Waiter goes to the kitchen...
    fetch('http://127.0.0.1:8000/api/expenses/', {
        method: 'GET',
        credentials: 'include', // <--- THIS IS MANDATORY for Auth to work!
        headers: {
            'Content-Type': 'application/json',
        }      
    })
    .then(response => {
      if (response.status === 401){
        console.log("User is not logged in");
        return null;
      }
      return response.json();
    })
      .then(data => {
        if (data && data.results){
          console.log("Data received:", data); // Check your browser console!
          setExpenses(data.results); // Update the Memory
        }
      })
      .catch(error => console.error("Error fetching data:", error));
  }, [])

  return (
    <Router>
      <div style={{ minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        width:"100%",
        maxWidth:"1200px",
        margin:"0 auto",
        padding:"0 20px"
      }}>
        <Navbar />
        
        {/* The "Switching" Area */}
        <div style={{ flex: 1 , width:"100%" }}>
            <Routes>
                {/* Route 1: Home Page (Pass expenses as a "Prop") */}
                <Route path="/" element={<Home expenses={expenses} />} />
                
                {/* Route 2: Login Page */}
                <Route path="/login" element={<Login />} />
                <Route path='/signup' element={<Signup/>} />
            </Routes>
        </div>

        <Footer />
      </div>
    </Router>

  )
}

export default App