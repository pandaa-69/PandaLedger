// frontend/src/config.js

// 1. Use the Real URL. This fixes the 404 errors immediately.
const API_URL = import.meta.env.DEV 
    ? "http://127.0.0.1:8000" 
    : "https://pandaledger-api.onrender.com";

export const getCSRFToken = () => {
    const name = 'csrftoken';
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
};

export const apiRequest = async (endpoint, options = {}) => {
    // Ensure we don't double-slash
    const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
    
    return fetch(`${API_URL}${cleanEndpoint}`, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),
            ...options.headers,
        },
        credentials: 'include',
    });
};

export default API_URL;