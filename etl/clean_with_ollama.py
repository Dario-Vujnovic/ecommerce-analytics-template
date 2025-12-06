import pandas as pd
import json
import ollama


def extract_json(text):
    """
    Extrahiert JSON, wenn der gesamte Text bereits gültiges JSON ist.
    Fängt Fehler sauber ab.
    """
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Falls trotzdem Text + JSON kommt:
        start = text.find("{")
        end = text.rfind("}") + 1
        json_str = text[start:end]
        return json.loads(json_str)


def clean_csv_with_ai(csv_path):
    df = pd.read_csv(csv_path)
    sample = df.head(5).to_dict(orient="records")

    prompt = f"""
    Du bekommst Beispielzeilen einer CSV-Datei.

    Gib NUR gültiges JSON zurück im Format:

    {{
      "schema": {{
        "alte_spalte": "neue_spalte"
      }}
    }}

    Hier die Beispielzeilen:
    {json.dumps(sample, indent=2)}
    """

    response = ollama.chat(
        model="llama3.1",
        messages=[{"role": "user", "content": prompt}]
    )

    ai_text = response["message"]["content"]

    print("\n🧠 Roh-Antwort des Modells:")
    print(ai_text)

    print("\n🔍 Extrahiere JSON...")
    result_json = extract_json(ai_text)

    return result_json


if __name__ == "__main__":
    result = clean_csv_with_ai("data/orders.csv")
    print("\n🎉 Gereinigtes Schema:")
    print(json.dumps(result, indent=2, ensure_ascii=False))

