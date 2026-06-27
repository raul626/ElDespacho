# El Despacho — Panel de Noticias Matutino

App Flask que genera un resumen diario balanceado de noticias (Peru + EE.UU., politica/economia/tecnologia) usando la API de Anthropic con la herramienta de busqueda web.

## Estructura
```
eldespacho/
  app.py
  requirements.txt
  templates/index.html
  static/style.css
  static/app.js
```

## Despliegue (mismo flujo que PortfolioIQ-Fortuna)

1. **Crear repo en GitHub** (ej. `raul626/ElDespacho`) y subir estos archivos via la interfaz web de GitHub (arrastrar y soltar / "Add file" -> "Upload files").

2. **Crear el servicio en Render**
   - New -> Web Service -> conecta el repo
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn app:app`
   - Plan: Free

3. **Variable de entorno en Render**
   - En el servicio -> Environment -> Add Environment Variable
   - Key: `ANTHROPIC_API_KEY`
   - Value: tu clave de la API de Anthropic (console.anthropic.com)
   - **Nunca subas la clave al repositorio de GitHub.**

4. **Deploy** — Render instala dependencias y levanta la app. La URL sera algo como `eldespacho.onrender.com`.

## Uso diario
Abre la URL en tu iPad cada mañana, toca "Generar resumen de hoy". El backend llama a Claude con la herramienta de busqueda web y devuelve titulares balanceados por seccion.

## Ajustar fuentes o secciones
Edita el diccionario `SOURCES` y `SYSTEM_PROMPT` en `app.py` para:
- Cambiar la lista de medios preferidos por seccion
- Agregar o quitar secciones
- Ajustar el numero de titulares por seccion (linea final del system prompt)

## Notas de costo
Cada clic en "Generar resumen" hace una llamada a la API con busqueda web (varias consultas internas). El costo es bajo para un uso de 1-2 veces al dia, pero si planeas abrir la app muchas veces al dia, considera agregar un cache simple (guardar el JSON del dia y solo regenerar si cambia la fecha).
