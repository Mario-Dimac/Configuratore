import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os
import json
import tempfile
import sys

# Trova una cartella scrivibile per il file di configurazione
def get_config_file():
    # Prova nella stessa cartella dell'eseguibile
    exe_dir = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__)
    config_path = os.path.join(exe_dir, 'main_menu.config')
    try:
        with open(config_path, 'a'):
            pass
        return config_path
    except Exception:
        # Se non scrivibile, usa la cartella temporanea dell'utente
        temp_path = os.path.join(tempfile.gettempdir(), 'main_menu.config')
        return temp_path

CONFIG_FILE = get_config_file()
PROGRAMMI_LABELS = [
    "Configura MCV",
    "Visualizza Configurazione",
    "Verifica Vincoli",
    "Aggiorna Prezzi Opzioni",
    "Configuratore"
]

# Carica i percorsi dal file di configurazione
def carica_percorsi():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = f.read().strip()
                if not data:
                    return None
                return json.loads(data)
        except Exception:
            # File corrotto o non valido: lo elimino per forzare la riconfigurazione
            try:
                os.remove(CONFIG_FILE)
            except Exception:
                pass
            return None
    return None

# Salva i percorsi nel file di configurazione
def salva_percorsi(percorso_dict):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(percorso_dict, f, indent=2)

# Finestra per selezionare i percorsi degli eseguibili
def configura_percorsi():
    percorsi = {}
    for label in PROGRAMMI_LABELS:
        messagebox.showinfo("Seleziona programma", f"Seleziona l'eseguibile per: {label}")
        path = filedialog.askopenfilename(title=f"Seleziona l'eseguibile per: {label}", filetypes=[("Eseguibile", "*.exe"), ("Tutti i file", "*.*")])
        if not path:
            messagebox.showerror("Errore", f"Percorso non selezionato per: {label}. Configurazione annullata.")
            return None
        percorsi[label] = path
    salva_percorsi(percorsi)
    return percorsi

# Lancia il programma selezionato
def lancia_programma(path):
    subprocess.Popen([path])

# MAIN
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Menu Principale Configuratore")
    root.geometry("400x400")

    percorsi = carica_percorsi()
    if not percorsi:
        if not messagebox.askyesno("Configurazione necessaria", "Devi selezionare i percorsi degli eseguibili la prima volta. Procedere?"):
            root.destroy()
            exit(0)
        percorsi = configura_percorsi()
        if not percorsi:
            root.destroy()
            exit(0)

    def reconfig():
        new_percorsi = configura_percorsi()
        if new_percorsi:
            global percorsi
            percorsi = new_percorsi
            messagebox.showinfo("OK", "Percorsi aggiornati!")

    for label in PROGRAMMI_LABELS:
        tk.Button(root, text=label, width=35, command=lambda l=label: lancia_programma(percorsi[l])).pack(pady=5)

    tk.Button(root, text="Configura Percorsi", width=35, command=reconfig).pack(pady=10)
    tk.Button(root, text="Esci", width=35, command=root.destroy).pack(pady=10)

    root.mainloop()
