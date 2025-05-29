import csv
import ast
import os
import tkinter as tk
from tkinter import filedialog, messagebox
import json

# Percorsi file
DIR = os.path.dirname(__file__)
PATH_OPZIONI = os.path.join(DIR, "Elenco_Opzioni.csv")
PROPOSTE_DIR = os.path.join(DIR, "Proposte")

# Carica vincoli dal CSV opzioni
# Restituisce lista di tuple: (macchina, valori_vincolo, valori_posizione)
def carica_vincoli():
    vincoli = []
    print("\nIntestazioni CSV:")
    with open(PATH_OPZIONI, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        print(reader.fieldnames)
        print("\nValori colonna 'Tipo Opzione' trovati:")
        tipi_opzione = set()
        for row in reader:
            val = row.get("Tipo Opzione")
            if val is not None:
                tipi_opzione.add(val.strip())
            else:
                tipi_opzione.add("<manca>")
        print(tipi_opzione)
    # Rilettura per parsing effettivo
    with open(PATH_OPZIONI, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        print("\nVincoli caricati dal file:")
        for row in reader:
            tipo_opz = row.get("Tipo Opzione")
            if tipo_opz is not None and tipo_opz.strip().lower() == "vincolo":
                vincoli_raw = row.get("Vincoli", "")
                posizioni_raw = row.get("Posizioni Ammesse", "")
                try:
                    vincoli_dict = json.loads(vincoli_raw) if vincoli_raw else {}
                except Exception:
                    import ast
                    vincoli_dict = ast.literal_eval(vincoli_raw) if vincoli_raw else {}
                try:
                    posizioni_dict = json.loads(posizioni_raw) if posizioni_raw else {}
                except Exception:
                    import ast
                    posizioni_dict = ast.literal_eval(posizioni_raw) if posizioni_raw else {}
                for macchina, valori_vincolo in vincoli_dict.items():
                    valori_posizione = posizioni_dict.get(macchina, [])
                    vincoli.append((macchina, valori_vincolo, valori_posizione))
                    # Stampa il vincolo letto
                    print(f"- Macchina: {macchina} | Vincoli: {valori_vincolo} | Posizioni vietate: {valori_posizione}")
    print("\nPrime 5 righe del file CSV:")
    with open(PATH_OPZIONI, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            print(row)
            if i >= 4:
                break
    return vincoli

# Permetti selezione file configurazione
# Restituisce path file selezionato
def scegli_file_configurazione():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Seleziona la configurazione macchina da verificare",
        initialdir=PROPOSTE_DIR,
        filetypes=[("CSV", "*.csv")]
    )
    return file_path

def scegli_file_configurazione_gui():
    def on_browse():
        file_path = filedialog.askopenfilename(
            title="Seleziona la configurazione macchina da verificare",
            initialdir=PROPOSTE_DIR,
            filetypes=[("CSV", "*.csv")]
        )
        if file_path:
            entry_file.delete(0, tk.END)
            entry_file.insert(0, file_path)

    def on_ok():
        nonlocal selected_file
        selected_file = entry_file.get()
        root.destroy()

    selected_file = None
    root = tk.Tk()
    root.title("Verifica Vincoli Configurazione")
    root.geometry("600x120")
    tk.Label(root, text="Seleziona il file di configurazione da verificare:").pack(pady=10)
    frame = tk.Frame(root)
    frame.pack(pady=5)
    entry_file = tk.Entry(frame, width=60)
    entry_file.pack(side=tk.LEFT, padx=5)
    tk.Button(frame, text="Sfoglia...", command=on_browse).pack(side=tk.LEFT)
    tk.Button(root, text="Verifica", command=on_ok, width=15).pack(pady=10)
    root.mainloop()
    return selected_file

# Carica configurazione proposta (ritorna dict: stazione -> {opzione: valore})
def carica_configurazione(path):
    selezioni = {}
    with open(path, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            stazione = row.get("Stazione") or row.get("stazione") or row.get("Posizione") or row.get("posizione")
            if not stazione:
                continue
            opzioni_raw = row.get("Opzioni Selezionate", "")
            selezioni[stazione] = {}
            if opzioni_raw and opzioni_raw.lower() != "(nessuna opzione selezionata)":
                for s in opzioni_raw.split(","):
                    s = s.strip()
                    if not s:
                        continue
                    if ":" in s:
                        opz, val = [x.strip() for x in s.split(":", 1)]
                        selezioni[stazione][normalizza(opz)] = normalizza(val)
                    else:
                        selezioni[stazione][normalizza(s)] = True
            for k, v in row.items():
                if k.lower() not in ("stazione", "posizione", "opzioni selezionate") and v and v.lower() != "(nessuna opzione selezionata)":
                    selezioni[stazione][normalizza(k.strip())] = normalizza(v.strip())
    return selezioni

def normalizza(x):
    if not isinstance(x, str):
        return x
    return ' '.join(x.strip().lower().split())

# Controlla i vincoli per la macchina e la configurazione
def controlla_vincoli(macchina, selezioni, vincoli):
    violazioni = []
    valori_selezionati = set()
    for opzdict in selezioni.values():
        for opz, val in opzdict.items():
            if isinstance(val, bool):
                valori_selezionati.add(normalizza(opz))
            else:
                valori_selezionati.add(normalizza(opz))
                valori_selezionati.add(normalizza(val))
    for macchina_v, valori_vincolo, valori_posizione in vincoli:
        if macchina_v.upper() != macchina.upper():
            continue
        trovato_vincolo = any(normalizza(v) in valori_selezionati for v in valori_vincolo)
        trovato_posizione = any(normalizza(p) in valori_selezionati for p in valori_posizione)
        if valori_vincolo and valori_posizione and trovato_vincolo and trovato_posizione:
            violazioni.append(("GLOBALE", valori_vincolo, valori_posizione))
    return violazioni

if __name__ == "__main__":
    print("--- Verifica Vincoli Configurazione ---")
    config_path = scegli_file_configurazione_gui()
    if not config_path:
        print("Nessun file selezionato. Uscita.")
        exit(0)
    macchina = os.path.basename(config_path).split("_")[0].upper()
    selezioni = carica_configurazione(config_path)
    vincoli = carica_vincoli()
    violazioni = controlla_vincoli(macchina, selezioni, vincoli)
    if violazioni:
        msg = f"ATTENZIONE: Configurazione NON ammessa per la macchina '{macchina}'.\n\n"
        for stz, valori_vincolo, valori_posizione in violazioni:
            msg += f"- Stazione {stz}: Vincolo: {', '.join(valori_vincolo)} NON compatibile con {', '.join(valori_posizione)}\n"
        print(msg)
        try:
            root = tk.Tk(); root.withdraw()
            messagebox.showwarning("Vincoli configurazione", msg)
        except Exception:
            pass
    else:
        print(f"Configurazione OK per la macchina '{macchina}'. Nessun vincolo violato.")
        try:
            root = tk.Tk(); root.withdraw()
            messagebox.showinfo("OK", f"Configurazione OK per la macchina '{macchina}'. Nessun vincolo violato.")
        except Exception:
            pass
