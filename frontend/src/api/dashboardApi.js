import apiClient from "./apiClient";

export const getDashboardStats = async () => {
  const response = await apiClient.get("/api/dashboard/stats");
  return response.data;
};

export const getRecentActivity = async () => {
  const response = await apiClient.get("/api/dashboard/recent");
  return response.data;
};