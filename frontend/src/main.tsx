import "./index.css";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route, NavLink } from "react-router";

import Shop from "./components/Shop";
import Login from "./components/Login";
import Checkout from "./components/Checkout";

import AppBar from "@mui/material/AppBar";
import Box from "@mui/material/Box";
import CssBaseline from "@mui/material/CssBaseline";
import { createTheme, ThemeProvider } from "@mui/material/styles";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";

import { red } from "@mui/material/colors";

const theme = createTheme({
  palette: {
    primary: {
      main: red[700],
    },
    secondary: {
      main: red[500],
    },
  },
});

import { useEffect, useState } from "react";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";
import { getCurrentUsername } from "./utils";

export default function NavBar() {
  const [username, setUsername] = useState("");

  useEffect(() => {
    const syncAuth = async () => {
      setUsername(await getCurrentUsername());
      console.log(username);
    };

    syncAuth();

    const onAuthChanged = () => {
      syncAuth();
    };

    window.addEventListener("auth-changed", onAuthChanged);
    return () => window.removeEventListener("auth-changed", onAuthChanged);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("username");
    localStorage.removeItem("role");
    setUsername("");
    window.dispatchEvent(new Event("auth-changed"));
  };

  return (
    <AppBar position="static" color="primary">
      <Toolbar>
        <Typography variant="h6" sx={{ flexGrow: 1 }}>
          Restaurant App
        </Typography>

        <Button component={NavLink} to="/" color="inherit">
          Shop
        </Button>

        {username ? (
          <>
            <Typography sx={{ mx: 2 }}>Hello, {username}</Typography>
            <Button onClick={handleLogout} color="inherit">
              Logout
            </Button>
          </>
        ) : (
          <Button component={NavLink} to="/login" color="inherit">
            Login / Register
          </Button>
        )}
      </Toolbar>
    </AppBar>
  );
}

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <BrowserRouter>
        <NavBar />
        <Box sx={{ p: 2 }}>
          <Routes>
            <Route path="/" element={<Shop />} />
            <Route path="/login" element={<Login />} />
            <Route path="/checkout" element={<Checkout />} />
          </Routes>
        </Box>
      </BrowserRouter>
    </ThemeProvider>
  );
}

const root = document.getElementById("root");

ReactDOM.createRoot(root!).render(<App />);
