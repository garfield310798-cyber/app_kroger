import os
import base64
import time
import json
import requests
from typing import Any, Dict, Optional

from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# ==== KROGER CONFIG (ENV VARS) ====
CLIENT_ID     = os.getenv("KROGER_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("KROGER_CLIENT_SECRET", "")
SCOPE         = "product.compact"
TOKEN_URL     = "https://api.kroger.com/v1/connect/oauth2/token"
LOCATIONS_URL = "https://api.kroger.com/v1/locations?filter.zipCode.near={zip}&filter.limit=10"

# ==== PROJECTS CONFIG ====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECTS_DIR = os.getenv("PROJECTS_DIR", os.path.join(BASE_DIR, "projects"))

_token_cache = {"value": None, "exp": 0}
_projects_cache: Dict[str, Dict[str, Any]] = {}

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# -------------------------
# Kroger token
# -------------------------
def get_access_token() -> str:
    if not CLIENT_ID or not CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="Missing KROGER_CLIENT_ID / KROGER_CLIENT_SECRET")

    now = int(time.time())
    if _token_cache["value"] and now < _token_cache["exp"]:
        return _token_cache["value"]

    auth = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    r = requests.post(
        TOKEN_URL,
        headers={
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/x-www-form-urlencoded"
        },
        data={"grant_type": "client_credentials", "scope": SCOPE},
        timeout=20
    )
    if r.status_code != 200:
        raise HTTPException(status_code=502, detail=f"Token error: {r.status_code} {r.text}")

    data = r.json()
    token = data.get("access_token")
    expires_in = int(data.get("expires_in", 1800))
    if not token:
        raise HTTPException(status_code=502, detail="No access_token in response")

    _token_cache["value"] = token
    _token_cache["exp"] = now + max(60, expires_in - 60)
    return token


# -------------------------
# Projects helpers
# -------------------------
def _safe_project_id(name: str) -> str:
    base = os.path.basename(name)
    if base.lower().endswith(".json"):
        base = base[:-5]
    return base

def list_projects() -> list:
    if not os.path.isdir(PROJECTS_DIR):
        return []
    files = []
    for fn in os.listdir(PROJECTS_DIR):
        if fn.lower().endswith(".json"):
            pid = _safe_project_id(fn)
            files.append({"id": pid, "filename": fn})
    files.sort(key=lambda x: x["id"].lower())
    return files

def load_project(project_id: str) -> Dict[str, Any]:
    projects = list_projects()
    match = next((p for p in projects if p["id"] == project_id), None)
    if not match:
        raise HTTPException(status_code=404, detail="Project not found")

    path = os.path.join(PROJECTS_DIR, match["filename"])
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="Project file missing")

    mtime = os.path.getmtime(path)
    cached = _projects_cache.get(project_id)
    if cached and cached.get("mtime") == mtime:
        return cached["data"]

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Invalid JSON in project: {e}")

    _projects_cache[project_id] = {"mtime": mtime, "data": data}
    return data

def find_upc_in_project(project_data: Dict[str, Any], upc: str) -> Optional[Dict[str, Any]]:
    for shelf_name, items in project_data.items():
        if not isinstance(items, list):
            continue
        for it in items:
            if not isinstance(it, dict):
                continue
            if str(it.get("UPC", "")).strip() == upc:
                bay = it.get("Bay", "N/D")
                fixture = it.get("Fixture", "N/D")
                pos = it.get("Pos", "N/D")
                desc = it.get("Product Description", it.get("Description", "—"))
                location_str = f"{shelf_name} | Bay {bay} | Fixture {fixture} | Pos {pos}"
                return {"upc": upc, "description": desc, "location": location_str, "raw": it, "shelf": shelf_name}
    return None


# -------------------------
# Routes
# -------------------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# ---- Kroger endpoints ----
@app.get("/api/stores")
def api_stores(zip: str = Query(..., min_length=5, max_length=10)):
    token = get_access_token()
    url = LOCATIONS_URL.format(zip=zip)
    r = requests.get(url, headers={"Authorization": f"Bearer {token}", "Accept": "application/json"}, timeout=20)
    if r.status_code != 200:
        raise HTTPException(status_code=502, detail=f"Stores error: {r.status_code} {r.text}")

    stores = r.json().get("data", [])
    out = []
    for s in stores:
        addr = s.get("address", {})
        out.append({
            "locationId": s.get("locationId"),
            "addressLine1": addr.get("addressLine1"),
            "city": addr.get("city"),
            "state": addr.get("state"),
            "zipCode": addr.get("zipCode"),
        })
    return {"data": out}


def _best_size_url(sizes: list) -> Optional[str]:
    """De una lista de sizes, devuelve la URL del tamaño más grande."""
    if not sizes:
        return None

    order = {"xlarge": 5, "large": 4, "medium": 3, "small": 2, "thumbnail": 1}

    def score(s: dict) -> int:
        sz = str(s.get("size", "")).lower()
        if sz in order:
            return order[sz]
        w = s.get("width") or 0
        h = s.get("height") or 0
        try:
            return int(w) + int(h)
        except Exception:
            return 0

    best = max(sizes, key=score)
    return best.get("url")


@app.get("/api/product")
def api_product(upc: str = Query(..., min_length=6), store: str = Query(..., min_length=3)):
    if not upc.isdigit():
        raise HTTPException(status_code=400, detail="UPC must be digits")

    token = get_access_token()
    url = (
        "https://api.kroger.com/v1/products"
        f"?filter.productId={upc}"
        f"&filter.locationId={store}"
    )
    r = requests.get(url, headers={"Authorization": f"Bearer {token}", "Accept": "application/json"}, timeout=20)
    if r.status_code != 200:
        raise HTTPException(status_code=502, detail=f"Product error: {r.status_code} {r.text}")

    data = r.json().get("data", [])
    if not data:
        return {"found": False}

    prod = data[0]
    name = prod.get("description", "–")

    # Ubicación: Aisle, Bay, Shelf, Posición
    aisle_info = prod.get("aisleLocations", [])
    if aisle_info:
        a0 = aisle_info[0]
        aisle = a0.get("description", "No disponible")
        bay = a0.get("bayNumber", "N/D")
        shelf = a0.get("shelfNumber", "N/D")
        position = a0.get("shelfPositionInBay", "N/D")
        location = f"Aisle {aisle}, Bay {bay}, Shelf {shelf}, Posición {position}"
    else:
        location = "No disponible"

    # Imágenes: solo diferentes (por imagen), y usar el tamaño más grande de cada una
    image_urls = []
    images = prod.get("images") or []
    for img in images:
        sizes = img.get("sizes") or []
        best_url = _best_size_url(sizes)
        if best_url and best_url not in image_urls:
            image_urls.append(best_url)

    return {
        "found": True,
        "name": name,
        "upc": upc,
        "store": store,
        "location": location,
        "image_urls": image_urls
    }


# ---- Projects endpoints ----
@app.get("/api/projects")
def api_projects():
    return {"data": list_projects()}

@app.get("/api/project")
def api_project(project: str = Query(..., min_length=1)):
    data = load_project(project)
    return {"project": project, "data": data}

@app.get("/api/project_lookup")
def api_project_lookup(project: str = Query(..., min_length=1), upc: str = Query(..., min_length=6)):
    upc = upc.strip()
    if not upc.isdigit():
        raise HTTPException(status_code=400, detail="UPC must be digits")

    pdata = load_project(project)
    hit = find_upc_in_project(pdata, upc)
    if not hit:
        return {"found": False, "project": project, "upc": upc}

    return {
        "found": True,
        "project": project,
        "upc": upc,
        "description": hit["description"],
        "location": hit["location"],
        "raw": hit["raw"],
        "shelf": hit["shelf"],
    }
