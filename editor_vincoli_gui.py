import csv
import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import ast
import logging

# --- Logging ---
LOG_FILE = os.path.join(os.path.dirname(__file__), "errorEditorVincoli.log")
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# --- Configurazione percorso CSV ---
CONF_PATH = os.path.join(os.path.dirname(__file__), "editorVincoli.conf")
def get_csv_dir():
    if os.path.exists(CONF_PATH):
        try:
            with open(CONF_PATH, 'r', encoding='utf-8') as f:
                path = f.readline().strip()
                if path and os.path.isdir(path):
                    return path
        except Exception as e:
            logging.error(f"Errore lettura conf: {e}")
    # Chiedi all'utente la cartella
    root = tk.Tk(); root.withdraw()
    messagebox.showinfo("Seleziona cartella CSV", "Seleziona la cartella dove si trovano Elenco_Macchine.csv ed Elenco_Opzioni.csv.")
    path = filedialog.askdirectory(title="Seleziona cartella CSV")
    if not path:
        messagebox.showerror("Errore", "Cartella CSV obbligatoria. Il programma verrà chiuso.")
        logging.error("Cartella CSV non selezionata")
        exit(1)
    with open(CONF_PATH, 'w', encoding='utf-8') as f:
        f.write(path)
    return path

# --- Percorsi file ---
CSV_DIR = get_csv_dir()
CSV_OPZIONI = os.path.join(CSV_DIR, "Elenco_Opzioni.csv")
CSV_MACCHINE = os.path.join(CSV_DIR, "Elenco_Macchine.csv")
JSON_VINCOLI = os.path.join(CSV_DIR, "vincoli_macchine.json")

# --- Inizio programma ---
try:
    # Controlla se i file CSV esistono
    if not os.path.isfile(CSV_OPZIONI):
        raise FileNotFoundError(f"File non trovato: {CSV_OPZIONI}")
    if not os.path.isfile(CSV_MACCHINE):
        raise FileNotFoundError(f"File non trovato: {CSV_MACCHINE}")

    # Carica i dati da CSV e JSON
    with open(CSV_OPZIONI, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        opzioni = [row for row in reader]
    with open(CSV_MACCHINE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        macchine = [row for row in reader]
    with open(JSON_VINCOLI, 'r', encoding='utf-8') as f:
        vincoli = json.load(f)

    # Finestra visualizzazione opzioni
    class OpzioniViewer(tk.Tk):
        def __init__(self, opzioni):
            super().__init__()
            self.title("Visualizza Opzioni per Macchina")
            self.geometry("900x600")
            self.opzioni = opzioni
            self._build_gui()

        def _build_gui(self):
            frame = tk.Frame(self)
            frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
            # --- ComboBox Macchina ---
            macchine_set = set()
            for row in self.opzioni:
                macs = [m.strip() for m in (row.get("Macchine Compatibili", "") or "").split(",") if m.strip()]
                macchine_set.update(macs)
            macchine = sorted(macchine_set)
            tk.Label(frame, text="Seleziona Macchina:").pack(anchor="w")
            self.cmb_macchina = ttk.Combobox(frame, values=macchine, state="readonly")
            self.cmb_macchina.pack(anchor="w")
            self.cmb_macchina.bind("<<ComboboxSelected>>", self._update_opzioni)
            # --- Lista opzioni ---
            self.tree = ttk.Treeview(frame, columns=("opzione", "valori", "posizioni"), show="headings", height=25)
            self.tree.heading("opzione", text="Opzione")
            self.tree.heading("valori", text="Valori Possibili")
            self.tree.heading("posizioni", text="Posizioni Ammesse")
            self.tree.column("opzione", width=220)
            self.tree.column("valori", width=320)
            self.tree.column("posizioni", width=180)
            self.tree.pack(fill=tk.BOTH, expand=True, pady=10)

        def _update_opzioni(self, event=None):
            macchina = self.cmb_macchina.get()
            opzioni_per_pos = []
            for row in self.opzioni:
                macs = [m.strip() for m in (row.get("Macchine Compatibili", "") or "").split(",") if m.strip()]
                if macchina not in macs:
                    continue
                opzione = row.get("Opzione", "").strip()
                valori = row.get("Valori Possibili", "").strip()
                pos_amm = row.get("Posizioni Ammesse", "").strip()
                posizioni = []
                if pos_amm:
                    try:
                        pos_dict = ast.literal_eval(pos_amm)
                        posizioni = pos_dict.get(macchina, [])
                    except Exception:
                        pass
                if not posizioni:
                    opzioni_per_pos.append(("", opzione, valori, ""))
                else:
                    for pos in posizioni:
                        opzioni_per_pos.append((str(pos), opzione, valori, str(pos)))
            opzioni_per_pos.sort(key=lambda x: (x[0] if x[0] else "zzz", x[1]))
            self.tree.delete(*self.tree.get_children())
            for pos, opzione, valori, pos_disp in opzioni_per_pos:
                self.tree.insert("", "end", values=(opzione, valori, pos_disp))

    app = OpzioniViewer(opzioni)
    app.mainloop()

except Exception as e:
    logging.error(f"Errore nel programma: {e}")
    messagebox.showerror("Errore", f"Si è verificato un errore: {e}")
    exit(1)

