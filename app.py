# ---------------- streamlit_app.py (Versión 3.0 - Sistema de Etiquetas) ----------------

from __future__ import annotations
import streamlit as st
import google.generativeai as genai
import json
from typing import List, Dict
import os

# ---------- LISTAS DE OPCIONES ----------

# Nueva lista completa de etiquetas, organizada para el selector
ALL_TAGS = [
    # Atributos Físicos y Apariencia
    "Edad: Teen (18+)", "Edad: Joven (20-29)", "Edad: MILF (30-45)", "Edad: Madura/Cougar (45+)",
    "Cuerpo: Petite/Delgada", "Cuerpo: Curvy/Gruesa (Thick)", "Cuerpo: BBW/Talla Grande", "Cuerpo: Atlético/Fitness", "Cuerpo: Musculosa",
    "Cabello: Rubia", "Cabello: Morena", "Cabello: Pelirroja", "Cabello: Pelo Negro",
    "Etnia: Latina", "Etnia: Asiática", "Etnia: Ébano (Ebony)", "Etnia: India", "Etnia: Blanca/Caucásica",
    "Rasgos: Tatuajes", "Rasgos: Piercings", "Rasgos: Pechos Grandes", "Rasgos: Pechos Pequeños", "Rasgos: Pechos Naturales", "Rasgos: Trasero Grande (Big Ass)",
    "Participantes: Solo (Chica)", "Participantes: Pareja (Chica/Chico)", "Participantes: Pareja (Chica/Chica)",
    # Actos y Prácticas
    "Práctica: Anal", "Práctica: Oral (Blowjob/Deepthroat)", "Práctica: Doble Penetración", "Práctica: Creampie",
    "Práctica: Squirt", "Práctica: Handjob", "Práctica: Footjob", "Práctica: Bukkake / Gangbang",
    "Práctica: BDSM", "Práctica: Bondage", "Práctica: Sumisión", "Práctica: Dominación",
    "Fetiche: Látex", "Fetiche: Cuero (Leather)", "Fetiche: Tacones (Heels)", "Fetiche: Lencería",
    # Géneros, Temáticas y Escenarios
    "Rol: Madrastra/Padrastro", "Rol: Hermanastra/o", "Rol: Profesora/Estudiante", "Rol: Jefa/Empleado", "Rol: Doctora/Enfermera",
    "Escenario: Público", "Escenario: Oficina", "Escenario: Casting/Entrevista", "Escenario: Masaje", "Escenario: Fiesta", "Escenario: Cámara Espía (Spycam)",
    "Parodia: Dibujos Animados / Anime", "Parodia: Cosplay",
    "Estilo: Amateur / Casero", "Estilo: POV (Punto de Vista)",
]

INTENSITY_LEVELS = ("Neutral", "Coqueto", "Sumisa", "Dominante", "Fetichista")
AVAILABLE_LANGUAGES = ("Español", "Inglés", "Francés", "Portugués", "Alemán", "Ruso", "Neerlandés")
LANGUAGE_EMOJI_MAP = {
    "Español": "🇪🇸", "Inglés": "🇺🇸", "Francés": "🇫🇷", "Portugués": "🇵🇹🇧🇷",
    "Alemán": "🇩🇪", "Ruso": "🇷🇺", "Neerlandés": "🇳🇱",
}

# ---------- CONFIGURACIÓN PÁGINA ----------
st.set_page_config(page_title="Sexy AI Message Generator", page_icon="✨", layout="centered")

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
generation_type = st.selectbox("1. ¿Qué quieres generar?", ("Descripción para Post", "DM para Fans"))

dm_type = ""
physical_features = ""
if generation_type == "DM para Fans":
    dm_type = st.radio("🎯 Propósito del DM", ("Mass DM Free (Atraer)", "Mass DM $ (Vender)", "Mass Sub (Retener)"), index=0)
else:
    physical_features = st.text_input("✨ Tus 3 características físicas principales (opcional)", placeholder="Ej: pelo rojo, ojos verdes, tatuajes", help="Describe 3 rasgos para que la IA se inspire y los incorpore.")

# MEJORA: Sistema de Etiquetas
selected_tags = st.multiselect(
    "2. Elige de 2 a 10 etiquetas para definir el contenido",
    options=ALL_TAGS,
    max_selections=10,
)

intensity = st.selectbox("3. Nivel de intensidad", options=INTENSITY_LEVELS, index=1)
output_languages = st.multiselect("4. Idiomas de salida", options=AVAILABLE_LANGUAGES, default=["Español", "Inglés"])
num_messages = st.slider("5. Cantidad de ideas a generar", 1, 10, 3)

st.write("---")

# ================= BOTÓN =================
if st.button("🚀 Generar Contenido"):
    # MEJORA: Validación de selección de etiquetas
    if len(selected_tags) < 2:
        st.warning("Por favor, selecciona al menos 2 etiquetas para obtener mejores resultados.")
    elif not output_languages:
        st.error("Por favor, selecciona al menos un idioma de salida.")
    else:
        # ---------- CONSTRUCCIÓN DEL PROMPT FINAL CON ETIQUETAS ----------
        language_clause = ", ".join(output_languages)
        tags_clause = ", ".join(selected_tags)

        task_description = ""
        if generation_type == "DM para Fans":
            task_description = f"Tu Misión es generar {num_messages} ideas de mensajes directos (DM) para fans con el propósito de: `{dm_type}`."
        else:
            task_description = f"Tu Misión es generar {num_messages} ideas de descripciones o pies de foto (captions) para un post en una red social."

        prompt = f"""
        **Tu Identidad y Rol (Actúa como si fueras esta persona):**
        Eres una creadora de contenido para adultos. Encarnas a una persona definida por las siguientes etiquetas: `{tags_clause}`.
        Tu personalidad y tono deben ser `{intensity}`.
        Si se especifican características físicas adicionales (`{physical_features if physical_features else 'No especificadas'}`), incorpóralas para dar un toque personal y auténtico.
        Tu conocimiento base es el de una experta en psicología sexual, de ventas y marketing digital para creadores.

        **{task_description}**

        **Manual de Estilo Creativo (Reglas Obligatorias):**
        1.  **SÍNTESIS CREATIVA:** Tu creación DEBE ser una representación directa y creativa de la combinación de TODAS las etiquetas seleccionadas. Cada etiqueta es una orden.
        2.  **CERO CLICHÉS:** PROHIBIDO usar frases genéricas como "suscríbete", "contenido exclusivo", "no te lo pierdas". Sé original, provocadora e ingeniosa.
        3.  **VARIEDAD RADICAL:** Cada una de las {num_messages} ideas debe ser RADICALMENTE diferente de las otras. Usa ángulos y técnicas creativas distintas para cada una (storytelling, preguntas, etc.).
        4.  **GENERACIÓN MULTILINGÜE:** Para CADA idea, debes proveer una versión en CADA UNO de los siguientes idiomas: `{language_clause}`. La versión en 'Inglés' debe ser una adaptación coloquial y natural (jerga de EE. UU.), no una traducción literal.
        5.  **FORMATO DE SALIDA (JSON ESTRICTO):** Tu única respuesta debe ser un objeto JSON válido con la clave "messages", que contiene una lista de ideas. Cada idea tiene un "id" y una lista de "outputs" para cada idioma.
            **Ejemplo de formato de salida:**
            {{
              "messages": [
                {{
                  "id": 1,
                  "outputs": [
                    {{ "language": "Español", "text": "Texto en español basado en las etiquetas." }},
                    {{ "language": "Inglés", "text": "Colloquial English text based on the tags." }}
                  ]
                }}
              ]
            }}

        Ahora, encarna tu rol y genera el contenido más específico y potente posible.
        """.strip()

        # ---------- LLAMADA A GEMINI ----------
        with st.spinner("🧠 La IA está combinando las etiquetas en algo espectacular..."):
            try:
                model = genai.GenerativeModel('gemini-1.5-flash-latest')
                generation_config = genai.types.GenerationConfig(temperature=1.0)
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
                    st.success("✅ ¡Contenido de ultra-nicho generado!")
                    for item in msgs:
                        idea_id = item.get("id", "?")
                        st.markdown(f"#### Idea de Contenido #{idea_id}")
                        outputs = item.get("outputs", [])
                        if outputs:
                            for output in outputs:
                                lang = output.get("language", "Desconocido")
                                text = output.get("text", "No generado.")
                                emoji = LANGUAGE_EMOJI_MAP.get(lang, "🏳️")
                                st.markdown(f"{emoji} **{lang}:** {text}")
                        st.write("---")

            except json.JSONDecodeError:
                st.error("❌ La IA devolvió un formato de JSON inválido. Revisa la respuesta bruta:")
                st.code(raw, language="text")

# ---------- PIE ----------
st.markdown("<div style='text-align:center;font-size:0.8em; margin-top: 2em;'>Powered by Google Gemini</div>", unsafe_allow_html=True)