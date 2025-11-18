import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Login.css";
import { login }  from "../services/api";


export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  async function handleSubmit(e) {
  e.preventDefault();
  setError("");

  console.log("Enviando datos:", username, password);

  try {
    const data = await login(username, password);

    console.log("Respuesta backend:", data);

    localStorage.setItem("access", data.access);
    localStorage.setItem("refresh", data.refresh);

    navigate("/dashboard");
     console.log("Intentando iniciar sesión...");
  } catch (err) {
    console.error("ERROR:", err);
    setError("Usuario o contraseña incorrectos");
  }
}

  return (
    <div style={styles.container}>
      <form onSubmit={handleSubmit} style={styles.form}>
        <h2 style={styles.title}>Iniciar Sesión</h2>

        <input
          type="text"
          placeholder="Usuario"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          style={styles.input}
          required
        />

        <input
          type="password"
          placeholder="Contraseña"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          style={styles.input}
          required
        />

        {error && <p style={styles.error}>{error}</p>}

        <button type="submit" style={styles.button}>Entrar</button>
      </form>
    </div>
  );
}

const styles = {
  container: {
    height: "100vh",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    background: "#f5f5f5",
  },
  form: {
    width: "320px",
    display: "flex",
    flexDirection: "column",
    padding: "30px",
    borderRadius: "8px",
    background: "white",
    boxShadow: "0 0 10px rgba(0,0,0,0.1)",
  },
  title: {
    textAlign: "center",
    marginBottom: "20px",
  },
  input: {
    padding: "10px",
    marginBottom: "15px",
    fontSize: "16px",
    borderRadius: "4px",
    border: "1px solid #ccc",
  },
  button: {
    padding: "10px",
    fontSize: "16px",
    borderRadius: "4px",
    border: "none",
    background: "#007bff",
    color: "white",
    cursor: "pointer",
  },
  error: {
    color: "red",
    marginBottom: "10px",
    textAlign: "center",
  },
};