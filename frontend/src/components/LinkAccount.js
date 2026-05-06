import React, { useCallback, useEffect, useState } from "react";
import { usePlaidLink } from "react-plaid-link";
import api from "../services/api";

export default function LinkAccount() {
  const [linkToken, setLinkToken] = useState(null);
  const [status, setStatus] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.createLinkToken()
      .then((d) => setLinkToken(d.link_token))
      .catch((e) => setError(e.message + " — set PLAID_CLIENT_ID and PLAID_SECRET in backend/.env"));
  }, []);

  const onSuccess = useCallback(async (publicToken) => {
    try {
      await api.exchangePublicToken(publicToken);
      setStatus("Account linked. You can fetch transactions from the dashboard.");
    } catch (e) {
      setError(e.message);
    }
  }, []);

  const { open, ready } = usePlaidLink({
    token: linkToken,
    onSuccess,
  });

  return (
    <div>
      <h1>Link a bank account</h1>
      {error && <div className="alert error">{error}</div>}
      {status && <div className="alert success">{status}</div>}
      <div className="card">
        <p>Connect your account using Plaid sandbox. Use credentials <code>user_good</code> / <code>pass_good</code>.</p>
        <button className="btn" onClick={() => open()} disabled={!ready || !linkToken}>
          {linkToken ? "Connect with Plaid" : "Loading link token..."}
        </button>
      </div>
    </div>
  );
}
