// Centralized Frontend Configuration
// Reads VITE_API_BASE_URL from environment variables, or defaults to local server
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:10000";
