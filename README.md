# Ecuaplanet-Back-Graficas
# API de Extracción de Datos para Gráficas (Gemini)
## Descripción

Esta API de Flask extrae datos relevantes para la generación de gráficas a partir de texto utilizando el modelo Gemini Pro de Google.  Recibe una cadena de texto como entrada y, mediante una solicitud a la API de Gemini, intenta extraer los datos en formato JSON adecuado para crear una gráfica (específicamente, las etiquetas del eje X y los valores del eje Y).  Maneja errores de solicitud y de formato de respuesta.

## Lenguaje

Python

## Requisitos

*   Python 3.6+
*   Flask
*   `requests`
*   `python-dotenv`
*   Una clave de API válida para Gemini Pro de Google.

## Instalación

1.  **Clonar el repositorio:**

    ```bash
    git clone [https://github.com/isaaxcbps/Ecuaplanet-Back-Graficas.git](https://github.com/isaaxcbps/Ecuaplanet-Back-Graficas.git)
    cd Ecuaplanet-Back-Graficas
    ```

2.  **Crear un entorno virtual (recomendado):**

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # En Linux/macOS
    venv\Scripts\activate  # En Windows
    ```

3.  **Instalar las dependencias:**

    ```bash
    pip install flask requests python-dotenv
    ```

4.  **Configurar la clave de API:**

    *   Crea un archivo llamado `.env` en el directorio raíz del proyecto.
    *   Dentro del archivo `.env`, agrega la siguiente línea, reemplazando `TU_CLAVE_DE_API` con tu clave real de Gemini:

        ```
        GEMINI_API_KEY=TU_CLAVE_DE_API
        ```
     * Asegúrate de *no* incluir el archivo `.env` en tu sistema de control de versiones (p. ej., agrégalo a `.gitignore` si usas Git) para evitar exponer tu clave de API.

## Estructura del Código

- El código define una aplicación Flask con un único endpoint: `/api/extract_chart_data`.
- Utiliza la biblioteca `python-dotenv` para cargar variables de entorno desde un archivo `.env`.
- La función `extract_chart_data` maneja las solicitudes POST.
    - Obtiene la entrada `initialResponse` del cuerpo JSON de la solicitud.
    - Construye un prompt para la API de Gemini, solicitando la extracción de datos en formato JSON.
    - Realiza una solicitud a la API de Gemini.
    - Valida exhaustivamente la respuesta de Gemini para garantizar que tenga el formato correcto.
        - Comprueba que la respuesta sea un JSON válido.
        - Verifica la presencia y tipo de los campos `candidates`, `content` y `parts`.
        - Asegura que el texto extraído sea un JSON con las claves `labels` y `values`, y que estos sean listas.
    - Maneja los errores:
        - `requests.exceptions.RequestException`: Errores relacionados con la solicitud HTTP.
        - `json.JSONDecodeError`: Errores al decodificar la respuesta JSON.
        - `Exception`: Cualquier otro error inesperado.
    - Devuelve los datos extraídos en formato JSON o un mensaje de error adecuado.
- La aplicación se ejecuta en modo de depuración en el puerto 5000, accesible desde cualquier interfaz de red (`0.0.0.0`).

## Ejecución

1.  **Asegúrate de haber seguido los pasos de instalación.**
2.  **Ejecuta la aplicación:**

    ```bash
    python your_script_name.py  # Reemplaza con el nombre de tu archivo Python (app.py en este caso).
    ```

    La aplicación Flask se iniciará y estará escuchando en `http://0.0.0.0:5000`.

## Uso

La API tiene un único endpoint: `/api/extract_chart_data`.  Debes enviar una solicitud POST a este endpoint con un cuerpo JSON que contenga la clave `initialResponse`. El valor de esta clave debe ser el texto del cual quieres extraer los datos.

**Ejemplo de solicitud (usando `curl`):**

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"initialResponse": "Las ventas fueron: Enero 10, Febrero 25, Marzo 18"}' \
  http://localhost:5000/api/extract_chart_data
