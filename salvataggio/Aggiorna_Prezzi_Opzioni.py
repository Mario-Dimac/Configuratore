import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv
import os
import json

CSV_PATH = os.path.join(os.path.dirname(__file__), "Elenco_Opzioni.csv")

class PrezziOpzioniApp:
    def __init__(self, master):
        self.master = master
        master.title("Aggiorna Prezzi Opzioni")
        self.dati = []  # Lista di dict per ogni opzione
        self.rows = []  # (opzione, valore, prezzo_var, row_idx, prezzo_orig)
        self.load_csv()
        self.setup_ui()

    def load_csv(self):
        self.dati.clear()
        if not os.path.exists(CSV_PATH):
            messagebox.showerror("Errore", f"File {CSV_PATH} non trovato.")
            return
        with open(CSV_PATH, "r", newline="", encoding="utf-8") as f:
            # Salta eventuali righe di commento o vuote all'inizio
            while True:
                pos = f.tell()
                line = f.readline()
                if not line:
                    return  # file vuoto
                if line.strip().lower().startswith("opzione,"):
                    f.seek(pos)
                    break
            reader = csv.DictReader(f)
            for row in reader:
                # Salta righe vuote o incomplete
                if not row.get("Opzione") or not row.get("Valori Possibili"):
                    continue
                self.dati.append(row)

    def setup_ui(self):
        frame = ttk.Frame(self.master)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        self.inner_frame = ttk.Frame(canvas)
        self.inner_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set, height=500)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        # Intestazioni
        ttk.Label(self.inner_frame, text="Opzione", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=2, pady=2)
        ttk.Label(self.inner_frame, text="Valore", font=("Arial", 10, "bold")).grid(row=0, column=1, padx=2, pady=2)
        ttk.Label(self.inner_frame, text="Prezzo", font=("Arial", 10, "bold")).grid(row=0, column=2, padx=2, pady=2)
        self.rows.clear()
        row_idx = 1
        for opzione in self.dati:
            valori = [v.strip() for v in opzione["Valori Possibili"].split(",") if v.strip()]
            costi = opzione["Costo Opzione"].strip()
            try:
                costi_dict = json.loads(costi) if costi and costi.startswith("{") else {v: costi for v in valori}
            except Exception:
                costi_dict = {v: "" for v in valori}
            for valore in valori:
                prezzo_var = tk.StringVar(value=str(costi_dict.get(valore, "")))
                ttk.Label(self.inner_frame, text=opzione["Opzione"]).grid(row=row_idx, column=0, padx=2, pady=2)
                ttk.Label(self.inner_frame, text=valore).grid(row=row_idx, column=1, padx=2, pady=2)
                entry = ttk.Entry(self.inner_frame, textvariable=prezzo_var, width=10)
                entry.grid(row=row_idx, column=2, padx=2, pady=2)
                self.rows.append((opzione, valore, prezzo_var, row_idx, costi_dict.get(valore, "")))
                row_idx += 1
        btn = ttk.Button(self.master, text="Salva Prezzi", command=self.salva_prezzi)
        btn.pack(pady=10)

    def salva_prezzi(self):
        # Ricostruisci la struttura costi per ogni opzione
        opzione_to_valori = {}
        for opzione, valore, prezzo_var, _, _ in self.rows:
            key = opzione["Opzione"]
            if key not in opzione_to_valori:
                opzione_to_valori[key] = {"row": opzione, "valori": {}}
            opzione_to_valori[key]["valori"][valore] = prezzo_var.get()
        # Aggiorna i dati
        for opzione_key, info in opzione_to_valori.items():
            opzione_row = info["row"]
            valori = [v.strip() for v in opzione_row["Valori Possibili"].split(",") if v.strip()]
            costi_dict = {v: info["valori"][v] for v in valori if info["valori"][v]}
            if len(costi_dict) == 1:
                # Se c'è un solo valore, salva come numero semplice
                opzione_row["Costo Opzione"] = list(costi_dict.values())[0]
            else:
                opzione_row["Costo Opzione"] = json.dumps(costi_dict, ensure_ascii=False)
        # Salva su CSV SOLO se ci sono dati
        if self.dati:
            with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=self.dati[0].keys())
                writer.writeheader()
                writer.writerows(self.dati)
            messagebox.showinfo("Salvataggio", "Prezzi aggiornati su Elenco_Opzioni.csv.")
        else:
            messagebox.showerror("Errore", "Nessun dato da salvare!")

if __name__ == "__main__":
    root = tk.Tk()
    app = PrezziOpzioniApp(root)
    root.mainloop()
