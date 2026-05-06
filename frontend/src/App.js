import React from "react";
import { Routes, Route, NavLink } from "react-router-dom";
import Dashboard from "./components/Dashboard";
import Transactions from "./components/Transactions";
import LinkAccount from "./components/LinkAccount";
import Predictions from "./components/Predictions";

export default function App() {
  return (
    <div className="app">
      <nav className="nav">
        <div className="brand">SmartFinance</div>
        <NavLink to="/" end>Dashboard</NavLink>
        <NavLink to="/transactions">Transactions</NavLink>
        <NavLink to="/link">Link Account</NavLink>
        <NavLink to="/predictions">Predictions</NavLink>
      </nav>
      <div className="container">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/transactions" element={<Transactions />} />
          <Route path="/link" element={<LinkAccount />} />
          <Route path="/predictions" element={<Predictions />} />
        </Routes>
      </div>
    </div>
  );
}
