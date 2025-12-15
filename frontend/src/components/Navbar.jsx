import React from 'react';

function Navbar() {
  return (
    <nav style={styles.nav}>
      <div style={styles.logo}>🐼 PandaLedger</div>
      <div style={styles.links}>
        <a href="#" style={styles.link}>Dashboard</a>
        <a href="#" style={styles.link}>Add Expense</a>
        <a href="#" style={styles.link}>Login</a>
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
    backgroundColor: '#1a1a1a', // Dark mode background
    color: 'white',
    boxShadow: '0 2px 10px rgba(0,0,0,0.3)',
  },
  logo: {
    fontSize: '1.5rem',
    fontWeight: 'bold',
    color: '#a78bfa', // A nice purple panda color
  },
  links: {
    display: 'flex',
    gap: '20px',
  },
  link: {
    textDecoration: 'none',
    color: '#ccc',
    fontSize: '1rem',
    cursor: 'pointer',
  }
};

export default Navbar;