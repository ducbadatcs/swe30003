import { createRoot } from "react-dom/client";
import { useState } from "react";
import {
  BrowserRouter,
  Routes,
  Route,
  NavLink,
  useNavigate,
} from "react-router";
import "./styles.scss";

import App from "./App.tsx";
import Login from "./Login.tsx";
import Register from "./Register.tsx";
import Checkout from "./Checkout.tsx";

export function Layout() {
  const [isLoggedIn, setIsLoggedIn] = useState(
    () => !!localStorage.getItem("token"),
  );
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("token");
    setIsLoggedIn(false);
    navigate("/");
  };

  return (
    <div>
      <nav className="navbar bg-black text-white">
        <div className="container-fluid">
          <div className="text-white navbar-brand">SWE30003 - Project</div>
          <div className="d-flex gap-3">
            <NavLink
              to="/"
              className="nav-item text-white text-decoration-none"
            >
              Home
            </NavLink>

            {isLoggedIn ? (
              <button
                onClick={handleLogout}
                className="nav-item text-white text-decoration-none bg-transparent border-0"
              >
                Logout
              </button>
            ) : (
              <NavLink
                to="/login"
                className="nav-item text-white text-decoration-none"
              >
                Login
              </NavLink>
            )}

            <NavLink
              to="/checkout"
              className="nav-item text-white text-decoration-none"
            >
              Checkout
            </NavLink>
          </div>
        </div>
      </nav>

      <Routes>
        <Route path="/" element={<App />} />
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login />} />
        <Route path="/checkout" element={<Checkout />} />
      </Routes>
    </div>
  );
}

const root = document.getElementById("root");

createRoot(root!).render(
  <BrowserRouter>
    <Layout />
  </BrowserRouter>,
);
