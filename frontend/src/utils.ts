import axios from "axios";

export async function getCurrentUsername(): Promise<string> {
  const token = localStorage.getItem("access_token");
  if (!token) return "";

  try {
    const response = await axios.get(
      "http://127.0.0.1:8000/customer/current-customer",
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      },
    );

    return response.data?.username ?? "";
  } catch {
    return "";
  }
}

export async function isLoggedIn(): Promise<boolean> {
  return (await getCurrentUsername()) !== "";
}
