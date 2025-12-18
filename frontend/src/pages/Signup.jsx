import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';

function Signup() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const navigate = useNavigate();

    const handleSignup = (e) => {
        e.preventDefault();

        // connects to the backend URL we tested yesterday
        fetch('http://127.0.0.1:8000/api/auth/signup/', { 
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error("Signup failed");
            }
            return response.json();
        })
        .then(data => {
            console.log("Signup Success", data);
            alert("Account created! 🐼 Please Log In.");
            navigate('/login'); // Redirect to login after success
        })
        .catch(error => {
            console.error('Error:', error);
            alert("Signup Failed! Username might be taken.");
        });
    };

    return (
        <div style={styles.container}>
            <div style={styles.card}>
                <h1 style={{ marginBottom: "20px" }}>📝 Join PandaLedger</h1>
                <form onSubmit={handleSignup} style={styles.form}>
                    <input 
                        type="text" 
                        placeholder="Choose Username" 
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        style={styles.input}
                    />
                    <input 
                        type="password" 
                        placeholder="Choose Password" 
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        style={styles.input}
                    />
                    <button type="submit" style={styles.button}>Create Account</button>
                </form>
                
                <p style={{ marginTop: "15px", color: "#888" }}>
                    Already have an account? <Link to="/login" style={{ color: "#a78bfa" }}>Log in</Link>
                </p>
            </div>
        </div>
    );
}

const styles = {
    container: { display: "flex", justifyContent: "center", alignItems: "center", height: "80vh" },
    card: { backgroundColor: "#222", padding: "40px", borderRadius: "15px", boxShadow: "0 4px 15px rgba(0,0,0,0.5)", textAlign: "center", border: "1px solid #333", width: "300px" },
    form: { display: "flex", flexDirection: "column", gap: "15px" },
    input: { padding: "12px", borderRadius: "8px", border: "none", backgroundColor: "#333", color: "white", fontSize: "1rem", outline: "none" },
    button: { padding: "12px", borderRadius: "8px", border: "none", backgroundColor: "#a78bfa", color: "#1a1a1a", fontWeight: "bold", fontSize: "1rem", cursor: "pointer" }
};

export default Signup;