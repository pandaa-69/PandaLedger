// ✅ In production, use relative URLs so Vercel rewrite works
// ✅ In local dev, fall back to Django localhost

const API_URL =
  import.meta.env.DEV
    ? "http://127.0.0.1:8000"
    : ""; // 👈 IMPORTANT (relative paths in prod)

// 1. Helper to grab the 'csrftoken' cookie Django sends
export const getCSRFToken = () => {
  const name = "csrftoken";
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(";").shift();
  return null;
};

// 2. Fetch wrapper
export const apiRequest = async (endpoint, options = {}) => {
  const url = endpoint.startsWith("http")
    ? endpoint
    : `${API_URL}${endpoint}`;

  return fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCSRFToken(),
      ...options.headers,
    },
    credentials: "include", // ✅ REQUIRED
  });
};

export default API_URL;
