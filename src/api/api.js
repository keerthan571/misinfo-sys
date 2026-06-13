import apiClient from "./apiClient";

// Detect API
export const detectNews = (text) => {
  return apiClient.post("/detect/", {
    text: text,
  });
};

// Graph API
export const getGraph = (text) => {
  return apiClient.post("/graph/", {
    text: text,
  });
};

// Influence API
export const getInfluence = (text) => {
  return apiClient.post("/influence/", {
    text: text,
  });
};

// Prediction API
export const predictSpread = (text) => {
  return apiClient.post("/predict/", {
    text: text,
  });
};