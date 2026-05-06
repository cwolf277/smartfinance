import React, { useEffect, useState } from "react";
import api from "../services/api";

export default function Transactions() {
  const [txns, setTxns] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const refresh = () => {
    setLoading(true);
    api.getStoredTransactions(500)
      .then((d) => setTxns(d.transactions || []))
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => { refresh(); }, []);

  const runEtl = async () => {
    setLoading(true);
    setError(null);
    try {
      await api.runEtl("data/sample_transactions.csv");
      refresh();
    } catch (e) {
      setError(e.message);
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>Transactions</h1>
      {error && <div className="alert error">{error}</div>}
      <div className="card">
        <button className="btn" onClick={runEtl} disabled={loading}>
          {loading ? "Running..." : "Run ETL on sample data"}
        </button>
        <button className="btn secondary" style={{ marginLeft: 8 }} onClick={refresh} disabled={loading}>
          Refresh
        </button>
      </div>
      <div className="card">
        <table>
          <thead>
            <tr>
              <th>Date</th>
              <th>Name</th>
              <th>Category</th>
              <th style={{ textAlign: "right" }}>Amount</th>
            </tr>
          </thead>
          <tbody>
            {txns.map((t) => (
              <tr key={t.transaction_id}>
                <td>{t.date}</td>
                <td>{t.name}</td>
                <td>{t.category}</td>
                <td style={{ textAlign: "right" }}>${parseFloat(t.amount).toFixed(2)}</td>
              </tr>
            ))}
            {txns.length === 0 && (
              <tr><td colSpan="4">No transactions yet.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
