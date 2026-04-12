import type {
  Branch,
  MenuItemType,
  BranchInventory,
  Staff,
  StaffRole,
} from "./schemas";
import axios from "axios";

export async function fetchBranches(): Promise<Branch[]> {
  const response = await axios.get<Branch[]>(
    "http://127.0.0.1:8000/branches/list-branches",
  );
  return response.data;
}

export async function fetchStaffs(): Promise<Staff[]> {
  const response = await axios.get<Staff[]>(
    "http://127.0.0.1:8000/staffs/list-staffs",
  );
  return response.data;
}

export async function fetchMenuItems(): Promise<MenuItemType[]> {
  const response = await axios.get<MenuItemType[]>(
    "http://127.0.0.1:8000/menu/list-menu-items",
  );
  return response.data;
}

export async function fetchInventory(
  branchId: number,
): Promise<BranchInventory[]> {
  const response = await axios.get<BranchInventory[]>(
    "http://127.0.0.1:8000/menu/list-item-in-inventory",
    {
      params: {
        branch_id: branchId,
      },
    },
  );
  return response.data;
}

export async function fetchCurrentStaff(): Promise<{ branch_id: number }> {
  const token = localStorage.getItem("access_token");
  if (!token) {
    throw new Error("Missing access token");
  }

  const response = await axios.get<{ branch_id: number }>(
    "http://127.0.0.1:8000/staffs/current-staff",
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    },
  );

  return response.data;
}

export async function registerBranch(name: string, address: string) {
  const formData = new FormData();
  formData.append("name", name);
  formData.append("address", address);
  await axios.post("http://127.0.0.1:8000/branches/register-branch", formData);
}

export async function registerStaff(input: {
  username: string;
  password: string;
  role: StaffRole;
  branchId: number;
}) {
  const formData = new FormData();
  formData.append("username", input.username);
  formData.append("password", input.password);

  await axios.post("http://127.0.0.1:8000/staffs/register-staff", formData, {
    params: {
      role: input.role,
      branch_id: input.branchId,
    },
  });
}

export async function createMenuItem(name: string, price: number) {
  await axios.post("http://127.0.0.1:8000/menu/create-menu-item", null, {
    params: { name, price },
  });
}

export async function restockMenuItem(
  branchId: number,
  itemId: number,
  quantity: number,
) {
  const token = localStorage.getItem("access_token");
  if (!token) {
    throw new Error("Missing access token");
  }
  const formData = new FormData();
  formData.append("branch_id", branchId.toString());
  formData.append("item_id", itemId.toString());
  formData.append("quantity", quantity.toString());

  await axios.patch("http://127.0.0.1:8000/menu/restock-menu-item", formData, {
    // params: {
    //   branch_id: input.branchId,
    //   item_id: input.itemId,
    //   quantity: input.quantity,
    // },
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}

export function clearAuth() {
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

export function reloadPage() {
  window.dispatchEvent(new Event("auth-changed"));
  window.location.href = "/";
}
