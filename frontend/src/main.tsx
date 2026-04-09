import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router";
import App from "./App";
import NavBar from "./components/NavBar";
import Shop from "./components/Shop";
import Login from "./components/Login";

const root = document.getElementById("root");

ReactDOM.createRoot(root!).render(
  <div>
    <NavBar></NavBar>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Shop />}></Route>
        <Route path="/login" element={<Login />}></Route>
      </Routes>
    </BrowserRouter>
    ,
  </div>,
);
