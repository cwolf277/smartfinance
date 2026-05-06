import axios from "axios";

const API_BASE = process.env.REACT_APP_API_URL || "http://localhost:5000";

const client = axios.create({
  baseURL: API_BASE,
  timeout: 15000,
});

export const api = {
  health: () => client.get("/health").then((r) => r.data),
  createLinkToken: () => client.post("/create_link_token").then((r) => r.data),
  exchangePublicToken: (publicToken) =>
    client.post("/exchange_public_token", { public_token: publicToken }).then((r) => r.data),
  getPlaidTransactions: () => client.get("/get_transactions").then((r) => r.data),
  getStoredTransactions: (limit = 100) =>
    client.get(`/transactions?limit=${limit}`).then((r) => r.data),
  runEtl: (source) => client.post("/etl/run", { source }).then((r) => r.data),
  trainModel: () => client.post("/ml/train").then((r) => r.data),
  predict: (features) => client.post("/ml/predict", features).then((r) => r.data),
};

export default api;
