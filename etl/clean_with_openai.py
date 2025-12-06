import os
import pandas as pd
import json
from openai import OpenAI
from dotenv import load_dotenv

# ENV laden
load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

def clean_csv_with_ai(csv_path):
    """
    Nutzt DeepSeek, um CSV-Daten zu analysieren
    und ein einheitliches Spaltenschema als JSON zurückzugeben.
    """

    df = pd.read_csv(csv_path)
    sample = df.head(5).to_dict(orient="records")

    prompt = f"""
    Du bekommst ein Beispiel aus einer CSV-Datei.
    Deine Aufgabe:

    1. Erkenne die Bedeutung jeder Spalte.
    2. Gib ein vereinheitlichtes Schema zurück, z.B.:
        - order_id
        - customer
        - amount
        - order_date
    3. Gib ausschließlich valides JSON zurück:
       {{
         "schema": {{
            "alte_spalte": "neue_spalte",
            "alte_spalte2": "neue_spalte2"
         }}
       }}

    Beispiel-Daten:
    {json.dumps(sample, indent=2, ensure_ascii=False)}
    """

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}]
    )

    ai_text = response.choices[0].message["content"]

    return json.loads(ai_text)


if __name__ == "__main__":
    print("🚀 DeepSeek Cleaning gestartet...\n")
    result = clean_csv_with_ai("data/orders.csv")
    print("🎉 Vorschlag Schema (von DeepSeek):\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))
