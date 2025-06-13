# ---------------- streamlit_app.py (Versión 2.0 Luminarys Production) ----------------

from __future__ import annotations
import streamlit as st
import google.generativeai as genai
import json
from typing import List, Dict
import os

# ---------- LISTAS DE OPCIONES ----------

# Lista de nichos más completa
ALL_NICHES = [
    # Atributos Físicos / Estética
    "Atributo: BBW / Talla Grande",
    "Atributo: Pies (Foot Fetish)",
    "Atributo: Madura (Mature / Cougar / MILF)",
    "Atributo: Petite / Pequeña",
    "Atributo: Fitness / Musculosa",
    "Atributo: Tatuajes y Piercings (Alt-Model)",
    "Atributo: Gótica / Emo",
    "Atributo: Pelirroja",
    "Atributo: Rubia",
    "Atributo: Latina",
    "Atributo: Asiática",
    "Atributo: Ébano (Ebony)",
    # Actividades / Fetiches
    "Actividad: ASMR Erótico",
    "Actividad: Dominación Financiera (Findom)",
    "Actividad: Juego de Roles (Roleplay)",
    "Actividad: Humillación / Degradación",
    "Actividad: Adoración (Worship)",
    "Actividad: BDSM / Bondage",
    "Actividad: Cuckolding",
    "Actividad: Contenido de Embarazo (Pregnancy)",
    "Actividad: Fumar (Smoking Fetish)",
    # Hobbies / Creatividad
    "Hobby: Arte Sin Censura",
    "Hobby: Cosplay (Erótico y General)",
    "Hobby: Escritura / Poesía Erótica",
    "Hobby: Gamer / Videojuegos",
    "Hobby: Conversación (Experiencia Novio/a Virtual)",
]

# Lista de intensidades reordenada y sin Cosplay
INTENSITY_LEVELS = ("Neutral", "Coqueto", "Sumisa", "Dominante", "Fetichista")

# Lista de idiomas disponibles
AVAILABLE_LANGUAGES = ("Español", "Inglés", "Francés", "Portugués", "Alemán", "Ruso", "Neerlandés")

# Mapeo de idiomas a emojis para una visualización más atractiva
LANGUAGE_EMOJI_MAP = {
    "Español": "🇪🇸",
    "Inglés": "🇺🇸",
    "Francés": "🇫🇷",
    "Portugués": "🇵🇹🇧🇷",
    "Alemán": "🇩🇪",
    "Ruso": "🇷🇺",
    "Neerlandés": "🇳🇱",
}

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
    st.error("No se encontró la clave de API de Gemini. Asegúrate de añadirla a los 'Secrets'.")
    st.stop()

# ---------- CABECERA Y BRANDING ----------
st.title("💌 Sexy AI Message Generator")
st.markdown("by **Luminarys Production**")
st.write("---")

# ---------- CONTROLES DE LA APP ----------

# 1. Selector de tipo de generación
generation_type = st.selectbox(
    "1. ¿Qué quieres generar?",
    ("DM para Fans", "Descripción para Post")
)

# Controles condicionales
dm_type = ""
physical_features = ""
if generation_type == "DM para Fans":
    dm_type = st.radio(
        "🎯 Propósito del DM",
        ("Mass DM Free (Atraer)", "Mass DM $ (Vender)", "Mass Sub (Retener)"),
        index=0,
    )
else: # generation_type == "Descripción para Post"
    physical_features = st.text_input(
        "✨ Tus 3 características físicas principales",
        placeholder="Ej: pelo rojo, ojos verdes, tatuajes en el brazo",
        help="Describe 3 rasgos físicos para que la IA los mencione sutilmente en la descripción."
    )

selected_niches = st.multiselect(
    "2. Elige hasta 2 nichos para combinar",
    options=ALL_NICHES,
    max_selections=2,
)

# 2. Selector de intensidad actualizado
intensity = st.selectbox(
    "3. Nivel de intensidad",
    options=INTENSITY_LEVELS,
    index=1 # 'Coqueto' por defecto
)

# 4. Selector de idiomas
output_languages = st.multiselect(
    "4. Idiomas de salida",
    options=AVAILABLE_LANGUAGES,
    default=["Español", "Inglés"]
)

num_messages = st.slider(
    "5. Cantidad de ideas a generar", 1, 10, 3
)

st.write("---")

# ================= BOTÓN =================
if st.button("🚀 Generar Contenido"):
    if not output_languages:
        st.error("Por favor, selecciona al menos un idioma de salida.")
    else:
        # ---------- CONSTRUCCIÓN DINÁMICA DEL PROMPT ----------
        language_clause = ", ".join(output_languages)
        niche_clause = ", ".join(selected_niches) if selected_niches else "General / Sin nicho específico"

        task_description = ""
        if generation_type == "DM para Fans":
            task_description = f"Tu Tarea es generar {num_messages} mensajes directos (DM) para fans. El propósito de estos DMs es: `{dm_type}`."
        else: # generation_type == "Descripción para Post"
            task_description = f"Tu Tarea es generar {num_messages} descripciones o pies de foto (captions) para un post en una red social. Estas descripciones deben ser seductoras y atractivas."
            if physical_features:
                task_description += f" La creadora ha descrito sus características físicas como: `{physical_features}`. Debes incorporar sutilmente alguna de estas características en el texto para hacerlo más personal."

        prompt = f"""
        **Tu Rol y Personalidad:**
        Eres una IA que encarna el rol de una experta en psicología sexual y socioemocional, psicología de ventas y estrategia de marketing. Eres una creadora de contenido veterana y exitosa en plataformas como OnlyFans, Fansly y FanCentro. Entiendes profundamente cómo crear conexiones y deseo a través de las palabras. Tienes un conocimiento enciclopédico en todas las áreas de la sexualidad y las dinámicas de los nichos de contenido para adultos.

        **Instrucción Principal:**
        {task_description}

        **Reglas Estrictas para la Generación:**
        1.  **Combinación de Nichos:** El contenido debe fusionar creativamente los siguientes nichos: `{niche_clause}`. Si no se selecciona ninguno, enfócate en un estilo más general.
        2.  **Intensidad:** El tono debe corresponder a este nivel de intensidad: `{intensity}`.
        3.  **Generación Multilingüe:** Para CADA una de las {num_messages} ideas, debes proveer una versión en CADA UNO de los siguientes idiomas: `{language_clause}`.
        4.  **Adaptación Cultural (Inglés):** La versión en 'Inglés' NO debe ser una traducción literal del español. Debe sonar como una hablante nativa de Estados Unidos (USA), usando jerga y expresiones coloquiales apropiadas para el nicho y la intensidad.
        5.  **Formato de Salida Obligatorio (JSON):** Devuelve ÚNICAMENTE un objeto JSON válido. La estructura debe ser una clave "messages", que contiene una lista. Cada elemento de la lista es una 'idea' de mensaje. Cada 'idea' contiene una clave "outputs", que es una lista de objetos, donde cada objeto tiene una clave "language" y una "text".

            **Ejemplo de formato de salida para 1 idea en 2 idiomas:**
            {{
              "messages": [
                {{
                  "id": 1,
                  "outputs": [
                    {{ "language": "Español", "text": "El texto en español va aquí." }},
                    {{ "language": "Inglés", "text": "The English text goes here." }}
                  ]
                }}
              ]
            }}

        Ahora, basándote en tu profundo conocimiento, genera el contenido.
        """.strip()

        # ---------- LLAMADA A GEMINI ----------
        with st.spinner("🧠 La IA está pensando..."):
            try:
                model = genai.GenerativeModel('gemini-1.5-flash-latest')
                generation_config = genai.types.GenerationConfig(temperature=1.0) # Máxima creatividad
                response = model.generate_content(prompt, generation_config=generation_config)
                raw = response.text.strip()
            except Exception as exc:
                st.error(f"❌ Error con la API de Gemini: {exc}")
                st.stop()

            # ---------- PARSEO Y VISUALIZACIÓN ----------
            try:
                if raw.startswith("```json"):
                    raw = raw.replace("```json", "").replace("```", "").strip()
                data = json.loads(raw)
                msgs = data.get("messages", [])
                
                if not msgs:
                    st.error("La respuesta de la IA no contenía mensajes. Intenta de nuevo.")
                    st.code(raw, language="json")
                else:
                    st.success("✅ ¡Contenido fresco generado!")
                    for i, item in enumerate(msgs, 1):
                        st.markdown(f"#### Idea de Contenido #{i}")
                        outputs = item.get("outputs", [])
                        if outputs:
                            for output in outputs:
                                lang = output.get("language", "Desconocido")
                                text = output.get("text", "No generado.")
                                emoji = LANGUAGE_EMOJI_MAP.get(lang, "🏳️")
                                st.markdown(f"{emoji} **{lang}:** {text}")
                        st.write("---")

            except json.JSONDecodeError:
                st.error("❌ La IA devolvió un formato de JSON inválido. Respuesta bruta:")
                st.code(raw, language="text")

# ---------- PIE ----------
st.markdown(
    """
<div style='text-align:center;font-size:0.8em; margin-top: 2em;'>
Powered by Google Gemini
</div>
""",
    unsafe_allow_html=True,
)