import axios from "axios";

function clearAuth() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("role");
  localStorage.removeItem("username");
}

export async function getCurrentUsername(): Promise<string> {
  const storedUsername = localStorage.getItem("username");
  if (storedUsername) return storedUsername;

  const token = localStorage.getItem("access_token");
  const role = localStorage.getItem("role");

  if (!token || !role) return "";

  const endpoint =
    role === "customer"
      ? "http://127.0.0.1:8000/customer/current-customer"
      : "http://127.0.0.1:8000/staffs/current-staff";

  try {
    const response = await axios.get(endpoint, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    const username = response.data?.username ?? "";
    if (username) localStorage.setItem("username", username);
    return username;
  } catch {
    clearAuth();
    return "";
  }
}

export async function getCurrentRole(): Promise<string> {
  const storedRole = localStorage.getItem("role");
  if (storedRole) return storedRole;

  const token = localStorage.getItem("access_token");
  if (!token) return "";

  try {
    const response = await axios.get(
      "http://127.0.0.1:8000/staffs/current-staff",
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      },
    );

    const role = response.data?.role ?? "";
    if (role) localStorage.setItem("role", role);
    return role;
  } catch {
    try {
      await axios.get("http://127.0.0.1:8000/customer/current-customer", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      localStorage.setItem("role", "customer");
      return "customer";
    } catch {
      clearAuth();
      return "";
    }
  }
}

export async function isLoggedIn(): Promise<boolean> {
  return (await getCurrentUsername()) !== "";
}
