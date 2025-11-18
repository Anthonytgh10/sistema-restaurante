import { useEffect, useState } from "react";
import  api  from "../services/api";

export default function Productos() {
  const [productos, setProductos] = useState([]);
  const [nuevo, setNuevo] = useState({ nombre: "", precio: "" });

  const cargarProductos = async () => {
    const data = await api.get("/api/productos/");
    setProductos(data);
  };

  const crearProducto = async () => {
    await api.post("/api/productos/", nuevo);
    setNuevo({ nombre: "", precio: "" });
    cargarProductos();
  };

  const eliminarProducto = async (id) => {
    await api.delete(`/api/productos/${id}/`);
    cargarProductos();
  };

  useEffect(() => {
    cargarProductos();
  }, []);

  return (
    <div style={{ padding: 20 }}>
      <h1>Productos</h1>

      <h3>Crear producto</h3>
      <input
        placeholder="Nombre"
        value={nuevo.nombre}
        onChange={(e) => setNuevo({ ...nuevo, nombre: e.target.value })}
      />
      <input
        placeholder="Precio"
        value={nuevo.precio}
        onChange={(e) => setNuevo({ ...nuevo, precio: e.target.value })}
      />
      <button onClick={crearProducto}>Guardar</button>

      <h3>Lista de productos</h3>
      <ul>
        {productos.map((p) => (
          <li key={p.id}>
            {p.nombre} - ${p.precio}
            <button onClick={() => eliminarProducto(p.id)}>
              Eliminar
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
