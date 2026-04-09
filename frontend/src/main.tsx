import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router";

import Shop from "./components/Shop";
import Login from "./components/Login";
import Checkout from "./components/Checkout";
import { red } from "@mui/material/colors";

import { NavLink } from "react-router";

import AppBar from "@mui/material/AppBar";
import Box from "@mui/material/Box";
import Toolbar from "@mui/material/Toolbar";

import { Button } from "@mui/material";

export default function NavBar() {
  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static" sx={{ backgroundColor: red[700] }}>
        <Toolbar>
          <Button component={NavLink} to="/" color="inherit">
            Shop
          </Button>
          <Button component={NavLink} to="/login" color="inherit">
            Login
          </Button>
          <Button component={NavLink} to="/checkout" color="inherit">
            Checkout
          </Button>
        </Toolbar>
      </AppBar>
    </Box>
  );
}

function App() {
  return (
    <BrowserRouter>
      <NavBar />
      <Routes>
        <Route path="/" element={<Shop />} />
        <Route path="/login" element={<Login />} />
        <Route path="/checkout" element={<Checkout />}></Route>
      </Routes>
    </BrowserRouter>
  );
}

const root = document.getElementById("root");

ReactDOM.createRoot(root!).render(<App />);
