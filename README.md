# Creai TravelBot – Agente Virtual de Viajes (Slack + Gemini)

Agente virtual para solicitudes de viaje de negocio en Creai, operando por mensajes directos en Slack y desplegado en Google Cloud Run. Procesa eventos de Slack por webhook HTTP en el puerto 8080, integra la IA conversacional de Gemini usando el SDK oficial, y almacena información en Google Sheets y Firebase.

---

## Características principales

- Conversación fluida y natural por DM en Slack.
- Recepción de eventos **solo por HTTP POST** en el endpoint público `/slack/events` (no sockets, no RTM).
- Backend en Python, preparado para Google Cloud Run.
- Motor IA principal: Gemini (`google-genai`). Fallback automático a agentes open source si Gemini falla.
- Gestión de usuarios y políticas desde Google Sheets. Datos sensibles y preferencias en Firebase.
- Validación, logs y QA robustos.
- Todos los precios y políticas en USD.

---

## Quickstart

### 1. Clona el repositorio

```bash
git clone https://github.com/tu-org/creai-travelbot.git
cd creai-travelbot
2. Instala dependencias
bash
Copiar
Editar
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
requirements.txt debe incluir al menos:

bash
Copiar
Editar
google-genai
Flask
firebase-admin
gspread
oauth2client
requests
python-dotenv
# y cualquier otra librería auxiliar (ej. para validar firma Slack)
3. Configura variables de entorno
El bot requiere las siguientes variables de entorno (puedes usar .env):

env
Copiar
Editar
GEMINI_API_KEY=tu_api_key_de_gemini
SLACK_SIGNING_SECRET=tu_signing_secret_de_slack
SLACK_BOT_TOKEN=tu_bot_token_de_slack
GOOGLE_APPLICATION_CREDENTIALS=path/al/archivo/service_account.json
FIREBASE_CREDENTIALS=path/al/archivo/firebase_credentials.json
4. Configuración de Slack
Crea una app en Slack (si no existe).

Activa Event Subscriptions:

URL de Request:

arduino
Copiar
Editar
https://travelbot-slack-uxcqgkjcna-uc.a.run.app/slack/events
Asegúrate de que la app tenga permisos para:

Leer mensajes en DMs (im:history)

Enviar mensajes (chat:write)

Leer usuarios (users:read)

Usa el token y el signing secret correctos en las variables de entorno.

5. Deploy en Google Cloud Run
Empaqueta la app (Dockerfile recomendado) y despliega en Google Cloud Run.

Expón el servicio en el puerto 8080.

Verifica que el endpoint /slack/events es accesible públicamente.

6. Uso de Gemini
El bot usa la librería google-genai.

Sigue siempre la guía oficial para instanciar el cliente y realizar inferencia.

No uses librerías legacy ni métodos obsoletos.

El API key de Gemini debe estar en la variable de entorno GEMINI_API_KEY.

7. Seguridad y QA
Toda petición de Slack debe validar firma (X-Slack-Signature, X-Slack-Request-Timestamp).

Los datos sensibles van cifrados en Firebase.

Todos los logs críticos (errores, caídas de servicio, fallos de Gemini, etc.) deben alertar al equipo técnico.

El bot nunca responde en canales, solo en DMs, y jamás expone datos sensibles fuera del contexto privado.

Troubleshooting
Si el bot no responde en Slack:

Revisa los logs del endpoint en Google Cloud Run.

Valida la configuración del webhook y firma de Slack.

Asegúrate de que el puerto es 8080 y la ruta es /slack/events.

Confirma que GEMINI_API_KEY y credenciales de Google están bien configuradas.

Si Gemini da error o timeout:

El bot intentará fallback automático a un motor open source.

Si todo falla, el usuario será notificado y el error será logueado.

Recursos útiles
Guía oficial Gemini (Python)

Documentación Gemini

API Slack Events

Google Cloud Run

Firebase Admin Python SDK

License
MIT (o la que corresponda a tu proyecto)

Copiar
Editar
