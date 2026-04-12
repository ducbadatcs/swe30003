export type Branch = {
  id: number;
  name: string;
  address: string;
};

export type StaffRole = "staff" | "kitchen" | "cashier" | "manager";

export type Staff = {
  id: number;
  username: string;
  role: StaffRole;
  branch_id: number;
};

export type MenuItemType = {
  id: number;
  name: string;
  price: number;
};

export type BranchInventory = {
  branch_id: number;
  item_id: number;
  quantity: number;
};

export type Notice = {
  severity: "success" | "error";
  message: string;
};

export type SelectFieldProps = {
  label: string;
  value: string;
  onChange: (value: string) => void;
  options: Array<{ value: string; label: string }>;
  disabled?: boolean;
};
