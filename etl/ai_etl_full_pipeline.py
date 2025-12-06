import pandas as pd
import json
import ollama
import os
import psycopg2
from dotenv import load_dotenv


# --------------------------
# 1. KI SCHEMA ERKENNUNG
# --------------------------
def get_ai_schema(df_sample):
    prompt = f"""
    Du bekommst Beispielzeilen einer CSV.

    Deine Aufgabe:
    - Erkenne automatisch, welche Spalten gemeint sind.
    - Erstelle ein professionelles Standardschema.
    - Gib NUR gültiges JSON zurück.

    {{
      "schema": {{
        "alte_spalte": "neue_spalte"
      }}
    }}

    Beispielzeilen:
    {json.dumps(df_sample, indent=2)}
    """

    response = ollama.chat(
        model="llama3.1",
        messages=[{"role": "user", "content": prompt}]
    )

    ai_text = response["message"]["content"]

    # JSON extrahieren
    try:
        return json.loads(ai_text)
    except:
        start = ai_text.find("{")
        end = ai_text.rfind("}") + 1
        return json.loads(ai_text[start:end])


# --------------------------
# 2. CSV TRANSFORMATION
# --------------------------
def apply_schema(df, schema):
    df = df.rename(columns=schema)
    return df


# --------------------------
# 3. UPLOAD TO POSTGRES
# --------------------------
def load_to_postgres(df, table_name):
    load_dotenv()

    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        sslmode="require"
    )
    cursor = conn.cursor()

    # Tabelle anlegen (automatisch)
    columns = ", ".join([f"{col} TEXT" for col in df.columns])
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns});")
    conn.commit()

    # Daten einfügen
    for _, row in df.iterrows():
        cursor.execute(
            f"INSERT INTO {table_name} VALUES ({','.join(['%s']*len(row))})",
            list(row)
        )
    conn.commit()

    cursor.close()
    conn.close()


# --------------------------
# RUN PIPELINE
# --------------------------
if __name__ == "__main__":

    print("📂 Lade CSV...")
    df = pd.read_csv("data/orders.csv")

    print("🧠 KI analysiert Schema...")
    ai_schema = get_ai_schema(df.head(5).to_dict(orient="records"))
    mapping = ai_schema["schema"]

    print(f"➡️ Mapping erhalten:\n{json.dumps(mapping, indent=2)}")

    print("🔧 Wende Mapping auf CSV an...")
    df_clean = apply_schema(df, mapping)

    print("📤 Lade Daten nach PostgreSQL...")
    load_to_postgres(df_clean, table_name="clean_ai_data")

    print("\n🎉 ETL komplett: CSV → KI → PostgreSQL fertig!")
