# ---------------- streamlit_app.py (Versión Luminarys Production con Nichos) ----------------

from __future__ import annotations
import streamlit as st
import google.generativeai as genai
import json
from typing import List, Dict
import os

# ---------- LISTA DE NICHOS DISPONIBLES ----------
# He procesado y limpiado la lista que me diste para usarla en el selector.
ALL_NICHES = [
    # Atributos Físicos o Estética
    "Atributo: BBW / Talla Grande",
    "Atributo: Pies (Foot Fetish)",
    "Atributo: Madura (Mature / Cougar)",
    "Atributo: Petite / Pequeña",
    "Atributo: Musculosa",
    "Atributo: Tatuajes y Piercings (Alt-Model)",
    "Atributo: Gótica / Emo",
    "Atributo: Rasgos Étnicos (Latina, Asiática, etc.)",
    # Actividades o Fetiches
    "Actividad: ASMR Erótico",
    "Actividad: Dominación Financiera (Findom)",
    "Actividad: Juego de Roles (Roleplay)",
    "Actividad: Humillación y Degradación",
    "Actividad: Adoración (Worship)",
    "Actividad: BDSM",
    "Actividad: Cuckolding",
    "Actividad: Contenido de Embarazo (Pregnancy)",
    # Hobbies, Arte y Creatividad
    "Hobby: Arte Sin Censura",
    "Hobby: Cosplay (Erótico y No Erótico)",
    "Hobby: Escritura y Poesía Erótica",
    "Hobby: Fitness y Culturismo",
    "Hobby: Conversación (Experiencia Novio/a Virtual)",
]


# ---------- CONFIGURACIÓN PÁGINA ----------
st.set_page_config(
    page_title="Sexy AI Message Generator",
    page_icon="✨",
    layout="centered",
)

# ---------- CLAVE GEMINI ----------
try:
    api_key = os.environ['GEMINI_API_KEY']
    genai.configure(api_key=api_key)
except KeyError:
    st.error("No se encontró la clave de API de Gemini. Asegúrate de añadirla a los 'Secrets' en Replit.")
    st.stop()


# ---------- CABECERA Y BRANDING ----------
st.title("💌 Sexy AI Message Generator")
st.markdown("by **Luminarys Production**")
st.write("---")
st.markdown(
    "Genera mensajes persuasivos y coquetos para tus campañas en múltiples idiomas."
)


# ---------- CONTROLES DE LA APP ----------
msg_type: str = st.radio(
    "🎯 Tipo de mensaje",
    ("Mass DM Free (Atraer)", "Mass DM $ (Vender)", "Mass Sub (Retener)"),
    index=0,
)

intensity: str = st.selectbox(
    "🔞 Nivel de intensidad",
    ("Coqueto", "Sumisa", "Dominante", "Fetichista", "Neutral", "Cosplay"),
)

# ---------- MEJORA: Selector de Nichos ----------
selected_niches = st.multiselect(
    label="⭐ Nicho (puedes elegir hasta 2 para combinarlos)",
    options=ALL_NICHES,
    max_selections=2,
    help="Selecciona los nichos que quieres que la IA combine en el mensaje."
)

num_messages: int = st.slider(
    "🔢 Cantidad de mensajes a generar", 1, 10, 3
)

st.write("---")

# ================= BOTÓN =================
if st.button("🚀 Generar Nuevos Mensajes"):
    # ---------- PROMPT FINAL CON COMBINACIÓN DE NICHOS ---------- # <-- MEJORA PRINCIPAL
    niche_clause = ", ".join(selected_niches) if selected_niches else "General / Sin nicho específico"

    prompt = f"""
    **Tu Rol y Personalidad:**
    Eres una IA que encarna el rol de una experta en psicología sexual y socioemocional, psicología de ventas y estrategia de marketing. Eres una creadora de contenido veterana y exitosa en plataformas como OnlyFans, Fansly y FanCentro. Te encanta crear contenido y, sobre todo, sabes que la clave del éxito está en la comunicación. A través de tus mensajes, puedes causar una impresión inolvidable y adaptarte perfectamente a lo que se te pide. Tienes un conocimiento enciclopédico en todas las áreas de la sexualidad.

    **Tu Tarea:**
    Genera EXACTAMENTE {num_messages} mensajes distintos. Cada mensaje debe tener una versión en español y una versión en inglés, siguiendo estas reglas:

    **Reglas Estrictas:**
    1.  **Contexto del Mensaje:** El mensaje es para una campaña de `{msg_type}` con un nivel de intensidad `{intensity}`.
    2.  **Combinación de Nichos:** Los nichos seleccionados son: `{niche_clause}`. Tu mensaje DEBE fusionar de manera creativa y coherente las ideas de estos nichos. Por ejemplo, si se selecciona 'Atributo: Madura' y 'Actividad: Dominación Financiera', el mensaje debe ser de una mujer mayor dominante dirigiéndose a un sumiso financiero. Si no se selecciona ningún nicho, crea un mensaje más general que se ajuste al tipo e intensidad.
    3.  **Versión en Español:** Debe ser persuasiva, cercana y usar un lenguaje que conecte con el público hispanohablante.
    4.  **Versión en Inglés:** NO debe ser una traducción literal. Adáptala para que suene como una hablante nativa de Estados Unidos (USA). Usa un lenguaje coloquial, informal y natural para la situación. Piensa en cómo lo diría una creadora popular en Los Ángeles.
    5.  **Estilo General:** Evita clichés. Sé creativa, sugerente y crea un sentido de urgencia o curiosidad.
    6.  **Formato de Salida Obligatorio:** Devuelve ÚNICAMENTE un objeto JSON válido. La estructura debe ser una clave "messages" que contenga una lista de objetos, donde cada objeto tiene una clave "spanish" y una "english".
        **Ejemplo de formato:**
        {{
          "messages": [
            {{ "spanish": "Mensaje en español.", "english": "Message in English." }}
          ]
        }}

    Ahora, basándote en tu profundo conocimiento y las reglas, genera los mensajes.
    """.strip()

    # ---------- LLAMADA A GEMINI CON CREATIVIDAD ----------
    try:
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        generation_config = genai.types.GenerationConfig(
            temperature=0.95
        )
        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )
        raw = response.text.strip()
    except Exception as exc:
        st.error(f"❌ Error con la API de Gemini: {exc}")
        st.stop()

    # ---------- PARSEO Y MOSTRAR RESULTADOS DOBLES ----------
    try:
        if raw.startswith("```json"):
            raw = raw.replace("```json", "").replace("```", "").strip()

        data: Dict[str, List[Dict[str, str]]] = json.loads(raw)
    except json.JSONDecodeError:
        st.error("❌ JSON inválido devuelto por la IA. Respuesta bruta:")
        st.code(raw, language="text")
        st.stop()

    msgs = data.get("messages", [])
    if not msgs:
        st.error("❌ La respuesta de la IA no contiene la clave 'messages' o está vacía.")
        st.stop()

    st.success("✅ ¡Mensajes multilingües y de nicho generados!")
    for i, item in enumerate(msgs, 1):
        st.markdown(f"#### Mensaje #{i}")
        st.markdown(f"🇪🇸 **Español:** {item.get('spanish', 'No generado.')}")
        st.markdown(f"🇺🇸 **English:** {item.get('english', 'Not generated.')}")
        st.write("---")

# ---------- PIE ----------
st.markdown(
    """
<div style='text-align:center;font-size:0.8em'>
Powered by Google Gemini
</div>
""",
    unsafe_allow_html=True,
)