import { useEffect, useState } from "react";
import axios from "axios";

type Product = {
  id?: string | number;
  name: string;
  price: number;
};

function ProductCard(product: Product) {
  return (
    <div className="col p-1 card">
      <h3>{product.name}</h3>
      <p>{product.price} VND</p>
    </div>
  );
}

export default function App() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

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

  if (loading) return <p>Loading products...</p>;
  if (error) return <p>{error}</p>;

  return (
    <div>
      <h1>Products</h1>
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
