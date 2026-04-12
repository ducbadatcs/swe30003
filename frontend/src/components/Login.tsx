import Button from "@mui/material/Button";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import Box from "@mui/material/Box";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import axios from "axios";
import { type FormEvent, useState } from "react";

export function CustomerLoginForm() {
  const [username, setUsername] = useState<string>("");
  const [password, setPassword] = useState<string>("");

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (localStorage.getItem("role")) {
      console.log(localStorage.getItem("role"));
      alert("Already logged in, please logged out first!");
      return;
    }
    const form = new FormData();
    form.append("username", username);
    form.append("password", password);
    axios
      .post("http://localhost:8000/customer/token", form)
      .then((response) => {
        console.log(response);
        return response.data;
      })
      .then((data) => {
        const access_token: string = data.access_token;
        localStorage.setItem("access_token", access_token);
        localStorage.setItem("username", username);
        localStorage.setItem("role", "customer");
        alert("Login Success!");
        window.dispatchEvent(new Event("auth-changed"));
        window.location.href = "/";
      })
      .catch((error) => {
        console.error(error);
        alert("Error: Invalid customer username or password");
      });
  };
  return (
    <Paper sx={{ p: 3 }}>
      <Stack spacing={2} component="form" onSubmit={handleSubmit}>
        <Typography variant="h5">Customer Login</Typography>
        <TextField
          label="Username"
          name="username"
          id="customer-login-form-username"
          onChange={(e) => setUsername(e.target.value)}
          fullWidth
        />
        <TextField
          label="Password"
          name="password"
          type="password"
          id="customer-login-form-password"
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

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (password != repeatPassword) {
      alert("Passwords don't match!");
      return;
    }
    // console.log(username);
    // console.log(password);
    const formData = new FormData();
    formData.append("username", username);
    formData.append("password", password);
    axios
      .post("http://localhost:8000/customer/register-customer", formData)
      .then((response) => {
        console.log(response);
        alert("Registered successfully! Please log in.");
      })
      .catch((error) => {
        console.error(error);
        alert("Registered unsuccessfully; see server logs");
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
          required
          onChange={(e) => setUsername(e.target.value)}
          fullWidth
        />
        <TextField
          label="Password"
          name="password"
          type="password"
          id="register-form-password"
          required
          onChange={(e) => setPassword(e.target.value)}
          fullWidth
        />
        <TextField
          label="Repeat Password"
          name="repeat-password"
          type="password"
          id="register-form-repeat-password"
          required
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

export function StaffLoginForm() {
  const [username, setUsername] = useState<string>("");
  const [password, setPassword] = useState<string>("");

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const formData = new FormData();
    formData.append("username", username);
    formData.append("password", password);
    axios
      .post("http://localhost:8000/staffs/token", formData)
      .then((response) => {
        console.log(response);
        return response.data;
      })
      .then((data) => {
        const access_token: string = data.access_token;
        localStorage.setItem("access_token", access_token);
        localStorage.setItem("username", username);
        localStorage.setItem("role", "staff");
        alert("Login Success!");
        window.dispatchEvent(new Event("auth-changed"));
        window.location.href = "/";
      })
      .catch((error) => {
        console.error(error);
      });
  };

  return (
    <Paper sx={{ p: 3 }}>
      <Stack spacing={2} component="form" onSubmit={handleSubmit}>
        <Typography variant="h5">Staff Login</Typography>
        <TextField
          label="Username"
          name="username"
          id="staff-login-form-username"
          required
          onChange={(e) => setUsername(e.target.value)}
          fullWidth
        />
        <TextField
          label="Password"
          name="password"
          type="password"
          id="staff-login-form-password"
          required
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
          <StaffLoginForm />
        </Stack>
      </Paper>
      <Stack spacing={3}>
        <CustomerLoginForm />
        <RegisterForm />
      </Stack>
    </Box>
  );
}
