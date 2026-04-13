import requests
from bs4 import BeautifulSoup
import csv
import os
from datetime import datetime

URL = "https://www.web-agri.fr/marches-agricoles/engrais"

FILE = "engrais_wa_scrap.csv"


# -----------------------------
# 1. Télécharger la page
# -----------------------------
def get_page():
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    r = requests.get(URL, headers=headers, timeout=10)
    r.raise_for_status()
    return r.text


# -----------------------------
# 2. Parser les données
# -----------------------------
def parse_data(html):
    soup = BeautifulSoup(html, "html.parser")

    text = soup.get_text("\n", strip=True)

    lines = text.split("\n")

    data = {}

    current_product = None

    for i, line in enumerate(lines):

        line = line.strip()

        # Détection des produits
        if line in [
            "PK",
            "Triple 17",
            "Ammonitrate 27%",
            "Ammonitrate 33.5%",
            "DAP",
            "MOP",
            "Solution azotée",
            "Super phosphate triple",
            "Urée"
        ]:
            current_product = line

        # Détection du prix
        if current_product and "Prix" in line:
            # le prix est généralement 1 ou 2 lignes après
            try:
                for j in range(i, i + 5):
                    if j < len(lines):
                        val = lines[j].replace(",", ".")
                        if val.replace(".", "").isdigit():
                            price = float(val)
                            data[current_product] = price
                            current_product = None
                            break
            except:
                pass

    return data


# -----------------------------
# 3. Normalisation colonnes CSV
# -----------------------------
def normalize(engrais_wa_scrap):

    mapping = {
        "PK": "pk",
        "Triple 17": "3x17",
        "Ammonitrate 27%": "ammo27",
        "Ammonitrate 33.5%": "ammo33",
        "DAP": "dap",
        "MOP": "mop",
        "Solution azotée": "solaz",
        "Super phosphate triple": "superp3x",
        "Urée": "uree"
    }

    result = {}

    for k, v in data.items():
        if k in mapping:
            result[mapping[k]] = v

    return result


# -----------------------------
# 4. Sauvegarde CSV
# -----------------------------
def save_csv(engrais_wa_scrap):

    date = datetime.now().strftime("%Y-%m-%d")

    columns = [
        "date",
        "pk",
        "3x17",
        "ammo27",
        "ammo33",
        "dap",
        "mop",
        "solaz",
        "superp3x",
        "uree"
    ]

    file_exists = os.path.exists(FILE)

    # lecture existant
    rows = []
    if file_exists:
        with open(FILE, newline="") as f:
            rows = list(csv.reader(f))

    # éviter doublon
    if rows and rows[-1][0] == date:
        print("Déjà enregistré aujourd'hui")
        return

    row = [date]

    for col in columns[1:]:
        row.append(data.get(col, ""))

    with open(FILE, "a", newline="") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow(columns)

        writer.writerow(row)

    print("OK ajouté :", row)


# -----------------------------
# 5. MAIN
# -----------------------------
def main():
    html = get_page()
    raw_data = parse_data(html)
    data = normalize(raw_data)

    save_csv(data)


if __name__ == "__main__":
    main()
