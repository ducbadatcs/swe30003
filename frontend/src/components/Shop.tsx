import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Typography from "@mui/material/Typography";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import Box from "@mui/material/Box";
import axios from "axios";
import { useEffect, useState } from "react";
import {
  Button,
  Divider,
  Paper,
  Stack,
  FormControl,
  InputLabel,
  Select,
  MenuItem as MuiMenuItem,
} from "@mui/material";

import {
  getCurrentUsername,
  fetchBranches,
  fetchMenuItems,
  fetchInventory,
} from "../helpers";
import {
  type MenuItemType,
  type Branch,
  type BranchInventory,
} from "../schemas";

type Cart = Record<number, number>;

export default function Shop() {
  const [username, setUsername] = useState<string>("");
  const [userId, setUserId] = useState<number>(0);
  const [shop, setShop] = useState<MenuItemType[]>([]);
  const [branches, setBranches] = useState<Branch[]>([]);
  const [inventory, setInventory] = useState<BranchInventory[]>([]);
  const [selectedBranchId, setSelectedBranchId] = useState<number>(0);
  const [cart, setCart] = useState<Cart>({});

  const cartItems = Object.entries(cart)
    .map(([itemId, quantity]) => {
      const item = shop.find((menuItem) => menuItem.id === Number(itemId));
      if (!item) return null;

      return {
        id: item.id,
        name: item.name,
        quantity,
        price: item.price,
      };
    })
    .filter(
      (
        item,
      ): item is {
        id: number;
        name: string;
        quantity: number;
        price: number;
      } => item !== null,
    );

  useEffect(() => {
    // async
    async function fetchContents() {
      setBranches(await fetchBranches());
      setShop(await fetchMenuItems());
      setInventory(await fetchInventory(0));
    }
    fetchContents();
  }, []);

  useEffect(() => {
    async function setName() {
      const name = await getCurrentUsername();
      setUsername(name);
    }
    setName();
  }, []);

  const handleBranchChange = async (e: Event) => {
    if (!e.target.value) {
      alert("error something idk");
    }
    setSelectedBranchId(e.target.value);
    setInventory(await fetchInventory(e.target.value));
    setCart({}); // optionally clear cart on branch change
  };

  const handleCheckout = async () => {
    try {
      const token = localStorage.getItem("access_token");
      if (!token) {
        alert("You need to login first before checkout.");
        return;
      }

      // Fetch customer details to get the correct customer ID
      const userRes = await axios.get(
        "http://127.0.0.1:8000/customer/current-customer",
        {
          headers: { Authorization: `Bearer ${token}` },
        },
      );
      const customerId = userRes.data.id;

      // Make the order API call
      // selectedBranchId and customerId in query string; cart (items) in body
      const response = await axios.post(
        `http://127.0.0.1:8000/orders/make-order/?customer_id=${customerId}&branch_id=${selectedBranchId}`,
        cart,
        {
          headers: { Authorization: `Bearer ${token}` },
        },
      );

      alert(`Order Success!`);
      setCart({});
    } catch (error) {
      console.error(error);
      alert("Failed to place order. Please try again.");
    }
  };

  const cartTotal = cartItems.reduce(
    (sum, item) => sum + item.price * item.quantity,
    0,
  );

  const inventoryByItemId = new Map(
    inventory.map((row) => [row.item_id, row.quantity]),
  );

  return (
    <Stack spacing={3}>
      <Paper sx={{ p: 3 }}>
        <Stack
          direction={{ xs: "column", sm: "row" }}
          justifyContent="space-between"
          alignItems={{ xs: "flex-start", sm: "center" }}
          spacing={2}
        >
          <Box>
            <Typography variant="h4">Shop</Typography>
            {username != "" ? (
              <Typography color="text.secondary" sx={{ mt: 1 }}>
                Hello {username}, what would you like to order? Browse the menu
                and add items to your cart.
              </Typography>
            ) : (
              <Typography color="text.secondary" sx={{ mt: 1 }}>
                Please log in to order
              </Typography>
            )}
          </Box>
          <FormControl sx={{ minWidth: 200 }}>
            <InputLabel>Branch</InputLabel>
            <Select
              label="Branch"
              value={selectedBranchId}
              onChange={(e) => {
                handleBranchChange(e);
              }}
            >
              {branches.map((branch) => (
                <MuiMenuItem key={branch.id} value={String(branch.id)}>
                  {branch.name}
                </MuiMenuItem>
              ))}
            </Select>
          </FormControl>
        </Stack>
      </Paper>

      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: {
            xs: "1fr",
            xl: "minmax(0, 1.65fr) minmax(320px, 0.85fr)",
          },
          gap: 3,
          alignItems: "start",
        }}
      >
        <Box
          sx={{
            display: "grid",
            gridTemplateColumns: {
              xs: "1fr",
              sm: "repeat(2, minmax(0, 1fr))",
              lg: "repeat(3, minmax(0, 1fr))",
            },
            gap: 2,
          }}
        >
          {shop.map((item) => {
            const available = inventoryByItemId.get(item.id) ?? 0;

            return (
              <Card
                key={item.id}
                sx={{ display: "flex", flexDirection: "column" }}
              >
                <CardContent sx={{ flexGrow: 1 }}>
                  <Stack spacing={1}>
                    <Typography variant="h6">{item.name}</Typography>
                    <Typography variant="body1" color="text.secondary">
                      ${item.price.toFixed(2)}
                    </Typography>
                    <Typography variant="body2">
                      Available in this branch: {available}
                    </Typography>
                  </Stack>
                </CardContent>
                <Box sx={{ p: 2, pt: 0 }}>
                  <Button
                    fullWidth
                    variant="contained"
                    disabled={available === 0}
                    onClick={() => {
                      setCart((currentCart) => ({
                        ...currentCart,
                        [item.id]: (currentCart[item.id] ?? 0) + 1,
                      }));
                    }}
                  >
                    Add to cart
                  </Button>
                </Box>
              </Card>
            );
          })}
        </Box>

        <Paper sx={{ p: 3 }}>
          <Stack spacing={2.5}>
            <Box>
              <Typography variant="h5">Cart</Typography>
              <Typography color="text.secondary" sx={{ mt: 1 }}>
                Review what you’ve added before checking out.
              </Typography>
            </Box>
            <Divider />

            {cartItems.length === 0 ? (
              <Typography color="text.secondary">
                Your cart is empty. Add something from the menu to get started.
              </Typography>
            ) : (
              <Box>
                {" "}
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Product</TableCell>
                        <TableCell>Quantity</TableCell>
                        <TableCell>Price Per Item</TableCell>
                        <TableCell>Total Item Price</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {cartItems.map((item) => (
                        <TableRow key={item.id}>
                          <TableCell>{item.name}</TableCell>
                          <TableCell>{item.quantity}</TableCell>
                          <TableCell>${item.price.toFixed(2)}</TableCell>
                          <TableCell>
                            ${(item.price * item.quantity).toFixed(2)}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
                {username != "" ? (
                  <Button
                    fullWidth
                    variant="contained"
                    onClick={handleCheckout}
                  >
                    Checkout
                  </Button>
                ) : (
                  <Typography>
                    You need to login first before checkout.
                  </Typography>
                )}
              </Box>
            )}

            <Divider />
            <Box
              sx={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              <Typography color="text.secondary">Total</Typography>
              <Typography variant="h6">${cartTotal.toFixed(2)}</Typography>
            </Box>
          </Stack>
        </Paper>
      </Box>
    </Stack>
  );
}
