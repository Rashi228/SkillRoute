export const API_URL = import.meta.env.VITE_API_URL || (import.meta.env.DEV ? "http://127.0.0.1:8000" : "");

if (import.meta.env.PROD && !import.meta.env.VITE_API_URL) {
    console.warn("VITE_API_URL is not set in production. API calls may fail if relative paths are not used.");
}
