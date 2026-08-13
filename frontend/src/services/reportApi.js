import axios from "axios";

const API = axios.create({
  baseURL: "https://misinfo-system.onrender.com/api/reports",
});

export const getReports = async () => {
  const response = await API.get("/");
  return response.data;
};

export const getReport = async (reportId) => {
  const response = await API.get(`/${reportId}`);
  return response.data;
};

export const deleteReport = async (reportId) => {
  const response = await API.delete(`/${reportId}`);
  return response.data;
};

export const downloadPDF = async (reportId) => {
  const response = await API.get(`/${reportId}/pdf`);
  return response.data;
};

export const downloadCSV = async (reportId) => {
  const response = await API.get(`/${reportId}/csv`);
  return response.data;
};