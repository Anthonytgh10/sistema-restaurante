import { useEffect, useState } from "react";
import  api  from "../services/api";

export default function Mesas() {
  const [mesas, setMesas] = useState([]);

  const cargar = async () => {
    const data = await api.get("/api/mesas/");
    setMesas(data);
  };

  const ocuparMesa = async (id) => {
    await api.post(`/api/mesas/${id}/ocupar/`);
    cargar();
  };

  const liberarMesa = async (id) => {
    await api.post(`/api/mesas/${id}/liberar/`);
    cargar();
  };

  useEffect(() => {
    cargar();
  }, []);

  return (
    <div style={{ padding: 20 }}>
      <h1>Mesas</h1>
      {mesas.map((m) => (
        <div key={m.id}>
          Mesa {m.id} - Estado: {m.estado}
          {m.estado === "libre" ? (
            <button onClick={() => ocuparMesa(m.id)}>Ocupar</button>
          ) : (
            <button onClick={() => liberarMesa(m.id)}>Liberar</button>
          )}
        </div>
      ))}
    </div>
  );
}
