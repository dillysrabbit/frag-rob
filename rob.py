from flask import Flask, request, jsonify
from openai import OpenAI
from flask_cors import CORS
import os
import logging

app = Flask(__name__)
CORS(app)

# Logging konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# OpenAI-Client initialisieren
try:
    openai.api.key = os.environ.get("OPENAI_API_KEY"))
    if not client.api_key: # Überprüfen, ob der API Key gesetzt ist
        raise ValueError("OPENAI_API_KEY ist nicht gesetzt. Bitte Umgebungsvariable setzen.")
    logger.info("OpenAI-API erfolgreich initialisiert.")
except ValueError as e:
    logger.error(f"Initialisierungsfehler: {e}")
    exit(1) # Beende das Programm, wenn der API-Key fehlt

SYSTEM_PROMPT = (
    "Du bist Rob, ein preisgekrönter Journalist eines deutschen Leitmediums. Du bist ein überzeugter Europäer und Transatlantiker. Deine Haltung ist undogmatisch-konservativ. Du bist Experte für die bundesdeutsche Innen- und Außenpolitik. Du hast fundierte Kenntnisse der politischen Geschichte der Bundesrepublik, des Föderalismus, der politischen Parteien und des Parteiensystems in Bund und Ländern und der politischen Kommunikation. Du kennst die relevanten politischen Akteure, die Funktionsweise von Verwaltung und Ministerien und die Dynamiken der Macht. Deine Aufgabe ist es Dir zunächst eine Übersicht über den Stand der aktuellen politischen Diskussion zu dem angefragten Thema zu verschaffen und dann auf Basis der gewonnenen Erkenntnisse und deines Wissens eine fundierte journalistische Einordnung des angefragten Themas vorzunehmen, die zentralen Akteure (Personen und Organisationen) zu benennen, ihre Positionen und Argumente zu reflektieren und möglichst mit direkten Zitaten zu unterstützen.Nimm dann eine kritische Bewertung dieser Positionen und Argumente vor und wäge sie gegeneinander ab, bevor Du schließlich in einen pointierten Meinungsbeitrag deine Haltung zu dem angefragten Thema wider gibst."
)

@app.route('/chat', methods=['POST'])
def chat():
    if not request.is_json:
        logger.warning("Ungültige Anfrage: Kein JSON.")
        return jsonify({'error': 'Ungültige Anfrage: Erwarte JSON'}), 400

    data = request.get_json()
    user_input = data.get('message')

    if not user_input:
        logger.warning("Ungültige Anfrage: Keine Nachricht erhalten.")
        return jsonify({'error': 'Ungültige Anfrage: Nachricht fehlt'}), 400

    if len(user_input) > 4000:  # Beispielhafte Validierung
        logger.warning(f"Ungültige Anfrage: Nachricht zu lang ({len(user_input)} Zeichen).")
        return jsonify({'error': 'Ungültige Anfrage: Nachricht zu lang (max. 4000 Zeichen erlaubt)'}), 400

    try:
        response = client.chat.completions.create(
            model="gpt-4",  # Oder gpt-3.5-turbo, je nach Verfügbarkeit
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input}
            ],
            max_tokens=3000, # ggf. anpassen
            temperature=1.0 # ggf. anpassen
        )
        bot_reply = response.choices[0].message.content.strip()
        logger.info(f"Erfolgreiche Anfrage: Antwortlänge {len(bot_reply)} Zeichen.")
        return jsonify({'response': bot_reply}), 200

    except openai.APIError as e:
        logger.error(f"OpenAI API Fehler: {e}")
        return jsonify({'error': f"OpenAI API Fehler: {e.http_status} - {e.error.message}"}), e.http_status if hasattr(e, 'http_status') else 500
    except openai.RateLimitError as e:
        logger.error(f"OpenAI Rate Limit Fehler: {e}")
        return jsonify({'error': "OpenAI Rate Limit erreicht. Bitte später erneut versuchen."}), 429
    except openai.APIConnectionError as e:
        logger.error(f"OpenAI Verbindungsfehler: {e}")
        return jsonify({'error': "Verbindung zur OpenAI API fehlgeschlagen."}), 500
    except openai.InvalidRequestError as e:
        logger.error(f"OpenAI Ungültige Anfrage Fehler: {e}")
        return jsonify({'error': f"Ungültige Anfrage an die OpenAI API: {e.error.message}"}), 400
    except Exception as e:
        logger.exception("Unerwarteter Fehler:") # Gibt den gesamten Stacktrace aus!
        return jsonify({'error': 'Ein unerwarteter Fehler ist aufgetreten.'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
