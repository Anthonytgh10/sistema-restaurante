import { logout } from "../logout";

export default function Dashboard() {
  return (
    <div style={{ padding: 20 }}>
      <h1>Bienvenido al Panel</h1>
      <button onClick={logout}>Cerrar sesión</button>
    </div>
  );
}
