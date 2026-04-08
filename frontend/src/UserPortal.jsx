import { useEffect, useMemo, useState } from "react";
import { apiRequest } from "./api";

const SESSION_KEY = "restaurant-user-session";

function formatCurrency(value) {
  return new Intl.NumberFormat("en-AU", {
    style: "currency",
    currency: "AUD",
  }).format(value ?? 0);
}

function formatDate(value) {
  if (!value) {
    return "N/A";
  }

  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? value : parsed.toLocaleDateString();
}

function loadSavedSession() {
  try {
    const saved = localStorage.getItem(SESSION_KEY);
    return saved ? JSON.parse(saved) : null;
  } catch {
    return null;
  }
}

export default function UserPortal() {
  const [session, setSession] = useState(() => loadSavedSession());
  const [loginForm, setLoginForm] = useState({
    username: "alice",
    password: "password123",
  });
  const [portal, setPortal] = useState(null);
  const [cart, setCart] = useState([]);
  const [checkoutForm, setCheckoutForm] = useState({
    branchId: "",
    orderType: "pickup",
    promotionId: "",
  });
  const [menuQuery, setMenuQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [loginLoading, setLoginLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function loadPortal(customerId) {
    setLoading(true);
    setError("");

    try {
      const portalData = await apiRequest(`/api/customer-portal/${customerId}`);
      setPortal(portalData);
      setCheckoutForm((current) => ({
        branchId: current.branchId || portalData.branches[0]?.branchId || "",
        orderType: current.orderType || "pickup",
        promotionId:
          current.promotionId || portalData.promotions[0]?.promoId || "",
      }));
    } catch (requestError) {
      setError(requestError.message);
      setPortal(null);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (session?.customerId) {
      void loadPortal(session.customerId);
    }
  }, [session?.customerId]);

  async function handleLogin(event) {
    event.preventDefault();
    setLoginLoading(true);
    setError("");
    setMessage("");

    try {
      const loginData = await apiRequest("/api/auth/login", {
        method: "POST",
        body: JSON.stringify(loginForm),
      });
      setSession(loginData);
      localStorage.setItem(SESSION_KEY, JSON.stringify(loginData));
      setMessage(`Welcome back, ${loginData.fullName}.`);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoginLoading(false);
    }
  }

  function handleLogout() {
    localStorage.removeItem(SESSION_KEY);
    setSession(null);
    setPortal(null);
    setCart([]);
    setCheckoutForm({ branchId: "", orderType: "pickup", promotionId: "" });
    setMessage("Signed out.");
  }

  function addToCart(menuItem) {
    setCart((current) => {
      const existingItem = current.find(
        (item) => item.itemId === menuItem.itemId,
      );
      if (existingItem) {
        return current.map((item) =>
          item.itemId === menuItem.itemId
            ? { ...item, quantity: item.quantity + 1 }
            : item,
        );
      }

      return [
        ...current,
        {
          itemId: menuItem.itemId,
          name: menuItem.name,
          price: menuItem.price,
          quantity: 1,
        },
      ];
    });
    setMessage(`${menuItem.name} added to checkout.`);
  }

  function changeCartQuantity(itemId, delta) {
    setCart((current) =>
      current
        .map((item) =>
          item.itemId === itemId
            ? { ...item, quantity: item.quantity + delta }
            : item,
        )
        .filter((item) => item.quantity > 0),
    );
  }

  function removeFromCart(itemId) {
    setCart((current) => current.filter((item) => item.itemId !== itemId));
  }

  const cartTotal = useMemo(
    () => cart.reduce((sum, item) => sum + item.price * item.quantity, 0),
    [cart],
  );

  const cartCount = useMemo(
    () => cart.reduce((sum, item) => sum + item.quantity, 0),
    [cart],
  );

  const visibleMenu = (portal?.menuItems || []).filter((item) => {
    const query = menuQuery.trim().toLowerCase();
    if (!query) {
      return true;
    }
    return (
      item.name.toLowerCase().includes(query) ||
      item.itemId.toLowerCase().includes(query)
    );
  });

  async function handleCheckout(event) {
    event.preventDefault();

    if (!session?.customerId) {
      setError("Please log in before checking out.");
      return;
    }

    if (cart.length === 0) {
      setError("Add at least one item before checkout.");
      return;
    }

    setLoading(true);
    setError("");
    setMessage("");

    try {
      const createdOrder = await apiRequest("/api/orders", {
        method: "POST",
        body: JSON.stringify({
          customer_id: session.customerId,
          branch_id: checkoutForm.branchId,
          order_type: checkoutForm.orderType,
          promotion_id: checkoutForm.promotionId || null,
          items: cart.map((item) => ({
            menu_item_id: item.itemId,
            quantity: item.quantity,
          })),
        }),
      });

      setCart([]);
      setMessage(
        `Order ${createdOrder.orderId} placed for ${formatCurrency(createdOrder.totalAmount)}.`,
      );
      await loadPortal(session.customerId);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="portal-page">
      {!session ? (
        <main className="auth-layout">
          <section className="auth-hero">
            <p className="eyebrow">Customer portal</p>
            <h1>Log in, order, and track your checkout.</h1>
            <p>
              This portal is for customers only. It supports login, menu
              browsing, cart building, checkout, and order history. There is no
              payment step in this assignment.
            </p>

            <div className="auth-highlights">
              <div>
                <strong>1</strong>
                <span>Sign in</span>
              </div>
              <div>
                <strong>2</strong>
                <span>Choose items</span>
              </div>
              <div>
                <strong>3</strong>
                <span>Checkout summary</span>
              </div>
            </div>
          </section>

          <section className="auth-card shell-card">
            <div className="card-heading">
              <div>
                <p className="eyebrow">Access</p>
                <h2>Customer login</h2>
              </div>
              <span className="badge">Seeded demo</span>
            </div>

            <form className="stacked-form" onSubmit={handleLogin}>
              <label>
                Username
                <input
                  type="text"
                  value={loginForm.username}
                  onChange={(event) =>
                    setLoginForm((current) => ({
                      ...current,
                      username: event.target.value,
                    }))
                  }
                  placeholder="alice"
                />
              </label>

              <label>
                Password
                <input
                  type="password"
                  value={loginForm.password}
                  onChange={(event) =>
                    setLoginForm((current) => ({
                      ...current,
                      password: event.target.value,
                    }))
                  }
                  placeholder="password123"
                />
              </label>

              <button
                className="primary-button"
                type="submit"
                disabled={loginLoading}
              >
                {loginLoading ? "Signing in..." : "Sign in"}
              </button>
            </form>

            <p className="hint">
              Try the seeded account <strong>alice / password123</strong>.
            </p>
          </section>
        </main>
      ) : (
        <main className="portal-layout">
          <header className="topbar shell-card">
            <div>
              <p className="eyebrow">Restaurant portal</p>
              <h1>Welcome, {session.fullName}</h1>
              <p className="topbar-copy">
                Browse the menu, build a cart, and submit a checkout summary.
              </p>
            </div>

            <div className="account-card">
              <span
                className={`badge status-${session.loyaltyStatus.toLowerCase()}`}
              >
                {session.loyaltyStatus}
              </span>
              <strong>{formatCurrency(cartTotal)}</strong>
              <span>{cartCount} items in checkout</span>
              <button type="button" onClick={handleLogout}>
                Log out
              </button>
            </div>
          </header>

          {error ? (
            <div className="feedback feedback-error">{error}</div>
          ) : null}
          {message ? (
            <div className="feedback feedback-success">{message}</div>
          ) : null}

          <section className="summary-grid">
            <article className="metric-card shell-card">
              <span>Points</span>
              <strong>{session.points}</strong>
            </article>
            <article className="metric-card shell-card">
              <span>Orders</span>
              <strong>{portal?.orders.length ?? 0}</strong>
            </article>
            <article className="metric-card shell-card">
              <span>Branches</span>
              <strong>{portal?.branches.length ?? 0}</strong>
            </article>
            <article className="metric-card shell-card">
              <span>Menu items</span>
              <strong>{portal?.menuItems.length ?? 0}</strong>
            </article>
          </section>

          <section className="content-grid">
            <article className="panel shell-card">
              <div className="card-heading">
                <div>
                  <p className="eyebrow">Menu</p>
                  <h2>Browse dishes</h2>
                </div>
                <label className="inline-search">
                  <span>Search</span>
                  <input
                    type="text"
                    value={menuQuery}
                    onChange={(event) => setMenuQuery(event.target.value)}
                    placeholder="burger, latte, item-001"
                  />
                </label>
              </div>

              {loading && !portal ? (
                <div className="empty-state">Loading your portal...</div>
              ) : (
                <div className="menu-grid">
                  {visibleMenu.map((item) => (
                    <article className="menu-card" key={item.itemId}>
                      <div>
                        <div className="menu-card-top">
                          <h3>{item.name}</h3>
                          <span>{formatCurrency(item.price)}</span>
                        </div>
                        <p>{item.itemId}</p>
                      </div>

                      <div className="card-footer">
                        <span
                          className={`badge ${item.isAvailable ? "badge-live" : "badge-muted"}`}
                        >
                          {item.isAvailable ? "available" : "unavailable"}
                        </span>
                        <button
                          type="button"
                          onClick={() => addToCart(item)}
                          disabled={!item.isAvailable}
                        >
                          Add to checkout
                        </button>
                      </div>
                    </article>
                  ))}
                </div>
              )}
            </article>

            <aside className="checkout-column">
              <article className="panel shell-card sticky-panel">
                <div className="card-heading">
                  <div>
                    <p className="eyebrow">Checkout</p>
                    <h2>Summary</h2>
                  </div>
                  <span className="badge">No payment step</span>
                </div>

                <form className="stacked-form" onSubmit={handleCheckout}>
                  <label>
                    Branch
                    <select
                      value={checkoutForm.branchId}
                      onChange={(event) =>
                        setCheckoutForm((current) => ({
                          ...current,
                          branchId: event.target.value,
                        }))
                      }
                    >
                      {portal?.branches.map((branch) => (
                        <option key={branch.branchId} value={branch.branchId}>
                          {branch.location}
                        </option>
                      ))}
                    </select>
                  </label>

                  <label>
                    Order type
                    <select
                      value={checkoutForm.orderType}
                      onChange={(event) =>
                        setCheckoutForm((current) => ({
                          ...current,
                          orderType: event.target.value,
                        }))
                      }
                    >
                      <option value="pickup">Pickup</option>
                      <option value="dine-in">Dine-in</option>
                      <option value="delivery">Delivery</option>
                    </select>
                  </label>

                  <label>
                    Promotion
                    <select
                      value={checkoutForm.promotionId}
                      onChange={(event) =>
                        setCheckoutForm((current) => ({
                          ...current,
                          promotionId: event.target.value,
                        }))
                      }
                    >
                      <option value="">No promotion</option>
                      {portal?.promotions.map((promotion) => (
                        <option
                          key={promotion.promoId}
                          value={promotion.promoId}
                        >
                          {promotion.promoId}
                        </option>
                      ))}
                    </select>
                  </label>

                  <div className="checkout-list">
                    {cart.length === 0 ? (
                      <div className="empty-state compact">
                        Your checkout is empty.
                      </div>
                    ) : (
                      cart.map((item) => (
                        <div className="checkout-line" key={item.itemId}>
                          <div>
                            <strong>{item.name}</strong>
                            <p>
                              {item.quantity} x {formatCurrency(item.price)}
                            </p>
                          </div>
                          <div className="checkout-line-actions">
                            <span>
                              {formatCurrency(item.price * item.quantity)}
                            </span>
                            <button
                              type="button"
                              onClick={() =>
                                changeCartQuantity(item.itemId, -1)
                              }
                            >
                              -
                            </button>
                            <button
                              type="button"
                              onClick={() => changeCartQuantity(item.itemId, 1)}
                            >
                              +
                            </button>
                            <button
                              type="button"
                              onClick={() => removeFromCart(item.itemId)}
                            >
                              Remove
                            </button>
                          </div>
                        </div>
                      ))
                    )}
                  </div>

                  <div className="checkout-total">
                    <span>Total</span>
                    <strong>{formatCurrency(cartTotal)}</strong>
                  </div>

                  <button
                    className="primary-button"
                    type="submit"
                    disabled={cart.length === 0}
                  >
                    Submit order
                  </button>
                </form>

                <p className="hint">
                  Checkout only captures the item list and total price.
                </p>
              </article>
            </aside>
          </section>

          <section className="content-grid secondary-grid">
            <article className="panel shell-card">
              <div className="card-heading">
                <div>
                  <p className="eyebrow">Orders</p>
                  <h2>Recent orders</h2>
                </div>
              </div>

              <div className="order-list">
                {(portal?.orders || []).length === 0 ? (
                  <div className="empty-state">No orders yet.</div>
                ) : (
                  portal.orders.map((order) => (
                    <article className="order-card" key={order.orderId}>
                      <div className="order-card-top">
                        <div>
                          <strong>{order.orderId}</strong>
                          <p>
                            {order.orderType} · {order.branchId}
                          </p>
                        </div>
                        <div className="order-card-meta">
                          <span
                            className={`badge status-${order.status.replaceAll(" ", "-")}`}
                          >
                            {order.status}
                          </span>
                          <strong>{formatCurrency(order.totalAmount)}</strong>
                        </div>
                      </div>

                      <ul className="order-items">
                        {order.items.map((item) => (
                          <li key={`${order.orderId}-${item.menuItemId}`}>
                            <span>
                              {item.quantity} x {item.name}
                            </span>
                            <strong>{formatCurrency(item.total)}</strong>
                          </li>
                        ))}
                      </ul>
                    </article>
                  ))
                )}
              </div>
            </article>

            <article className="panel shell-card">
              <div className="card-heading">
                <div>
                  <p className="eyebrow">Extras</p>
                  <h2>Branches and offers</h2>
                </div>
              </div>

              <div className="side-stack">
                <div className="info-grid">
                  {portal?.branches.map((branch) => (
                    <article className="info-card" key={branch.branchId}>
                      <strong>{branch.location}</strong>
                      <p>{branch.posConfig}</p>
                      <span>{branch.inventoryCount} inventory records</span>
                    </article>
                  ))}
                </div>

                <div className="promo-grid">
                  {portal?.promotions.length ? (
                    portal.promotions.slice(0, 3).map((promotion) => (
                      <article className="promo-card" key={promotion.promoId}>
                        <strong>{promotion.promoId}</strong>
                        <p>
                          {promotion.discountType} discount until{" "}
                          {formatDate(promotion.validUntil)}
                        </p>
                        <span>{promotion.discountValue}</span>
                      </article>
                    ))
                  ) : (
                    <div className="empty-state compact">No active offers.</div>
                  )}
                </div>
              </div>
            </article>
          </section>
        </main>
      )}
    </div>
  );
}
