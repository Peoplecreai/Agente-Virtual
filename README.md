Contexto general
Desarrolla desde cero, en Python, un agente virtual para solicitudes de viajes de negocio en Creai, que opera únicamente vía mensajes directos (DM) en Slack. El backend se despliega en Google Cloud.
Conéctate a Google Sheets (para consultar usuarios y políticas), Firebase (para guardar datos personales, preferencias y memoria conversacional), Gemini (como primer motor IA, y si no cumple, reemplaza automáticamente por un agente conversacional open source tipo Llama, Mistral, Rasa, u otro equivalente). Usa SerpAPI para búsquedas de direcciones o venues, y cualquier otro servicio gratuito o open source necesario.

No uses la API de Okibi ni ninguna solución de pago para IA conversacional. Prioriza siempre servicios gratuitos, open source o económicos.

## Instalación y configuración

1. Instala las dependencias de Python:

   ```bash
   pip install -r requirements.txt
   ```

2. Define las siguientes variables de entorno para ejecutar el bot:

   - `SLACK_BOT_TOKEN` y `SLACK_SIGNING_SECRET`: credenciales de tu aplicación Slack.
   - `GEMINI_API_KEY`: API key para la librería oficial `google-genai`.
   - `GOOGLE_SHEET_ID`: ID de la hoja de Google Sheets que contiene la información de usuarios.
   - `GOOGLE_SERVICE_ACCOUNT`: ruta al JSON del servicio de Google para acceder a Sheets y Firebase.
   - `LLAMA_MODEL_PATH` (opcional): modelo local a usar si Gemini falla.

3. Ejecuta la aplicación de desarrollo:

   ```bash
   python app.py
   ```

   El servidor se inicia en `http://0.0.0.0:8080`.

## Endpoint de Slack

El bot recibe todos los eventos de Slack vía HTTP POST en la ruta:

```
https://travelbot-slack-uxcqgkjcna-uc.a.run.app/slack/events
```

Registra esta URL en Slack (Event Subscriptions > Request URL). La firma se valida automáticamente usando los encabezados `X-Slack-Signature` y `X-Slack-Request-Timestamp` según la [documentación oficial](https://api.slack.com/authentication/verifying-requests-from-slack).

## Uso de Gemini

El código sigue la guía oficial de [google-genai](https://github.com/googleapis/python-genai) para generar contenido:

```python
from google import genai

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="mensaje del usuario aquí",
)
texto = response.text
```

Si Gemini no está disponible, se usa un modelo open source (por ejemplo, Llama) como respaldo automático.

Requisitos funcionales y reglas
Conversación natural: El bot debe interpretar y responder mensajes en lenguaje libre (“hola”, “viajo a Madrid”, “voy de CDMX a NYC del 12 al 16”). Extrae todos los datos relevantes, confirma, pide lo que falta y nunca fuerza formatos rígidos.

Identificación automática: Obtén Slack ID y cruza en Google Sheets para nombre, fecha de nacimiento, seniority (L-0 a L-10, L7+ es C-level), email y cualquier otro dato disponible. Si algo falta, solicítalo al usuario y guárdalo en Firebase.

Datos sensibles: El número de pasaporte y visa solo se pide cuando hace falta (por destino); se almacena cifrado en Firebase y solo se confirma en viajes futuros (permitiendo actualización).

Política de viajes:

Vuelos: clase económica, equipaje de mano incluido.

Hospedaje: solo hoteles en zona segura y cerca del venue; tarifas máximas por seniority y región (en USD):

C-Level: México $150, EUA/Canadá $200, Latam $180, Europa $250

General: México $75, EUA/Canadá $150, Latam $120, Europa $180

Viáticos diarios (USD): México/Latam $50, EUA/Canadá $120, Europa $100.

Hospedaje compartido solo como opción, nunca impuesto.

Cualquier excepción a políticas (presupuesto, clase, zona) se escala a Finanzas/Presidencia y se informa al usuario.

Extracción y validación:

Extrae fechas, origen, destino, venue/dirección (si es ambigua, usa SerpAPI/Gemini para buscar la real).

Pide y valida motivos de viaje, preferencias (aerolínea, hotel, asiento, equipaje, viajero frecuente).

Valida datos: fechas coherentes, ciudades existentes, todos los montos y tarifas en USD, ninguna omisión.

Opciones y confirmación:

Presenta al menos 3 vuelos y hoteles dentro de política. Permite cambiar cualquier dato antes de confirmar.

Si no hay opciones válidas, busca alternativas o lo informa y sugiere solución.

Muestra siempre resumen antes de confirmar y enviar a Finanzas.

Si algo falla, no avanzas y notificas al usuario (con logs).

Memoria y personalización:

Guarda preferencias y memoria de viajes. En siguientes viajes, solo confirma datos vigentes (“¿Quieres mismo hotel que la vez pasada?”).

Después de cerrar la solicitud, sugiere tips y lugares en el destino, y pide feedback.

Usa los datos previos para mejorar experiencia y nunca pedir dos veces lo mismo.

Robustez, debugging y QA
Si el bot no responde en Slack, detecta y loguea:

Errores de conexión Slack API (auth, permisos, eventos).

Problemas de deploy (puertos, endpoints, timeouts Google Cloud).

Fallos al llamar Gemini o el agente IA alternativo (status codes, respuestas vacías, caídas).

Problemas con Google Sheets (acceso, credenciales, limits).

Errores en Firebase (conexión, escritura, reglas).

Exceptions no capturadas, stack traces y fallos lógicos.

Genera logs detallados y envía notificaciones al equipo técnico en errores críticos (por webhook, correo, Slack, lo que sea más rápido).

Siempre avisa al usuario si hay un error técnico (“Estamos experimentando un problema, ya fue reportado al equipo. Por favor, intenta más tarde”).

Permite reanudar solicitudes interrumpidas (timeout, crash) recuperando contexto desde Firebase.

Motor de IA conversacional
Por default usa Gemini para entender y generar lenguaje natural.

Si Gemini no responde correctamente o no es suficiente, implementa un agente open source (Llama, Mistral, Rasa, etc.) y lo usas como fallback inmediato.

Si ninguna IA está disponible, avisa al usuario y reporta a ingeniería.

No uses Okibi, ni ningún servicio de pago para el motor IA.

User Stories y Criterios de Aceptación
US1. Como usuario, quiero poder solicitar viajes en lenguaje natural y que el bot extraiga todo lo relevante sin forzar formatos.
Criterio: Extrae y confirma todos los datos, sin requerir frases o comandos especiales.

US2. Como usuario, quiero que el bot valide y confirme toda la información antes de enviar, para evitar errores.
Criterio: Muestra resumen para confirmación antes de cerrar y enviar.

US3. Como usuario, quiero que mis preferencias y datos sensibles se almacenen seguros y solo se pidan una vez, pero pueda actualizarlos.
Criterio: Usa Firebase, confirma datos existentes antes de pedir y permite edición.

US4. Como usuario, quiero recibir solo opciones dentro de política y saber cuando algo no se puede, con explicación clara.
Criterio: Si algo excede límites, lo escala y explica por qué.

US5. Como usuario, quiero modificar cualquier dato antes de la confirmación final, sin repetir todo el proceso.
Criterio: Permite editar partes específicas del flujo sin resetear.

US6. Como usuario, quiero que mis datos sensibles solo se pidan y expongan por DM, nunca en canales públicos.
Criterio: Todas las interacciones confidenciales se hacen solo por DM.

US7. Como usuario, quiero poder pausar y reanudar el proceso sin perder avance, en caso de interrupciones.
Criterio: Guarda el progreso y recupera el contexto desde Firebase.

US8. Como usuario, quiero que todos los montos y tarifas estén en USD.
Criterio: Siempre presenta valores y cálculos en dólares estadounidenses.

US9. Como usuario, quiero recibir sugerencias y feedback post-viaje, y que se tome en cuenta mi retroalimentación.
Criterio: El bot sugiere lugares, pide feedback y aprende para la siguiente vez.

US10. Como usuario, quiero que cualquier error técnico se reporte automáticamente y que siempre se me avise si no se pudo procesar mi solicitud.
Criterio: El bot genera logs y avisa al usuario cada vez que hay un error.

Checklist de QA
¿Responde SIEMPRE a cualquier DM en Slack?

¿Loguea todo error de integración, deploy o servicio externo?

¿Valida todas las entradas contra política Creai y edge cases?

¿Permite editar y confirmar cada dato antes de enviar?

¿Escala solicitudes fuera de política?

¿Solo almacena y pide datos sensibles una vez, permitiendo actualización?

¿Opera 100 % bajo DM, nunca expone información en canales?

¿Puede cambiar de Gemini a open source IA automáticamente si falla?

¿Guarda memoria y preferencias por usuario?

¿Sugiere lugares/tips y pide feedback post-viaje?

¿Todos los precios están en USD?

¿Permite reanudar procesos caídos sin perder avance?

¿Siempre avisa al usuario de cualquier error, incluso si es técnico?

No omitas ninguna función, validación, ni edge case. Desarrolla desde cero, usando Python. El agente debe ser robusto, resiliente y auditable, cumpliendo políticas, experiencia de usuario y QA descritos. El foco es que si el bot deja de responder o hay cualquier error, siempre lo detecta, lo loguea, lo reporta y lo comunica al usuario.
