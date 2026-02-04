import requests
import base64

# ==== CONFIGURACIÓN ====
client_id = "appproductsearch2025-bbc7gpw1"
client_secret = "ow-G_sFu8xnSMXkOX5lZbXDbytOj_5_btyKCYw4D"
scope = "product.compact"

# Puedes cambiar esto por el ZIP que quieras explorar
zip_code = "40229"  # Louisville, KY por ejemplo

# ==== OBTENER TOKEN ====
def get_access_token():
    url = "https://api.kroger.com/v1/connect/oauth2/token"
    auth = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()

    response = requests.post(
        url,
        headers={
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/x-www-form-urlencoded"
        },
        data={
            "grant_type": "client_credentials",
            "scope": scope
        }
    )

    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print("❌ Error al obtener token:", response.json())
        return None

# ==== OBTENER LOCALES POR ZIP ====
def get_locations(token, zip_code):
    url = f"https://api.kroger.com/v1/locations?filter.zipCode.near={zip_code}&filter.limit=10"
    response = requests.get(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }
    )

    if response.status_code == 200:
        data = response.json().get("data", [])
        if not data:
            print("⚠️ No se encontraron tiendas en ese ZIP.")
        else:
            print("🏬 Tiendas encontradas:")
            for store in data:
                address = store.get("address", {})
                print(f"- ID: {store.get('locationId')}")
                print(f"  Nombre: {store.get('name')}")
                print(f"  Dirección: {address.get('addressLine1')}, {address.get('city')}, {address.get('state')} {address.get('zipCode')}")
                print()
    else:
        print("❌ Error al consultar tiendas:", response.json())

# ==== FLUJO PRINCIPAL ====
if __name__ == "__main__":
    token = get_access_token()
    if token:
        get_locations(token, zip_code)
