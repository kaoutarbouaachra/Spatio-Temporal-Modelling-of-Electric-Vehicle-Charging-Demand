import pandas as pd
import os

# Dossier racine contenant les dossiers par année
root_folder = 'fichierbrutsexcel'

# Mapping des noms de colonnes vers noms standardisés
standard_cols = {
    'CP ID': 'CPID',
    'CP_ID': 'CPID',
    'CPID': 'CPID',
    'Consum(kWh)': 'Consumed(kWh)',
    'CONSUMED': 'Consumed(kWh)',
    'Consumed': 'Consumed(kWh)',
    'Amount': 'Amount',
    'AMOUNT': 'Amount',
    'Duration': 'Duration',
    'DURATION': 'Duration',
    'Start': 'Start',
    'START': 'Start',
    'start time':'Start',
    'Amt':'Amount'
}

# Colonnes à garder
colonnes_cibles = ['Amount', 'CPID', 'Consumed(kWh)', 'Duration', 'Start']

# Dossier de sortie racine
output_root_folder = 'fichiersexceluniformises'
os.makedirs(output_root_folder, exist_ok=True)

# Lister les dossiers dans fichierbrutsexcel (supposés être des années)
for annee in sorted(os.listdir(root_folder)):
    folder_path = os.path.join(root_folder, annee)
    if not os.path.isdir(folder_path):
        continue

    # Créer dossier de sortie pour cette année
    output_folder = os.path.join(output_root_folder, annee)
    os.makedirs(output_folder, exist_ok=True)

    fichiers = [f for f in os.listdir(folder_path) if f.endswith('.xlsx')]

    for fichier in fichiers:
        path = os.path.join(folder_path, fichier)
        try:
            df = pd.read_excel(path, engine='openpyxl')
        except Exception as e:
            print(f" Erreur de lecture {fichier} dans {annee} : {e}")
            continue

        # Nettoyer noms colonnes
        df.columns = [col.strip() for col in df.columns]

        # Renommer colonnes
        df = df.rename(columns={col: standard_cols[col] for col in df.columns if col in standard_cols})

        # Filtrer colonnes
        colonnes_presentes = [col for col in colonnes_cibles if col in df.columns]
        if len(colonnes_presentes) < 3:
            print(f" Trop peu de colonnes reconnues dans {fichier} ({annee}), ignoré.")
            continue

        df = df[colonnes_presentes]

        # Sauvegarde
        output_path = os.path.join(output_folder, fichier)
        df.to_excel(output_path, index=False)
        print(f" {fichier} ({annee}) uniformisé.")

print(" Tous les fichiers par année ont été uniformisés.")
