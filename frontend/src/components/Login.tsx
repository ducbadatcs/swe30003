import Button from "@mui/material/Button";
import TextField from "@mui/material/TextField";
import axios from "axios";
import { useState } from "react";

export function LoginForm() {
  const [username, setUsername] = useState<string>("");
  const [password, setPassword] = useState<string>("");

  const handleSubmit = (event: Event) => {
    event.preventDefault();
    const form = new FormData();
    form.append("username", username);
    form.append("password", password);
    axios
      .post("http://localhost:8000/customer/verify-customer", form)
      .then((response) => {
        console.log(response);
      });
  };
  return (
    <form action="">
      <p>Login:</p>
      <TextField
        label="username"
        variant="outlined"
        onChange={(e) => {
          setUsername(e.target.value);
        }}
      ></TextField>
      <TextField
        label="password"
        type="password"
        // value=""
        variant="outlined"
        onChange={(e) => {
          setPassword(e.target.value);
        }}
      ></TextField>
      <Button variant="contained" onClick={handleSubmit}>
        Submit
      </Button>
    </form>
  );
}

export default function Login() {
  return (
    <div>
      <LoginForm></LoginForm>
    </div>
  );
}
