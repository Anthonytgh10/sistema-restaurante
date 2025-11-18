import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Productos from "./pages/Productos";
import Mesas from "./pages/Mesas";
import Pedidos from "./pages/Pedidos";
import Facturacion from "./pages/Facturacion";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/productos" element={<Productos />} />
        <Route path="/mesas" element={<Mesas />} />
        <Route path="/pedidos" element={<Pedidos />} />
        <Route path="/facturacion" element={<Facturacion />} />
      </Routes>
    </Router>
  );
}

export default App;
