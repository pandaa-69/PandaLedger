const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

// 1. Helper to grab the 'csrftoken' cookie Django sends
export const getCSRFToken = () => {
    const name = 'csrftoken';
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
};

// 2. A wrapper for 'fetch' so you don't have to add headers manually everywhere
export const apiRequest = async (endpoint, options = {}) => {
    const url = endpoint.startsWith('http') ? endpoint : `${API_URL}${endpoint}`;
    
    return fetch(url, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(), // Automatically attaches the security token
            ...options.headers,
        },
        credentials: 'include', // Automatically sends cookies to Render
    });
};

export default API_URL;