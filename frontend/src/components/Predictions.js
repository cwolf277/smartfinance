import React, { useState } from "react";
import api from "../services/api";

const DEFAULTS = {
  monthly_spend: 2500,
  txn_count: 35,
  avg_txn: 71.4,
  max_txn: 320,
  weekend_ratio: 0.3,
  category_diversity: 6,
};

export default function Predictions() {
  const [features, setFeatures] = useState(DEFAULTS);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [trainOutput, setTrainOutput] = useState(null);

  const update = (k, v) => setFeatures((f) => ({ ...f, [k]: parseFloat(v) || 0 }));

  const train = async () => {
    setError(null);
    try {
      const res = await api.trainModel();
      setTrainOutput(res);
    } catch (e) {
      setError(e.message);
    }
  };

  const predict = async () => {
    setError(null);
    try {
      const res = await api.predict(features);
      setResult(res);
    } catch (e) {
      setError(e.message);
    }
  };

  return (
    <div>
      <h1>Overspending prediction</h1>
      {error && <div className="alert error">{error}</div>}

      <div className="card">
        <h3>1. Train model</h3>
        <p>Trains logistic regression on stored transactions. Run ETL first if no data.</p>
        <button className="btn" onClick={train}>Train model</button>
        {trainOutput && (
          <pre style={{ marginTop: 12, background: "#f1f5f9", padding: 12, borderRadius: 6 }}>
            {JSON.stringify(trainOutput, null, 2)}
          </pre>
        )}
      </div>

      <div className="card">
        <h3>2. Predict overspending risk</h3>
        <div className="grid">
          {Object.keys(DEFAULTS).map((k) => (
            <div key={k}>
              <label style={{ display: "block", fontSize: 13, color: "#64748b" }}>{k}</label>
              <input
                type="number"
                step="0.01"
                value={features[k]}
                onChange={(e) => update(k, e.target.value)}
                style={{ width: "100%", padding: 8, border: "1px solid #cbd5e1", borderRadius: 6 }}
              />
            </div>
          ))}
        </div>
        <button className="btn" style={{ marginTop: 16 }} onClick={predict}>Predict</button>

        {result && result.ok && (
          <div style={{ marginTop: 16 }}>
            <p>Probability of overspending: <strong>{(result.overspend_probability * 100).toFixed(1)}%</strong></p>
            <p>Risk level: <strong className={`risk-${result.risk_level}`}>{result.risk_level.toUpperCase()}</strong></p>
          </div>
        )}
      </div>
    </div>
  );
}
