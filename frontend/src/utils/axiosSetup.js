import axios from "axios";

// Set base URL for backend API
// In production, this will use REACT_APP_API_URL from environment variables
// In development, it falls back to localhost
axios.defaults.baseURL = process.env.REACT_APP_API_URL || "http://localhost:8000";

// Clear any existing headers
delete axios.defaults.headers.common['Authorization'];

// Request interceptor: always send Authorization and X-Company-ID (except for login/register)
axios.interceptors.request.use((config) => {
  // Don't add auth headers for login or register requests
  if (config.url?.includes('/api/auth/login') || config.url?.includes('/api/auth/register')) {
    return config;
  }
  
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;

  const cid = localStorage.getItem("currentCompanyId");
  if (cid) config.headers["X-Company-ID"] = cid;

  return config;
});

// Optional: 403 handling for company mismatch
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 403 && error.response?.data?.detail?.includes("company")) {
      // Clear invalid company and force reselect
      localStorage.removeItem("currentCompanyId");
      window.location.reload();
    }
    return Promise.reject(error);
  }
);
