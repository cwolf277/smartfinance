import React, { useEffect, useState } from "react";
import { Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import api from "../services/api";

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

export default function Dashboard() {
  const [txns, setTxns] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.getStoredTransactions(500)
      .then((d) => setTxns(d.transactions || []))
      .catch((e) => setError(e.message));
  }, []);

  const total = txns.reduce((acc, t) => acc + (parseFloat(t.amount) || 0), 0);
  const avgTxn = txns.length ? total / txns.length : 0;
  const categoryTotals = txns.reduce((acc, t) => {
    const k = t.category || "Uncategorized";
    acc[k] = (acc[k] || 0) + (parseFloat(t.amount) || 0);
    return acc;
  }, {});

  const data = {
    labels: Object.keys(categoryTotals),
    datasets: [
      {
        label: "Spend by category ($)",
        data: Object.values(categoryTotals),
        backgroundColor: "#2563eb",
      },
    ],
  };

  return (
    <div>
      <h1>Dashboard</h1>
      {error && <div className="alert error">{error}</div>}
      <div className="grid">
        <div className="card stat">
          <div className="label">Transactions</div>
          <div className="value">{txns.length}</div>
        </div>
        <div className="card stat">
          <div className="label">Total spend</div>
          <div className="value">${total.toFixed(2)}</div>
        </div>
        <div className="card stat">
          <div className="label">Avg transaction</div>
          <div className="value">${avgTxn.toFixed(2)}</div>
        </div>
        <div className="card stat">
          <div className="label">Categories</div>
          <div className="value">{Object.keys(categoryTotals).length}</div>
        </div>
      </div>

      {txns.length > 0 && (
        <div className="card">
          <h3>Spend by category</h3>
          <Bar data={data} />
        </div>
      )}

      {txns.length === 0 && (
        <div className="card">
          <p>No transactions yet. Run the ETL pipeline or link an account.</p>
        </div>
      )}
    </div>
  );
}
