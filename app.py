from flask import Flask, request, jsonify, send_from_directory
import requests
import os
import json
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import io
import base64
from uuid import uuid4

load_dotenv()

app = Flask(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=' + GEMINI_API_KEY

#  carpeta 'static' para las imágenes
STATIC_FOLDER = 'static'
if not os.path.exists(STATIC_FOLDER):
    os.makedirs(STATIC_FOLDER)

@app.route('/api/extract_chart_data', methods=['POST'])
def extract_chart_data():
    try:
        initial_response = request.json.get('initialResponse')
        if not initial_response:
            return jsonify({'error': 'Missing initialResponse'}), 400

        prompt = f"""
        Basado en el siguiente texto, extrae los datos para una gráfica de BARRAS.
        Devuelve los datos EN FORMATO JSON, con las siguientes claves:
        "labels" (array de strings) y "values" (array de números).

        Texto:
        {initial_response}

        Ejemplo de respuesta:
        {{
          "labels": ["Enero", "Febrero", "Marzo"],
          "values": [10, 25, 18]
        }}
        """

        response = requests.post(GEMINI_API_URL, json={
            'contents': [{'parts': [{'text': prompt}]}],
        })
        response.raise_for_status()

        response_data = response.json()
        if not response_data or not response_data.get('candidates') or not isinstance(response_data['candidates'], list) or len(response_data['candidates']) == 0 or not response_data['candidates'][0].get('content') or not response_data['candidates'][0]['content'].get('parts') or not isinstance(response_data['candidates'][0]['content']['parts'], list) or len(response_data['candidates'][0]['content']['parts']) == 0 or not isinstance(response_data['candidates'][0]['content']['parts'][0].get('text'), str):
             return jsonify({'error': 'Invalid response format from Gemini API', 'details': response_data}), 500 #  detalles del error

        json_text = response_data['candidates'][0]['content']['parts'][0]['text']

        try:
            chart_data = json.loads(json_text)
            if not isinstance(chart_data, dict) or 'labels' not in chart_data or not isinstance(chart_data['labels'], list) or 'values' not in chart_data or not isinstance(chart_data['values'], list):
                return jsonify({'error': 'Invalid response format from Gemini API, labels or values missing or wrong type'}), 500
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid JSON returned by Gemini API'}), 500

        # --- Generación de la Gráfica con Matplotlib ---
        labels = chart_data['labels']
        values = chart_data['values']

        plt.figure(figsize=(8, 6))  # Tamaño de la figura (ancho, alto) - Ajusta según necesites
        plt.bar(labels, values, color='skyblue')  # Gráfico de barras.  Cambia 'skyblue' por otro color si quieres.
        plt.xlabel("Categorías")   #  etiqueta en el eje X
        plt.ylabel("Valores")      #  etiqueta en el eje Y
        plt.title("Datos Extraídos") # Título de la gráfica
        plt.xticks(rotation=45, ha="right")  # Rota las etiquetas del eje X para que sean legibles
        plt.tight_layout() # Ajusta el espaciado

        # --- Guardar la Gráfica como Imagen (en memoria y luego a un archivo) ---
        img_buffer = io.BytesIO() # Crea un buffer en memoria
        plt.savefig(img_buffer, format='png')  # Guarda la gráfica en el buffer, en formato PNG
        img_buffer.seek(0) #  puntero al principio
        plt.close()

        #  nombre único para el archivo de imagen
        image_filename = f"chart_{uuid4()}.png"
        image_path = os.path.join(STATIC_FOLDER, image_filename)

        # Guarda la imagen desde el buffer al archivo
        with open(image_path, 'wb') as image_file:
            image_file.write(img_buffer.read())

        # --- Devolver la URL de la Imagen ---
        image_url = f"http://192.168.1.7:5000/static/{image_filename}" #  URL completa (¡AJUSTA!)
        return jsonify({'imageUrl': image_url})



    except requests.exceptions.RequestException as e:
        print(f"Error de solicitud: {e}")
        return jsonify({'error': 'Request error', 'details': str(e)}), 500
    except Exception as e:
        print(f"Error inesperado: {e}")  #  errores en la consola
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500


# Nueva ruta para servir las imágenes estáticas
@app.route('/static/<filename>')
def static_files(filename):
    return send_from_directory(STATIC_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')