import axios from "axios";

// Request interceptor: always send Authorization and X-Company-ID
axios.interceptors.request.use((config) => {
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
