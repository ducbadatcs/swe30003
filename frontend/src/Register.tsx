import { useState } from "react";
import axios from "axios";

export default function Register() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const registerFormData = new FormData();

  return (
    // Use vh-100 for full screen height and d-flex for centering
    <div className="vh-100 d-flex justify-content-center align-items-center">
      <form
        onSubmit={(event) => {
          event.preventDefault();

          // add stuff to formData so that axios can send it to backend
          registerFormData.append("username", username);
          registerFormData.append("password", password);
          axios({
            method: "post",
            url: "http://localhost:8000/register",
            data: registerFormData,
            headers: { "Content-Type": "multipart/form-data" },
          })
            .then((response) => {
              console.log(response);
              alert("Registered successfully!");
            })
            .catch((error) => {
              console.error(error);
              alert("Registered unsuccessfully!");
            });
        }}
        method="post"
        className="card p-4 shadow-sm" // Optional: adds a card look
      >
        <div>
          <h2>Register</h2>
          <label htmlFor="username" className="form-label">
            Username
          </label>
          <input
            required
            type="text"
            name="username"
            id="username"
            className="form-control"
            onChange={(e) => setUsername(e.target.value)}
          />
          <br />
          <label htmlFor="password" className="form-label">
            Password
          </label>
          <input
            required
            type="password"
            name="password"
            id="password"
            className="form-control"
            onChange={(e) => setPassword(e.target.value)}
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
