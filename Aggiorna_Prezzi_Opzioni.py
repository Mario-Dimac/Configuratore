import tkinter as tk  # Importa il modulo tkinter per la GUI
from tkinter import ttk, filedialog, messagebox  # Importa widget e dialoghi aggiuntivi di tkinter
import csv  # Importa il modulo csv per la gestione dei file CSV
import os  # Importa il modulo os per operazioni su file e percorsi
import json  # Importa il modulo json per la gestione di dati in formato JSON
import sys  # Importa il modulo sys per operazioni di sistema
import logging  # aggiunto per la gestione dei log

# Definisce il percorso del file di configurazione che contiene la cartella dei CSV
CONFIG_PATH_FILE = os.path.join(os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__), 'config_path.txt')

# Configura il logging: crea un file di log per errori e problemi
LOG_FILE = os.path.join(os.path.dirname(__file__), "aggiorna_prezzi.log")
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

class PrezziOpzioniApp:
    """Classe principale dell'applicazione per la gestione dei prezzi delle opzioni."""
    def __init__(self, master):
        self.master = master  # Finestra principale Tk
        master.title("Aggiorna Prezzi Opzioni")  # Titolo della finestra
        self.dati = []  # Lista di dict per ogni opzione letta dal CSV
        self.rows = []  # Lista di tuple (opzione, valore, prezzo_var, row_idx, prezzo_orig) per la UI
        self.load_csv()  # Carica i dati dal file CSV
        self.setup_ui()  # Crea l'interfaccia grafica

    def load_csv(self):
        """Carica i dati delle opzioni dal file CSV."""
        self.dati.clear()  # Svuota la lista dati
        if not os.path.exists(PATH_OPZIONI):  # Se il file non esiste
            logging.error(f"File {PATH_OPZIONI} non trovato.")  # Logga l'errore
            messagebox.showerror("Errore", f"File {PATH_OPZIONI} non trovato.")
            return
        try:
            with open(PATH_OPZIONI, "r", newline="", encoding="utf-8") as f:
                # Salta eventuali righe di commento o vuote all'inizio del file
                while True:
                    pos = f.tell()  # Salva la posizione corrente
                    line = f.readline()  # Legge una riga
                    if not line:
                        return  # file vuoto
                    if line.strip().lower().startswith("opzione,"):
                        f.seek(pos)  # Torna all'inizio della riga dell'intestazione
                        break
                reader = csv.DictReader(f)  # Crea un lettore CSV a dizionario
                for row in reader:
                    # Salta righe vuote o incomplete
                    if not row.get("Opzione") or not row.get("Valori Possibili"):
                        continue
                    self.dati.append(row)  # Aggiunge la riga ai dati
        except Exception as e:
            logging.error(f"Errore durante il caricamento del CSV: {e}")  # Logga eventuali errori
            messagebox.showerror("Errore", f"Errore durante il caricamento del CSV:\n{e}")

    def setup_ui(self):
        """Crea l'interfaccia grafica dell'applicazione."""
        frame = ttk.Frame(self.master)  # Crea un frame principale
        frame.pack(fill="both", expand=True, padx=10, pady=10)  # Posiziona il frame
        canvas = tk.Canvas(frame)  # Crea un canvas per lo scroll
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)  # Scrollbar verticale
        self.inner_frame = ttk.Frame(canvas)  # Frame interno per i dati
        self.inner_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))  # Aggiorna l'area scrollabile
        )
        canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")  # Inserisce il frame interno nel canvas
        canvas.configure(yscrollcommand=scrollbar.set, height=500)  # Collega la scrollbar
        canvas.pack(side="left", fill="both", expand=True)  # Posiziona il canvas
        scrollbar.pack(side="right", fill="y")  # Posiziona la scrollbar
        # Intestazioni delle colonne
        ttk.Label(self.inner_frame, text="Opzione", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=2, pady=2)
        ttk.Label(self.inner_frame, text="Valore", font=("Arial", 10, "bold")).grid(row=0, column=1, padx=2, pady=2)
        ttk.Label(self.inner_frame, text="Prezzo", font=("Arial", 10, "bold")).grid(row=0, column=2, padx=2, pady=2)
        self.rows.clear()  # Svuota la lista delle righe UI
        row_idx = 1  # Indice della riga
        for opzione in self.dati:  # Per ogni opzione nei dati
            valori = [v.strip() for v in opzione["Valori Possibili"].split(",") if v.strip()]  # Lista dei valori possibili
            costi = opzione["Costo Opzione"].strip()  # Prezzi associati
            try:
                # Prova a caricare i prezzi come dizionario JSON, altrimenti crea un dizionario con lo stesso prezzo per tutti i valori
                costi_dict = json.loads(costi) if costi and costi.startswith("{") else {v: costi for v in valori}
            except Exception as e:
                logging.error(f"Errore parsing JSON per opzione '{opzione['Opzione']}': {e}")  # Logga errori di parsing
                costi_dict = {v: "" for v in valori}  # In caso di errore, prezzi vuoti
            for valore in valori:  # Per ogni valore possibile
                prezzo_var = tk.StringVar(value=str(costi_dict.get(valore, "")))  # Variabile per il prezzo
                ttk.Label(self.inner_frame, text=opzione["Opzione"]).grid(row=row_idx, column=0, padx=2, pady=2)  # Etichetta opzione
                ttk.Label(self.inner_frame, text=valore).grid(row=row_idx, column=1, padx=2, pady=2)  # Etichetta valore
                entry = ttk.Entry(self.inner_frame, textvariable=prezzo_var, width=10)  # Campo di inserimento prezzo
                entry.grid(row=row_idx, column=2, padx=2, pady=2)  # Posiziona il campo
                self.rows.append((opzione, valore, prezzo_var, row_idx, costi_dict.get(valore, "")))  # Salva la riga
                row_idx += 1  # Passa alla riga successiva
        btn = ttk.Button(self.master, text="Salva Prezzi", command=self.salva_prezzi)  # Bottone per salvare
        btn.pack(pady=10)  # Posiziona il bottone

    def salva_prezzi(self):
        """Salva i prezzi aggiornati nel file CSV."""
        # Ricostruisce la struttura costi per ogni opzione
        opzione_to_valori = {}
        for opzione, valore, prezzo_var, _, _ in self.rows:
            key = opzione["Opzione"]
            if key not in opzione_to_valori:
                opzione_to_valori[key] = {"row": opzione, "valori": {}}
            opzione_to_valori[key]["valori"][valore] = prezzo_var.get()
        # Aggiorna i dati delle opzioni
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
            try:
                with open(PATH_OPZIONI, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=self.dati[0].keys())  # Scrittore CSV
                    writer.writeheader()  # Scrive l'intestazione
                    writer.writerows(self.dati)  # Scrive tutte le righe
                messagebox.showinfo("Salvataggio", "Prezzi aggiornati su Elenco_Opzioni.csv.")  # Messaggio di conferma
            except Exception as e:
                logging.error(f"Errore durante il salvataggio del CSV: {e}")  # Logga errori di scrittura
                messagebox.showerror("Errore", f"Errore durante il salvataggio del CSV:\n{e}")
        else:
            messagebox.showerror("Errore", "Nessun dato da salvare!")  # Messaggio se non ci sono dati

if __name__ == "__main__":
    root = tk.Tk()  # Crea la finestra principale Tk
    app = PrezziOpzioniApp(root)  # Istanzia l'applicazione
    def on_exit():
        logging.info("Chiusura applicazione richiesta dall'utente.")
        try:
            root.destroy()
        except Exception as e:
            logging.error(f"Errore durante la chiusura della finestra principale: {e}")
        sys.exit(0)
    root.protocol("WM_DELETE_WINDOW", on_exit)
    # Pulsante ESCI grande e ben visibile
    exit_btn = tk.Button(root, text="ESCI", command=on_exit, bg="#d9534f", fg="white", font=("Arial", 16, "bold"), height=2, width=12)
    exit_btn.pack(side="bottom", anchor="e", padx=20, pady=20)
    root.mainloop()  # Avvia il ciclo principale della GUI
