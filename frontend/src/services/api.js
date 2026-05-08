import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000",
  headers: {
    "Content-Type": "application/json"
  },
  timeout: 180000
});

export const analyzeText = async (payload) => {
  const response = await api.post("/analyze", payload);
  return response.data;
};

export default api;
