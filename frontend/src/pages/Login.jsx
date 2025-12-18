import React, { useState } from 'react';
import { data, useNavigate, Link } from 'react-router-dom';


function Login() {
    const [username, setUsername]=useState('');
    const [password, setPassword]=useState('');
    const navigate = useNavigate(); // this will allw us to change pages via code 

const handleLogin = (e) => {
        e.preventDefault();

        // sending the credential to Django Backend
        fetch('http://127.0.0.1:8000/api/auth/login/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password }),
            credentials: 'include' // <--- 1. ADD THIS (Critical!)
        })
        .then(response => {
            if (!response.ok) {
                // If password is wrong (status 400/401), throw error to go to .catch
                throw new Error("Login failed");
            }
            return response.json(); // <--- 2. ADD THIS (Convert to JSON)
        })
        .then(data => {
            console.log("Login Success", data);
            
            // Now data.username actually exists!
            localStorage.setItem('user', JSON.stringify(data.username));

            alert("Welcome back, " + data.username + "! 🐼");
            
            navigate('/');
            window.location.reload();
        })
        .catch(error => {
            console.error('Error:', error);
            alert("Login Failed! Check username/password");
        });
    };
return (
        <div style={styles.container}>
            <div style={styles.card}>
                <h1 style={{ marginBottom: "20px" }}>🔐 Login</h1>
                <form onSubmit={handleLogin} style={styles.form}>
                    <input 
                        type="text" 
                        placeholder="Username" 
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        style={styles.input}
                    />
                    <input 
                        type="password" 
                        placeholder="Password" 
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        style={styles.input}
                    />
                    <button type="submit" style={styles.button}>Enter the Matrix</button>
                </form>
                <p style={{ marginTop: "15px", color: "#888" }}>
                    New here? <Link to="/signup" style={{ color: "#a78bfa" }}>Create Account</Link>
                </p>
            </div>
        </div>
    );
}


const styles = {
    container: {
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        height: "80vh", // Center vertically
    },
    card: {
        backgroundColor: "#222",
        padding: "40px",
        borderRadius: "15px",
        boxShadow: "0 4px 15px rgba(0,0,0,0.5)",
        textAlign: "center",
        border: "1px solid #333",
        width: "300px"
    },
    form: { display: "flex", flexDirection: "column", gap: "15px" },
    input: {
        padding: "12px",
        borderRadius: "8px",
        border: "none",
        backgroundColor: "#333",
        color: "white",
        fontSize: "1rem",
        outline: "none"
    },
    button: {
        padding: "12px",
        borderRadius: "8px",
        border: "none",
        backgroundColor: "#a78bfa",
        color: "#1a1a1a",
        fontWeight: "bold",
        fontSize: "1rem",
        cursor: "pointer",
        transition: "transform 0.1s"
    }
};

export default Login;