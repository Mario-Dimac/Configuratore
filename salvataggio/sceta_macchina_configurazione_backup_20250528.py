import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog, ttk # Importa ttk per il combobox
import csv
import ast
import os

root_main = tk.Tk()
root_main.withdraw()

# --- VARIABILE GLOBALE PER MEMORIZZARE LE SCELTE ---
# Questa deve essere globale per persistere tra le chiamate delle funzioni.
scelte_stazioni = {}

# --- FINESTRA LATERALE PERSISTENTE (singleton) ---
win_selezioni = None
labels_selezioni = {}

def crea_o_mostra_win_selezioni():
    global win_selezioni, labels_selezioni
    if win_selezioni is not None and win_selezioni.winfo_exists():
        win_selezioni.deiconify()
        win_selezioni.lift()
        aggiorna_finestra_selezioni()
        return win_selezioni
    win_selezioni = tk.Toplevel(root_main)
    win_selezioni.title("Selezioni correnti")
    win_selezioni.geometry("350x500+1200+100")
    frame_selezioni = tk.Frame(win_selezioni)
    frame_selezioni.pack(fill="both", expand=True, padx=10, pady=10)
    label_titolo = tk.Label(frame_selezioni, text="Stazione / Opzioni selezionate", font=("Arial", 12, "bold"))
    label_titolo.pack(anchor="w")
    labels_selezioni = {}
    def get_prezzo_opzione(opzione, valore):
        # Cerca il prezzo per una coppia opzione/valore leggendo Elenco_Opzioni.csv
        try:
            with open("d:/Progetti Python e Script/Vibroalimentatori/Costruzione/Configuratore/Elenco_Opzioni.csv", newline='', encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row["Opzione"].strip() == opzione:
                        costi = row.get("Costo Opzione", "").strip()
                        try:
                            costi_dict = ast.literal_eval(costi) if costi and costi.startswith("{") else {v.strip(): costi for v in row.get("Valori Possibili", "").split(",") if v.strip()}
                        except Exception:
                            costi_dict = {v.strip(): '' for v in row.get("Valori Possibili", "").split(",") if v.strip()}
                        return costi_dict.get(valore, '')
        except Exception:
            pass
        return ''

    def formatta_opzione_con_prezzo(opzione_str):
        # opzione_str può essere "Opzione: valore" oppure solo "Opzione" o solo "valore"
        if ":" in opzione_str:
            opzione, valore = [x.strip() for x in opzione_str.split(":", 1)]
        elif "(" in opzione_str and ")" in opzione_str:
            # es: Marposs (Cricche 2 sonde)
            opzione = opzione_str.split("(")[0].strip()
            valore = opzione_str.split("(")[1].split(")")[0].strip()
        else:
            opzione = opzione_str.strip()
            valore = opzione_str.strip()
        prezzo = get_prezzo_opzione(opzione, valore)
        if prezzo:
            return f"{opzione_str} [{prezzo} €]"
        else:
            return opzione_str

    def aggiorna_finestra_selezioni_local():
        global labels_selezioni
        for lbl in labels_selezioni.values():
            lbl.destroy()
        labels_selezioni.clear()
        tutte_le_stazioni = []
        if hasattr(root_main, 'elenco_stazioni_globali'):
            tutte_le_stazioni = root_main.elenco_stazioni_globali
        else:
            tutte_le_stazioni = list(scelte_stazioni.keys())
        for k in tutte_le_stazioni:
            v = scelte_stazioni.get(k, "")
            if v.strip():
                opzioni = [x.strip() for x in v.split(",") if x.strip()]
                testo = ", ".join([formatta_opzione_con_prezzo(o) for o in opzioni])
            else:
                testo = "(nessuna opzione selezionata)"
            lbl = tk.Label(frame_selezioni, text=f"{k}: {testo}", font=("Arial", 11))
            lbl.pack(anchor="w")
            labels_selezioni[k] = lbl
    win_selezioni.aggiorna_finestra_selezioni = aggiorna_finestra_selezioni_local
    aggiorna_finestra_selezioni_local()
    # Pulsante per cancellare la configurazione
    def cancella_configurazione():
        import os
        if os.path.exists(TEMP_CONFIG_PATH):
            os.remove(TEMP_CONFIG_PATH)
        scelte_stazioni.clear()
        aggiorna_finestra_selezioni_local()
    btn_cancella = tk.Button(frame_selezioni, text="Cancella configurazione", font=("Arial", 10, "bold"), bg="#e57373", fg="white", command=cancella_configurazione)
    btn_cancella.pack(anchor="s", pady=10, fill="x")
    # Pulsante per stampare/salvare il riepilogo
    def stampa_riepilogo():
        from tkinter import filedialog
        import csv
        file_path = filedialog.asksaveasfilename(
            parent=win_selezioni,
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("Tutti i file", "*.*")],
            title="Salva riepilogo configurazione"
        )
        if not file_path:
            return
        tutte_le_stazioni = []
        if hasattr(root_main, 'elenco_stazioni_globali'):
            tutte_le_stazioni = root_main.elenco_stazioni_globali
        else:
            tutte_le_stazioni = list(scelte_stazioni.keys())
        with open(file_path, "w", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Stazione", "Opzioni Selezionate"])
            for k in tutte_le_stazioni:
                v = scelte_stazioni.get(k, "")
                if v.strip():
                    opzioni = [x.strip() for x in v.split(",") if x.strip()]
                    testo = ", ".join([formatta_opzione_con_prezzo(o) for o in opzioni])
                else:
                    testo = "(nessuna opzione selezionata)"
                writer.writerow([k, testo])
    btn_stampa = tk.Button(frame_selezioni, text="STAMPA", font=("Arial", 11, "bold"), bg="#2196f3", fg="white", command=stampa_riepilogo)
    btn_stampa.pack(anchor="s", pady=5, fill="x")
    def chiudi_win_selezioni():
        win_selezioni.withdraw()
    win_selezioni.protocol("WM_DELETE_WINDOW", chiudi_win_selezioni)
    return win_selezioni

def aggiorna_finestra_selezioni():
    global win_selezioni
    if win_selezioni is not None and win_selezioni.winfo_exists():
        win_selezioni.aggiorna_finestra_selezioni()

# --- FINESTRA UTILITY CON PULSANTE RIAPRI SELEZIONI ---
# RIMOSSO: la finestra utility Tkinter non è più necessaria, il pulsante resta solo su Matplotlib
# win_utility = None
# def crea_o_mostra_win_utility():
#     pass  # Funzione vuota, non più usata

# --- Utility per leggere le posizioni delle stazioni dal CSV macchine ---
def get_posizioni_stazioni(macchina):
    with open("d:/Progetti Python e Script/Vibroalimentatori/Costruzione/Configuratore/Elenco_Macchine.csv", newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["Nome Macchina"].strip() == macchina:
                pos_str = row.get("Posizioni Stazioni (gradi)", "")
                max_stazioni = int(row.get("Max Stazioni", 0)) if row.get("Max Stazioni") else 0
                posizioni = []
                if pos_str:
                    for x in pos_str.split(","):
                        x = x.strip()
                        if not x:
                            continue
                        try:
                            posizioni.append(float(x))
                        except Exception:
                            print(f"[ATTENZIONE] Valore posizione non valido per {macchina}: '{x}'")
                if max_stazioni and len(posizioni) != max_stazioni:
                    print(f"[ATTENZIONE] Per {macchina}: Max Stazioni={max_stazioni} ma posizioni trovate={len(posizioni)}. Controlla il CSV!")
                return posizioni
    return []

def scegli_macchina():
    # Leggi tutte le macchine disponibili dal CSV
    with open("d:/Progetti Python e Script/Vibroalimentatori/Costruzione/Configuratore/Elenco_Macchine.csv", newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        macchine = [row["Nome Macchina"] for row in reader if row.get("Nome Macchina")]
    root = tk.Toplevel(root_main)
    root.title("Seleziona Macchina")
    root.geometry("350x120")
    tk.Label(root, text="Scegli la macchina:", font=("Arial", 11, "bold")).pack(pady=10)
    selected = tk.StringVar(value=macchine[0] if macchine else "")
    combo = ttk.Combobox(root, textvariable=selected, values=macchine, state="readonly", font=("Arial", 11))
    combo.pack(pady=5)
    result = {'macchina': None}
    def conferma():
        result['macchina'] = selected.get()
        root.destroy()
    btn = tk.Button(root, text="Conferma", command=conferma, font=("Arial", 11, "bold"), bg="#4caf50", fg="white")
    btn.pack(pady=10)
    root.grab_set()
    root.wait_window()
    return result['macchina']

# --- Costruzione dinamica delle opzioni disponibili per ogni stazione e globali ---
def carica_opzioni_da_csv(per_macchina="MCV1"):
    opzioni_per_stazione = {}
    opzioni_globali = {}
    uscite_per_macchina = []
    # Prima, recupera le posizioni di uscita per la macchina
    with open("d:/Progetti Python e Script/Vibroalimentatori/Costruzione/Configuratore/Elenco_Macchine.csv", newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["Nome Macchina"].strip() == per_macchina:
                for key in row:
                    if key.startswith("Posizione Uscita") and row[key]:
                        num = key.split()[-1]
                        nome_uscita = f"Uscita {num}"
                        uscite_per_macchina.append(normalizza_nome(nome_uscita))
                break
    with open("d:/Progetti Python e Script/Vibroalimentatori/Costruzione/Configuratore/Elenco_Opzioni.csv", newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tipo = row["Tipo Opzione"].strip()
            opzione = row["Opzione"].strip()
            macchine = [m.strip() for m in row["Macchine Compatibili"].split(",") if m.strip()]
            if per_macchina not in macchine:
                continue
            if tipo == "Stazione":
                posizioni_raw = row["Posizioni Ammesse"].strip()
                if posizioni_raw:
                    try:
                        pos_dict = ast.literal_eval(posizioni_raw)
                        pos_list = pos_dict.get(per_macchina, [])
                        for pos in pos_list:
                            nome_stazione_key = normalizza_nome(f"Stazione {pos}" if str(pos).isdigit() else pos)
                            if nome_stazione_key not in opzioni_per_stazione:
                                opzioni_per_stazione[nome_stazione_key] = []
                            opzioni_per_stazione[nome_stazione_key].append(opzione)
                    except Exception as e:
                        print(f"[ERRORE] Errore parsing 'Posizioni Ammesse' per opzione '{opzione}': {e}. Valore: '{posizioni_raw}'")
            elif tipo == "Globale":
                normalized_global_key = normalizza_nome("Punto 0 (ore 3)")
                if normalized_global_key not in opzioni_globali:
                    opzioni_globali[normalized_global_key] = []
                opzioni_globali[normalized_global_key].append(opzione)
            elif tipo == "Uscita":
                # Associa questa opzione a tutte le uscite della macchina
                for uscita_key in uscite_per_macchina:
                    if uscita_key not in opzioni_per_stazione:
                        opzioni_per_stazione[uscita_key] = []
                    opzioni_per_stazione[uscita_key].append(opzione)
    return opzioni_per_stazione, opzioni_globali

def get_extra_posizioni(macchina):
    """Restituisce una lista di tuple (angolo, nome) per sensori e uscite, se presenti nel CSV."""
    with open("d:/Progetti Python e Script/Vibroalimentatori/Costruzione/Configuratore/Elenco_Macchine.csv", newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["Nome Macchina"].strip() == macchina:
                extra = []
                for key in row:
                    if key.startswith("Posizione Sensore") and row[key]:
                        try:
                            ang = float(row[key])
                            extra.append((ang, "Sensore"))
                        except ValueError: # Cattura specificamente ValueError per float
                            print(f"[ATTENZIONE] Valore non numerico per {key} in {macchina}: '{row[key]}'")
                            pass
                    if key.startswith("Posizione Uscita") and row[key]:
                        try:
                            num = key.split()[-1]
                            ang = float(row[key])
                            extra.append((ang, f"Uscita {num}"))
                        except ValueError: # Cattura specificamente ValueError per float
                            print(f"[ATTENZIONE] Valore non numerico per {key} in {macchina}: '{row[key]}'")
                            pass
                return extra
    return []

# --- Funzioni per salvataggio/caricamento temporaneo ---
TEMP_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "configurazione_temp.csv")

def salva_configurazione_temp():
    print("[DEBUG] Salvataggio scelte_stazioni:", scelte_stazioni)
    with open(TEMP_CONFIG_PATH, "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Posizione", "Opzioni Selezionate"])
        for k, v in scelte_stazioni.items():
            print(f"[DEBUG] SCRITTURA CSV: {k} -> {v}")
            writer.writerow([k, v])
    # Debug: mostra il contenuto del file appena scritto
    with open(TEMP_CONFIG_PATH, "r", encoding="utf-8") as f:
        print("[DEBUG] CONTENUTO FILE TEMP DOPO SCRITTURA:")
        for line in f:
            print(line.strip())

def carica_configurazione_temp():
    scelte_stazioni.clear()  # Svuota prima di caricare
    if not os.path.exists(TEMP_CONFIG_PATH):
        print("[DEBUG] File temp non trovato!")
        return
    with open(TEMP_CONFIG_PATH, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key_norm = normalizza_nome(row["Posizione"])
            scelte_stazioni[key_norm] = row["Opzioni Selezionate"]
    print("[DEBUG] scelte_stazioni dopo carica_configurazione_temp:", scelte_stazioni)
    # Debug: mostra il contenuto del file appena letto
    with open(TEMP_CONFIG_PATH, "r", encoding="utf-8") as f:
        print("[DEBUG] CONTENUTO FILE TEMP DOPO LETTURA:")
        for line in f:
            print(line.strip())

def normalizza_nome(nome):
    """Normalizza il nome per essere usato come chiave nel dizionario, rimuovendo spazi e rendendolo uniforme."""
    return nome.strip().replace(" ", "_").replace("(", "").replace(")", "").replace(".", "").replace("-", "_").lower()

# --- Funzione principale per mostrare la disposizione ---
global fig_mcv
fig_mcv = None

def mostra_disposizione_mcv1():
    global scelte_stazioni, fig_mcv
    macchina = scegli_macchina()
    if not macchina:
        print("Nessuna macchina selezionata.")
        return

    opzioni_per_stazione, opzioni_globali = carica_opzioni_da_csv(macchina)
    carica_configurazione_temp()  # <-- carica le scelte temporanee se esistono
    pos_angoli = get_posizioni_stazioni(macchina)
    if not pos_angoli:
        print(f"Nessuna posizione trovata per {macchina}")
        return

    n_settori = 40
    angolo_settore = 360 / n_settori
    raggio = 1
    centro = (0, 0)

    posizioni_disegno = [(0, "Punto 0 (ore 3)")]
    for i, ang in enumerate(pos_angoli):
        posizioni_disegno.append((ang, f"Stazione {i+1}"))
    extra = get_extra_posizioni(macchina)
    posizioni_disegno.extend(extra)
    # Salva l'elenco di tutte le stazioni normalizzate per il riepilogo
    elenco_stazioni_globali = [normalizza_nome(nome) for _, nome in posizioni_disegno]
    root_main.elenco_stazioni_globali = elenco_stazioni_globali

    fig, ax = plt.subplots(figsize=(10, 10))
    fig_mcv = fig
    disco = plt.Circle(centro, raggio, fill=False, linewidth=2)
    ax.add_artist(disco)

    for i in range(n_settori):
        ang = np.deg2rad(-i * angolo_settore)
        x = raggio * np.cos(ang)
        y = raggio * np.sin(ang)
        ax.plot([0, x], [0, y], color="#cccccc", linewidth=0.7)

    stazioni_coords = []
    testo_scelte = {}
    evidenza_patches = {}

    for angolo, nome_originale in posizioni_disegno:
        nome_normalizzato = normalizza_nome(nome_originale)
        ang_rad = np.deg2rad(-angolo)
        x = 0.92 * raggio * np.cos(ang_rad)
        y = 0.92 * raggio * np.sin(ang_rad)

        ax.plot([0, x], [0, y], color="red", linewidth=2)

        if nome_originale.startswith("Stazione") or nome_originale.startswith("Uscita") or nome_originale.startswith("Punto 0"):
            evidenza = plt.Circle((x, y), 0.07, color="gold", zorder=4, alpha=0.7, linewidth=2, fill=True, ec="orange")
            ax.add_patch(evidenza)
            evidenza_patches[nome_originale] = evidenza
            stazioni_coords.append((x, y, nome_originale))

        marker = ax.plot(x, y, 'o', color="blue", zorder=5)
        ax.text(1.08 * raggio * np.cos(ang_rad), 1.08 * raggio * np.sin(ang_rad), nome_originale, fontsize=10, ha='center', va='center', bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="gray", lw=0.5, alpha=0.7))

        initial_text = scelte_stazioni.get(nome_normalizzato, "")
        testo = ax.text(x, y + 0.08, initial_text, fontsize=9, ha='center', va='center', color="green", zorder=10)
        testo_scelte[nome_normalizzato] = testo

    # --- PULSANTE PER RIAPRIRE LA FINESTRA LATERALE ---
    def on_btn_mostra_selezioni(event=None):
        crea_o_mostra_win_selezioni()
    btn_ax = plt.axes([0.82, 0.01, 0.15, 0.05])
    btn = plt.Button(btn_ax, 'Mostra selezioni', color='#e0e0e0', hovercolor='#b0b0b0')
    btn.on_clicked(on_btn_mostra_selezioni)

    def seleziona_opzioni_tkinter(nome_originale_stazione, opzioni_disponibili, selezione_precedente_str):
        print("[DEBUG] APERTA seleziona_opzioni_tkinter", opzioni_disponibili)
        root = tk.Toplevel(root_main)
        root.grab_set()
        root.title(f"Configura {nome_originale_stazione}")
        root.geometry("350x300")

        var_dict = {}
        frame = tk.Frame(root)
        frame.pack(padx=10, pady=10, fill="both", expand=True)

        label = tk.Label(frame, text=f"Opzioni disponibili per {nome_originale_stazione}:", font=("Arial", 11, "bold"))
        label.pack(anchor="w")

        selezionate_set = set()
        if selezione_precedente_str:
            selezionate_set = set([s.strip() for s in selezione_precedente_str.split(",") if s.strip()])

        for opzione in opzioni_disponibili:
            var = tk.BooleanVar(value=(opzione in selezionate_set))
            cb = tk.Checkbutton(frame, text=opzione, variable=var, anchor="w")
            cb.pack(anchor="w")
            var_dict[opzione] = var

        scelta_finale_list = []
        confirmed = {'value': False}

        def conferma():
            for opz, var in var_dict.items():
                if var.get():
                    scelta_finale_list.append(opz)
            confirmed['value'] = True
            print("[DEBUG] CONFERMA premuto, scelta_finale_list:", scelta_finale_list)
            root.destroy()
            aggiorna_finestra_selezioni()  # Aggiorna la finestra selezioni dopo ogni conferma

        def on_close():
            confirmed['value'] = False
            print("[DEBUG] FINESTRA CHIUSA, confirmed:", confirmed['value'])
            print("[DEBUG] FINESTRA CHIUSA senza conferma")
            root.destroy()

        btn = tk.Button(frame, text="Conferma", command=conferma, font=("Arial", 11, "bold"), bg="#4caf50", fg="white")
        btn.pack(pady=10)
        root.protocol("WM_DELETE_WINDOW", on_close)
        root.wait_window()  # <-- NON usare mainloop!

        if confirmed['value']:
            return scelta_finale_list
        else:
            return None

    def on_click(event):
        if event.inaxes != ax:
            return
        x_click, y_click = event.xdata, event.ydata
        min_dist = 0.12 # Raggio di cliccabilità
        stazione_trovata_original_name = None
        for x_station, y_station, nome_originale_staz in stazioni_coords:
            dist = np.sqrt((x_station - x_click)**2 + (y_station - y_click)**2)
            if dist < min_dist:
                stazione_trovata_original_name = nome_originale_staz
                break
        if stazione_trovata_original_name:
            nome_normalizzato_key = normalizza_nome(stazione_trovata_original_name)
            # Feedback visivo: bordo verde per la stazione cliccata, arancione per le altre
            for patch_nome, patch in evidenza_patches.items():
                if patch_nome == stazione_trovata_original_name:
                    patch.set_edgecolor('lime')
                    patch.set_linewidth(3)
                else:
                    patch.set_edgecolor('orange')
                    patch.set_linewidth(2)
            fig.canvas.draw()
            # Determina le opzioni disponibili per questa stazione
            opzioni_disponibili = []
            if nome_normalizzato_key in opzioni_per_stazione:
                opzioni_disponibili = opzioni_per_stazione[nome_normalizzato_key]
            elif nome_normalizzato_key in opzioni_globali:
                opzioni_disponibili = opzioni_globali[nome_normalizzato_key]

            # --- LOGICA GENERALE: mostra i valori possibili per ogni opzione, solo quelli abilitati per la macchina selezionata ---
            # Se opzioni_disponibili contiene una sola opzione e questa ha valori possibili nel CSV, mostra i valori possibili
            if opzioni_disponibili:
                nuove_opzioni = []
                is_uscita = nome_normalizzato_key.startswith('uscita')
                with open("d:/Progetti Python e Script/Vibroalimentatori/Costruzione/Configuratore/Elenco_Opzioni.csv", newline='', encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    if is_uscita:
                        for row in reader:
                            if row["Opzione"].strip().lower() == "uscita":
                                macchine = [m.strip() for m in row["Macchine Compatibili"].split(",") if m.strip()]
                                if macchina in macchine:
                                    # Prima cerca i vincoli, se presenti
                                    vincoli_raw = row.get("Vincoli", "").strip()
                                    valori_filtrati = []
                                    if vincoli_raw:
                                        try:
                                            vincoli_dict = ast.literal_eval(vincoli_raw)
                                            vincoli_macchina = vincoli_dict.get(macchina, [])
                                            valori_filtrati = vincoli_macchina
                                        except Exception as e:
                                            print(f"[ERRORE] Errore parsing 'Vincoli' per opzione 'Uscita': {e}. Valore: '{vincoli_raw}'")
                                    # Se non ci sono vincoli, mostra tutti i valori possibili
                                    if not valori_filtrati:
                                        valori_filtrati = [v.strip() for v in row["Valori Possibili"].split(",") if v.strip()]
                                    nuove_opzioni = [f"Uscita: {v}" for v in valori_filtrati] if valori_filtrati else ["Uscita"]
                                    break
                    else:
                        for opzione in opzioni_disponibili:
                            for row in reader:
                                if row["Opzione"].strip() == opzione:
                                    macchine = [m.strip() for m in row["Macchine Compatibili"].split(",") if m.strip()]
                                    if macchina in macchine:
                                        valori = [v.strip() for v in row["Valori Possibili"].split(",") if v.strip()]
                                        vincoli_raw = row.get("Vincoli", "").strip()
                                        valori_filtrati = valori
                                        if vincoli_raw:
                                            try:
                                                vincoli_dict = ast.literal_eval(vincoli_raw)
                                                vincoli_macchina = vincoli_dict.get(macchina, [])
                                                if vincoli_macchina:
                                                    valori_filtrati = [v for v in valori if v in vincoli_macchina]
                                            except Exception as e:
                                                print(f"[ERRORE] Errore parsing 'Vincoli' per opzione '{opzione}': {e}. Valore: '{vincoli_raw}'")
                                        if valori_filtrati:
                                            nuove_opzioni.extend(valori_filtrati)
                                        else:
                                            nuove_opzioni.append(opzione)
                                        break
                            f.seek(0)
                if nuove_opzioni:
                    opzioni_disponibili = nuove_opzioni
            print("[DEBUG] opzioni_disponibili:", opzioni_disponibili)
            selezione_precedente_str = scelte_stazioni.get(nome_normalizzato_key, "")
            scelta_corrente_list = seleziona_opzioni_tkinter(stazione_trovata_original_name, opzioni_disponibili, selezione_precedente_str)
            print("[DEBUG] scelta_corrente_list:", scelta_corrente_list)
            if scelta_corrente_list is not None:
                scelte_stazioni[nome_normalizzato_key] = ', '.join(scelta_corrente_list)
                if nome_normalizzato_key in testo_scelte:
                    testo_scelte[nome_normalizzato_key].set_text(', '.join(scelta_corrente_list))
                print(f"[DEBUG] Selezione aggiornata per {nome_normalizzato_key}: {scelte_stazioni[nome_normalizzato_key]}")
                salva_configurazione_temp()
                aggiorna_finestra_selezioni()
                fig.canvas.draw()

    # Collega il click
    fig.canvas.mpl_connect('button_press_event', on_click)
    plt.show()


if __name__ == "__main__":
    mostra_disposizione_mcv1()
