# ---------------- streamlit_app.py (Versión 8.0 - Corrección Final de UI) ----------------

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
    "Práctica: Anal", "Práctica: Oral (Blowjob/Deepthroat)", "Práctica: Doble Penetración", "Práctica: Creampie", "Práctica: Squirt",
    "Práctica: Handjob", "Práctica: Footjob", "Práctica: BDSM", "Práctica: Bondage", "Práctica: Sumisión", "Práctica: Dominación",
    "Fetiche: Látex", "Fetiche: Cuero (Leather)", "Fetiche: Tacones (Heels)", "Fetiche: Lencería",
    "Rol: Madrastra/Padrastro", "Rol: Hermanastra/o", "Rol: Profesora/Estudiante", "Rol: Jefa/Empleado", "Rol: Doctora/Enfermera",
    "Escenario: Público", "Escenario: Oficina", "Escenario: Casting/Entrevista", "Escenario: Masaje", "Escenario: Fiesta", "Escenario: Cámara Espía (Spycam)",
    "Parodia: Cosplay", "Estilo: Amateur / Casero", "Estilo: POV (Punto de Vista)",
]
INTENSITY_LEVELS = ("Neutral", "Coqueto", "Sumisa", "Dominante", "Fetichista")
AVAILABLE_LANGUAGES = ("Español", "Inglés", "Francés", "Portugués", "Alemán", "Ruso", "Neerlandés")
LANGUAGE_EMOJI_MAP = {"Español": "🇪🇸", "Inglés": "🇺🇸", "Francés": "🇫🇷", "Portugués": "🇵🇹🇧🇷", "Alemán": "🇩🇪", "Ruso": "🇷🇺", "Neerlandés": "🇳🇱"}
DEFAULT_PERSONA = "Eres una IA que encarna el rol de una experta en psicología sexual y socioemocional, psicología de ventas y estrategia de marketing. Eres una creadora de contenido veterana y exitosa. Tu conocimiento base es enciclopédico en todas las áreas de la sexualidad y las dinámicas de los nichos de contenido para adultos."

# ---------- CONFIGURACIÓN PÁGINA ----------
st.set_page_config(page_title="Sexy AI Message Generator", page_icon="✨", layout="wide")

# --- INICIALIZACIÓN DE LA MEMORIA DE SESIÓN ---
# Se asegura de que las variables existan desde el principio
if 'favorites' not in st.session_state: st.session_state.favorites = []
if 'last_generation' not in st.session_state: st.session_state.last_generation = []
if 'profiles' not in st.session_state: st.session_state.profiles = {}
# 'active_profile_name' se manejará con el propio widget

# ---------- CLAVE GEMINI ----------
try:
    api_key = os.environ['GEMINI_API_KEY']
    genai.configure(api_key=api_key)
except KeyError:
    st.error("No se encontró la clave de API de Gemini. Asegúrate de añadirla a los 'Secrets'.")
    st.stop()

# ==================== BARRA LATERAL (SIDEBAR) PARA PERFILES ====================
with st.sidebar:
    st.title("🎭 Gestor de Perfiles")
    st.markdown("Crea y guarda diferentes personalidades para la IA.")

    profile_names = ["-- Ninguno --"] + list(st.session_state.profiles.keys())
    
    # Selector para cargar un perfil existente. Usamos una clave 'key' para que Streamlit maneje el estado.
    active_profile_name = st.selectbox(
        "Cargar Perfil",
        options=profile_names,
        key='selected_profile_name' # Clave para vincular al estado de la sesión
    )

    st.markdown("---")

    with st.expander("➕ Crear Nuevo Perfil"):
        with st.form("new_profile_form", clear_on_submit=True):
            new_profile_name = st.text_input("Nombre del Perfil*")
            new_profile_desc = st.text_area("Descripción de la Personalidad*", height=200, placeholder="Ej: Eres una diosa dominante y juguetona...")
            new_profile_tags = st.multiselect("Etiquetas Predeterminadas", options=ALL_TAGS)
            new_profile_intensity = st.selectbox("Intensidad Predeterminada", options=INTENSITY_LEVELS, index=1)
            submitted = st.form_submit_button("Guardar Perfil")
            if submitted:
                if new_profile_name and new_profile_desc:
                    st.session_state.profiles[new_profile_name] = {
                        "description": new_profile_desc,
                        "tags": new_profile_tags,
                        "intensity": new_profile_intensity
                    }
                    st.session_state.selected_profile_name = new_profile_name
                    st.success(f"¡Perfil '{new_profile_name}' guardado!")
                    st.rerun()
                else:
                    st.error("El nombre y la descripción del perfil son obligatorios.")

    if active_profile_name != "-- Ninguno --":
        st.markdown("---")
        if st.button(f"🗑️ Eliminar Perfil '{active_profile_name}'", use_container_width=True):
            del st.session_state.profiles[active_profile_name]
            st.session_state.selected_profile_name = "-- Ninguno --"
            st.success("Perfil eliminado.")
            st.rerun()

# ==================== PÁGINA PRINCIPAL ====================
st.title("💌 Sexy AI Message Generator")
st.markdown("by **Luminarys Production**")

# --- SECCIÓN PARA MOSTRAR FAVORITOS GUARDADOS ---
if st.session_state.favorites:
    st.markdown("---")
    with st.expander("⭐ Mis Contenidos Favoritos Guardados", expanded=True):
        for i, fav_item in enumerate(st.session_state.favorites):
            # Lógica para mostrar y eliminar favoritos (sin cambios)
            st.markdown(f"**Favorito #{i+1}**")
            # ... (código de visualización y borrado se mantiene igual)
            outputs = fav_item.get("outputs", [])
            if outputs:
                for output in outputs:
                    lang, text = output.get("language", ""), output.get("text", "")
                    emoji = LANGUAGE_EMOJI_MAP.get(lang, "🏳️")
                    st.markdown(f"{emoji} **{lang}:** {text}")
            if st.button(f"🗑️ Eliminar", key=f"delete_fav_{fav_item['unique_id']}"):
                st.session_state.favorites.pop(i)
                st.rerun()
            st.markdown("---")

# <<<<<<<<<<<<<<<<<<<< INICIO DE LA CORRECCIÓN LÓGICA >>>>>>>>>>>>>>>>>>>>
# Se obtienen los valores por defecto DESPUÉS de que el usuario interactúe con la barra lateral.
active_profile_data = st.session_state.profiles.get(st.session_state.get('selected_profile_name', '-- Ninguno --'), {})
default_tags = active_profile_data.get('tags', [])
default_intensity = active_profile_data.get('intensity', 'Coqueto')

# ---------- COLUMNAS PARA LA INTERFAZ ----------
col1, col2 = st.columns([1, 1.2])

with col1:
    st.header("1. Define tu Contenido")
    generation_type = st.selectbox("¿Qué quieres generar?", ("Descripción para Post", "DM para Fans"))
    dm_type = st.radio("🎯 Propósito del DM", ("Mass DM Free (Atraer)", "Mass DM $ (Vender)", "Mass Sub (Retener)")) if generation_type == "DM para Fans" else ""
    physical_features = st.text_input("✨ Tus características físicas (opcional)", placeholder="Ej: pelo rojo, ojos verdes, tatuajes") if generation_type == "Descripción para Post" else ""
    
    selected_tags = st.multiselect("Elige de 2 a 10 etiquetas", options=ALL_TAGS, max_selections=10, default=default_tags)
    intensity = st.selectbox("Nivel de intensidad", options=INTENSITY_LEVELS, index=INTENSITY_LEVELS.index(default_intensity), help="Este valor se actualiza al cargar un perfil.")
    output_languages = st.multiselect("Idiomas de salida", options=AVAILABLE_LANGUAGES, default=["Español", "Inglés"])
    num_messages = st.slider("Cantidad de ideas a generar", 1, 10, 3)

    if st.button("🚀 Generar Contenido", use_container_width=True):
        if len(selected_tags) < 2: st.warning("Por favor, selecciona al menos 2 etiquetas.")
        elif not output_languages: st.error("Por favor, selecciona al menos un idioma de salida.")
        else:
            persona_clause = active_profile_data.get('description', DEFAULT_PERSONA)
            # El resto de la lógica del prompt y la llamada a la API no necesita cambios
            # ... (código idéntico al anterior)
            language_clause = ", ".join(output_languages)
            tags_clause = ", ".join(selected_tags)
            task_description = f"Tu Misión es generar {num_messages} ideas de mensajes directos (DM) con el propósito de: `{dm_type}`." if generation_type == "DM para Fans" else f"Tu Misión es generar {num_messages} ideas de descripciones o pies de foto para un post."
            prompt = f"""
            **Tu Identidad y Rol:** {persona_clause} Tu personalidad debe ser `{intensity}`. Actúas desde la perspectiva de una persona definida por las etiquetas: `{tags_clause}`. Si se especifican características físicas (`{physical_features or 'No especificadas'}`), incorpóralas de forma auténtica.
            **{task_description}**
            **Manual de Estilo Creativo y Reglas:** 1. **Mostrar, no Decir:** Transforma las etiquetas en acciones y sentimientos, no las listes. 2. **CERO CLICHÉS y CERO HASHTAGS:** Prohibido usar frases genéricas y hashtags (`#`). 3. **ADAPTACIÓN CULTURAL AVANZADA:** La versión en 'Inglés' debe ser una adaptación coloquial (jerga de EE. UU.). 4. **FORMATO JSON ESTRICTO:** Tu única respuesta debe ser un objeto JSON con la clave "messages", que contiene una lista. Cada elemento tiene un "id" y una lista de "outputs" para cada idioma.
            **Ejemplo de formato:** {{"messages": [{{"id": 1, "outputs": [ {{"language": "Español", "text": "..."}}, {{"language": "Inglés", "text": "..."}} ] }}]}}
            Genera el contenido.
            """.strip()
            with st.spinner("🧠 Encarnando nueva personalidad..."):
                try:
                    model = genai.GenerativeModel('gemini-1.5-flash-latest')
                    generation_config = genai.types.GenerationConfig(temperature=1.0)
                    response = model.generate_content(prompt, generation_config=generation_config)
                    raw = response.text.strip()
                    if raw.startswith("```json"): raw = raw.replace("```json", "").replace("```", "").strip()
                    data = json.loads(raw)
                    st.session_state.last_generation = data.get("messages", [])
                    if not st.session_state.last_generation: st.error("La IA no devolvió mensajes. Intenta de nuevo.")
                except Exception as e:
                    st.error(f"Ocurrió un error: {e}")
                    st.session_state.last_generation = []

with col2:
    if st.session_state.last_generation:
        st.header("2. Elige tus Favoritos")
        for i, item in enumerate(st.session_state.last_generation):
            # Lógica para mostrar y guardar el contenido recién generado (sin cambios)
            idea_id = item.get("id", i + 1)
            outputs = item.get("outputs", [])
            item['unique_id'] = hash(frozenset(o['text'] for o in outputs))
            st.markdown(f"**Idea de Contenido #{idea_id}**")
            if outputs:
                for output in outputs:
                    lang, text = output.get("language", ""), output.get("text", "")
                    emoji = LANGUAGE_EMOJI_MAP.get(lang, "🏳️")
                    st.markdown(f"{emoji} **{lang}:** {text}")
            is_favorited = any(fav.get('unique_id') == item['unique_id'] for fav in st.session_state.favorites)
            if is_favorited:
                st.success("✔️ Guardado")
            else:
                if st.button(f"⭐ Guardar Idea", key=f"save_{item['unique_id']}"):
                    st.session_state.favorites.append(item)
                    st.session_state.last_generation.pop(i)
                    st.rerun()
            st.markdown("---")