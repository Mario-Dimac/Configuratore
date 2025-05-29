import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv
import os
import json
import shutil

MACCHINE_FIELDS = [
    "Nome Macchina",
    "Codice",
    "Descrizione",
    "Costo Base",
    "Diametro Minimo",
    "Diametro Massimo",
    "Lunghezza Massima",
    "Max Stazioni",
    "Posizioni Stazioni (gradi)"  # Nuova colonna
]
OPZIONI_FIELDS = [
    "Opzione",
    "Valori Possibili",
    "Costo Opzione",
    "Macchine Compatibili",
    "Vincoli",
    "Posizioni Ammesse",
    "Tipo Opzione"  # Nuova colonna
]

class ConfiguratoreApp:
    def __init__(self, master):
        self.master = master
        master.title("Configuratore Macchine - Editor CSV")

        # Controlla la presenza dei file CSV e chiedi all'utente di selezionarli se mancanti
        self.ensure_csv_file("Elenco_Macchine.csv")
        self.ensure_csv_file("Elenco_Opzioni.csv")

        # Definisci il percorso del CSV delle macchine
        self.macchine_csv_path = os.path.join(os.path.dirname(__file__), "Elenco_Macchine.csv")

        self.notebook = ttk.Notebook(master)
        self.notebook.pack(fill="both", expand=True)

        # Carica i nomi delle macchine da Elenco_Macchine.csv
        self.macchine_nomi = []
        self.macchine_fieldnames = self.get_macchine_fieldnames()
        self.carica_macchine()

        # Tab Macchine
        self.frame_macchine = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_macchine, text="Macchine")
        self.setup_tab(self.frame_macchine, self.macchine_fieldnames, "Elenco_Macchine.csv")

        # Tab Opzioni
        self.frame_opzioni = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_opzioni, text="Opzioni")
        self.setup_tab_opzioni(self.frame_opzioni, OPZIONI_FIELDS, "Elenco_Opzioni.csv")

    def get_macchine_fieldnames(self):
        path = os.path.join(os.path.dirname(__file__), "Elenco_Macchine.csv")
        if os.path.exists(path):
            with open(path, "r", newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                for row in reader:
                    return row
        return MACCHINE_FIELDS

    def ensure_csv_file(self, filename):
        path = os.path.join(os.path.dirname(__file__), filename)
        if not os.path.exists(path):
            messagebox.showwarning("File mancante", f"Il file {filename} non è stato trovato. Selezionalo manualmente.")
            file_path = filedialog.askopenfilename(title=f"Seleziona {filename}", filetypes=[("CSV files", "*.csv")])
            if not file_path:
                messagebox.showerror("Errore", f"Il file {filename} è obbligatorio. Il programma verrà chiuso.")
                self.master.destroy()
                return
            try:
                shutil.copy(file_path, path)
            except Exception as e:
                messagebox.showerror("Errore", f"Impossibile copiare il file: {e}")
                self.master.destroy()
                return

    def carica_macchine(self):
        self.macchine_nomi = []
        if os.path.exists(self.macchine_csv_path):
            with open(self.macchine_csv_path, "r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get("Nome Macchina", ""):
                        self.macchine_nomi.append(row)  # Salva l'intero dict, non solo il nome
        # Aggiorna la tabella se già creata
        if hasattr(self, 'frame_macchine'):
            for widget in self.frame_macchine.winfo_children():
                widget.destroy()
            self.setup_tab(self.frame_macchine, self.macchine_fieldnames, "Elenco_Macchine.csv")

    def setup_tab_opzioni(self, frame, fieldnames, default_csv):
        tree = ttk.Treeview(frame, columns=fieldnames, show="headings")
        for col in fieldnames:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        entry_frame = ttk.Frame(frame)
        entry_frame.pack(fill="x", padx=10, pady=5)
        entries = {}
        checkboxes = {}
        macchine_frame = None
        vincoli_button = None
        tipo_opzione_var = tk.StringVar(value="Stazione")
        for i, field in enumerate(fieldnames):
            ttk.Label(entry_frame, text=field).grid(row=0, column=i, padx=2, pady=2)
            if field == "Macchine Compatibili":
                macchine_frame = ttk.Frame(entry_frame)
                macchine_frame.grid(row=1, column=i, padx=2, pady=2)
                checkboxes.clear()
                for row in self.macchine_nomi:
                    nome = row["Nome Macchina"] if isinstance(row, dict) else row
                    var = tk.BooleanVar()
                    cb = ttk.Checkbutton(macchine_frame, text=nome, variable=var)
                    cb.pack(anchor="w")
                    checkboxes[nome] = var
                entries[field] = checkboxes
            elif field == "Costo Opzione":
                costo_entry = ttk.Entry(entry_frame)
                costo_entry.grid(row=1, column=i, padx=2, pady=2)
                entries[field] = costo_entry
                def apri_costi_dialog():
                    valori = [v.strip() for v in entries["Valori Possibili"].get().split(",") if v.strip()]
                    costi_attuali = entries["Costo Opzione"].get()
                    try:
                        costi_dict = json.loads(costi_attuali) if costi_attuali and costi_attuali.strip().startswith("{") else {v: costi_attuali for v in valori}
                    except Exception:
                        costi_dict = {v: "" for v in valori}
                    CostiDialog(entry_frame, valori, costi_dict, lambda d: (entries["Costo Opzione"].delete(0, tk.END), entries["Costo Opzione"].insert(0, json.dumps(d, ensure_ascii=False))))
                costi_button = ttk.Button(entry_frame, text="Modifica Costi", command=apri_costi_dialog)
                costi_button.grid(row=2, column=i, padx=2, pady=2)
            elif field == "Vincoli":
                vincoli_entry = ttk.Entry(entry_frame)
                vincoli_entry.grid(row=1, column=i, padx=2, pady=2)
                entries[field] = vincoli_entry
                def apri_vincoli_dialog():
                    opzione = entries["Opzione"].get()
                    valori_possibili = [v.strip() for v in entries["Valori Possibili"].get().split(",") if v.strip()]
                    vincoli_attuali = entries["Vincoli"].get()
                    try:
                        vincoli_dict = json.loads(vincoli_attuali) if vincoli_attuali else {}
                    except Exception:
                        vincoli_dict = {}
                    # Usa solo i nomi delle macchine per la dialog
                    macchine_nomi_str = [row["Nome Macchina"] if isinstance(row, dict) else row for row in self.macchine_nomi]
                    def on_save_vincoli(d):
                        entries["Vincoli"].delete(0, tk.END)
                        entries["Vincoli"].insert(0, json.dumps(d, ensure_ascii=False))
                        aggiorna_vincoli_e_riga()
                    VincoliDialog(entry_frame, macchine_nomi_str, valori_possibili, vincoli_dict, on_save_vincoli)
                vincoli_button = ttk.Button(entry_frame, text="Modifica Vincoli", command=apri_vincoli_dialog)
                vincoli_button.grid(row=2, column=i, padx=2, pady=2)
            elif field == "Posizioni Ammesse":
                posizioni_entry = ttk.Entry(entry_frame)
                posizioni_entry.grid(row=1, column=i, padx=2, pady=2)
                entries[field] = posizioni_entry
                def apri_posizioni_dialog():
                    opzione = entries["Opzione"].get()
                    macchine_compatibili = [m.strip() for m in entries["Macchine Compatibili"].keys() if entries["Macchine Compatibili"][m].get()]
                    if not macchine_compatibili:
                        messagebox.showwarning("Attenzione", "Seleziona almeno una macchina compatibile per questa opzione.")
                        return
                    posizioni_per_macchina = {}
                    for macchina in macchine_compatibili:
                        max_stazioni = 10
                        for row in self.macchine_nomi:
                            nome = row["Nome Macchina"] if isinstance(row, dict) else row
                            if nome == macchina:
                                try:
                                    max_stazioni = int(row.get("Max Stazioni", 10)) if isinstance(row, dict) and row.get("Max Stazioni") else 10
                                except Exception:
                                    max_stazioni = 10
                        posizioni_per_macchina[macchina] = [str(i+1) for i in range(max_stazioni)]
                    posizioni_attuali = entries["Posizioni Ammesse"].get()
                    try:
                        posizioni_dict = json.loads(posizioni_attuali) if posizioni_attuali else {}
                    except Exception:
                        posizioni_dict = {}
                    def on_save_posizioni(d):
                        entries["Posizioni Ammesse"].delete(0, tk.END)
                        entries["Posizioni Ammesse"].insert(0, json.dumps(d, ensure_ascii=False))
                        selected = tree.selection()
                        if selected:
                            idx = int(selected[0])
                            values = []
                            for f in fieldnames:
                                if f == "Macchine Compatibili":
                                    selezionate = [nome for nome, var in checkboxes.items() if var.get()]
                                    values.append(",".join(selezionate))
                                else:
                                    values.append(entries[f].get())
                            dati[idx] = dict(zip(fieldnames, values))
                            aggiorna_tabella()
                        else:
                            messagebox.showwarning("Attenzione", "Seleziona una riga da modificare prima di modificare le posizioni.")
                    PosizioniDialog(entry_frame, macchine_compatibili, posizioni_per_macchina, posizioni_dict, on_save_posizioni)
                posizioni_button = ttk.Button(entry_frame, text="Modifica Posizioni", command=apri_posizioni_dialog)
                posizioni_button.grid(row=2, column=i, padx=2, pady=2)
            elif field == "Tipo Opzione":
                tipo_combo = ttk.Combobox(entry_frame, textvariable=tipo_opzione_var, values=["Stazione", "Globale", "Uscita"], state="readonly", width=10)
                tipo_combo.grid(row=1, column=i, padx=2, pady=2)
                entries[field] = tipo_opzione_var
                # Precompila valori possibili se si seleziona "Uscita"
                def on_tipo_change(event=None):
                    if tipo_opzione_var.get() == "Uscita":
                        entries["Valori Possibili"].delete(0, tk.END)
                        entries["Valori Possibili"].insert(0, "canali standard, canali con flap, nastro")
                tipo_combo.bind("<<ComboboxSelected>>", on_tipo_change)
            else:
                entry = ttk.Entry(entry_frame)
                entry.grid(row=1, column=i, padx=2, pady=2)
                entries[field] = entry

        # Guida contestuale per la compilazione delle opzioni
        guida_label = ttk.Label(frame, text="Esempio: per opzioni con valori multipli o a due livelli, inserisci tutti i valori separati da virgola.\nEsempio Marposs: 'Cricche 1 sonda, Cricche 2 sonde, Cricche 4 sonde'.\nEsempio IBG: 'Cricche 1 sonda, Cricche 2 sonde, Cricche 4 sonde, Struttura Sonda, Struttura Forca, Struttura Bobina'.\nPoi usa 'Modifica Vincoli' per abilitare solo i valori ammessi per ogni macchina.", foreground="#003366", wraplength=700, justify="left")
        guida_label.pack(fill="x", padx=10, pady=(5,0))

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x", padx=10, pady=5)
        dati = []

        def aggiorna_tabella():
            tree.delete(*tree.get_children())
            for i, row in enumerate(dati):
                values = [row.get(f, "") for f in fieldnames]
                tree.insert("", "end", iid=i, values=values)

        def aggiungi_riga():
            values = []
            for f in fieldnames:
                if f == "Macchine Compatibili":
                    selezionate = [nome for nome, var in checkboxes.items() if var.get()]
                    values.append(",".join(selezionate))
                elif f == "Tipo Opzione":
                    values.append(tipo_opzione_var.get())
                else:
                    values.append(entries[f].get())
            if not values[0]:
                messagebox.showwarning("Attenzione", "Compila almeno il primo campo.")
                return
            dati.append(dict(zip(fieldnames, values)))
            aggiorna_tabella()
            for f in fieldnames:
                if f == "Macchine Compatibili":
                    for var in checkboxes.values():
                        var.set(False)
                elif f == "Tipo Opzione":
                    tipo_opzione_var.set("Stazione")
                else:
                    entries[f].delete(0, tk.END)

        def modifica_riga():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Attenzione", "Seleziona una riga da modificare.")
                return
            idx = int(selected[0])
            values = []
            for f in fieldnames:
                if f == "Macchine Compatibili":
                    selezionate = [nome for nome, var in checkboxes.items() if var.get()]
                    values.append(",".join(selezionate))
                elif f == "Tipo Opzione":
                    values.append(tipo_opzione_var.get())
                else:
                    values.append(entries[f].get())
            dati[idx] = dict(zip(fieldnames, values))
            aggiorna_tabella()

        # Aggiorna la riga selezionata quando si modifica il campo Vincoli
        def aggiorna_vincoli_e_riga():
            selected = tree.selection()
            if selected:
                idx = int(selected[0])
                values = []
                for f in fieldnames:
                    if f == "Macchine Compatibili":
                        selezionate = [nome for nome, var in checkboxes.items() if var.get()]
                        values.append(",".join(selezionate))
                    else:
                        values.append(entries[f].get())
                dati[idx] = dict(zip(fieldnames, values))
                aggiorna_tabella()

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x", padx=10, pady=5)
        dati = []

        def aggiorna_tabella():
            tree.delete(*tree.get_children())
            for i, row in enumerate(dati):
                values = [row.get(f, "") for f in fieldnames]
                tree.insert("", "end", iid=i, values=values)

        def aggiungi_riga():
            values = []
            for f in fieldnames:
                if f == "Macchine Compatibili":
                    selezionate = [nome for nome, var in checkboxes.items() if var.get()]
                    values.append(",".join(selezionate))
                else:
                    values.append(entries[f].get())
            if not values[0]:
                messagebox.showwarning("Attenzione", "Compila almeno il primo campo.")
                return
            dati.append(dict(zip(fieldnames, values)))
            aggiorna_tabella()
            for f in fieldnames:
                if f == "Macchine Compatibili":
                    for var in checkboxes.values():
                        var.set(False)
                else:
                    entries[f].delete(0, tk.END)

        def modifica_riga():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Attenzione", "Seleziona una riga da modificare.")
                return
            idx = int(selected[0])
            values = [entries[f].get() for f in fieldnames]
            dati[idx] = dict(zip(fieldnames, values))
            aggiorna_tabella()

        def elimina_riga():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Attenzione", "Seleziona una riga da eliminare.")
                return
            idx = int(selected[0])
            del dati[idx]
            aggiorna_tabella()

        def salva_csv():
            # Salva sempre sui file predefiniti
            path = os.path.join(os.path.dirname(__file__), default_csv)
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(dati)
            messagebox.showinfo("Salvataggio", f"CSV salvato su {os.path.basename(path)}.")

        def apri_csv():
            # Carica sempre dai file predefiniti
            path = os.path.join(os.path.dirname(__file__), default_csv)
            if not os.path.exists(path):
                messagebox.showwarning("Attenzione", f"File {os.path.basename(path)} non trovato.")
                return
            with open(path, "r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                dati.clear()
                dati.extend(reader)
            aggiorna_tabella()

        def on_select(event):
            selected = tree.selection()
            if not selected:
                return
            idx = int(selected[0])
            row = dati[idx]
            for f in fieldnames:
                if f == "Macchine Compatibili":
                    # Reset all
                    for var in checkboxes.values():
                        var.set(False)
                    compatibili = [x.strip() for x in row.get(f, "").split(",") if x.strip()]
                    for nome in compatibili:
                        if nome in checkboxes:
                            checkboxes[nome].set(True)
                elif f == "Tipo Opzione":
                    tipo_opzione_var.set(row.get(f, "Stazione"))
                else:
                    entries[f].delete(0, tk.END)
                    entries[f].insert(0, row.get(f, ""))

        ttk.Button(btn_frame, text="Aggiungi", command=aggiungi_riga).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="Modifica", command=modifica_riga).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="Elimina", command=elimina_riga).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="Salva CSV", command=salva_csv).pack(side="right", padx=2)
        ttk.Button(btn_frame, text="Apri CSV", command=apri_csv).pack(side="right", padx=2)

        tree.bind("<<TreeviewSelect>>", on_select)

    # La tab Macchine resta invariata
    def setup_tab(self, frame, fieldnames, default_csv):
        tree = ttk.Treeview(frame, columns=fieldnames, show="headings")
        for col in fieldnames:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        entry_frame = ttk.Frame(frame)
        entry_frame.pack(fill="x", padx=10, pady=5)
        entries = {}
        for i, field in enumerate(fieldnames):
            ttk.Label(entry_frame, text=field).grid(row=0, column=i, padx=2, pady=2)
            entry = ttk.Entry(entry_frame)
            entry.grid(row=1, column=i, padx=2, pady=2)
            entries[field] = entry

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x", padx=10, pady=5)
        dati = []

        def aggiorna_tabella():
            tree.delete(*tree.get_children())
            for i, row in enumerate(dati):
                values = [row.get(f, "") for f in fieldnames]
                tree.insert("", "end", iid=i, values=values)

        def aggiungi_riga():
            values = [entries[f].get() for f in fieldnames]
            if not values[0]:
                messagebox.showwarning("Attenzione", "Compila almeno il primo campo.")
                return
            dati.append(dict(zip(fieldnames, values)))
            aggiorna_tabella()
            for entry in entries.values():
                entry.delete(0, tk.END)

        def modifica_riga():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Attenzione", "Seleziona una riga da modificare.")
                return
            idx = int(selected[0])
            values = [entries[f].get() for f in fieldnames]
            dati[idx] = dict(zip(fieldnames, values))
            aggiorna_tabella()

        def elimina_riga():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Attenzione", "Seleziona una riga da eliminare.")
                return
            idx = int(selected[0])
            del dati[idx]
            aggiorna_tabella()

        def salva_csv():
            # Salva sempre sui file predefiniti
            path = os.path.join(os.path.dirname(__file__), default_csv)
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(dati)
            messagebox.showinfo("Salvataggio", f"CSV salvato su {os.path.basename(path)}.")

        def apri_csv():
            # Carica sempre dai file predefiniti
            path = os.path.join(os.path.dirname(__file__), default_csv)
            if not os.path.exists(path):
                messagebox.showwarning("Attenzione", f"File {os.path.basename(path)} non trovato.")
                return
            with open(path, "r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                dati.clear()
                dati.extend(reader)
            aggiorna_tabella()

        def on_select(event):
            selected = tree.selection()
            if not selected:
                return
            idx = int(selected[0])
            row = dati[idx]
            for f in fieldnames:
                entries[f].delete(0, tk.END)
                entries[f].insert(0, row.get(f, ""))

        ttk.Button(btn_frame, text="Aggiungi", command=aggiungi_riga).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="Modifica", command=modifica_riga).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="Elimina", command=elimina_riga).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="Salva CSV", command=salva_csv).pack(side="right", padx=2)
        ttk.Button(btn_frame, text="Apri CSV", command=apri_csv).pack(side="right", padx=2)

        # Funzione per aggiornare dinamicamente le checkbox delle macchine compatibili e le posizioni ammesse
    def aggiorna_macchine_e_checkbox(self):
        # Ricarica le macchine e aggiorna le checkbox in Opzioni
        self.carica_macchine()
        # Aggiorna le checkbox solo se la tab Opzioni è attiva
        if hasattr(self, 'frame_opzioni'):
            for widget in self.frame_opzioni.winfo_children():
                if isinstance(widget, ttk.Frame):
                    for child in widget.winfo_children():
                        if isinstance(child, ttk.Frame):
                            # Trova il frame delle checkbox
                            for cb in child.winfo_children():
                                cb.destroy()
                            # Ricrea le checkbox
                            for row in self.macchine_nomi:
                                nome = row["Nome Macchina"] if isinstance(row, dict) else row
                                var = tk.BooleanVar()
                                cb = ttk.Checkbutton(child, text=nome, variable=var)
                                cb.pack(anchor="w")
            # Nota: per una sincronizzazione completa, servirebbe anche aggiornare le entry e i dati associati

    # Modifica in setup_tab per chiamare aggiorna_macchine_e_checkbox dopo ogni modifica alle macchine
    def setup_tab(self, frame, fieldnames, default_csv):
        tree = ttk.Treeview(frame, columns=fieldnames, show="headings")
        for col in fieldnames:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        entry_frame = ttk.Frame(frame)
        entry_frame.pack(fill="x", padx=10, pady=5)
        entries = {}
        for i, field in enumerate(fieldnames):
            ttk.Label(entry_frame, text=field).grid(row=0, column=i, padx=2, pady=2)
            entry = ttk.Entry(entry_frame)
            entry.grid(row=1, column=i, padx=2, pady=2)
            entries[field] = entry

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x", padx=10, pady=5)
        dati = []

        def aggiorna_tabella():
            tree.delete(*tree.get_children())
            for i, row in enumerate(dati):
                values = [row.get(f, "") for f in fieldnames]
                tree.insert("", "end", iid=i, values=values)

        def aggiungi_riga():
            values = [entries[f].get() for f in fieldnames]
            if not values[0]:
                messagebox.showwarning("Attenzione", "Compila almeno il primo campo.")
                return
            dati.append(dict(zip(fieldnames, values)))
            aggiorna_tabella()
            for entry in entries.values():
                entry.delete(0, tk.END)

        def modifica_riga():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Attenzione", "Seleziona una riga da modificare.")
                return
            idx = int(selected[0])
            values = [entries[f].get() for f in fieldnames]
            dati[idx] = dict(zip(fieldnames, values))
            aggiorna_tabella()

        def elimina_riga():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Attenzione", "Seleziona una riga da eliminare.")
                return
            idx = int(selected[0])
            del dati[idx]
            aggiorna_tabella()

        def salva_csv():
            # Salva sempre sui file predefiniti
            path = os.path.join(os.path.dirname(__file__), default_csv)
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(dati)
            messagebox.showinfo("Salvataggio", f"CSV salvato su {os.path.basename(path)}.")

        def apri_csv():
            # Carica sempre dai file predefiniti
            path = os.path.join(os.path.dirname(__file__), default_csv)
            if not os.path.exists(path):
                messagebox.showwarning("Attenzione", f"File {os.path.basename(path)} non trovato.")
                return
            with open(path, "r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                dati.clear()
                dati.extend(reader)
            aggiorna_tabella()

        def on_select(event):
            selected = tree.selection()
            if not selected:
                return
            idx = int(selected[0])
            row = dati[idx]
            for f in fieldnames:
                entries[f].delete(0, tk.END)
                entries[f].insert(0, row.get(f, ""))

        ttk.Button(btn_frame, text="Aggiungi", command=aggiungi_riga).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="Modifica", command=modifica_riga).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="Elimina", command=elimina_riga).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="Salva CSV", command=salva_csv).pack(side="right", padx=2)
        ttk.Button(btn_frame, text="Apri CSV", command=apri_csv).pack(side="right", padx=2)

        tree.bind("<<TreeviewSelect>>", on_select)

class VincoliDialog(tk.Toplevel):
    def __init__(self, parent, macchine, valori, vincoli_dict, on_save):
        super().__init__(parent)
        self.title("Modifica Vincoli")
        self.vincoli = {m: set(v) for m, v in vincoli_dict.items()}
        self.macchine = macchine
        self.valori = valori
        self.on_save = on_save
        self.vars = {}  # (macchina, valore) -> tk.BooleanVar
        ttk.Label(self, text="Seleziona i valori ammessi per ogni macchina:").pack(pady=5)
        frame = ttk.Frame(self)
        frame.pack(padx=10, pady=10)
        for i, macchina in enumerate(macchine):
            ttk.Label(frame, text=macchina).grid(row=i, column=0, sticky="w")
            for j, valore in enumerate(valori):
                var = tk.BooleanVar(value=macchina in self.vincoli and valore in self.vincoli[macchina])
                cb = ttk.Checkbutton(frame, text=valore, variable=var)
                cb.grid(row=i, column=j+1, sticky="w")
                self.vars[(macchina, valore)] = var
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="Salva", command=self.salva).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Annulla", command=self.destroy).pack(side="left", padx=5)
    def salva(self):
        result = {}
        for macchina in self.macchine:
            valori = [valore for valore in self.valori if self.vars[(macchina, valore)].get()]
            if valori:
                result[macchina] = valori
        self.on_save(result)
        self.destroy()

class PosizioniDialog(tk.Toplevel):
    def __init__(self, parent, macchine, posizioni_per_macchina, posizioni_dict, on_save):
        super().__init__(parent)
        self.title("Modifica Posizioni Ammesse")
        self.posizioni = {m: set(p) for m, p in posizioni_dict.items()}
        self.macchine = macchine
        self.posizioni_per_macchina = posizioni_per_macchina
        self.on_save = on_save
        self.vars = {}  # (macchina, posizione) -> tk.BooleanVar
        ttk.Label(self, text="Seleziona le posizioni ammesse per ogni macchina:").pack(pady=5)
        frame = ttk.Frame(self)
        frame.pack(padx=10, pady=10)
        for i, macchina in enumerate(macchine):
            ttk.Label(frame, text=macchina).grid(row=i, column=0, sticky="w")
            posizioni = self.posizioni_per_macchina.get(macchina, [str(j+1) for j in range(10)])
            for j, posizione in enumerate(posizioni):
                var = tk.BooleanVar(value=macchina in self.posizioni and posizione in self.posizioni[macchina])
                cb = ttk.Checkbutton(frame, text=posizione, variable=var)
                cb.grid(row=i, column=j+1, sticky="w")
                self.vars[(macchina, posizione)] = var
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="Salva", command=self.salva).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Annulla", command=self.destroy).pack(side="left", padx=5)
    def salva(self):
        result = {}
        for macchina in self.macchine:
            posizioni = [posizione for posizione in self.posizioni_per_macchina.get(macchina, []) if self.vars[(macchina, posizione)].get()]
            if posizioni:
                result[macchina] = posizioni
        self.on_save(result)
        self.destroy()

class CostiDialog(tk.Toplevel):
    def __init__(self, parent, valori, costi_dict, on_save):
        super().__init__(parent)
        self.title("Modifica Costi per Valore")
        self.valori = valori
        self.costi_dict = costi_dict.copy()
        self.on_save = on_save
        self.vars = {}
        frame = ttk.Frame(self)
        frame.pack(padx=10, pady=10)
        for i, valore in enumerate(valori):
            ttk.Label(frame, text=valore).grid(row=i, column=0, sticky="w")
            var = tk.StringVar(value=str(costi_dict.get(valore, "")))
            entry = ttk.Entry(frame, textvariable=var, width=10)
            entry.grid(row=i, column=1, sticky="w")
            self.vars[valore] = var
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="Salva", command=self.salva).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Annulla", command=self.destroy).pack(side="left", padx=5)
    def salva(self):
        result = {v: self.vars[v].get() for v in self.valori if self.vars[v].get()}
        self.on_save(result)
        self.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ConfiguratoreApp(root)
    root.mainloop()