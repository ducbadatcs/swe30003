import { useEffect, useState } from "react";
import axios from "axios";

type Product = {
  id?: string | number;
  name: string;
  price: number;
};

function ProductCard(product: Product) {
  const addToCart = async () => {
    const token = localStorage.getItem("token");

    await axios.post(
      "http://localhost:8000/cart/add",
      { product_id: product.id },
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      },
    );
  };

  return (
    <div className="col p-1 card">
      <h3>{product.name}</h3>
      <p>{product.price} VND</p>
      <button onClick={addToCart}>Add to Cart</button>
    </div>
  );
}

export default function App() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const response = await axios.get<Product[]>(
          "http://localhost:8000/products",
        );
        setProducts(response.data);
      } catch (err) {
        console.error("Error getting data:", err);
        setError("Failed to load products.");
      } finally {
        setLoading(false);
      }
    };

    fetchProducts();
  }, []);

  useEffect(() => {
    // You can use this anywhere in your React components
    const token = localStorage.getItem("token");
    setIsLoggedIn(!!token);
  });

  if (loading) return <p>Loading products...</p>;
  if (error) return <p>{error}</p>;

  return (
    <div>
      <h1>Products</h1>
      <h2>{isLoggedIn ? "Welcome!" : "Please log in"}</h2>
      <div style={{ width: "80%" }} className="card mx-auto p-1">
        {products.length === 0 ? (
          <p className="mx-auto">No products yet!</p>
        ) : (
          products.map((product) => ProductCard(product))
        )}
      </div>
    </div>
  );
}
