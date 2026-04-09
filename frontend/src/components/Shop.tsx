import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import CardMedia from "@mui/material/CardMedia";
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
import { Button, Paper } from "@mui/material";

type MenuItem = {
  id: number;
  name: string;
  price: number;
};

type Cart = Record<number, number>;
// const [cart, setCart] = useState<Cart>({});

export default function Shop() {
  const [shop, setShop] = useState<MenuItem[]>([]);
  const [cart, setCart] = useState<Cart>({});

  useEffect(() => {
    axios
      .get<MenuItem[]>("http://127.0.0.1:8000/menu/list-menu-items")
      .then((response) => {
        setShop(response.data);
      })
      .catch((err) => console.error(err));
  }, []);

  const cartRows = Object.entries(cart).map(([itemId, quantity]) => {
    const item = shop.find((menuItem) => menuItem.id === Number(itemId));
    if (!item) return null;

    return (
      <TableRow key={item.id}>
        <TableCell>{item.name}</TableCell>
        <TableCell>{quantity}</TableCell>
        <TableCell>{item.price}</TableCell>
      </TableRow>
    );
  });

  return (
    <div>
      <Box sx={{ display: "flex", flexDirection: "row", mx: "auto" }}>
        {shop.map((item) => (
          <Card
            key={item.id}
            sx={{
              width: 280,
              minHeight: 20,
              display: "flex",
              flexDirection: "column",
            }}
          >
            <CardMedia></CardMedia>
            <CardContent>
              <Typography variant="h4" component="div">
                {item.name}
              </Typography>
              <Typography variant="h5" component="div">
                {item.price}
              </Typography>
            </CardContent>
            <Button
              onClick={() => {
                setCart((currentCart) => ({
                  ...currentCart,
                  [item.id]: (currentCart[item.id] ?? 0) + 1,
                }));
              }}
            >
              Add to cart
            </Button>
          </Card>
        ))}
      </Box>
      <Box>
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Product</TableCell>
                <TableCell>Quantity</TableCell>
                <TableCell>Cost (per one item)</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>{cartRows}</TableBody>
          </Table>
        </TableContainer>
      </Box>
    </div>
  );
}
