import csv
import json
import os

# Percorsi file
DIR = os.path.dirname(__file__)
CSV_OPZIONI = os.path.join(DIR, "Elenco_Opzioni.csv")
JSON_VINCOLI = os.path.join(DIR, "vincoli_macchine.json")

# Estrai vincoli dal CSV e salva in JSON
vincoli_per_macchina = {}

with open(CSV_OPZIONI, newline='', encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        vincoli_raw = row.get("Vincoli", "")
        if not vincoli_raw:
            continue
        try:
            vincoli_dict = json.loads(vincoli_raw)
        except Exception:
            import ast
            vincoli_dict = ast.literal_eval(vincoli_raw)
        for macchina, vincoli in vincoli_dict.items():
            if macchina not in vincoli_per_macchina:
                vincoli_per_macchina[macchina] = []
            # Aggiungi tutti i vincoli trovati per la macchina
            if isinstance(vincoli, list):
                vincoli_per_macchina[macchina].extend(vincoli)
            else:
                vincoli_per_macchina[macchina].append(vincoli)

# Salva su file JSON
with open(JSON_VINCOLI, 'w', encoding='utf-8') as f:
    json.dump(vincoli_per_macchina, f, indent=2, ensure_ascii=False)

print(f"Vincoli estratti e salvati in {JSON_VINCOLI}")
