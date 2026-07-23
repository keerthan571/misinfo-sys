<<<<<<< HEAD
import axios from "axios";

const apiClient = axios.create({
  baseURL: "http://127.0.0.1:8000",
  headers: {
    "Content-Type": "application/json",
  },
});

export default apiClient;
=======
import axios from 'axios';

// Create an Axios instance
const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api', // FastAPI default URL
  headers: {
    'Content-Type': 'application/json'
  }
});

export default apiClient;
>>>>>>> 8b44c954ba4e4703454da20488ed0a29cac18568
