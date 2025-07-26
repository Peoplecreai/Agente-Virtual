# Creai TravelBot – Agente Virtual de Viajes (Slack + Gemini)

Creai TravelBot es un asistente para gestionar solicitudes de viaje corporativo mediante mensajes directos en Slack.  El backend está escrito en Python y se ejecuta en Google Cloud Run.  Todas las interacciones se reciben a través de la API de eventos de Slack y las respuestas se generan con la API Gemini de Google.

---

## Características principales

- Conversación natural por DM en Slack.
- **Eventos recibidos únicamente por HTTP POST** en `/slack/events`.
- IA principal: Gemini (`google-generativeai`) con fallback a modelos open source.
- Configuración de usuarios en Google Sheets y almacenamiento seguro en Firebase.
- Validación de firmas de Slack y registro detallado de errores.

---

## Instalación rápida

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-org/creai-travelbot.git
cd creai-travelbot
```

### 2. Crear entorno y dependencias

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

`requirements.txt` incluye, entre otras:

- `Flask`
- `slack_bolt`
- `google-generativeai`
- `firebase-admin`
- `gspread`

### 3. Variables de entorno

Configura un archivo `.env` (o exporta en tu entorno) con:

```bash
GEMINI_API_KEY=<tu_api_key>
SLACK_SIGNING_SECRET=<tu_signing_secret>
SLACK_BOT_TOKEN=<tu_bot_token>
GOOGLE_SERVICE_ACCOUNT=<ruta/al/service_account.json>
GOOGLE_SHEET_ID=<id_de_tu_hoja>
```

### 4. Configuración de Slack

1. Crea una aplicación en [Slack API](https://api.slack.com/apps) si aún no existe.
2. Activa **Event Subscriptions** y define la _Request URL_ a
   `https://<tu-dominio>/slack/events`.
3. Otorga a la app los permisos `im:history`, `chat:write` y `users:read`.
4. Copia el **Bot User OAuth Token** y el **Signing Secret** en las variables de entorno anteriores.
5. Sigue la [guía oficial de Slack Events API](https://api.slack.com/apis/connections/events-api)
   para verificar `X-Slack-Signature` y `X-Slack-Request-Timestamp` en cada
   solicitud.

### 5. Uso de la API Gemini

El bot emplea el paquete `google-generativeai` siguiendo la guía oficial de
[Google AI Studio](https://ai.google.dev/docs).  Para inicializar el cliente:

```python
from google import generativeai as genai
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-pro")
```

Todas las llamadas deben realizarse tal cual lo especifica la documentación,
utilizando `generate_content` para enviar el texto del usuario y obteniendo la
respuesta en `response.text`.

### 6. Ejecución local

```bash
flask run --host 0.0.0.0 --port 8080
```

Slack enviará los eventos a `http://localhost:8080/slack/events` si usas una
herramienta de túnel como `ngrok`.

### 7. Despliegue en Cloud Run

1. Crea una imagen con tu herramienta de contenedores favorita.
2. Despliega en Google Cloud Run exponiendo el puerto `8080`.
3. Asegúrate de que el endpoint `/slack/events` sea público.

### 8. Pruebas

Ejecuta los tests con:

```bash
pytest
```

---

## Recursos adicionales

- [Documentación oficial de Slack Events API](https://api.slack.com/apis/connections/events-api)
- [Guía de `google-generativeai`](https://ai.google.dev/docs)
- [Firebase Admin Python SDK](https://firebase.google.com/docs/admin/setup)
- [Google Cloud Run](https://cloud.google.com/run)

## Licencia

MIT
