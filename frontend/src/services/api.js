const API_URL = "http://127.0.0.1:8000/api";

async function request(method, route, body = null) {
  const options = { method };

  if (body) {
    options.headers = { "Content-Type": "application/json" };
    options.body = JSON.stringify(body);
  }

  const res = await fetch(API_URL + route, options);
  return res.json();
}

export const api = {
  get: (route) => request("GET", route),
  post: (route, body) => request("POST", route, body),
  put: (route, body) => request("PUT", route, body),
  delete: (route) => request("DELETE", route),
};

// LOGIN
export async function login(username, password) {
  console.log("Enviando petición al backend...");
  try {
    const response = await fetch(`${API_URL}/login/`, {
      method: "POST",
      headers: { "Content-Type": "application/json",
        "Accept": "application/json",
       },
      body: JSON.stringify({ username, password }),
    });

    // Parseamos la respuesta JSON
    const data = await response.json();

    // Verificamos si recibimos los tokens
   if (response.ok && data.access && data.refresh) {
  return data;
}

throw new Error(data.error || "Usuario o contraseña incorrectos");

  } catch (err) {
    throw new Error(err.message || "Error al conectarse al servidor");
  }
}

// GET ejemplo con token
export async function getProductos() {
  const accessToken = localStorage.getItem("access");

  const response = await fetch(`${API_URL}/productos/`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      "Authorization": "Bearer " + accessToken,
    },
  });

  if (!response.ok) {
    throw new Error("No se pudo obtener los productos");
  }

  return response.json();
}

// REFRESH token (opcional)
export async function refreshToken() {
  const refreshToken = localStorage.getItem("refresh");

  const response = await fetch(`${API_URL}/token/refresh/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh: refreshToken }),
  });

  const data = await response.json();

  if (response.ok && data.access) {
    localStorage.setItem("access", data.access);
    return data.access;
  } else {
    throw new Error("No se pudo refrescar el token");
  }
}

// PROFILE
export async function getProfile() {
  const token = localStorage.getItem("access");

  const res = await fetch(`${API_URL}/profile/`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (res.status === 401) throw new Error("Token expirado");

  return res.json();
}

export default api;

