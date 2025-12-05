import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv

CSV_PATH = "data/orders.csv"

"""
Erwartete CSV-Spalten:
- order_id
- customer
- amount
- order_date

Funktion:
- Lädt die CSV
- Erstellt Tabelle raw_orders falls nicht vorhanden
- Schreibt die Daten in raw_orders
"""


# .env laden
load_dotenv()

HOST = os.getenv("DB_HOST")
PORT = os.getenv("DB_PORT")
NAME = os.getenv("DB_NAME")
USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASSWORD")

# Verbindung aufbauen
conn = psycopg2.connect(
    host=HOST,
    port=PORT,
    dbname=NAME,
    user=USER,
    password=PASSWORD,
    sslmode="require"
)

cursor = conn.cursor()

# CSV einlesen
df = pd.read_csv(CSV_PATH)

# Tabelle erstellen
cursor.execute("""
    CREATE TABLE IF NOT EXISTS raw_orders (
        order_id VARCHAR(50),
        customer VARCHAR(100),
        amount NUMERIC,
        order_date DATE
    );
""")
conn.commit()

# Daten einfügen
for _, row in df.iterrows():
    cursor.execute(
        "INSERT INTO raw_orders (order_id, customer, amount, order_date) VALUES (%s, %s, %s, %s)",
        (row["order_id"], row["customer"], row["amount"], row["order_date"])
    )

conn.commit()

cursor.close()
conn.close()

print("✔️ CSV erfolgreich in PostgreSQL geladen!")
