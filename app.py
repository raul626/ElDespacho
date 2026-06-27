import os
import json
import re
from datetime import datetime
from flask import Flask, render_template, jsonify, request
import requests

app = Flask(__name__)

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-sonnet-4-6"

# Fuentes balanceadas por defecto. Editar aqui para ajustar el panel de medios.
SOURCES = {
    "peru_politica": ["El Comercio", "La Republica", "Peru21", "Expreso", "RPP", "Andina"],
    "peru_economia": ["Gestion", "BCRP", "Andina", "El Comercio - Economia"],
    "us_politica": ["Reuters", "AP", "The Wall Street Journal", "NPR", "The Hill", "Washington Post"],
    "us_finanzas": ["Reuters", "Bloomberg", "WSJ", "CNBC", "Schwab Market Update"],
    "tecnologia": ["Reuters Technology", "The Verge", "Ars Technica", "Bloomberg Technology"],
}

SECTION_LABELS = {
    "peru_politica": "Peru - Politica",
    "peru_economia": "Peru - Economia",
    "us_politica": "EE.UU. - Politica",
    "us_finanzas": "EE.UU. - Finanzas",
    "tecnologia": "Tecnologia",
}

SYSTEM_PROMPT = """Eres un editor de noticias que prepara un despacho matutino balanceado para un lector en Peru.
Reglas estrictas:
1. Usa la herramienta de busqueda web para encontrar noticias REALES de hoy o de las ultimas 24-48 horas.
2. Para temas politicamente sensibles, balancea deliberadamente fuentes con distintas lineas editoriales (no dependas de una sola fuente por seccion).
3. Separa hechos de opinion. No incluyas tu propia opinion ni interpretacion politica.
4. Cada titular debe tener: titulo corto, 1-2 lineas de contexto factual, y el nombre de la fuente.
5. Nunca reproduzcas texto citado de mas de 15 palabras de una misma fuente; parafrasea.
6. Responde UNICAMENTE con JSON valido, sin texto antes o despues, sin backticks de markdown.

Formato de salida (JSON):
{
  "fecha": "YYYY-MM-DD",
  "secciones": {
    "peru_politica": [{"titulo": "...", "contexto": "...", "fuente": "..."}],
    "peru_economia": [...],
    "us_politica": [...],
    "us_finanzas": [...],
    "tecnologia": [...]
  }
}
Incluye entre 4 y 6 titulares por seccion."""


def build_user_prompt():
    today = datetime.now().strftime("%Y-%m-%d")
    lines = [f"Fecha de hoy: {today}.", "Genera el despacho matutino con estas secciones y fuentes preferidas:"]
    for key, label in SECTION_LABELS.items():
        lines.append(f"- {label}: prioriza fuentes como {', '.join(SOURCES[key])}, pero usa cualquier fuente confiable si es necesario.")
    return "\n".join(lines)


def extract_json(text):
    text = text.strip()
    text = re.sub(r"^```json", "", text)
    text = re.sub(r"^```", "", text)
    text = re.sub(r"```$", "", text)
    return json.loads(text.strip())


@app.route("/")
def index():
    return render_template("index.html", labels=SECTION_LABELS)


@app.route("/api/news-digest", methods=["POST"])
def news_digest():
    if not ANTHROPIC_API_KEY:
        return jsonify({"error": "ANTHROPIC_API_KEY no configurada en el servidor."}), 500

    payload = {
        "model": MODEL,
        "max_tokens": 4000,
        "system": SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": build_user_prompt()}],
        "tools": [{"type": "web_search_20250305", "name": "web_search", "max_uses": 12}],
    }

    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }

    try:
        resp = requests.post(ANTHROPIC_API_URL, headers=headers, json=payload, timeout=170)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        return jsonify({"error": f"Error llamando a la API de Anthropic: {str(e)}"}), 502

    full_text = "".join(
        block.get("text", "") for block in data.get("content", []) if block.get("type") == "text"
    )

    try:
        parsed = extract_json(full_text)
    except (json.JSONDecodeError, AttributeError):
        return jsonify({"error": "No se pudo interpretar la respuesta del modelo.", "raw": full_text}), 502

    return jsonify(parsed)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
