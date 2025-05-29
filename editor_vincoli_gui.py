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

# Crea il file JSON vuoto se non esiste
if not os.path.isfile(JSON_VINCOLI):
    with open(JSON_VINCOLI, 'w', encoding='utf-8') as f:
        json.dump([], f, indent=2, ensure_ascii=False)

# --- Inizio programma ---
try:
    # Controlla se i file CSV esistono
    if not os.path.isfile(CSV_OPZIONI):
        raise FileNotFoundError(f"File non trovato: {CSV_OPZIONI}")
    if not os.path.isfile(CSV_MACCHINE):
        raise FileNotFoundError(f"File non trovato: {CSV_MACCHINE}")

    # Carica i dati da CSV e JSON
    with open(CSV_OPZIONI, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=',')
        opzioni = [row for row in reader]
    with open(CSV_MACCHINE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=',')
        macchine = [row for row in reader]
    with open(JSON_VINCOLI, 'r', encoding='utf-8') as f:
        vincoli = json.load(f)

    # DEBUG: stampa il contenuto di Elenco_Macchine.csv
    # print('DEBUG - Contenuto Elenco_Macchine.csv:')
    # for row in macchine:
    #     print(row)

    # DEBUG: stampa il contenuto di Elenco_Opzioni.csv
    # print('DEBUG - Contenuto Elenco_Opzioni.csv:')
    # for row in opzioni:
    #     print(row)

    # Finestra selezione macchina
    class MacchinaSelector(tk.Tk):
        def __init__(self, macchine, opzioni):
            super().__init__()
            self.title("Seleziona Macchina")
            self.geometry("400x180")  # Più alta
            # Cerca i nomi delle macchine nelle colonne più comuni
            self.macchine = sorted({
                row.get("Macchina", "").strip() or row.get("Nome", "").strip() or row.get("Nome Macchina", "").strip() or row.get("codice", "").strip()
                for row in macchine
                if row.get("Macchina", "").strip() or row.get("Nome", "").strip() or row.get("Nome Macchina", "").strip() or row.get("codice", "").strip()
            })
            self.opzioni = opzioni
            self._build_gui()

        def _build_gui(self):
            try:
                self.state('zoomed')  # Fullscreen su Windows
            except Exception:
                pass
            frame = tk.Frame(self)
            frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
            tk.Label(frame, text="Seleziona una macchina:").pack(anchor="w")
            self.cmb_macchina = ttk.Combobox(frame, values=self.macchine, state="readonly")
            self.cmb_macchina.pack(anchor="w", fill=tk.X)
            self.cmb_macchina.focus_set()
            self.cmb_macchina.bind("<Return>", self._on_confirm)
            btn = ttk.Button(frame, text="Conferma", command=self._on_confirm)
            btn.pack(pady=10)

        def _on_confirm(self, event=None):
            macchina = self.cmb_macchina.get()
            if not macchina:
                messagebox.showwarning("Attenzione", "Seleziona una macchina.")
                return
            self.destroy()
            PosizioniOpzioniViewer(macchina, self.opzioni).mainloop()

    # Finestra posizioni e opzioni
    class PosizioniOpzioniViewer(tk.Tk):
        def __init__(self, macchina, opzioni):
            super().__init__()
            self.title(f"Posizioni e Opzioni per {macchina}")
            try:
                self.state('zoomed')  # Fullscreen su Windows
            except Exception:
                pass
            self.macchina = macchina
            self.opzioni = opzioni
            self._build_gui()

        def _build_gui(self):
            self.geometry("1500x800")  # Riduci altezza finestra principale di 100 punti
            frame = tk.Frame(self)
            frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
            tk.Label(frame, text=f"Macchina selezionata: {self.macchina}", font=("Arial", 14, "bold")).pack(anchor="w", pady=(0,10))
            # Frame per le due liste affiancate
            lists_frame = tk.Frame(frame)
            lists_frame.pack(fill=tk.BOTH, expand=True)
            # Scrollbar verticale per le due liste
            vsb_left = ttk.Scrollbar(lists_frame, orient="vertical")
            vsb_right = ttk.Scrollbar(lists_frame, orient="vertical")
            # Lista sinistra
            self.tree_left = ttk.Treeview(lists_frame, columns=("posizione", "opzione", "valori"), show="headings", height=25, selectmode="browse", yscrollcommand=vsb_left.set)
            vsb_left.config(command=self.tree_left.yview)
            self.tree_left.heading("posizione", text="Posizione")
            self.tree_left.heading("opzione", text="Opzione")
            self.tree_left.heading("valori", text="Valori Possibili")
            self.tree_left.column("posizione", width=120, anchor="center")
            self.tree_left.column("opzione", width=260, anchor="w")
            self.tree_left.column("valori", width=260, anchor="w")
            self.tree_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,0))
            vsb_left.pack(side=tk.LEFT, fill=tk.Y)
            # Label "VIETA" tra le due liste
            vieta_label = tk.Label(lists_frame, text="VIETA", font=("Arial", 16, "bold"), fg="red")
            vieta_label.pack(side=tk.LEFT, padx=10, pady=10)
            # Lista destra (duplicato)
            self.tree_right = ttk.Treeview(lists_frame, columns=("posizione", "opzione", "valori"), show="headings", height=25, selectmode="browse", yscrollcommand=vsb_right.set)
            vsb_right.config(command=self.tree_right.yview)
            self.tree_right.heading("posizione", text="Posizione")
            self.tree_right.heading("opzione", text="Opzione")
            self.tree_right.heading("valori", text="Valori Possibili")
            self.tree_right.column("posizione", width=120, anchor="center")
            self.tree_right.column("opzione", width=260, anchor="w")
            self.tree_right.column("valori", width=260, anchor="w")
            self.tree_right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,0))
            vsb_right.pack(side=tk.LEFT, fill=tk.Y)
            # Pulsanti in fondo
            btn_frame = tk.Frame(frame)
            btn_frame.pack(fill=tk.X, pady=(20,0))
            btn_crea_regola = ttk.Button(btn_frame, text="Crea regola", command=self._crea_regola)
            btn_crea_regola.pack(side=tk.LEFT, padx=10, pady=10)
            btn_elimina = ttk.Button(btn_frame, text="Elimina regola", command=self._elimina_regola)
            btn_elimina.pack(side=tk.LEFT, padx=10, pady=10)
            btn_esci = ttk.Button(btn_frame, text="Esci", command=self.destroy)
            btn_esci.pack(side=tk.RIGHT, padx=10, pady=10)
            self._populate_tree()

        def _populate_tree(self):
            pos_opz = []
            for row in self.opzioni:
                opzione = row.get("Opzione", "").strip()
                valori = row.get("Valori Possibili", "").strip()
                macchine_compatibili = row.get("Macchine Compatibili", "").strip()
                macchine_list = [m.strip().upper() for m in macchine_compatibili.split(',') if m.strip()]
                if self.macchina.strip().upper() not in macchine_list:
                    continue
                pos_amm = row.get("Posizioni Ammesse", "").strip()
                valori_possibili = [v.strip() for v in valori.split(',') if v.strip()]
                if not valori_possibili:
                    valori_possibili = [""]
                for valore in valori_possibili:
                    posizioni = []
                    if pos_amm:
                        try:
                            pos_dict = ast.literal_eval(pos_amm)
                            posizioni = pos_dict.get(self.macchina, [])
                        except Exception as e:
                            print('DEBUG - Errore parsing posizioni:', e)
                            pass
                    if posizioni:
                        for pos in posizioni:
                            pos_opz.append((str(pos), opzione, valore, macchine_compatibili))
                    else:
                        pos_opz.append(("", opzione, valore, macchine_compatibili))
            pos_opz.sort(key=lambda x: (x[0] if x[0] else "zzz", x[1], x[2]))
            self.tree_left.delete(*self.tree_left.get_children())
            self.tree_right.delete(*self.tree_right.get_children())
            for pos, opzione, valore, macchine_compatibili in pos_opz:
                self.tree_left.insert("", "end", values=(pos, opzione, valore))
                self.tree_right.insert("", "end", values=(pos, opzione, valore))

        def _crea_regola(self):
            sel_left = self.tree_left.selection()
            sel_right = self.tree_right.selection()
            if not sel_left or not sel_right:
                messagebox.showwarning("Attenzione", "Seleziona una riga a sinistra e una a destra.")
                return
            left_values = self.tree_left.item(sel_left[0], 'values')
            right_values = self.tree_right.item(sel_right[0], 'values')
            regola = {
                "macchina": self.macchina,
                "se": {
                    "posizione": left_values[0],
                    "opzione": left_values[1],
                    "valore": left_values[2]
                },
                "vieta": {
                    "posizione": right_values[0],
                    "opzione": right_values[1],
                    "valore": right_values[2]
                }
            }
            try:
                with open(JSON_VINCOLI, 'r', encoding='utf-8') as f:
                    try:
                        vincoli = json.load(f)
                        if isinstance(vincoli, dict):
                            vincoli = [vincoli]
                    except Exception:
                        vincoli = []
            except FileNotFoundError:
                vincoli = []
            except Exception as e:
                logging.error(f"Errore lettura vincoli_macchine.json: {e}")
                vincoli = []
            vincoli.append(regola)
            try:
                with open(JSON_VINCOLI, 'w', encoding='utf-8') as f:
                    json.dump(vincoli, f, indent=2, ensure_ascii=False)
                    f.flush()
                    os.fsync(f.fileno())
                # Mostra solo una riga di conferma
                print('Regola aggiunta a vincoli_macchine.json')
                messagebox.showinfo("Regola creata", "Regola aggiunta con successo!")
            except Exception as e:
                logging.error(f"Errore scrittura vincoli_macchine.json: {e}")
                messagebox.showerror("Errore", f"Errore nella scrittura del file vincoli_macchine.json: {e}")

        def _elimina_regola(self):
            # Mostra una finestra con tutte le regole per la macchina corrente, seleziona e conferma eliminazione
            try:
                with open(JSON_VINCOLI, 'r', encoding='utf-8') as f:
                    vincoli = json.load(f)
                    if isinstance(vincoli, dict):
                        vincoli = [vincoli]
            except Exception as e:
                logging.error(f"Errore lettura vincoli_macchine.json: {e}")
                messagebox.showerror("Errore", f"Errore nella lettura del file vincoli_macchine.json: {e}")
                return
            # Filtra solo le regole della macchina corrente
            regole_macchina = [r for r in vincoli if r.get("macchina", "") == self.macchina]
            if not regole_macchina:
                messagebox.showinfo("Nessuna regola trovata", "Non ci sono regole da eliminare per questa macchina.")
                return
            # Finestra di selezione regola
            sel_win = tk.Toplevel(self)
            sel_win.title("Seleziona regola da eliminare")
            sel_win.geometry("1200x600")  # Più grande
            tk.Label(sel_win, text=f"Regole per {self.macchina}", font=("Arial", 12, "bold")).pack(pady=8)
            # Scrollbar per la treeview delle regole
            frame_tree = tk.Frame(sel_win)
            frame_tree.pack(fill=tk.BOTH, expand=True)
            vsb = ttk.Scrollbar(frame_tree, orient="vertical")
            tree = ttk.Treeview(frame_tree, columns=("se_pos", "se_opz", "se_val", "vieta_pos", "vieta_opz", "vieta_val"), show="headings", height=20, yscrollcommand=vsb.set)
            vsb.config(command=tree.yview)
            tree.heading("se_pos", text="SE - Posizione")
            tree.heading("se_opz", text="SE - Opzione")
            tree.heading("se_val", text="SE - Valore")
            tree.heading("vieta_pos", text="VIETA - Posizione")
            tree.heading("vieta_opz", text="VIETA - Opzione")
            tree.heading("vieta_val", text="VIETA - Valore")
            tree.column("se_pos", width=120)
            tree.column("se_opz", width=220)
            tree.column("se_val", width=220)
            tree.column("vieta_pos", width=120)
            tree.column("vieta_opz", width=220)
            tree.column("vieta_val", width=220)
            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
            vsb.pack(side=tk.LEFT, fill=tk.Y)
            for idx, r in enumerate(regole_macchina):
                tree.insert("", "end", iid=str(idx), values=(
                    r.get("se", {}).get("posizione", ""),
                    r.get("se", {}).get("opzione", ""),
                    r.get("se", {}).get("valore", ""),
                    r.get("vieta", {}).get("posizione", ""),
                    r.get("vieta", {}).get("opzione", ""),
                    r.get("vieta", {}).get("valore", "")
                ))
            def conferma_elimina():
                sel = tree.selection()
                if not sel:
                    messagebox.showwarning("Attenzione", "Seleziona una regola da eliminare.", parent=sel_win)
                    return
                idx = int(sel[0])
                regola_da_eliminare = regole_macchina[idx]
                if not messagebox.askyesno("Conferma eliminazione", "Vuoi eliminare la regola selezionata? Questa azione non è reversibile.", parent=sel_win):
                    return
                # Ricostruisci la lista senza la regola selezionata
                nuova_lista = [r for r in vincoli if r is not regola_da_eliminare]
                try:
                    with open(JSON_VINCOLI, 'w', encoding='utf-8') as f:
                        json.dump(nuova_lista, f, indent=2, ensure_ascii=False)
                        f.flush()
                        os.fsync(f.fileno())
                    messagebox.showinfo("Regola eliminata", "Regola eliminata con successo!", parent=sel_win)
                    sel_win.destroy()
                except Exception as e:
                    logging.error(f"Errore scrittura vincoli_macchine.json: {e}")
                    messagebox.showerror("Errore", f"Errore nella scrittura del file vincoli_macchine.json: {e}", parent=sel_win)
            btn = ttk.Button(sel_win, text="Elimina regola selezionata", command=conferma_elimina)
            btn.pack(pady=10)

    # Avvio programma
    app = MacchinaSelector(macchine, opzioni)
    app.mainloop()

except Exception as e:
    logging.error(f"Errore nel programma: {e}")
    messagebox.showerror("Errore", f"Si è verificato un errore: {e}")
    exit(1)

