import "bootstrap/dist/css/bootstrap.min.css";
import React from "react";
import { Route, Routes, Link } from "react-router-dom";
import AppContent from "./AppContent";
import GAApp from "./GAApp";
import ManagementPage from "./ManagementPage";

function App() {
  return (
    <div className="container mt-5">
      <h1 className="mb-4">Production Schedule Optimizer</h1>
      <nav className="mb-4">
        <ul className="nav nav-tabs">
          <li className="nav-item">
            <Link className="nav-link" to="/">
              Greedy Algorithm
            </Link>
          </li>
          <li className="nav-item">
            <Link className="nav-link" to="/ga">
              Genetic Algorithm
            </Link>
          </li>
          <li className="nav-item">
            <Link className="nav-link" to="/management">
              Management
            </Link>
          </li>
        </ul>
      </nav>

      <Routes>
          <Route path="/" element={<AppContent />} />
          <Route path="/ga" element={<GAApp />} />
          <Route path="/management" element={<ManagementPage />} />
        </Routes>
    </div>
  );
}

export default App;
