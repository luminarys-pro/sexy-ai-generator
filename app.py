# ---------------- streamlit_app.py (Versión 6.0 - Gestión de Estado Corregida) ----------------

from __future__ import annotations
import streamlit as st
import google.generativeai as genai
import json
from typing import List, Dict
import os

# ---------- LISTAS DE OPCIONES ----------
ALL_TAGS = [
    "Edad: Teen (18+)", "Edad: Joven (20-29)", "Edad: MILF (30-45)", "Edad: Madura/Cougar (45+)",
    "Cuerpo: Petite/Delgada", "Cuerpo: Curvy/Gruesa (Thick)", "Cuerpo: BBW/Talla Grande", "Cuerpo: Atlético/Fitness", "Cuerpo: Musculosa",
    "Cabello: Rubia", "Cabello: Morena", "Cabello: Pelirroja", "Cabello: Pelo Negro",
    "Etnia: Latina", "Etnia: Asiática", "Etnia: Ébano (Ebony)", "Etnia: India", "Etnia: Blanca/Caucásica",
    "Rasgos: Tatuajes", "Rasgos: Piercings", "Rasgos: Pechos Grandes", "Rasgos: Pechos Pequeños", "Rasgos: Pechos Naturales", "Rasgos: Trasero Grande (Big Ass)",
    "Participantes: Solo (Chica)", "Participantes: Pareja (Chica/Chico)", "Participantes: Pareja (Chica/Chica)",
    "Práctica: Anal", "Práctica: Oral (Blowjob/Deepthroat)", "Práctica: Doble Penetración", "Práctica: Creampie",
    "Práctica: Squirt", "Práctica: Handjob", "Práctica: Footjob", "Práctica: Bukkake / Gangbang",
    "Práctica: BDSM", "Práctica: Bondage", "Práctica: Sumisión", "Práctica: Dominación",
    "Fetiche: Látex", "Fetiche: Cuero (Leather)", "Fetiche: Tacones (Heels)", "Fetiche: Lencería",
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
st.set_page_config(page_title="Sexy AI Message Generator", page_icon="✨", layout="wide") # Layout Ancho para más espacio

# --- INICIALIZACIÓN DE LA MEMORIA DE SESIÓN ---
if 'favorites' not in st.session_state:
    st.session_state.favorites = []
if 'last_generation' not in st.session_state:
    st.session_state.last_generation = []

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

# --- SECCIÓN PARA MOSTRAR FAVORITOS GUARDADOS ---
if st.session_state.favorites:
    st.markdown("---")
    with st.expander("⭐ Mis Contenidos Favoritos Guardados", expanded=True):
        for i, fav_item in enumerate(st.session_state.favorites):
            st.markdown(f"**Favorito #{i+1}**")
            outputs = fav_item.get("outputs", [])
            if outputs:
                for output in outputs:
                    lang = output.get("language", "")
                    text = output.get("text", "")
                    emoji = LANGUAGE_EMOJI_MAP.get(lang, "🏳️")
                    st.markdown(f"{emoji} **{lang}:** {text}")
            
            if st.button(f"🗑️ Eliminar", key=f"delete_fav_{fav_item['unique_id']}"):
                st.session_state.favorites.pop(i)
                st.rerun()
            st.markdown("---")

# ---------- COLUMNAS PARA LA INTERFAZ ----------
col1, col2 = st.columns([1, 1])

with col1:
    # ---------- CONTROLES DE LA APP ----------
    st.header("1. Define tu Contenido")
    generation_type = st.selectbox("¿Qué quieres generar?", ("Descripción para Post", "DM para Fans"))
    
    dm_type = ""
    physical_features = ""
    if generation_type == "DM para Fans":
        dm_type = st.radio("🎯 Propósito del DM", ("Mass DM Free (Atraer)", "Mass DM $ (Vender)", "Mass Sub (Retener)"), index=0)
    else:
        physical_features = st.text_input("✨ Tus 3 características físicas (opcional)", placeholder="Ej: pelo rojo, ojos verdes, tatuajes")

    selected_tags = st.multiselect("Elige de 2 a 10 etiquetas", options=ALL_TAGS, max_selections=10)
    intensity = st.selectbox("Nivel de intensidad", options=INTENSITY_LEVELS, index=1)
    output_languages = st.multiselect("Idiomas de salida", options=AVAILABLE_LANGUAGES, default=["Español", "Inglés"])
    num_messages = st.slider("Cantidad de ideas a generar", 1, 10, 3, key="num_slider")

    # ================= BOTÓN =================
    if st.button("🚀 Generar Contenido", use_container_width=True):
        if len(selected_tags) < 2:
            st.warning("Por favor, selecciona al menos 2 etiquetas para obtener mejores resultados.")
        elif not output_languages:
            st.error("Por favor, selecciona al menos un idioma de salida.")
        else:
            # (El prompt no cambia, sigue siendo el avanzado)
            language_clause = ", ".join(output_languages)
            tags_clause = ", ".join(selected_tags)
            task_description = ""
            if generation_type == "DM para Fans":
                task_description = f"Tu Misión es generar {num_messages} ideas de mensajes directos (DM) para fans con el propósito de: `{dm_type}`."
            else:
                task_description = f"Tu Misión es generar {num_messages} ideas de descripciones o pies de foto (captions) para un post en una red social."

            prompt = f"""
            **Tu Identidad Secreta (El Personaje que Debes Encarnar):** Eres una creadora de contenido experta. Tu personalidad y tono verbal deben ser `{intensity}`. Actúas DESDE la perspectiva de una persona definida por las siguientes etiquetas: `{tags_clause}`. Si se especifican características físicas adicionales (`{physical_features if physical_features else 'No especificadas'}`), estas son TUS características. Habla en primera persona sobre ellas. Tu conocimiento base es el de una experta en psicología sexual y de ventas, y marketing digital para creadores.
            **{task_description}**
            **Manual de Estilo Creativo (Reglas Obligatorias):** 1. **Mostrar, no Decir:** No LISTES las etiquetas. TRANSFÓRMALAS en acciones, sentimientos y descripciones. Si la etiqueta es "Rasgos: Tatuajes", no digas "tengo tatuajes", di "siente la tinta de mi piel contra la tuya...". 2. **CERO CLICHÉS:** PROHIBIDO usar frases genéricas como "suscríbete", "contenido exclusivo", "no te lo pierdas". 3. **PROHIBIDO HASHTAGS:** No generes NUNCA hashtags (`#`). 4. **ADAPTACIÓN CULTURAL AVANZADA:** Para CADA idea, genera una versión en los idiomas solicitados: `{language_clause}`. La versión en 'Inglés' DEBE ser una adaptación coloquial (jerga de EE. UU.). 5. **FORMATO DE SALIDA (JSON ESTRICTO):** Tu única respuesta debe ser un objeto JSON válido. Ejemplo de formato: {{"messages": [{{"id": 1, "outputs": [ {{"language": "Español", "text": "..."}}, {{"language": "Inglés", "text": "..."}} ] }}]}}
            Ahora, encarna tu rol y genera el contenido.
            """.strip()

            with st.spinner("🧠 Perfeccionando el arte de la seducción..."):
                try:
                    model = genai.GenerativeModel('gemini-1.5-flash-latest')
                    generation_config = genai.types.GenerationConfig(temperature=1.0)
                    response = model.generate_content(prompt, generation_config=generation_config)
                    raw = response.text.strip()
                    
                    if raw.startswith("```json"):
                        raw = raw.replace("```json", "").replace("```", "").strip()
                    data = json.loads(raw)
                    msgs = data.get("messages", [])
                    
                    if msgs:
                        # Guardamos la generación en la memoria de sesión
                        st.session_state.last_generation = msgs
                    else:
                        st.session_state.last_generation = []
                        st.error("La respuesta de la IA no contenía mensajes. Intenta de nuevo.")

                except json.JSONDecodeError:
                    st.session_state.last_generation = []
                    st.error("❌ La IA devolvió un formato de JSON inválido. Revisa la respuesta bruta:")
                    st.code(raw, language="text")
                except Exception as exc:
                    st.session_state.last_generation = []
                    st.error(f"❌ Error con la API de Gemini: {exc}")

with col2:
    # --- SECCIÓN PARA MOSTRAR CONTENIDO RECIÉN GENERADO ---
    if st.session_state.last_generation:
        st.header("2. Elige tus Favoritos")
        for i, item in enumerate(st.session_state.last_generation):
            idea_id = item.get("id", i + 1)
            outputs = item.get("outputs", [])
            item['unique_id'] = hash(frozenset(o['text'] for o in outputs))

            st.markdown(f"**Idea de Contenido #{idea_id}**")
            
            if outputs:
                for output in outputs:
                    lang = output.get("language", "")
                    text = output.get("text", "")
                    emoji = LANGUAGE_EMOJI_MAP.get(lang, "🏳️")
                    st.markdown(f"{emoji} **{lang}:** {text}")
            
            is_favorited = any(fav.get('unique_id') == item['unique_id'] for fav in st.session_state.favorites)
            if is_favorited:
                st.success("✔️ Guardado")
            else:
                if st.button(f"⭐ Guardar Idea", key=f"save_{item['unique_id']}"):
                    st.session_state.favorites.append(item)
                    # Eliminamos el item de la generación actual para que "se mueva" visualmente
                    st.session_state.last_generation.pop(i)
                    st.rerun()
            st.markdown("---")