import { useState, useEffect } from "react";

import axios from "axios";

type CheckoutItem = {
  product_id: number | null;
  username: string;
  quantity: number;
};

export function CheckoutCard(item: CheckoutItem){
  // pull product info from db first

  useEffect(() => {
    const product = axios.get()
  })

  return <div>
    <h2>Product: </h2>
    <p>Quantity: {item.quantity}</p>
  </div>
}

export default function Checkout() {
  const [isLoggedIn, setIsLoggedIn] = useState(() => {
    const token = localStorage.getItem("token");
    return !!token;
  });

  const [cart, setCart] = useState<CheckoutItem[]>([]);

  useEffect(() => {
    const fetchCart = async () => {
      await axios
        .get("http://localhost:8000/cart")
        .then((response) => 
          {
            console.log(response.data);
            setCart(response.data);
          })
        .catch((error) => {
          console.error(error);
        });
    };

    fetchCart();
  }, []);

  return <div>
    {
      cart.map(item => )
    }
  </div>;
}
