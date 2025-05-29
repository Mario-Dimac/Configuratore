import tkinter as tk  # Importa il modulo tkinter per la GUI
from tkinter import filedialog, messagebox, scrolledtext  # Importa widget e dialoghi aggiuntivi di tkinter
import csv  # Importa il modulo csv per la gestione dei file CSV
import ast  # Importa il modulo ast per la valutazione sicura di stringhe Python
import os  # Importa il modulo os per operazioni su file e percorsi
import sys  # Importa il modulo sys per operazioni di sistema
import logging  # Per la gestione dei log

# Definisce il percorso del file di configurazione che contiene la cartella dei CSV
CONFIG_PATH_FILE = os.path.join(os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__), 'config_path.txt')
# Configura il logging: crea un file di log per errori e problemi
LOG_FILE = os.path.join(os.path.dirname(__file__), "visualizza_configurazione.log")
logging.basicConfig(
    filename=LOG_FILE,  # File dove verranno salvati i log
    level=logging.ERROR,  # Livello minimo di log: ERROR
    format="%(asctime)s [%(levelname)s] %(message)s"  # Formato del messaggio di log
)

def get_csv_dir():
    """Restituisce la cartella dove si trovano i file CSV, chiedendola all'utente se necessario."""
    try:
        if os.path.exists(CONFIG_PATH_FILE):  # Se esiste il file di configurazione
            with open(CONFIG_PATH_FILE, 'r', encoding='utf-8') as f:
                path = f.readline().strip()  # Legge il percorso dalla prima riga
                if path and os.path.isdir(path):  # Verifica che il percorso sia valido
                    return path
        # Se il file non esiste o il percorso non è valido, chiede all'utente di selezionare la cartella
        import tkinter as tk
        from tkinter import filedialog, messagebox
        root = tk.Tk()  # Crea una finestra nascosta
        root.withdraw()
        messagebox.showinfo("Percorso CSV mancante", "Seleziona la cartella dove si trovano i file Elenco_Macchine.csv e Elenco_Opzioni.csv.")
        path = filedialog.askdirectory(title="Seleziona cartella CSV condivisa")  # Dialogo per selezionare la cartella
        if not path:
            messagebox.showerror("Errore", "Cartella CSV obbligatoria. Il programma verrà chiuso.")
            sys.exit(1)  # Esce dal programma se non viene selezionata una cartella
        with open(CONFIG_PATH_FILE, 'w', encoding='utf-8') as f:
            f.write(path)  # Salva il percorso selezionato nel file di configurazione
        return path
    except Exception as e:
        logging.error(f"Errore in get_csv_dir: {e}")  # Logga eventuali errori
        messagebox.showerror("Errore", f"Errore nella selezione cartella CSV:\n{e}")
        sys.exit(1)

# Ottiene la cartella dei CSV
CSV_DIR = get_csv_dir()
# Definisce i percorsi completi dei file CSV delle opzioni e delle macchine
PATH_OPZIONI = os.path.join(CSV_DIR, "Elenco_Opzioni.csv")
PATH_MACCHINE = os.path.join(CSV_DIR, "Elenco_Macchine.csv")

def get_prezzo_opzione(opzione, valore):
    """Restituisce il prezzo di una determinata opzione/valore leggendo dal CSV delle opzioni."""
    try:
        with open(PATH_OPZIONI, newline='', encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["Opzione"].strip() == opzione:
                    costi = row.get("Costo Opzione", "").strip()
                    try:
                        costi_dict = ast.literal_eval(costi) if costi and costi.startswith("{") else {v.strip(): costi for v in row.get("Valori Possibili", "").split(",") if v.strip()}
                    except Exception:
                        logging.error(f"Errore parsing costi per opzione '{opzione}': {costi}")
                        costi_dict = {v.strip(): '' for v in row.get("Valori Possibili", "").split(",") if v.strip()}
                    prezzo = costi_dict.get(valore, '')
                    try:
                        return float(prezzo.replace(",", ".")) if prezzo else 0.0
                    except Exception:
                        logging.error(f"Errore conversione prezzo per opzione '{opzione}', valore '{valore}': {prezzo}")
                        return 0.0
    except Exception as e:
        logging.error(f"Errore in get_prezzo_opzione: {e}")
    return 0.0

def scegli_file_configurazione():
    """Apre una finestra di dialogo per selezionare il file di configurazione da visualizzare."""
    return filedialog.askopenfilename(
        title="Seleziona file configurazione",
        filetypes=[("CSV files", "*.csv"), ("Tutti i file", "*.*")]
    )

def leggi_configurazione(path):
    """Legge la configurazione dal file CSV selezionato e restituisce una lista di tuple (posizione, opzioni)."""
    config = []
    try:
        with open(path, newline='', encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                pos = row.get("Stazione") or row.get("Posizione")
                opzioni = row.get("Opzioni Selezionate") or row.get("Opzioni")
                if pos and opzioni:
                    config.append((pos.strip(), opzioni.strip()))
    except Exception as e:
        logging.error(f"Errore in leggi_configurazione: {e}")
    return config

def formatta_riepilogo(config):
    """Formatta il riepilogo della configurazione, calcolando il totale e mostrando i prezzi delle opzioni."""
    lines = []
    totale = 0.0
    for pos, opzioni_str in config:
        # Sostituisci 'Punto 0 (ore 3)' con 'Accessori' nella visualizzazione
        pos_vis = pos.replace('punto_0_ore_3', 'Accessori').replace('Punto_0_ore_3', 'Accessori')
        opzioni = [x.strip() for x in opzioni_str.split(",") if x.strip()]
        for opzione_str in opzioni:
            if ":" in opzione_str:
                opzione, valore = [x.strip() for x in opzione_str.split(":", 1)]
            else:
                opzione = opzione_str.strip()
                valore = opzione_str.strip()
            # Gestione "Dischi trasporto: N"
            if opzione.lower().startswith("dischi trasporto"):
                try:
                    num_dischi = int(valore)
                except Exception:
                    num_dischi = 1
                prezzo_unit = get_prezzo_opzione(opzione, valore)
                prezzo = prezzo_unit * num_dischi if num_dischi > 1 else prezzo_unit
                totale += prezzo
                if prezzo:
                    lines.append(f"{pos_vis}: {opzione}: {valore}   [{prezzo_unit:.2f} € x {num_dischi} = {prezzo:.2f} €]")
                else:
                    lines.append(f"{pos_vis}: {opzione}: {valore}")
            else:
                prezzo = get_prezzo_opzione(opzione, valore)
                totale += prezzo
                if prezzo:
                    lines.append(f"{pos_vis}: {opzione}: {valore}   [{prezzo:.2f} €]")
                else:
                    lines.append(f"{pos_vis}: {opzione}: {valore}")
    lines.append("\n------------------------------")
    lines.append(f"TOTALE: {totale:.2f} €")
    return "\n".join(lines)

def main():
    """Funzione principale che avvia la GUI e gestisce il caricamento e la visualizzazione della configurazione."""
    root = tk.Tk()  # Crea la finestra principale Tk
    root.title("Visualizza Configurazione")  # Titolo della finestra
    root.geometry("800x500")  # Dimensione finestra

    def carica_e_mostra():
        """Carica il file di configurazione selezionato e mostra il riepilogo nella finestra di testo."""
        try:
            path = scegli_file_configurazione()
            if not path:
                return
            config = leggi_configurazione(path)
            if not config:
                messagebox.showerror("Errore", "File non valido o vuoto.")
                return
            riepilogo = formatta_riepilogo(config)
            text.delete(1.0, tk.END)
            text.insert(tk.END, riepilogo)
        except Exception as e:
            logging.error(f"Errore in carica_e_mostra: {e}")
            messagebox.showerror("Errore", f"Errore durante il caricamento della configurazione:\n{e}")

    def copia_testo():
        """Copia il riepilogo visualizzato negli appunti di sistema."""
        try:
            root.clipboard_clear()
            root.clipboard_append(text.get(1.0, tk.END))
            messagebox.showinfo("Copiato", "Riepilogo copiato negli appunti.")
        except Exception as e:
            logging.error(f"Errore in copia_testo: {e}")
            messagebox.showerror("Errore", f"Errore durante la copia negli appunti:\n{e}")

    btn = tk.Button(root, text="Seleziona configurazione...", command=carica_e_mostra, font=("Arial", 12, "bold"), bg="#2196f3", fg="white")  # Bottone per selezionare il file
    btn.pack(pady=10, fill="x")
    text = scrolledtext.ScrolledText(root, font=("Consolas", 12), wrap=tk.WORD)  # Area di testo per il riepilogo
    text.pack(expand=True, fill="both", padx=10, pady=10)
    btn_copia = tk.Button(root, text="Copia riepilogo", command=copia_testo, font=("Arial", 11), bg="#4caf50", fg="white")  # Bottone per copiare il riepilogo
    btn_copia.pack(pady=5, fill="x")
    root.mainloop()  # Avvia il ciclo principale della GUI

if __name__ == "__main__":
    main()
