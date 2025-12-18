import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';

function Navbar() {
  const [user, setUser] = useState(null);
  const navigate = useNavigate();

  // 1. Check if user is logged in when the Navbar loads
  useEffect(() => {
    const loggedInUser = localStorage.getItem('user');
    if (loggedInUser) {
      // The name is stored with quotes like "panda", so we clean it
      setUser(loggedInUser.replace(/"/g, '')); 
    }
  }, []);

  // 2. The Logout Function
  const handleLogout = () => {
    localStorage.removeItem('user'); // Throw away the ID card
    setUser(null); // Update State
    alert("Logged out successfully!");
    navigate('/login'); // Go back to login page
    window.location.reload(); // Force refresh to clear any stale data
  };

  return (
    <nav style={styles.nav}>
      <div style={styles.logo}>🐼 PandaLedger</div>
      
      <div style={styles.links}>
        <Link to="/" style={styles.link}>Dashboard</Link>
        
        {/* 3. The Magic Switch */}
        {user ? (
          <div style={{ display: 'flex', gap: '20px', alignItems: 'center' }}>
            <span style={{ color: '#4ade80' }}>Hi, {user} 👋</span>
            <button onClick={handleLogout} style={styles.logoutBtn}>Logout</button>
          </div>
        ) : (
          <Link to="/login" style={styles.link}>Login</Link>
        )}
      </div>
    </nav>
  );
}

const styles = {
  nav: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '1rem 2rem',
    backgroundColor: '#1a1a1a', 
    color: 'white',
    boxShadow: '0 2px 10px rgba(0,0,0,0.3)',
  },
  logo: { fontSize: '1.5rem', fontWeight: 'bold', color: '#a78bfa' },
  links: { display: 'flex', gap: '20px', alignItems: 'center' },
  link: { textDecoration: 'none', color: '#ccc', fontSize: '1rem', cursor: 'pointer' },
  logoutBtn: {
    backgroundColor: '#ef4444',
    color: 'white',
    border: 'none',
    padding: '5px 15px',
    borderRadius: '5px',
    cursor: 'pointer',
    fontWeight: 'bold'
  }
};

export default Navbar;