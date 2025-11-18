import { logout } from "../logout";
import { useNavigate } from "react-router-dom";
import { useState } from "react";

export default function Dashboard() {
  const navigate = useNavigate();
  const [hovered, setHovered] = useState(null);

  const handleNav = (ruta) => {
    navigate(ruta);
  };

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>🌙 Panel del Restaurante</h1>
      <p style={styles.subtitle}>Un diseño artístico y elegante</p>

      <div style={styles.cardContainer}>

        {[
          { ruta: "/productos", titulo: "🍽️ Productos", desc: "Gestión del menú" },
          { ruta: "/categorias", titulo: "📂 Categorías", desc: "Organización del menú" },
          { ruta: "/pedidos", titulo: "🧾 Pedidos", desc: "Control y seguimiento" },
          { ruta: "/usuarios", titulo: "👤 Usuarios", desc: "Roles y permisos" },
        ].map((item, index) => (
          <div
            key={index}
            style={{
              ...styles.card,
              transform: hovered === index ? "translateY(-12px) scale(1.05)" : "translateY(0)",
              boxShadow:
                hovered === index
                  ? "0px 15px 40px rgba(0,0,0,0.6)"
                  : "0px 10px 25px rgba(0,0,0,0.45)",
              border: hovered === index ? "1px solid rgba(255,255,255,0.45)" : "1px solid rgba(255,255,255,0.15)",
              backdropFilter: "blur(14px)",
            }}
            onMouseEnter={() => setHovered(index)}
            onMouseLeave={() => setHovered(null)}
            onClick={() => handleNav(item.ruta)}
          >
            <h3 style={styles.cardTitle}>{item.titulo}</h3>
            <p style={styles.cardText}>{item.desc}</p>
          </div>
        ))}

      </div>

      <button style={styles.logout} onClick={logout}>
        Cerrar sesión
      </button>
    </div>
  );
}



const styles = {
  container: {
    textAlign: "center",
    padding: "50px",
    background: "linear-gradient(135deg, #0f0f0f, #1a1a1a 40%, #121212)",
    minHeight: "100vh",
    color: "white",
  },

  title: {
    fontSize: "42px",
    marginBottom: "10px",
    fontWeight: "800",
    letterSpacing: "1px",
    textShadow: "0px 0px 18px rgba(255,255,255,0.3)",
  },

  subtitle: {
    fontSize: "17px",
    marginBottom: "40px",
    opacity: 0.75,
  },

  cardContainer: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))",
    gap: "35px",
    padding: "0 40px",
  },

  card: {
    padding: "25px",
    borderRadius: "18px",
    cursor: "pointer",
    transition: "0.35s ease",
    background: "rgba(255,255,255,0.07)",
    border: "1px solid rgba(255,255,255,0.15)",
    boxShadow: "0px 8px 25px rgba(0,0,0,0.45)",
  },

  cardTitle: {
    fontSize: "22px",
    marginBottom: "10px",
  },

  cardText: {
    fontSize: "15px",
    opacity: 0.8,
  },

  logout: {
    marginTop: "60px",
    padding: "12px 30px",
    background: "linear-gradient(135deg, #ff3d3d, #b80000)",
    color: "white",
    border: "none",
    borderRadius: "12px",
    cursor: "pointer",
    fontSize: "17px",
    fontWeight: "600",
    transition: "0.3s ease",
    boxShadow: "0px 6px 18px rgba(255,0,0,0.5)",
  },
};
