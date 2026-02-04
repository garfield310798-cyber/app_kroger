#! /usr/bin/env python3
#  -*- coding: utf-8 -*-
# GUI module: diseño completo + navegación simplificada y funcional

import sys
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.constants import *
import os.path

_location = os.path.dirname(__file__)
import app_kroger_support

class Toplevel1:
    def __init__(self, top=None):
        top.geometry("240x320+776+281")
        # top.overrideredirect(True)
        top.title("Toplevel 0")
        top.configure(background="#d9d9d9")

        self.top = top
        self.historial_frames = []

        # === FRAME MENU (siempre visible) ===
        self.Fr_Menu = tk.Frame(top, bg="#d9d9d9", bd=2, relief="groove")
        self.Fr_Menu.place(relx=0.004, rely=0.003, relheight=0.078, relwidth=0.992)
        self.Btn_Home = tk.Button(self.Fr_Menu, text="Home")
        self.Btn_Home.place(relx=0.065, rely=0.0, height=22, width=47)
        self.Btn_Back = tk.Button(self.Fr_Menu, text="Back")
        self.Btn_Back.place(relx=0.516, rely=0.0, height=22, width=47)

        # === FRAME HOME ===
        self.Fr_Home = tk.Frame(top, bg="#d9d9d9", bd=2, relief="groove")
        self.Btn_Config = tk.Button(self.Fr_Home, text="Config")
        self.Btn_Config.place(relx=0.4, rely=0.065, height=26, width=47)

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
        self.Lb_SSID.place(relx=0.1, rely=0.1)
        self.Lb_SSID_Value.place(relx=0.4, rely=0.1)
        self.Lb_IP.place(relx=0.1, rely=0.3)
        self.Lb_IP_Value.place(relx=0.4, rely=0.3)
        self.Lb_State.place(relx=0.1, rely=0.5)
        self.Lb_State_Value.place(relx=0.4, rely=0.5)

        # === FRAME NUM ===
        self.Fr_Num = tk.Frame(top, bg="#d9d9d9", bd=2, relief="groove")
        self.nums = []
        for i in range(10):
            btn = tk.Button(self.Fr_Num, text=str(i))
            btn.place(x=(i % 5) * 40, y=(i // 5) * 30, width=35, height=25)
            self.nums.append(btn)
        self.Btn_Num_Delete = tk.Button(self.Fr_Num, text="Del")
        self.Btn_Num_Arrow = tk.Button(self.Fr_Num, text="→")
        self.Btn_Num_Delete.place(x=0, y=70, width=35, height=25)
        self.Btn_Num_Arrow.place(x=45, y=70, width=35, height=25)

        # === FRAME CONNECT ===
        self.Fr_Connect = tk.Frame(top, bg="#d9d9d9", bd=2, relief="groove")
        self.Lb_SSID2 = tk.Label(self.Fr_Connect, text="SSID")
        self.Ent_SSID2_Value = tk.Entry(self.Fr_Connect)
        self.Lb_PASS = tk.Label(self.Fr_Connect, text="PASS")
        self.Ent_PASS_Value = tk.Entry(self.Fr_Connect)
        self.Btn_Save_Connect = tk.Button(self.Fr_Connect, text="Save & Connect")
        self.Lb_SSID2.place(relx=0.1, rely=0.1)
        self.Ent_SSID2_Value.place(relx=0.4, rely=0.1)
        self.Lb_PASS.place(relx=0.1, rely=0.3)
        self.Ent_PASS_Value.place(relx=0.4, rely=0.3)
        self.Btn_Save_Connect.place(relx=0.25, rely=0.5)

        # === FRAME SCAN ===
        self.Fr_Scan = tk.Frame(top, bg="#d9d9d9", bd=2, relief="groove")
        self.Lst_Scan_Value = tk.Listbox(self.Fr_Scan)
        self.Lst_Scan_Value.place(relx=0.1, rely=0.1, relwidth=0.8, relheight=0.8)

        # === FRAME PING ===
        self.Fr_Ping = tk.Frame(top, bg="#d9d9d9", bd=2, relief="groove")
        self.Txt_Ping_Value = tk.Text(self.Fr_Ping)
        self.Txt_Ping_Value.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.9)

        # === POSICIONES ===
        self.frames_posiciones = {
            self.Fr_Home: (0.208, 0.438, 0.484, 0.521),
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
        self.Btn_Info.configure(command=lambda: self.mostrar_frame(self.Fr_Info))
        self.Btn_Scan.configure(command=lambda: self.mostrar_frame(self.Fr_Scan))
        self.Btn_Connect.configure(command=lambda: self.mostrar_frame(self.Fr_Connect))
        self.Btn_Ping.configure(command=lambda: self.mostrar_frame(self.Fr_Ping))

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

def start_up():
    app_kroger_support.main()

if __name__ == '__main__':
    app_kroger_support.main()
