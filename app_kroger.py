#! /usr/bin/env python3
#  -*- coding: utf-8 -*-
# GUI module: diseño completo + navegación simplificada y funcional

import sys
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.constants import *
import os.path
import subprocess
import socket
import urllib.request
import re
import tkinter.messagebox as messagebox



_location = os.path.dirname(__file__)


class Toplevel1:
    def __init__(self, top=None):
        top.geometry("480x800+0+0")
        # top.overrideredirect(True)
        top.title("Toplevel 0")
        top.configure(background="#d9d9d9")

        self.top = top
        self.historial_frames = []


        # === FRAME MENU ===
        self.Fr_Menu = tk.Frame(top, bg="#d9d9d9", bd=2, relief="groove")
        self.Fr_Menu.place(relx=0.042, rely=0.0, relheight=0.078, relwidth=0.646)
        self.Btn_Home = tk.Button(self.Fr_Menu, text="Home")
        self.Btn_Home.place(relx=0.065, rely=0.0, height=22, width=47)
        self.Btn_Back = tk.Button(self.Fr_Menu, text="Back")
        self.Btn_Back.place(relx=0.516, rely=0.0, height=22, width=47)

        # === FRAME HOME ===
        self.Fr_Home = tk.Frame(top, bg="#d9d9d9", bd=2, relief="groove")
        self.Btn_Config = tk.Button(self.Fr_Home, text="Config")
        self.Btn_Config.place(relx=0.543, rely=0.724, height=176, width=197)
        

        # === FRAME CONFIG ===
        self.Fr_Config = tk.Frame(top, bg="#d9d9d9", bd=2, relief="groove")
        self.Btn_Wifi = tk.Button(self.Fr_Config, text="Wifi")
        self.Btn_Wifi.place(relx=0.065, rely=0.061, height=26, width=47)

        # === FRAME WIFI ===
        self.Fr_Wifi = tk.Frame(top, bg="#d9d9d9", bd=2, relief="groove")
        self.Btn_Info = tk.Button(self.Fr_Wifi, text="Info")
        self.Btn_Scan = tk.Button(self.Fr_Wifi, text="Scan")
        self.Btn_Connect = tk.Button(self.Fr_Wifi, text="Connect")
        self.Btn_Ping = tk.Button(self.Fr_Wifi, text="Ping")
        self.Btn_Info.place(relx=0.08, rely=0.069, height=26, width=47)
        self.Btn_Scan.place(relx=0.08, rely=0.276, height=26, width=47)
        self.Btn_Connect.place(relx=0.08, rely=0.483, height=26, width=47)
        self.Btn_Ping.place(relx=0.08, rely=0.69, height=26, width=47)

        # === FRAME INFO ===
        self.Fr_Info = tk.Frame(top, bg="#d9d9d9", bd=2, relief="groove")
        self.Lb_SSID = tk.Label(self.Fr_Info, text="SSID:")
        self.Lb_SSID_Value = tk.Label(self.Fr_Info, text="N/A")
        self.Lb_IP = tk.Label(self.Fr_Info, text="IP:")
        self.Lb_IP_Value = tk.Label(self.Fr_Info, text="N/A")
        self.Lb_State = tk.Label(self.Fr_Info, text="State:")
        self.Lb_State_Value = tk.Label(self.Fr_Info, text="N/A")
        self.Lb_Internet = tk.Label(self.Fr_Info, text="Internet:")
        self.Lb_Internet_Value = tk.Label(self.Fr_Info, text="N/A")

        self.Lb_SSID.place(relx=0.05, rely=0.1)
        self.Lb_SSID_Value.place(relx=0.35, rely=0.1)
        self.Lb_IP.place(relx=0.05, rely=0.3)
        self.Lb_IP_Value.place(relx=0.35, rely=0.3)
        self.Lb_State.place(relx=0.05, rely=0.5)
        self.Lb_State_Value.place(relx=0.35, rely=0.5)
        self.Lb_Internet.place(relx=0.05, rely=0.7)
        self.Lb_Internet_Value.place(relx=0.35, rely=0.7)

        # === FRAME NUM ===
        self.Fr_Num = tk.Frame(top, bg="#d9d9d9", bd=2, relief="groove")
        self.nums = []
        for i in range(10):
            btn = tk.Button(self.Fr_Num, text=str(i), command=lambda i=i: self.escribir_en_entry(str(i)))
            btn.place(relx=(i % 5) * 0.2, rely=(i // 5) * 0.4, width=30, height=30)
            self.nums.append(btn)
        self.Btn_Num_Delete = tk.Button(self.Fr_Num, text="Del", command=self.borrar_ultimo)
        self.Btn_Num_Arrow = tk.Button(self.Fr_Num, text="→")
        self.Btn_Num_Delete.place(relx=0.0, rely=0.8, width=30, height=30)
        self.Btn_Num_Arrow.place(relx=0.2, rely=0.8, width=30, height=30)

        # === FRAME CONNECT ===
        self.Fr_Connect = tk.Frame(top, bg="#d9d9d9", bd=2, relief="groove")
        self.Lb_SSID2 = tk.Label(self.Fr_Connect, text="SSID")
        self.Ent_SSID2_Value = tk.Entry(self.Fr_Connect)
        self.Ent_SSID2_Value.bind("<FocusIn>", lambda e: self.set_entry_activa(self.Ent_SSID2_Value))
        self.Lb_PASS = tk.Label(self.Fr_Connect, text="PASS")
        self.Ent_PASS_Value = tk.Entry(self.Fr_Connect)
        self.Ent_PASS_Value.bind("<FocusIn>", lambda e: self.set_entry_activa(self.Ent_PASS_Value))
        self.entrada_activa = self.Ent_PASS_Value
        self.Btn_Save_Connect = tk.Button(self.Fr_Connect, text="Save & Connect")
        self.Lb_SSID2.place(relx=0.05, rely=0.1)
        self.Ent_SSID2_Value.place(relx=0.3, rely=0.1, relwidth=0.6)
        self.Lb_PASS.place(relx=0.05, rely=0.4)
        self.Ent_PASS_Value.place(relx=0.3, rely=0.4, relwidth=0.6)
        self.Btn_Save_Connect.place(relx=0.3, rely=0.7, relwidth=0.5)

        # === FRAME SCAN ===
        self.Fr_Scan = tk.Frame(top, bg="#d9d9d9", bd=2, relief="groove")
        self.Lst_Scan_Value = tk.Listbox(self.Fr_Scan)
        self.Lst_Scan_Value.bind("<<ListboxSelect>>", self.copiar_ssid_al_portapapeles)
        self.Lst_Scan_Value.place(relx=0.0, rely=0.0, relwidth=1.0, relheight=1.0)

        # === FRAME PING ===
        self.Fr_Ping = tk.Frame(top, bg="#d9d9d9", bd=2, relief="groove")
        self.Txt_Ping_Value = tk.Text(self.Fr_Ping)
        self.Txt_Ping_Value.place(relx=0.0, rely=0.0, relwidth=1.0, relheight=1.0)

        # === GESTIÓN DE VISIBILIDAD ===
        self.frames_posiciones = {
            self.Fr_Home: (0.021, 0.088, 0.9, 0.958),
            self.Fr_Config: (0.125, 0.375, 0.516, 0.646),
            self.Fr_Wifi: (0.292, 0.156, 0.453, 0.521),
            self.Fr_Info: (0.375, 0.531, 0.328, 0.563),
            self.Fr_Num: (0.0, 0.125, 0.453, 0.979),
            self.Fr_Scan: (0.125, 0.375, 0.328, 0.646),
            self.Fr_Connect: (0.083, 0.5, 0.297, 0.813),
            self.Fr_Ping: (0.417, 0.656, 0.297, 0.521),
        }

        self.ocultar_todos_los_frames()
        self.mostrar_frame(self.Fr_Home)

        # === ACCIONES ===
        self.Btn_Home.configure(command=lambda: self.mostrar_frame(self.Fr_Home))
        self.Btn_Back.configure(command=self.ir_atras)
        self.Btn_Config.configure(command=lambda: self.mostrar_frame(self.Fr_Config))
        self.Btn_Wifi.configure(command=lambda: self.mostrar_frame(self.Fr_Wifi))
        self.Btn_Info.configure(command=self.actualizar_info)
        self.Btn_Scan.configure(command=self.escanear_wifi)
        self.Btn_Connect.configure(command=self.mostrar_connect_y_num)
        self.Btn_Ping.configure(command=lambda: self.mostrar_frame(self.Fr_Ping))
        self.Btn_Save_Connect.configure(command=self.save_and_connect)

        


    def ocultar_todos_los_frames(self):
        for f in self.frames_posiciones:
            f.place_forget()

    def mostrar_frame(self, frame):
        if not self.historial_frames or self.historial_frames[-1] != frame:
            self.historial_frames.append(frame)
        self.ocultar_todos_los_frames()
        pos = self.frames_posiciones[frame]
        frame.place(relx=pos[0], rely=pos[1], relheight=pos[2], relwidth=pos[3])

    def ir_atras(self):
        if len(self.historial_frames) > 1:
            self.historial_frames.pop()
            self.mostrar_frame(self.historial_frames[-1])

    def actualizar_info(self):

        # Obtener SSID (Linux - iwgetid)
        try:
            ssid = subprocess.check_output(["iwgetid", "-r"], encoding='utf-8').strip()
            if not ssid:
                ssid = "N/A"
        except:
            ssid = "N/A"

        # Obtener IP local
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip_address = s.getsockname()[0]
            s.close()
        except:
            ip_address = "N/A"

        # Estado general (solo Wi-Fi)
        estado = "Conectado" if ssid != "N/A" else "No conectado"

        # Verificar conexión a Internet
        try:
            urllib.request.urlopen("https://www.google.com", timeout=2)
            internet = "Sí"
        except:
            internet = "No"

        # Actualizar labels
        self.Lb_SSID_Value.configure(text=ssid)
        self.Lb_IP_Value.configure(text=ip_address)
        self.Lb_State_Value.configure(text=estado)
        self.Lb_Internet_Value.configure(text=internet)

        self.mostrar_frame(self.Fr_Info)
    
    def escanear_wifi(self):

        self.Lst_Scan_Value.delete(0, tk.END)  # Limpiar lista antes de escanear

        try:
            resultado = subprocess.check_output(["sudo", "iwlist", "wlan0", "scan"], encoding="utf-8", stderr=subprocess.DEVNULL)
            ssids = re.findall(r'ESSID:"([^"]+)"', resultado)
            ssids_unicos = list(dict.fromkeys(ssids))  # Eliminar duplicados preservando orden

            if ssids_unicos:
                for ssid in ssids_unicos:
                    self.Lst_Scan_Value.insert(tk.END, ssid)
            else:
                self.Lst_Scan_Value.insert(tk.END, "No se encontraron redes.")
        except Exception as e:
            self.Lst_Scan_Value.insert(tk.END, f"Error: {str(e)}")

        self.mostrar_frame(self.Fr_Scan)

    def copiar_ssid_al_portapapeles(self, event):
        seleccion = self.Lst_Scan_Value.curselection()
        if seleccion:
            ssid = self.Lst_Scan_Value.get(seleccion[0])
            self.top.clipboard_clear()
            self.top.clipboard_append(ssid)
            self.top.update()
            messagebox.showinfo("Copiado", f"'{ssid}' copiado al portapapeles.")

    def mostrar_connect_y_num(self):
        self.ocultar_todos_los_frames()
        self.Ent_SSID2_Value.delete(0, tk.END)
        self.Ent_PASS_Value.delete(0, tk.END)
        self.Fr_Connect.place(relx=0.083, rely=0.5, relheight=0.297, relwidth=0.813)
        self.Fr_Num.place(relx=0.0, rely=0.8, relheight=0.2, relwidth=1.0)
        self.historial_frames.append(self.Fr_Connect)

    def escribir_en_entry(self, valor):
        if self.entrada_activa:
            actual = self.entrada_activa.get()
            self.entrada_activa.delete(0, tk.END)
            self.entrada_activa.insert(0, actual + valor)

    def set_entry_activa(self, entry):
        self.entrada_activa = entry

  

    def save_and_connect(self):
        ssid = self.Ent_SSID_Value.get()
        password = self.Ent_PASS_Value.get()

        if not ssid or not password:
            messagebox.showerror("Error", "SSID y contraseña no pueden estar vacíos.")
            return

        try:
            # Opcional: eliminar conexiones previas con el mismo nombre
            subprocess.run(['nmcli', 'connection', 'delete', ssid], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # Intentar conectar
            result = subprocess.run(
                ['nmcli', 'dev', 'wifi', 'connect', ssid, 'password', password],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            if result.returncode == 0:
                messagebox.showinfo("Conectado", f"Conectado exitosamente a {ssid}")
            else:
                messagebox.showerror("Error al conectar", result.stderr)

        except Exception as e:
            messagebox.showerror("Excepción", f"Ocurrió un error:\n{str(e)}")


    def borrar_ultimo(self):
        if self.entrada_activa:
            actual = self.entrada_activa.get()
            self.entrada_activa.delete(0, tk.END)
            self.entrada_activa.insert(0, actual[:-1])



if __name__ == '__main__':
    root = tk.Tk()
    app = Toplevel1(root)
    root.mainloop()

