import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os
import json

MACCHINE_CSV = os.path.join(os.path.dirname(__file__), "Elenco_Macchine.csv")
OPZIONI_CSV = os.path.join(os.path.dirname(__file__), "Elenco_Opzioni.csv")

class ConfiguraMacchinaApp:
    def __init__(self, master):
        self.master = master
        master.title("Configura Macchina")

        # Carica dati
        self.macchine = self.carica_macchine()
        self.opzioni = self.carica_opzioni()

        # Selezione macchina
        ttk.Label(master, text="Seleziona Macchina:").pack(pady=5)
        self.macchina_var = tk.StringVar()
        self.macchina_combo = ttk.Combobox(master, textvariable=self.macchina_var, values=[m['Nome Macchina'] for m in self.macchine], state="readonly")
        self.macchina_combo.pack(pady=5)
        self.macchina_combo.bind("<<ComboboxSelected>>", self.aggiorna_opzioni)

        # Frame per le opzioni
        self.opzioni_frame = ttk.Frame(master)
        self.opzioni_frame.pack(padx=10, pady=10, fill="x")
        self.opzioni_widgets = []

        # Bottone per mostrare configurazione
        ttk.Button(master, text="Mostra Configurazione", command=self.mostra_configurazione).pack(pady=10)

    def carica_macchine(self):
        macchine = []
        with open(MACCHINE_CSV, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                macchine.append(row)
        return macchine

    def carica_opzioni(self):
        opzioni = []
        with open(OPZIONI_CSV, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                opzioni.append(row)
        return opzioni

    def aggiorna_opzioni(self, event=None):
        for widget in self.opzioni_widgets:
            widget.destroy()
        self.opzioni_widgets.clear()
        macchina = self.macchina_var.get()
        if not macchina:
            return
        macchina_dict = next((m for m in self.macchine if m['Nome Macchina'] == macchina), None)
        max_stazioni = int(macchina_dict['Max Stazioni']) if macchina_dict and macchina_dict.get('Max Stazioni') else 10
        # Sezione opzioni globali
        opzioni_globali = [o for o in self.opzioni if o.get('Tipo Opzione', 'Stazione') == 'Globale' and macchina in o['Macchine Compatibili'].split(",")]
        if opzioni_globali:
            globali_frame = ttk.LabelFrame(self.opzioni_frame, text="Opzioni Globali (per tutta la macchina)")
            globali_frame.pack(fill="x", pady=5)
            globali_label = ttk.Label(globali_frame, text="Seleziona le opzioni globali (valgono per tutta la macchina):", font=("Arial", 10, "bold"))
            globali_label.pack(anchor="w", padx=5, pady=(2,4))
            self.globali_vars = []  # lista di tuple (opzione, var, valore_var)
            for opzione_dict in opzioni_globali:
                opzione = opzione_dict['Opzione']
                var = tk.BooleanVar()
                cb = ttk.Checkbutton(globali_frame, text=opzione, variable=var)
                cb.pack(side="left", padx=2)
                valori = [v.strip() for v in opzione_dict.get('Valori Possibili', '').split(',') if v.strip()]
                vincoli = {}
                try:
                    vincoli = json.loads(opzione_dict.get('Vincoli', '{}'))
                except Exception:
                    pass
                valori_filtrati = valori
                if macchina in vincoli:
                    valori_filtrati = [v for v in valori if v in vincoli[macchina]]
                valore_var = tk.StringVar()
                if valori_filtrati:
                    valori_combo = ttk.Combobox(globali_frame, textvariable=valore_var, values=valori_filtrati, state="readonly", width=12)
                    valori_combo.pack(side="left", padx=1)
                self.globali_vars.append((opzione, var, valore_var))
        else:
            self.globali_vars = []
        # Per ogni stazione, permetti la selezione multipla di opzioni (checkbox)
        self.stazioni_opzioni_vars = []  # lista di liste di tk.BooleanVar
        self.stazioni_valori_vars = []   # lista di liste di tk.StringVar
        opzioni_compatibili = sorted(
            [o for o in self.opzioni if macchina in o['Macchine Compatibili'].split(",")],
            key=lambda x: x['Opzione'].lower()
        )
        self.opzioni_compatibili = {o['Opzione']: o for o in opzioni_compatibili}
        for i in range(max_stazioni):
            row_frame = ttk.Frame(self.opzioni_frame)
            row_frame.pack(fill="x", pady=2)
            label = ttk.Label(row_frame, text=f"Stazione {i+1}")
            label.pack(side="left", padx=5)
            opzione_vars = []
            valore_vars = []
            for opzione_dict in opzioni_compatibili:
                opzione = opzione_dict['Opzione']
                var = tk.BooleanVar()
                cb = ttk.Checkbutton(row_frame, text=opzione, variable=var)
                cb.pack(side="left", padx=2)
                opzione_vars.append((opzione, var))
                # Valori possibili per questa opzione
                valori = [v.strip() for v in opzione_dict.get('Valori Possibili', '').split(',') if v.strip()]
                vincoli = {}
                try:
                    vincoli = json.loads(opzione_dict.get('Vincoli', '{}'))
                except Exception:
                    pass
                valori_filtrati = valori
                if macchina in vincoli:
                    valori_filtrati = [v for v in valori if v in vincoli[macchina]]
                valore_var = tk.StringVar()
                valori_combo = ttk.Combobox(row_frame, textvariable=valore_var, values=valori_filtrati, state="readonly", width=12)
                valori_combo.pack(side="left", padx=1)
                valore_vars.append((opzione, valore_var))
            self.stazioni_opzioni_vars.append(opzione_vars)
            self.stazioni_valori_vars.append(valore_vars)
        # Istruzioni generali
        istruzioni = (
            "1. Seleziona la macchina da configurare.\n"
            "2. Scegli le opzioni globali (se presenti) che valgono per tutta la macchina.\n"
            "3. Per ogni stazione, seleziona le opzioni e i valori desiderati.\n"
            "4. Premi 'Mostra Configurazione' per vedere il riepilogo."
        )
        istruzioni_label = ttk.Label(self.opzioni_frame, text=istruzioni, foreground="#003366", wraplength=700, justify="left", font=("Arial", 10, "bold"))
        istruzioni_label.pack(fill="x", pady=(0,8))
        # Label sopra le stazioni
        stazioni_label = ttk.Label(self.opzioni_frame, text="Configura le opzioni per ogni stazione:", font=("Arial", 10, "bold"))
        stazioni_label.pack(anchor="w", pady=(10,2))

    def mostra_configurazione(self):
        macchina = self.macchina_var.get()
        if not macchina:
            messagebox.showwarning("Attenzione", "Seleziona una macchina.")
            return
        config = f"\n=== CONFIGURAZIONE MACCHINA ===\n\nMacchina: {macchina}\n"
        # Opzioni globali
        if hasattr(self, 'globali_vars') and self.globali_vars:
            config += "\nOpzioni globali:\n"
            for opzione, var, valore_var in self.globali_vars:
                if var.get():
                    valore = valore_var.get()
                    prezzo = ""
                    # Cerca il prezzo per il valore selezionato
                    opzione_dict = self.opzioni_compatibili.get(opzione)
                    if opzione_dict:
                        costi = opzione_dict.get('Costo Opzione', '').strip()
                        try:
                            costi_dict = json.loads(costi) if costi and costi.startswith('{') else {v.strip(): costi for v in opzione_dict.get('Valori Possibili', '').split(',') if v.strip()}
                        except Exception:
                            costi_dict = {v.strip(): '' for v in opzione_dict.get('Valori Possibili', '').split(',') if v.strip()}
                        if valore:
                            prezzo = costi_dict.get(valore, '')
                        else:
                            prezzo = list(costi_dict.values())[0] if costi_dict else ''
                    if valore:
                        config += f"  - {opzione} ({valore})"
                    else:
                        config += f"  - {opzione}"
                    if prezzo:
                        config += f"   [{prezzo} €]"
                    config += "\n"
        # Opzioni per stazione
        for i, (opzioni_vars, valori_vars) in enumerate(zip(self.stazioni_opzioni_vars, self.stazioni_valori_vars)):
            stazione_descr = []
            for (opzione, var), (_, valore_var) in zip(opzioni_vars, valori_vars):
                if var.get():
                    valore = valore_var.get()
                    prezzo = ""
                    opzione_dict = self.opzioni_compatibili.get(opzione)
                    if opzione_dict:
                        costi = opzione_dict.get('Costo Opzione', '').strip()
                        try:
                            costi_dict = json.loads(costi) if costi and costi.startswith('{') else {v.strip(): costi for v in opzione_dict.get('Valori Possibili', '').split(',') if v.strip()}
                        except Exception:
                            costi_dict = {v.strip(): '' for v in opzione_dict.get('Valori Possibili', '').split(',') if v.strip()}
                        if valore:
                            prezzo = costi_dict.get(valore, '')
                        else:
                            prezzo = list(costi_dict.values())[0] if costi_dict else ''
                    if valore:
                        descr = f"{opzione} ({valore})"
                    else:
                        descr = f"{opzione}"
                    if prezzo:
                        descr += f"   [{prezzo} €]"
                    stazione_descr.append(descr)
            if stazione_descr:
                config += f"\nStazione {i+1}:\n  - " + "\n  - ".join(stazione_descr) + "\n"
            else:
                config += f"\nStazione {i+1}: nessuna opzione selezionata\n"
        messagebox.showinfo("Configurazione", config)

if __name__ == "__main__":
    root = tk.Tk()
    app = ConfiguraMacchinaApp(root)
    root.mainloop()
