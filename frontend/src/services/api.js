import axios from "axios";

const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Add request interceptor for authentication if needed
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem("authToken");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export const creditRiskService = {
  // Analyze credit risk
  analyzeCreditRisk: async (data) => {
    try {
      const response = await api.post("/api/credit-risk/analyze", data);
      return response.data;
    } catch (error) {
      throw new Error(
        error.response?.data?.message || "Failed to analyze credit risk"
      );
    }
  },

  // Get statistics
  getStatistics: async () => {
    try {
      const response = await api.get("/api/credit-risk/statistics");
      return response.data;
    } catch (error) {
      throw new Error(
        error.response?.data?.message || "Failed to fetch statistics"
      );
    }
  },

  // Get analysis history
  getAnalysisHistory: async () => {
    try {
      const response = await api.get("/api/credit-risk/history");
      return response.data;
    } catch (error) {
      throw new Error(
        error.response?.data?.message || "Failed to fetch analysis history"
      );
    }
  },

  // ML service integration
  getLLMAnalysis: async (prompt) => {
    try {
      const response = await api.post("/api/ml/analyze", { prompt });
      return response.data;
    } catch (error) {
      throw new Error(
        error.response?.data?.message || "Failed to get LLM analysis"
      );
    }
  },

  // Dashboard statistics
  getDashboardStats: async () => {
    try {
      const response = await api.get("/api/v1/frontend/dashboard-stats");
      return response.data;
    } catch (error) {
      throw new Error(
        error.response?.data?.detail || "Failed to fetch dashboard statistics"
      );
    }
  },

  // Update dashboard statistics
  updateDashboardStats: async (statsData) => {
    try {
      const response = await api.put(
        "/api/v1/frontend/dashboard-stats",
        statsData
      );
      return response.data;
    } catch (error) {
      throw new Error(
        error.response?.data?.detail || "Failed to update dashboard statistics"
      );
    }
  },

  // Refresh dashboard statistics from actual data
  refreshDashboardStats: async () => {
    try {
      const response = await api.post(
        "/api/v1/frontend/dashboard-stats/refresh"
      );
      return response.data;
    } catch (error) {
      throw new Error(
        error.response?.data?.detail || "Failed to refresh dashboard statistics"
      );
    }
  },

  // Initialize dashboard with sample data
  initializeDashboardStats: async () => {
    try {
      const response = await api.post(
        "/api/v1/frontend/dashboard-stats/initialize"
      );
      return response.data;
    } catch (error) {
      throw new Error(
        error.response?.data?.detail ||
          "Failed to initialize dashboard statistics"
      );
    }
  },
};

export default api;
