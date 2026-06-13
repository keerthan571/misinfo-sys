import axios from 'axios';

// Create an Axios instance
const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api', // FastAPI default URL
  headers: {
    'Content-Type': 'application/json'
  }
});

export default apiClient;
