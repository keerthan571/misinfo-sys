import apiClient from "./apiClient";

export const getCurrentUser = async () => {
  const response = await apiClient.get("/api/auth/me");
  return response.data;
};