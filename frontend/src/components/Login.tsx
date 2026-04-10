import Button from "@mui/material/Button";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import Box from "@mui/material/Box";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import axios from "axios";
import { useState, type FormEvent } from "react";

export function LoginForm() {
  const [username, setUsername] = useState<string>("");
  const [password, setPassword] = useState<string>("");

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const form = new FormData();
    form.append("username", username);
    form.append("password", password);
    axios
      .post("http://localhost:8000/customer/token", form)
      .then((response) => {
        console.log(response);
      })
      .catch((error) => {
        console.error(error);
        alert("Error: Invalid customer username or password");
      });
  };
  return (
    <Paper sx={{ p: 3 }}>
      <Stack spacing={2} component="form" onSubmit={handleSubmit}>
        <Typography variant="h5">Login</Typography>
        <TextField
          label="Username"
          name="username"
          id="login-form-username"
          onChange={(e) => setUsername(e.target.value)}
          fullWidth
        />
        <TextField
          label="Password"
          name="password"
          type="password"
          id="login-form-password"
          onChange={(e) => setPassword(e.target.value)}
          fullWidth
        />
        <Button type="submit" variant="contained">
          Submit
        </Button>
      </Stack>
    </Paper>
  );
}

export function RegisterForm() {
  const [username, setUsername] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [repeatPassword, setRepeatPassword] = useState<string>("");

  const handleSubmit = (event) => {
    event.preventDefault();
    if (password != repeatPassword) {
      alert("Passwords don't match!");
      return;
    }
    console.log(username);
    console.log(password);
    const formData = new FormData();
    formData.append("username", username);
    formData.append("password", password);
    axios
      .post("http://localhost:8000/customer/register-customer", formData)
      .then((response) => {
        console.log(response);
      })
      .catch((error) => {
        console.error(error);
      });
  };

  return (
    <Paper sx={{ p: 3 }}>
      <Stack spacing={2} component="form" onSubmit={handleSubmit}>
        <Typography variant="h5">Register</Typography>
        <TextField
          label="Username"
          name="username"
          id="register-form-username"
          onChange={(e) => setUsername(e.target.value)}
          fullWidth
        />
        <TextField
          label="Password"
          name="password"
          type="password"
          id="register-form-password"
          onChange={(e) => setPassword(e.target.value)}
          fullWidth
        />
        <TextField
          label="Repeat Password"
          name="repeat-password"
          type="password"
          id="register-form-repeat-password"
          onChange={(e) => {
            setRepeatPassword(e.target.value);
          }}
          fullWidth
        />
        <Button type="submit" variant="contained">
          Submit
        </Button>
      </Stack>
    </Paper>
  );
}

export default function Login() {
  return (
    <Box
      sx={{
        display: "grid",
        gap: 3,
        gridTemplateColumns: { xs: "1fr", md: "1fr 1fr" },
      }}
    >
      <Paper sx={{ p: 3 }}>
        <Stack spacing={2}>
          <Typography variant="h4">Account</Typography>
          <Typography color="text.secondary">
            Login if you already have an account, or register a new one.
          </Typography>
        </Stack>
      </Paper>
      <Stack spacing={3}>
        <LoginForm />
        <RegisterForm />
      </Stack>
    </Box>
  );
}
