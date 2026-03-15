export default function Login() {
  return (
    // Use vh-100 for full screen height and d-flex for centering
    <div className="vh-100 d-flex justify-content-center align-items-center">
      <form
        action=""
        method="post"
        className="card p-4 shadow-sm" // Optional: adds a card look
      >
        <div>
          <label htmlFor="username" className="form-label">
            Username
          </label>
          <input
            type="text"
            name="username"
            id="username"
            className="form-control"
          />
          <br />
          <label htmlFor="password" className="form-label">
            Password
          </label>
          <input
            type="password"
            name="password"
            id="password"
            className="form-control"
          />
          <br />
          <input
            type="submit"
            value="Submit!"
            className="btn btn-primary w-100"
          />
        </div>
      </form>
    </div>
  );
}
