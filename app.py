from flask import Flask, request, jsonify
import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()  # Carga las variables de entorno desde el archivo .env

app = Flask(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=' + GEMINI_API_KEY #Reemplaza


@app.route('/api/extract_chart_data', methods=['POST'])
def extract_chart_data():
    try:
        initial_response = request.json.get('initialResponse')  # Obtiene la respuesta inicial del frontend
        if not initial_response:
            return jsonify({'error': 'Missing initialResponse'}), 400

        prompt = f"""
        Basado en el siguiente texto, extrae los datos relevantes para generar una gráfica. Devuelve los datos EN FORMATO JSON,
        con las siguientes claves: "labels" (un array de strings para las etiquetas del eje X) y "values" (un array de números para los valores del eje Y).
        Si el texto no contiene datos para una gráfica, devuelve un objeto con "labels" y "values" vacíos.

        Texto:
        {initial_response}

        Ejemplo de respuesta JSON válida:
        {{
          "labels": ["Enero", "Febrero", "Marzo"],
          "values": [10, 25, 18]
        }}

        Otro ejemplo (si no hay datos):
        {{
            "labels": [],
            "values": []
        }}
        """

        response = requests.post(GEMINI_API_URL, json={
            'contents': [{'parts': [{'text': prompt}]}],
        })
        response.raise_for_status()  # Lanza una excepción si la solicitud falla (4xx o 5xx)

        #Validaciones
        response_data = response.json()
        if not response_data or not response_data.get('candidates') or not isinstance(response_data['candidates'], list) or len(response_data['candidates']) == 0 or not response_data['candidates'][0].get('content') or not response_data['candidates'][0]['content'].get('parts') or not isinstance(response_data['candidates'][0]['content']['parts'], list) or len(response_data['candidates'][0]['content']['parts']) == 0 or not isinstance(response_data['candidates'][0]['content']['parts'][0].get('text'), str):
            return jsonify({'error': 'Invalid response format from Gemini API'}), 500


        json_text = response_data['candidates'][0]['content']['parts'][0]['text']

        try:
            chart_data = json.loads(json_text)
            #Validacion del JSON
            if not isinstance(chart_data, dict) or 'labels' not in chart_data or not isinstance(chart_data['labels'], list) or 'values' not in chart_data or not isinstance(chart_data['values'], list):
                 return jsonify({'error': 'Invalid response format from Gemini API, labels or values missing'}), 500

        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid JSON returned by Gemini API'}), 500


        return jsonify(chart_data)  # Devuelve los datos extraídos como JSON


    except requests.exceptions.RequestException as e:
        print(f"Error de solicitud: {e}")
        return jsonify({'error': 'Request error', 'details': str(e)}), 500
    except Exception as e:
        print(f"Error inesperado: {e}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')  