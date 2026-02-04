#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# app_kroger_v2.py — v2 con búsqueda de producto en Scan Product, mostrar imagen, ubicación y guardado de store

import tkinter as tk
import tkinter.messagebox as messagebox
import requests
import base64
import io
from PIL import Image, ImageTk
import os
import json

# ==== CONFIGURACIÓN KROGER ====
CLIENT_ID     = "appproductsearch2025-bbc7gpw1"
CLIENT_SECRET = "ow-G_sFu8xnSMXkOX5lZbXDbytOj_5_btyKCYw4D"
SCOPE         = "product.compact"
TOKEN_URL     = "https://api.kroger.com/v1/connect/oauth2/token"
LOCATIONS_URL = "https://api.kroger.com/v1/locations?filter.zipCode.near={zip}&filter.limit=10"
PRODUCT_URL = (
    "https://api.kroger.com/v1/products"
    "?filter.productId={product_id}"
    "&filter.locationId={store}"
)
CONFIG_PATH   = os.path.expanduser("~/app_kroger_config")

class Toplevel1:
    def __init__(self, top=None):
        # Ventana principal
        top.geometry("480x800+0+0")
        top.overrideredirect(True)
        top.configure(background="#d9d9d9")
        self.top = top
        self.historial_frames = []
        self.photo = None  # Referencia para imagen en canvas

        # Helper para focus en Entry
        def on_entry_focus(event):
            w = event.widget
            w.focus_force()
            w.icursor(tk.END)

        # === FRAME MENU ===
        self.Fr_Menu = tk.Frame(top, bg="#d9d9d9", bd=2, relief="groove")
        self.Fr_Menu.place(x=3, y=5, width=475, height=45)
        tk.Button(self.Fr_Menu, text="Home", font="-family {Segoe UI} -size 14",
                  command=lambda: self.mostrar_frame(self.Fr_Home)
        ).place(x=2, y=4, width=77, height=36)
        tk.Button(self.Fr_Menu, text="Salir", font="-family {Segoe UI} -size 14",
                  command=top.destroy
        ).place(x=84, y=4, width=77, height=36)
        self.Lb_Status = tk.Label(self.Fr_Menu, text="Home", anchor='w', bg="#d9d9d9",
                                  font="-family {Segoe UI} -size 13")
        self.Lb_Status.place(x=340, y=6, width=122, height=29)

        # === FRAME HOME ===
        self.Fr_Home = tk.Frame(top, bg="#d9d9d9", bd=2, relief="groove")
        tk.Button(self.Fr_Home, text="Load Project", font="-family {Segoe UI} -size 14",
                  command=lambda: self.mostrar_frame(self.Fr_Load_Project)
        ).place(x=20, y=10, width=137, height=126)
        tk.Button(self.Fr_Home, text="Scan Project", font="-family {Segoe UI} -size 14",
                  command=lambda: self.mostrar_frame(self.Fr_Scan_Project)
        ).place(x=171, y=10, width=137, height=126)
        tk.Button(self.Fr_Home, text="Scan Product", font="-family {Segoe UI} -size 14",
                  command=lambda: self.mostrar_frame(self.Fr_Scan_Product)
        ).place(x=320, y=10, width=137, height=126)
        tk.Button(self.Fr_Home, text="Set Store", font="-family {Segoe UI} -size 14",
                  command=lambda: self.mostrar_frame(self.Fr_Set_Store)
        ).place(x=20, y=150, width=137, height=126)

        # === FRAME LOAD_PROJECT ===
        self.Fr_Load_Project = tk.Frame(top, bg="#d9d9d9", bd=2, relief="groove")
        tk.Button(self.Fr_Load_Project, text="Load", font="-family {Segoe UI} -size 14"
        ).place(x=10, y=10, width=77, height=36)
        self.Lst_Load_Value = tk.Listbox(self.Fr_Load_Project, bg="white", font="TkFixedFont",
                                         selectbackground="#d9d9d9")
        self.Lst_Load_Value.place(x=10, y=60, width=454, height=672)

        # === FRAME SCAN_PROJECT ===
        self.Fr_Scan_Project = tk.Frame(top, bg="#d9d9d9", bd=2, relief="groove")
        tk.Label(self.Fr_Scan_Project, text="Info Project:", bg="#d9d9d9",
                 font="-family {Segoe UI} -size 11", anchor='w'
        ).place(x=5, y=5, width=91, height=26)
        self.Txt_Info_Project_Value = tk.Text(self.Fr_Scan_Project, wrap="word", state="disabled")
        self.Txt_Info_Project_Value.place(x=5, y=31, width=440, height=64)
        sb_proj = tk.Scrollbar(self.Fr_Scan_Project, orient='vertical', command=self.Txt_Info_Project_Value.yview)
        sb_proj.place(x=450, y=31, width=15, height=64)
        self.Txt_Info_Project_Value.configure(yscrollcommand=sb_proj.set)
        tk.Label(self.Fr_Scan_Project, text="UPC Product:", bg="#d9d9d9",
                 font="-family {Segoe UI} -size 11", anchor='w'
        ).place(x=5, y=96, width=91, height=26)
        self.Ent_UPC_Product_Value = tk.Entry(self.Fr_Scan_Project,
                                              font="-family {Courier New} -size 12",
                                              insertbackground='black', insertwidth=2)
        self.Ent_UPC_Product_Value.place(x=5, y=120, width=304, height=30)
        self.Ent_UPC_Product_Value.bind('<Button-1>', on_entry_focus)
        tk.Button(self.Fr_Scan_Project, text="X", font="-family {Segoe UI} -size 14",
                  command=self.limpiar_entry
        ).place(x=398, y=97, width=67, height=56)
        tk.Button(self.Fr_Scan_Project, text="Go", font="-family {Segoe UI} -size 14"
        ).place(x=321, y=98, width=67, height=56)
        tk.Label(self.Fr_Scan_Project, text="Info Product:", bg="#d9d9d9",
                 font="-family {Segoe UI} -size 11", anchor='w'
        ).place(x=5, y=163, width=91, height=26)
        self.Txt_Info_Product_Value = tk.Text(self.Fr_Scan_Project, wrap="word", state="disabled")
        self.Txt_Info_Product_Value.place(x=5, y=190, width=440, height=184)
        sb_prod = tk.Scrollbar(self.Fr_Scan_Project, orient='vertical', command=self.Txt_Info_Product_Value.yview)
        sb_prod.place(x=450, y=190, width=15, height=184)
        self.Txt_Info_Product_Value.configure(yscrollcommand=sb_prod.set)

        # === FRAME SCAN_PRODUCT ===
        self.Fr_Scan_Product = tk.Frame(top, bg="#d9d9d9", bd=2, relief="groove")
        self.Lb_UPC_Product_Label = tk.Label(self.Fr_Scan_Product,
            text="UPC Product:", bg="#d9d9d9",font="-family {Segoe UI} -size 11", anchor="w")
        self.Lb_UPC_Product_Label.place(x=5, y=5, width=200, height=26)

        self.Ent_UPC_Product_Value_1 = tk.Entry(self.Fr_Scan_Product,
                                                font="-family {Courier New} -size 12",
                                                insertbackground='black', insertwidth=2)
        self.Ent_UPC_Product_Value_1.place(x=5, y=30, width=304, height=30)
        self.Ent_UPC_Product_Value_1.bind('<Button-1>', on_entry_focus)
        self.upc_var = tk.StringVar()
        self.Ent_UPC_Product_Value_1.configure(textvariable=self.upc_var)
        self.upc_var.trace_add("write", self.on_upc_change)
        self.last_upc = ""
        tk.Button(self.Fr_Scan_Product, text="X", font="-family {Segoe UI} -size 14",
                  command=self.limpiar_entry
        ).place(x=396, y=6, width=67, height=56)
        tk.Button(self.Fr_Scan_Product, text="Go", font="-family {Segoe UI} -size 14",
                  command=self.scan_product
        ).place(x=319, y=6, width=67, height=56)
        tk.Label(self.Fr_Scan_Product, text="Image:", bg="#d9d9d9",
                 font="-family {Segoe UI} -size 11", anchor='w'
        ).place(x=5, y=62, width=51, height=26)
        self.Cnv_Image_Value = tk.Canvas(self.Fr_Scan_Product, bg="#d9d9d9", bd=2, relief="ridge")
        self.Cnv_Image_Value.place(x=5, y=90, width=320, height=240)
        self.Txt_Info_Product_Value_1 = tk.Text(self.Fr_Scan_Product, wrap="word", state="disabled")
        self.Txt_Info_Product_Value_1.place(x=5, y=360, width=440, height=124)
        sb_prod1 = tk.Scrollbar(self.Fr_Scan_Product, orient='vertical', command=self.Txt_Info_Product_Value_1.yview)
        sb_prod1.place(x=450, y=360, width=15, height=124)
        self.Txt_Info_Product_Value_1.configure(yscrollcommand=sb_prod1.set)

        # === FRAME SET_STORE ===
        self.Fr_Set_Store = tk.Frame(top, bg="#d9d9d9", bd=2, relief="groove")
        tk.Label(self.Fr_Set_Store, text="Enter Zip Code:", anchor='w', bg="#d9d9d9",
                 font="-family {Segoe UI} -size 11"
        ).place(x=5, y=5, width=111, height=26)
        self.Ent_Zip_Code_Value = tk.Entry(self.Fr_Set_Store,
                                           font="-family {Courier New} -size 12",
                                           insertbackground='black', insertwidth=2)
        self.Ent_Zip_Code_Value.place(x=8, y=32, width=304, height=30)
        self.Ent_Zip_Code_Value.bind('<Button-1>', on_entry_focus)
        tk.Button(self.Fr_Set_Store, text="X", font="-family {Segoe UI} -size 14",
                  command=self.limpiar_entry
        ).place(x=400, y=10, width=67, height=56)
        tk.Button(self.Fr_Set_Store, text="Go", font="-family {Segoe UI} -size 14",
                  command=self.fetch_and_display_stores
        ).place(x=323, y=10, width=67, height=56)
        tk.Label(self.Fr_Set_Store, text="Stores:", bg="#d9d9d9",
                 font="-family {Segoe UI} -size 11", anchor='w'
        ).place(x=5, y=66, width=51, height=26)
        self.Txt_Stores_Value = tk.Text(self.Fr_Set_Store, wrap="word", state="disabled")
        self.Txt_Stores_Value.place(x=10, y=100, width=440, height=314)
        sb_store = tk.Scrollbar(self.Fr_Set_Store, orient='vertical', command=self.Txt_Stores_Value.yview)
        sb_store.place(x=450, y=100, width=15, height=314)
        self.Txt_Stores_Value.configure(yscrollcommand=sb_store.set)

        # Componentes V1: Set Store final
        self.Lb_Set_Store_Status = tk.Label(self.Fr_Set_Store, text="Set Store:", bg="#d9d9d9",
                                         font="-family {Segoe UI} -size 11", anchor='w')
        self.Lb_Set_Store_Status.place(x=10, y=422, width=200, height=26)
        self.Ent_Set_Store_Value = tk.Entry(self.Fr_Set_Store,
                                            font="-family {Courier New} -size 12", insertbackground='black')
        self.Ent_Set_Store_Value.place(x=11, y=448, width=304, height=30)
        self.Ent_Set_Store_Value.bind('<Button-1>', on_entry_focus)
        tk.Button(self.Fr_Set_Store, text="Save", font="-family {Segoe UI} -size 14",
                  command=self.save_store
        ).place(x=320, y=442, width=147, height=46)

        # === FRAME NUMERIC KEYPAD ===
        self.Fr_Num = tk.Frame(top, bg="#d9d9d9", bd=2, relief="groove")
        for txt, x, y in [("7",10,10),("8",120,10),("9",233,10),
                          ("4",10,90),("5",122,90),("6",234,90),
                          ("1",10,169),("2",122,169),("3",234,169),
                          ("000",345,90),("0",345,169)]:
            tk.Button(self.Fr_Num, text=txt, font="-family {Segoe UI} -size 14",
                      command=lambda v=txt: self.escribir_numero(v)
            ).place(x=x, y=y, width=97, height=66)
        tk.Button(self.Fr_Num, text="<-", font="-family {Segoe UI} -size 14",
                  command=self.borrar_ultimo
        ).place(x=344, y=10, width=97, height=66)

        # Posiciones de frames
        self.frames_positions = {
            self.Fr_Home:         {'x':3,'y':52,'width':475,'height':745},
            self.Fr_Load_Project: {'x':3,'y':52,'width':475,'height':745},
            self.Fr_Scan_Project: {'x':3,'y':52,'width':475,'height':745},
            self.Fr_Scan_Product: {'x':3,'y':52,'width':475,'height':745},
            self.Fr_Set_Store:    {'x':3,'y':52,'width':475,'height':745},
        }

        self.ocultar_contenido()
        self.mostrar_frame(self.Fr_Home)

    def scan_product(self):
        # —————— Limpieza inicial ——————
        # Borramos Canvas e Info Text, y restauramos el label por defecto
        self.Cnv_Image_Value.delete("all")
        self.Txt_Info_Product_Value_1.configure(state="normal")
        self.Txt_Info_Product_Value_1.delete("1.0", "end")
        self.Txt_Info_Product_Value_1.configure(state="disabled")
        self.Lb_UPC_Product_Label.configure(text="UPC Product:")

        # 1) Leer UPC del Entry
        upc = self.Ent_UPC_Product_Value_1.get().strip()
        if not upc.isdigit():
            # Sólo mostrar error en el label, no tocamos el Canvas ni el Text
            self.Lb_UPC_Product_Label.configure(text="UPC inválido.")
            return

        # 2) Leer store_id desde el archivo de configuración
        try:
            with open(CONFIG_PATH, 'r') as f:
                store_id = f.read().strip()
        except FileNotFoundError:
            self.Lb_UPC_Product_Label.configure(text="Selecciona un store primero.")
            return

        if not store_id:
            self.Lb_UPC_Product_Label.configure(text="Selecciona un store primero.")
            return

        # 3) Obtener token
        token = self.get_access_token()
        if not token:
            self.Lb_UPC_Product_Label.configure(text="Error al obtener token.")
            return

        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }

        # 4) Petición al endpoint de products usando productId
        url = (
            "https://api.kroger.com/v1/products"
            "?filter.productId={product_id}"
            "&filter.locationId={store}"
        ).format(product_id=upc, store=store_id)
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            self.Lb_UPC_Product_Label.configure(text=f"Error al buscar producto: {r.status_code}")
            return

        data = r.json().get("data", [])
        if not data:
            self.Lb_UPC_Product_Label.configure(text="Producto no encontrado.")
            return

        prod = data[0]
        name = prod.get("description", "–")

        # 5) Extraer ubicación desde aisleLocations
        aisle_info = prod.get("aisleLocations", [])
        if aisle_info:
            desc     = aisle_info[0].get("description",        "No disponible")
            shelf    = aisle_info[0].get("shelfNumber",        "N/D")
            bay      = aisle_info[0].get("bayNumber",          "N/D")
            position = aisle_info[0].get("shelfPositionInBay", "N/D")
            ubicacion = f"{desc}, Estante {shelf}, Bahía {bay}, Posición {position}"
        else:
            ubicacion = "No disponible"

        # 6) Cargar imagen en el Canvas (importar io, PIL.Image, PIL.ImageTk)
        image_url = (prod.get("images") or [{}])[0].get("sizes", [{}])[0].get("url")
        if image_url:
            try:
                resp_img = requests.get(image_url)
                img_data = resp_img.content
                pil_img = Image.open(io.BytesIO(img_data))
                pil_img = pil_img.resize((320, 240), Image.LANCZOS)
                self.photo = ImageTk.PhotoImage(pil_img)  # mantener referencia
                self.Cnv_Image_Value.delete("all")
                self.Cnv_Image_Value.create_image(0, 0, image=self.photo, anchor='nw')
            except Exception:
                self.Cnv_Image_Value.delete("all")
                self.Cnv_Image_Value.create_text(
                    160, 120,
                    text="Error al cargar imagen",
                    anchor='center'
                )

        # 7) Volcar datos en el Text widget (sin tocar el label)
        info = (
            f"Nombre:    {name}\n"
            f"UPC:       {upc}\n"
            f"Ubicación: {ubicacion}\n"
        )
        self.last_upc = upc
        self.Txt_Info_Product_Value_1.configure(state="normal")
        self.Txt_Info_Product_Value_1.delete("1.0", "end")
        self.Txt_Info_Product_Value_1.insert("end", info)
        self.Txt_Info_Product_Value_1.configure(state="disabled")

        # 8) No modificamos el label en caso de éxito:  
        #    permanece "UPC Product:" hasta que ocurra otro error.




    def save_store(self):
        store_val = self.Ent_Set_Store_Value.get().strip()
        try:
            with open(CONFIG_PATH, 'w') as cfg:
                cfg.write(store_val)
            self.Lb_Set_Store_Status.configure(text=f"Store: {store_val}")
        except Exception as e:
            self.Lb_Set_Store_Status.configure(text=f"Error: {e}")

    def get_access_token(self):
        auth = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
        r = requests.post(
            TOKEN_URL,
            headers={"Authorization": f"Basic {auth}", "Content-Type": "application/x-www-form-urlencoded"},
            data={"grant_type": "client_credentials", "scope": SCOPE}
        )
        return r.json().get("access_token") if r.status_code == 200 else None

    def fetch_and_display_stores(self):
        zip_code = self.Ent_Zip_Code_Value.get().strip()
        token = self.get_access_token()
        self.Txt_Stores_Value.configure(state="normal")
        self.Txt_Stores_Value.delete("1.0", tk.END)
        if not token:
            self.Txt_Stores_Value.insert(tk.END, "Error al obtener token.\n")
        else:
            url = LOCATIONS_URL.format(zip=zip_code)
            r = requests.get(url, headers={"Authorization": f"Bearer {token}", "Accept": "application/json"})
            if r.status_code == 200:
                stores = r.json().get("data", [])
                if not stores:
                    self.Txt_Stores_Value.insert(tk.END, "No se encontraron tiendas.\n")
                else:
                    for s in stores:
                        addr = s.get("address", {})
                        line = f"ID: {s.get('locationId')}\nNombre: {s.get('name')}\n"
                        line += f"Dirección: {addr.get('addressLine1')}, {addr.get('city')}, {addr.get('state')} {addr.get('zipCode')}\n\n"
                        self.Txt_Stores_Value.insert(tk.END, line)
            else:
                self.Txt_Stores_Value.insert(tk.END, f"Error al consultar tiendas: {r.status_code}\n")
        self.Txt_Stores_Value.configure(state="disabled")

    def limpiar_entry(self):
        w = self.top.focus_get()
        if hasattr(w, 'delete'):
            w.delete(0, tk.END)
            w.focus_set()

    def escribir_numero(self, valor):
        w = self.top.focus_get()
        if hasattr(w, 'insert'):
            w.insert(tk.END, valor)
            w.focus_set()

    def borrar_ultimo(self):
        w = self.top.focus_get()
        if hasattr(w, 'get'):
            txt = w.get()
            if txt:
                w.delete(len(txt)-1, tk.END)
            w.focus_set()

    def ocultar_contenido(self):
        for f in self.frames_positions:
            f.place_forget()
        self.Fr_Num.place_forget()

    def mostrar_frame(self, frame):
        if not self.historial_frames or self.historial_frames[-1] != frame:
            self.historial_frames.append(frame)
        self.ocultar_contenido()
        pos = self.frames_positions[frame]
        frame.place(x=pos['x'], y=pos['y'], width=pos['width'], height=pos['height'])
        if frame in (self.Fr_Scan_Project, self.Fr_Scan_Product, self.Fr_Set_Store):
            self.Fr_Num.place(x=10, y=544, width=455, height=249)
            if frame == self.Fr_Scan_Project:
                self.Ent_UPC_Product_Value.focus_force()
                self.Ent_UPC_Product_Value.icursor(tk.END)
            elif frame == self.Fr_Scan_Product:
                self.Ent_UPC_Product_Value_1.focus_force()
                self.Ent_UPC_Product_Value_1.icursor(tk.END)
            else:
                self.Ent_Zip_Code_Value.focus_force()
                self.Ent_Zip_Code_Value.icursor(tk.END)
        names = {
            self.Fr_Home:         "Home",
            self.Fr_Load_Project: "Load Project",
            self.Fr_Scan_Project: "Scan Project",
            self.Fr_Scan_Product: "Scan Product",
            self.Fr_Set_Store:    "Set Store",
        }
        self.Lb_Status.configure(text=names.get(frame, ""))

    def on_upc_change(self, *args):
        current = self.upc_var.get()
        # si antes teníamos un UPC buscado y ahora se borró al menos un dígito...
        if self.last_upc and len(current) < len(self.last_upc):
            # limpiar Canvas
            self.Cnv_Image_Value.delete("all")
            # limpiar Text
            self.Txt_Info_Product_Value_1.configure(state="normal")
            self.Txt_Info_Product_Value_1.delete("1.0", "end")
            self.Txt_Info_Product_Value_1.configure(state="disabled")
            # restaurar label
            self.Lb_UPC_Product_Label.configure(text="UPC Product:")
            # resetear last_upc
            self.last_upc = ""

def main():
    root = tk.Tk()
    app = Toplevel1(root)
    root.mainloop()

if __name__ == '__main__':
    main()
