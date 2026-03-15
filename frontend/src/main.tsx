import { createRoot } from "react-dom/client";
import { BrowserRouter, Routes, Route, NavLink } from "react-router";
import "./styles.scss";

import App from "./App.tsx";
import Login from "./Login.tsx";

const root = document.getElementById("root");

createRoot(root!).render(
  <BrowserRouter>
    <div>
      <nav className="navbar  bg-black text-white">
        <div className="container-fluid">
          <div className="text-white navbar-brand">SWE30003 - Project</div>
          <div className="d-flex gap-3">
            <NavLink
              to="/"
              className="nav-item text-white text-decoration-none"
            >
              Home
            </NavLink>
            <NavLink
              to="/login"
              className="nav-item text-white text-decoration-none"
            >
              Login
            </NavLink>
            <NavLink
              to="/checkout"
              className="nav-item text-white text-decoration-none"
            >
              Checkout
            </NavLink>
          </div>
        </div>
      </nav>

      <div>
        <Routes>
          <Route path="/" element={<App />} />
          <Route path="/login" element={<Login />} />
        </Routes>
      </div>
    </div>
  </BrowserRouter>,
);
