import sys

content = """import { type ReactNode, useEffect, useState } from "react";

import axios from "axios";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Divider from "@mui/material/Divider";
import FormControl from "@mui/material/FormControl";
import InputLabel from "@mui/material/InputLabel";
import MenuItem from "@mui/material/MenuItem";
import Paper from "@mui/material/Paper";
import Select from "@mui/material/Select";
import Stack from "@mui/material/Stack";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";

import { getCurrentRole, getCurrentUsername } from "../utils";

// --- Types ---

type Branch = {
  id: number;
  name: string;
  address: string;
};

type StaffRole = "staff" | "kitchen" | "cashier" | "manager";

type Staff = {
  id: number;
  username: string;
  role: StaffRole;
  branch_id: number;
};

type MenuItemType = {
  id: number;
  name: string;
  price: number;
};

type BranchInventory = {
  branch_id: number;
  item_id: number;
  quantity: number;
};

type Notice = {
  severity: "success" | "error";
  message: string;
};

type SelectFieldProps = {
  label: string;
  value: string;
  onChange: (value: string) => void;
  options: Array<{ value: string; label: string }>;
  disabled?: boolean;
};

// --- Shared UI Components ---

function SectionCard({
  title,
  description,
  children,
}: {
  title: string;
  description: string;
  children: ReactNode;
}) {
  return (
    <Card sx={{ height: "100%" }}>
      <CardContent>
        <Stack spacing={2.5}>
          <Box>
            <Typography variant="h5">{title}</Typography>
            <Typography color="text.secondary" sx={{ mt: 0.5 }}>
              {description}
            </Typography>
          </Box>
          {children}
        </Stack>
      </CardContent>
    </Card>
  );
}

function SelectField({
  label,
  value,
  onChange,
  options,
  disabled,
}: SelectFieldProps) {
  return (
    <FormControl fullWidth>
      <InputLabel>{label}</InputLabel>
      <Select
        label={label}
        value={value}
        disabled={disabled}
        onChange={(event) => onChange(event.target.value)}
      >
        {options.map((option) => (
          <MenuItem key={option.value} value={option.value}>
            {option.label}
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  );
}

// --- API Helpers ---

async function fetchBranches(): Promise<Branch[]> {
  const response = await axios.get<Branch[]>(
    "http://127.0.0.1:8000/branches/list-branches",
  );
  return response.data;
}

async function fetchStaffs(): Promise<Staff[]> {
  const response = await axios.get<Staff[]>(
    "http://127.0.0.1:8000/staffs/list-staffs",
  );
  return response.data;
}

async function fetchMenuItems(): Promise<MenuItemType[]> {
  const response = await axios.get<MenuItemType[]>(
    "http://127.0.0.1:8000/menu/list-menu-items",
  );
  return response.data;
}

async function fetchInventory(branchId: number): Promise<BranchInventory[]> {
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

async function fetchCurrentStaff(): Promise<{ branch_id: number }> {
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

async function registerBranch(name: string, address: string) {
  await axios.post("http://127.0.0.1:8000/branches/register-branch", null, {
    params: { name, address },
  });
}

async function registerStaff(input: {
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

async function createMenuItem(name: string, price: number) {
  await axios.post("http://127.0.0.1:8000/menu/create-menu-item", null, {
    params: { name, price },
  });
}

async function restockMenuItem(input: {
  branchId: number;
  itemId: number;
  quantity: number;
}) {
  await axios.patch("http://127.0.0.1:8000/menu/restock-menu-item", null, {
    params: {
      branch_id: input.branchId,
      item_id: input.itemId,
      quantity: input.quantity,
    },
  });
}

// --- Section Components ---

function BranchSection({
  branches,
  onRefresh,
  setNotice,
}: {
  branches: Branch[];
  onRefresh: () => Promise<void>;
  setNotice: (n: Notice) => void;
}) {
  const [branchName, setBranchName] = useState("");
  const [branchAddress, setBranchAddress] = useState("");

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    try {
      await registerBranch(branchName.trim(), branchAddress.trim());
      setBranchName("");
      setBranchAddress("");
      await onRefresh();
      setNotice({ severity: "success", message: "Branch registered." });
    } catch {
      setNotice({ severity: "error", message: "Could not register branch." });
    }
  }

  return (
    <SectionCard
      title="Register Branch"
      description="Create a new branch before assigning staff or stock."
    >
      <Stack component="form" spacing={2} onSubmit={handleSubmit}>
        <TextField
          label="Branch Name"
          value={branchName}
          onChange={(event) => setBranchName(event.target.value)}
          fullWidth
          required
        />
        <TextField
          label="Branch Address"
          value={branchAddress}
          onChange={(event) => setBranchAddress(event.target.value)}
          fullWidth
          required
        />
        <Button type="submit" variant="contained">
          Register Branch
        </Button>
      </Stack>

      <Divider sx={{ my: 2 }} />

      <Typography variant="subtitle1" sx={{ mb: 1 }}>
        Current Branches
      </Typography>
      <TableContainer component={Paper} variant="outlined">
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Name</TableCell>
              <TableCell>Address</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {branches.map((branch) => (
              <TableRow key={branch.id}>
                <TableCell>{branch.id}</TableCell>
                <TableCell>{branch.name}</TableCell>
                <TableCell>{branch.address}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </SectionCard>
  );
}

function StaffSection({
  staffs,
  branches,
  onRefresh,
  setNotice,
}: {
  staffs: Staff[];
  branches: Branch[];
  onRefresh: () => Promise<void>;
  setNotice: (n: Notice) => void;
}) {
  const [staffUsername, setStaffUsername] = useState("");
  const [staffPassword, setStaffPassword] = useState("");
  const [staffRole, setStaffRole] = useState<StaffRole>("staff");
  const [staffBranchId, setStaffBranchId] = useState("");

  useEffect(() => {
    if (!staffBranchId && branches.length > 0) {
      setStaffBranchId(String(branches[0].id));
    }
  }, [branches, staffBranchId]);

  const branchOptions = branches.map((branch) => ({
    value: String(branch.id),
    label: `${branch.name} (#${branch.id})`,
  }));

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!staffBranchId) {
      setNotice({ severity: "error", message: "Choose a branch first." });
      return;
    }
    try {
      await registerStaff({
        username: staffUsername.trim(),
        password: staffPassword,
        role: staffRole,
        branchId: Number(staffBranchId),
      });
      setStaffUsername("");
      setStaffPassword("");
      await onRefresh();
      setNotice({ severity: "success", message: "Staff member registered." });
    } catch {
      setNotice({ severity: "error", message: "Could not register staff." });
    }
  }

  return (
    <SectionCard
      title="Register Staff"
      description="Create staff accounts and attach them to a branch."
    >
      <Stack component="form" spacing={2} onSubmit={handleSubmit}>
        <TextField
          label="Username"
          value={staffUsername}
          onChange={(event) => setStaffUsername(event.target.value)}
          fullWidth
          required
        />
        <TextField
          label="Password"
          type="password"
          value={staffPassword}
          onChange={(event) => setStaffPassword(event.target.value)}
          fullWidth
          required
        />
        <FormControl fullWidth>
          <InputLabel>Role</InputLabel>
          <Select
            label="Role"
            value={staffRole}
            onChange={(event) => setStaffRole(event.target.value as StaffRole)}
          >
            <MenuItem value="staff">Staff</MenuItem>
            <MenuItem value="kitchen">Kitchen</MenuItem>
            <MenuItem value="cashier">Cashier</MenuItem>
            <MenuItem value="manager">Manager</MenuItem>
          </Select>
        </FormControl>
        <SelectField
          label="Branch"
          value={staffBranchId}
          onChange={setStaffBranchId}
          options={branchOptions}
        />
        <Button type="submit" variant="contained">
          Register Staff
        </Button>
      </Stack>

      <Divider sx={{ my: 2 }} />

      <Typography variant="subtitle1" sx={{ mb: 1 }}>
        Current Staff
      </Typography>
      <TableContainer component={Paper} variant="outlined">
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Username</TableCell>
              <TableCell>Role</TableCell>
              <TableCell>Branch</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {staffs.map((staff) => (
              <TableRow key={staff.id}>
                <TableCell>{staff.id}</TableCell>
                <TableCell>{staff.username}</TableCell>
                <TableCell>{staff.role}</TableCell>
                <TableCell>
                  {branches.find((branch) => branch.id === staff.branch_id)
                    ?.name ?? staff.branch_id}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </SectionCard>
  );
}

function MenuSection({
  menuItems,
  onRefresh,
  setNotice,
}: {
  menuItems: MenuItemType[];
  onRefresh: () => Promise<void>;
  setNotice: (n: Notice) => void;
}) {
  const [menuName, setMenuName] = useState("");
  const [menuPrice, setMenuPrice] = useState("");

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    try {
      await createMenuItem(menuName.trim(), Number(menuPrice));
      setMenuName("");
      setMenuPrice("");
      await onRefresh();
      setNotice({ severity: "success", message: "Menu item added." });
    } catch {
      setNotice({ severity: "error", message: "Could not add menu item." });
    }
  }

  return (
    <SectionCard
      title="Add Menu Item"
      description="Create a new product for the shop menu."
    >
      <Stack component="form" spacing={2} onSubmit={handleSubmit}>
        <TextField
          label="Item Name"
          value={menuName}
          onChange={(event) => setMenuName(event.target.value)}
          fullWidth
          required
        />
        <TextField
          label="Price"
          type="number"
          slotProps={{
            htmlInput: { step: "0.01", min: "0" },
          }}
          value={menuPrice}
          onChange={(event) => setMenuPrice(event.target.value)}
          fullWidth
          required
        />
        <Button type="submit" variant="contained">
          Add Menu Item
        </Button>
      </Stack>

      <Divider sx={{ my: 2 }} />

      <Typography variant="subtitle1" sx={{ mb: 1 }}>
        Current Menu Items
      </Typography>
      <TableContainer component={Paper} variant="outlined">
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Name</TableCell>
              <TableCell>Price</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {menuItems.map((item) => (
              <TableRow key={item.id}>
                <TableCell>{item.id}</TableCell>
                <TableCell>{item.name}</TableCell>
                <TableCell>${item.price.toFixed(2)}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </SectionCard>
  );
}

function InventorySection({
  branches,
  menuItems,
  currentStaffBranchId,
  setNotice,
}: {
  branches: Branch[];
  menuItems: MenuItemType[];
  currentStaffBranchId: string;
  setNotice: (n: Notice) => void;
}) {
  const [inventory, setInventory] = useState<BranchInventory[]>([]);
  const [inventoryBranchId, setInventoryBranchId] = useState("");
  const [inventoryItemId, setInventoryItemId] = useState("");
  const [inventoryQuantity, setInventoryQuantity] = useState("");

  const branchOptions = branches.map((branch) => ({
    value: String(branch.id),
    label: `${branch.name} (#${branch.id})`,
  }));

  const itemOptions = menuItems.map((item) => ({
    value: String(item.id),
    label: `${item.name} (#${item.id})`,
  }));

  useEffect(() => {
    if (currentStaffBranchId) {
      setInventoryBranchId(currentStaffBranchId);
      return;
    }
    if (!inventoryBranchId && branches.length > 0) {
      setInventoryBranchId(String(branches[0].id));
    }
  }, [branches, currentStaffBranchId, inventoryBranchId]);

  useEffect(() => {
    const loadBranchInventory = async () => {
      if (!inventoryBranchId) {
        setInventory([]);
        return;
      }
      try {
        setInventory(await fetchInventory(Number(inventoryBranchId)));
      } catch {
        setInventory([]);
      }
    };
    void loadBranchInventory();
  }, [inventoryBranchId]);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!inventoryBranchId || !inventoryItemId) {
      setNotice({
        severity: "error",
        message: "Choose both a branch and a menu item.",
      });
      return;
    }
    if (currentStaffBranchId && inventoryBranchId !== currentStaffBranchId) {
      setNotice({
        severity: "error",
        message: "You can only restock your own branch.",
      });
      return;
    }
    try {
      await restockMenuItem({
        branchId: Number(inventoryBranchId),
        itemId: Number(inventoryItemId),
        quantity: Number(inventoryQuantity),
      });
      setInventoryQuantity("");
      setInventory(await fetchInventory(Number(inventoryBranchId)));
      setNotice({ severity: "success", message: "Inventory updated." });
    } catch {
      setNotice({ severity: "error", message: "Could not update inventory." });
    }
  }

  const selectedBranch = branches.find(
    (branch) => branch.id === Number(inventoryBranchId),
  );

  return (
    <SectionCard
      title="Restock Inventory"
      description="Assign menu items to a branch and update stock quantities."
    >
      <Stack component="form" spacing={2} onSubmit={handleSubmit}>
        <SelectField
          label="Branch"
          value={inventoryBranchId}
          onChange={setInventoryBranchId}
          options={branchOptions}
          disabled={Boolean(currentStaffBranchId)}
        />
        <SelectField
          label="Menu Item"
          value={inventoryItemId}
          onChange={setInventoryItemId}
          options={itemOptions}
        />
        <TextField
          label="Quantity"
          type="number"
          slotProps={{
            htmlInput: { min: "0", step: "1" },
          }}
          value={inventoryQuantity}
          onChange={(event) => setInventoryQuantity(event.target.value)}
          fullWidth
          required
        />
        <Button type="submit" variant="contained">
          Update Inventory
        </Button>
      </Stack>

      <Divider sx={{ my: 2 }} />

      <Typography variant="subtitle1" sx={{ mb: 1 }}>
        Inventory Snapshot
      </Typography>
      <Typography color="text.secondary" sx={{ mb: 1.5 }}>
        {selectedBranch
          ? `Showing stock for ${selectedBranch.name}`
          : "Choose a branch to view stock."}
      </Typography>
      <TableContainer component={Paper} variant="outlined">
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Item</TableCell>
              <TableCell>Quantity</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {inventory.map((entry) => (
              <TableRow key={`${entry.branch_id}-${entry.item_id}`}>
                <TableCell>
                  {menuItems.find((item) => item.id === entry.item_id)?.name ??
                    entry.item_id}
                </TableCell>
                <TableCell>{entry.quantity}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </SectionCard>
  );
}

// --- Main Admin Component ---

export default function Admin() {
  const [username, setUsername] = useState("");
  const [role, setRole] = useState("");
  const [notice, setNotice] = useState<Notice | null>(null);

  const [branches, setBranches] = useState<Branch[]>([]);
  const [staffs, setStaffs] = useState<Staff[]>([]);
  const [menuItems, setMenuItems] = useState<MenuItemType[]>([]);
  const [currentStaffBranchId, setCurrentStaffBranchId] = useState("");

  useEffect(() => {
    const syncAuth = async () => {
      setUsername(await getCurrentUsername());
      setRole(await getCurrentRole());

      try {
        const currentStaff = await fetchCurrentStaff();
        const branchId = String(currentStaff.branch_id);
        setCurrentStaffBranchId(branchId);
      } catch {
        setCurrentStaffBranchId("");
      }
    };

    void syncAuth();

    const onAuthChanged = () => {
      void syncAuth();
    };

    window.addEventListener("auth-changed", onAuthChanged);
    return () => window.removeEventListener("auth-changed", onAuthChanged);
  }, []);

  useEffect(() => {
    const loadData = async () => {
      try {
        const [branchData, staffData, menuData] = await Promise.all([
          fetchBranches(),
          fetchStaffs(),
          fetchMenuItems(),
        ]);
        setBranches(branchData);
        setStaffs(staffData);
        setMenuItems(menuData);
      } catch {
        setNotice({
          severity: "error",
          message: "Could not load the current admin data.",
        });
      }
    };

    void loadData();
  }, []);

  async function refreshCoreData() {
    const [branchData, staffData, menuData] = await Promise.all([
      fetchBranches(),
      fetchStaffs(),
      fetchMenuItems(),
    ]);

    setBranches(branchData);
    setStaffs(staffData);
    setMenuItems(menuData);
  }

  return (
    <Stack spacing={3}>
      <Paper
        sx={{
          p: 3,
          color: "common.white",
          background:
            "linear-gradient(135deg, rgba(124, 29, 28, 0.98), rgba(64, 17, 16, 0.98))",
        }}
      >
        <Stack spacing={1.5}>
          <Typography variant="overline" sx={{ letterSpacing: 2 }}>
            Administration
          </Typography>
          <Typography variant="h3">Operations Console</Typography>
          <Typography sx={{ maxWidth: 760, opacity: 0.9 }}>
            Manage branches, staff, menu items, and inventory from one place.
            The page reuses the same Material UI building blocks as the rest of
            the app, but keeps each action isolated in its own private helper
            function.
          </Typography>
          <Typography sx={{ opacity: 0.8 }}>
            Signed in as {username || "guest"}
            {role ? ` · role: ${role}` : ""}
          </Typography>
        </Stack>
      </Paper>

      {notice ? (
        <Alert severity={notice.severity}>{notice.message}</Alert>
      ) : null}

      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: {
            xs: "1fr",
            lg: "repeat(2, minmax(0, 1fr))",
          },
          gap: 3,
        }}
      >
        <BranchSection
          branches={branches}
          onRefresh={refreshCoreData}
          setNotice={setNotice}
        />
        <StaffSection
          staffs={staffs}
          branches={branches}
          onRefresh={refreshCoreData}
          setNotice={setNotice}
        />
        <MenuSection
          menuItems={menuItems}
          onRefresh={refreshCoreData}
          setNotice={setNotice}
        />
        <InventorySection
          branches={branches}
          menuItems={menuItems}
          currentStaffBranchId={currentStaffBranchId}
          setNotice={setNotice}
        />
      </Box>
    </Stack>
  );
}
"""

with open('/home/duc/Documents/SWE30003-Project/frontend/src/components/Admin.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

