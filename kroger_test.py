import requests
import base64

# === CONFIGURACIÓN ===
client_id = "appproductsearch2025-bbc7gpw1"
client_secret = "ow-G_sFu8xnSMXkOX5lZbXDbytOj_5_btyKCYw4D"
scope = "product.compact"
location_id = "02400366"  # Puedes cambiarlo por uno válido de tu zona
product_id = "0001111012066"  # Ejemplo: UPC de un producto real

# === OBTENER TOKEN ===
token_url = "https://api.kroger.com/v1/connect/oauth2/token"
auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()

token_response = requests.post(
    token_url,
    headers={
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/x-www-form-urlencoded"
    },
    data={
        "grant_type": "client_credentials",
        "scope": scope
    }
)

access_token = token_response.json().get("access_token")
if not access_token:
    print("❌ Error al obtener token:", token_response.json())
    exit()

print("✅ Token obtenido")

# === BUSCAR PRODUCTO ===
product_url = f"https://api.kroger.com/v1/products?filter.productId={product_id}&filter.locationId={location_id}"
product_response = requests.get(
    product_url,
    headers={
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
)

if product_response.status_code == 200:
    data = product_response.json()
    print("Tipo de data['data']:", type(data.get("data")))
    print("Contenido de data['data'][0]:", data.get("data", [])[0])

    
    for item in data.get("data", []):
        if isinstance(item, dict):
            name = item.get("description", "N/A")
            brand = item.get("brand", "N/A")
            upc = item.get("upc", "N/A")

            # === Obtener precio ===
            items = item.get("items", [])
            if items and isinstance(items[0], dict) and "price" in items[0]:
                price = items[0]["price"].get("regular", "N/D")
            else:
                price = "No disponible"

            # === Obtener imagen principal ===
            image_url = "No disponible"
            for image in item.get("images", []):
                if image.get("perspective") == "front" or image.get("featured", False):
                    sizes = image.get("sizes", [])
                    for size in sizes:
                        if size.get("size") == "medium":
                            image_url = size.get("url")
                            break
                    if image_url != "No disponible":
                        break
            
            # === Obtener ubicación en tienda ===
            aisle_info = item.get("aisleLocations", [])
            if aisle_info:
                aisle = aisle_info[0].get("description", "No disponible")
                shelf = aisle_info[0].get("shelfNumber", "N/D")
                bay = aisle_info[0].get("bayNumber", "N/D")
                position = aisle_info[0].get("shelfPositionInBay", "N/D")
                ubicacion = f"{aisle}, Estante {shelf}, Bahía {bay}, Posición {position}"
            else:
                ubicacion = "No disponible"

            # === Mostrar información ===
            print(f"- Nombre: {name}")
            print(f"  Marca: {brand}")
            print(f"  UPC: {upc}")
            print(f"  Precio: {price} USD")
            print(f"  Imagen principal: {image_url}\n")
            print(f"  Ubicación en tienda: {ubicacion}\n")
        else:
            print("⚠️ Elemento inesperado en 'data':", item)

