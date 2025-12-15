import React from "react";

function Footer(){
    return (
        <footer style={styles.footer}>
            <a href=" # mywebsitelink">
                <img src="/LOGO.jpg" alt="PandaLedger logo" style={{ height:"30px"}} />
            </a>
            <h5>© 2025 PandaLedger | Built by Durgesh Kumar(Panda) with 💖 and lots of ☕</h5>

        </footer>
    )
}

const styles = {
    footer: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '1rem 2rem',
    backgroundColor: '#1a1a1a', // Dark mode background
    color: '#05D647',
    boxShadow: '0 2px 10px rgba(0,0,0,0.3)',
    }
}

export default Footer;
