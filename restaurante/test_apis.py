import requests

BASE_URL = "http://127.0.0.1:8000/api"

# Probar GET
response = requests.get(f"{BASE_URL}/empleados/")
print("Empleados:", response.json())

# Probar POST (registrar entrada)
response = requests.post(f"{BASE_URL}/empleados/1/entrada/")
print("Entrada:", response.json())