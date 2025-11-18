// Project scaffold for "Sistema Restaurante" frontend (React + Vite + Tailwind)
// -------------------------------------------------------------
// Instructions: create a new folder `frontend`, paste the files below into the same structure,
// then run `npm install` and `npm run dev`.
// This single-file document contains multiple files separated by headers like: === FILE: path ===
// Copy each section into the corresponding file in your project.

=== FILE: package.json ===
{
  "name": "sistema-restaurante-frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "axios": "^1.4.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.14.1",
    "lucide-react": "^0.268.0",
    "@radix-ui/react-dialog": "^2.1.3"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.0.0",
    "autoprefixer": "^10.4.14",
    "postcss": "^8.4.24",
    "tailwindcss": "^4.2.1",
    "vite": "^5.0.0"
  }
}

=== FILE: vite.config.js ===
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      }
    }
  }
})

=== FILE: tailwind.config.cjs ===
module.exports = {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {}
  },
  plugins: []
}

=== FILE: postcss.config.cjs ===
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {}
  }
}

=== FILE: index.html ===
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Sistema Restaurante - Frontend</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>

=== FILE: src/main.jsx ===
import React from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import './index.css'

createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>
)

=== FILE: src/index.css ===
@tailwind base;
@tailwind components;
@tailwind utilities;

html, body, #root {
  height: 100%;
}

=== FILE: src/App.jsx ===
import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Mesas from './pages/Mesas'
import Empleados from './pages/Empleados'
import Ordenes from './pages/Ordenes'
import Layout from './components/Layout'

export default function App() {
  const isLogged = !!localStorage.getItem('token')

  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/" element={isLogged ? <Layout /> : <Navigate to="/login" />}>
        <Route index element={<Dashboard/>} />
        <Route path="mesas" element={<Mesas/>} />
        <Route path="ordenes" element={<Ordenes/>} />
        <Route path="empleados" element={<Empleados/>} />
      </Route>
    </Routes>
  )
}

=== FILE: src/components/Layout.jsx ===
import React from 'react'
import { Outlet, Link, useNavigate } from 'react-router-dom'
import { Home, Table, Users, LogOut } from 'lucide-react'

export default function Layout(){
  const navigate = useNavigate()
  const logout = () => {
    localStorage.removeItem('token')
    navigate('/login')
  }

  return (
    <div className="min-h-screen flex bg-gray-100">
      <aside className="w-64 bg-white shadow-md">
        <div className="p-4 text-xl font-bold">Restaurante</div>
        <nav className="p-4 space-y-2">
          <Link to="/" className="flex items-center gap-2 p-2 rounded hover:bg-gray-100"><Home size={18}/> Dashboard</Link>
          <Link to="/mesas" className="flex items-center gap-2 p-2 rounded hover:bg-gray-100"><Table size={18}/> Mesas</Link>
          <Link to="/ordenes" className="flex items-center gap-2 p-2 rounded hover:bg-gray-100"><Users size={18}/> Ordenes</Link>
          <Link to="/empleados" className="flex items-center gap-2 p-2 rounded hover:bg-gray-100"><Users size={18}/> Empleados</Link>
        </nav>
        <div className="absolute bottom-4 p-4 w-64">
          <button onClick={logout} className="flex items-center gap-2 text-sm text-red-600">
            <LogOut size={16}/> Cerrar sesión
          </button>
        </div>
      </aside>

      <main className="flex-1 p-6">
        <Outlet />
      </main>
    </div>
  )
}

=== FILE: src/components/MesaCard.jsx ===
import React from 'react'

export default function MesaCard({mesa}){
  const estadoColor = mesa.estado === 'ocupada' ? 'bg-red-200' : mesa.estado === 'reservada' ? 'bg-yellow-200' : 'bg-green-200'
  return (
    <div className={`p-4 rounded shadow ${estadoColor}`}>
      <div className="text-lg font-semibold">Mesa {mesa.numero}</div>
      <div>Capacidad: {mesa.capacidad}</div>
      <div>Estado: {mesa.estado}</div>
    </div>
  )
}

=== FILE: src/services/api.js ===
import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' }
})

// Add token automatically
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export const authLogin = (payload) => api.post('/login/', payload)
export const getMesas = () => api.get('/mesas/')
export const getEmpleados = () => api.get('/empleados/')
export const getOrdenes = () => api.get('/ordenes/')

export default api

=== FILE: src/pages/Login.jsx ===
import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { authLogin } from '../services/api'

export default function Login(){
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)
  const nav = useNavigate()

  const submit = async (e)=>{
    e.preventDefault()
    try{
      const res = await authLogin({username, password})
      // assuming backend returns { token: '...' }
      localStorage.setItem('token', res.data.token)
      nav('/')
    }catch(err){
      setError('Credenciales inválidas')
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-gray-50 to-gray-100">
      <form onSubmit={submit} className="w-full max-w-md p-8 bg-white rounded shadow">
        <h1 className="text-2xl font-bold mb-6">Iniciar sesión</h1>
        {error && <div className="text-red-600 mb-2">{error}</div>}
        <label className="block mb-2">Usuario
          <input value={username} onChange={e=>setUsername(e.target.value)} className="w-full p-2 border rounded mt-1" />
        </label>
        <label className="block mb-4">Contraseña
          <input type="password" value={password} onChange={e=>setPassword(e.target.value)} className="w-full p-2 border rounded mt-1" />
        </label>
        <button className="w-full p-2 bg-blue-600 text-white rounded">Entrar</button>
      </form>
    </div>
  )
}

=== FILE: src/pages/Dashboard.jsx ===
import React from 'react'

export default function Dashboard(){
  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Dashboard</h1>
      <div className="grid grid-cols-3 gap-4">
        <div className="p-4 bg-white rounded shadow">Ventas del día</div>
        <div className="p-4 bg-white rounded shadow">Mesas ocupadas</div>
        <div className="p-4 bg-white rounded shadow">Mesas libres</div>
      </div>
    </div>
  )
}

=== FILE: src/pages/Mesas.jsx ===
import React, { useEffect, useState } from 'react'
import { getMesas } from '../services/api'
import MesaCard from '../components/MesaCard'

export default function Mesas(){
  const [mesas, setMesas] = useState([])

  useEffect(()=>{
    getMesas().then(res => setMesas(res.data)).catch(()=>{})
  },[])

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Mesas</h1>
      <div className="grid grid-cols-3 gap-4">
        {mesas.map(m => <MesaCard key={m.id} mesa={m} />)}
      </div>
    </div>
  )
}

=== FILE: src/pages/Empleados.jsx ===
import React, { useEffect, useState } from 'react'
import { getEmpleados } from '../services/api'

export default function Empleados(){
  const [empleados, setEmpleados] = useState([])

  useEffect(()=>{
    getEmpleados().then(res => setEmpleados(res.data)).catch(()=>{})
  },[])

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Empleados</h1>
      <div className="grid grid-cols-3 gap-4">
        {empleados.map(emp => (
          <div key={emp.id} className="p-4 bg-white rounded shadow">
            <div className="font-semibold">{emp.nombre}</div>
            <div className="text-sm">Cargo: {emp.cargo}</div>
          </div>
        ))}
      </div>
    </div>
  )
}

=== FILE: src/pages/Ordenes.jsx ===
import React, { useEffect, useState } from 'react'
import { getOrdenes } from '../services/api'

export default function Ordenes(){
  const [ordenes, setOrdenes] = useState([])

  useEffect(()=>{
    getOrdenes().then(res => setOrdenes(res.data)).catch(()=>{})
  },[])

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Órdenes</h1>
      <div className="space-y-3">
        {ordenes.map(o => (
          <div key={o.id} className="p-3 bg-white rounded shadow">
            <div className="font-semibold">Orden #{o.id} - Mesa {o.mesa}</div>
            <div className="text-sm">Estado: {o.estado}</div>
          </div>
        ))}
      </div>
    </div>
  )
}

=== FILE: README.md ===
# Frontend - Sistema Restaurante

Este proyecto es un frontend en React (Vite + Tailwind) diseñado para consumir la API Django del repositorio principal.

## Pasos para iniciar
1. Instalar dependencias: `npm install`
2. Iniciar servidor dev: `npm run dev` (estará en http://localhost:5173)
3. El proxy en vite.config.js reenvía `/api` a `http://localhost:8000`.

## Notas
- Ajusta los endpoints en `src/services/api.js` según tu backend (nombres y rutas).
- El login asume que el endpoint `/api/login/` devuelve `{ token: '...' }`.

---

// FIN DEL ARCHIVO
