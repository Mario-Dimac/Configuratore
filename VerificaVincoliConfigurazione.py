import csv
import ast
import os
import tkinter as tk
from tkinter import filedialog, messagebox
import json
import logging
import sys

# Carica vincoli da file JSON (vincoli_macchine.json)
def carica_vincoli_json(path_json, macchina):
    with open(path_json, encoding="utf-8") as f:
        data = json.load(f)
    # Restituisce solo i vincoli della macchina richiesta, come lista di dict
    return data.get(macchina, [])

if __name__ == "__main__":
    logging.info("--- Verifica Vincoli Configurazione ---")
    print("--- Verifica Vincoli Configurazione ---")
    try:
        # Percorsi file
        DIR = os.path.dirname(__file__)
        PROPOSTE_DIR = os.path.join(DIR, "Proposte")
        # Utility: get a single hidden Tk root for all dialogs
        _tk_root = None
        def get_tk_root():
            global _tk_root
            if _tk_root is None:
                _tk_root = tk.Tk()
                _tk_root.withdraw()
            return _tk_root
        # Dialog per selezionare file configurazione
        def scegli_file_configurazione_gui():
            def on_browse():
                file_path = filedialog.askopenfilename(
                    title="Seleziona la configurazione macchina da verificare",
                    initialdir=PROPOSTE_DIR,
                    filetypes=[("CSV", "*.csv")],
                    parent=dialog
                )
                if file_path:
                    entry_file.delete(0, tk.END)
                    entry_file.insert(0, file_path)
            def on_ok():
                nonlocal selected_file
                selected_file = entry_file.get()
                dialog.destroy()
            def on_cancel():
                nonlocal selected_file
                selected_file = None
                dialog.destroy()
            selected_file = None
            root = get_tk_root()
            dialog = tk.Toplevel(root)
            dialog.title("Verifica Vincoli Configurazione")
            dialog.geometry("600x120")
            dialog.grab_set()
            tk.Label(dialog, text="Seleziona il file di configurazione da verificare:").pack(pady=10)
            frame = tk.Frame(dialog)
            frame.pack(pady=5)
            entry_file = tk.Entry(frame, width=60)
            entry_file.pack(side=tk.LEFT, padx=5)
            tk.Button(frame, text="Sfoglia...", command=on_browse).pack(side=tk.LEFT)
            tk.Button(dialog, text="Verifica", command=on_ok, width=15).pack(pady=10)
            tk.Button(dialog, text="Annulla", command=on_cancel, width=10).pack(pady=2)
            dialog.protocol("WM_DELETE_WINDOW", on_cancel)
            dialog.wait_window()
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
        def controlla_vincoli_condizionali(macchina, selezioni, vincoli):
            violazioni = []
            for macchina_v, valori_vincolo, _ in vincoli:
                if macchina_v.upper() != macchina.upper():
                    continue
                if isinstance(valori_vincolo, list):
                    for vincolo in valori_vincolo:
                        se = vincolo.get("se", {})
                        vietato = vincolo.get("vietato", {})
                        stz_se = se.get("stazione")
                        opz_se = normalizza(se.get("opzione", ""))
                        val_se = normalizza(se.get("valore", ""))
                        stz_viet = vietato.get("stazione")
                        opz_viet = normalizza(vietato.get("opzione", ""))
                        val_viet = normalizza(vietato.get("valore", ""))
                        if stz_se in selezioni and selezioni[stz_se].get(opz_se) == val_se:
                            if stz_viet in selezioni and selezioni[stz_viet].get(opz_viet) == val_viet:
                                violazioni.append(f"Se in {stz_se} c'è {opz_se}: {val_se}, in {stz_viet} non può esserci {opz_viet}: {val_viet}")
            return violazioni
        # --- INIZIO LOGICA PRINCIPALE ---
        root = get_tk_root()
        vincoli_json_path = filedialog.askopenfilename(
            title="Seleziona il file dei vincoli (vincoli_macchine.json)",
            initialdir=DIR,
            filetypes=[("JSON", "*.json")],
            parent=root
        )
        if not vincoli_json_path:
            logging.error("Nessun file vincoli selezionato. Uscita.")
            print("Nessun file vincoli selezionato. Uscita.")
            try:
                messagebox.showerror("Errore", "Nessun file vincoli selezionato. Il programma verrà chiuso.", parent=root)
            except Exception:
                pass
            sys.exit(0)
        config_path = scegli_file_configurazione_gui()
        logging.info(f"File configurazione selezionato: {config_path}")
        if not config_path:
            logging.error("Nessun file selezionato. Uscita.")
            print("Nessun file selezionato. Uscita.")
            try:
                messagebox.showerror("Errore", "Nessun file di configurazione selezionato. Il programma verrà chiuso.", parent=root)
            except Exception:
                pass
            sys.exit(0)
        macchina = os.path.basename(config_path).split("_")[0].upper()
        logging.info(f"Macchina: {macchina}")
        logging.info("PRIMA di carica_configurazione")
        selezioni = carica_configurazione(config_path)
        logging.info("DOPO carica_configurazione")
        logging.debug(f"Selezioni: {selezioni}")
        logging.info("PRIMA di carica_vincoli (JSON)")
        vincoli = carica_vincoli_json(vincoli_json_path, macchina)
        logging.info("DOPO carica_vincoli (JSON)")
        logging.debug(f"Vincoli caricati: {vincoli}")
        if not vincoli:
            logging.warning("Nessun vincolo trovato per la macchina!")
            print("Nessun vincolo trovato per la macchina!")
            try:
                messagebox.showinfo("Nessun vincolo", "Nessun vincolo trovato per la macchina!", parent=root)
            except Exception:
                pass
            sys.exit(0)
        logging.info("PRIMA di controlla_vincoli_condizionali")
        # Adatta la struttura per la funzione (macchina, vincoli, None)
        violazioni_cond = controlla_vincoli_condizionali(macchina, selezioni, [(macchina, vincoli, None)])
        logging.info("DOPO controlla_vincoli_condizionali")
        logging.info(f"Violazioni condizionali trovate: {violazioni_cond}")
        if violazioni_cond:
            msg = f"ATTENZIONE: Configurazione NON ammessa per la macchina '{macchina}'.\n\n"
            for v in violazioni_cond:
                msg += f"- {v}\n"
            print(msg)
            logging.warning(msg)
            try:
                messagebox.showwarning("Vincoli configurazione", msg, parent=root)
            except Exception:
                pass
        else:
            okmsg = f"Configurazione OK per la macchina '{macchina}'. Nessun vincolo violato."
            print(okmsg)
            logging.info(okmsg)
            try:
                messagebox.showinfo("OK", okmsg, parent=root)
            except Exception:
                pass
        print("--- Fine Verifica Vincoli Configurazione ---")
        logging.info("--- Fine Verifica Vincoli Configurazione ---")
    except Exception as e:
        import traceback
        logging.error(f"Errore inatteso: {e}")
        logging.error(traceback.format_exc())
        print("Errore inatteso:", e)
        try:
            messagebox.showerror("Errore inatteso", str(e), parent=get_tk_root())
        except Exception:
            pass
