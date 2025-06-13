# ---------------- streamlit_app.py (Versión Final y Completa) ----------------

from __future__ import annotations
import streamlit as st
import google.generativeai as genai
import json
from typing import List, Dict
import os

# ---------- LISTAS DE OPCIONES Y CONSTANTES ----------
ALL_TAGS = [
    "Edad: Teen (18+)", "Edad: Joven (20-29)", "Edad: MILF (30-45)", "Edad: Madura/Cougar (45+)", "Cuerpo: Petite/Delgada", "Cuerpo: Curvy/Gruesa (Thick)", "Cuerpo: BBW/Talla Grande", "Cuerpo: Atlético/Fitness", "Cuerpo: Musculosa", "Cabello: Rubia", "Cabello: Morena", "Cabello: Pelirroja", "Cabello: Pelo Negro", "Etnia: Latina", "Etnia: Asiática", "Etnia: Ébano (Ebony)", "Etnia: India", "Etnia: Blanca/Caucásica", "Rasgos: Tatuajes", "Rasgos: Piercings", "Rasgos: Pechos Grandes", "Rasgos: Pechos Pequeños", "Rasgos: Pechos Naturales", "Rasgos: Trasero Grande (Big Ass)", "Participantes: Solo (Chica)", "Participantes: Pareja (Chica/Chico)", "Participantes: Pareja (Chica/Chica)", "Práctica: Anal", "Práctica: Oral (Blowjob/Deepthroat)", "Práctica: Doble Penetración", "Práctica: Creampie", "Práctica: Squirt", "Práctica: Handjob", "Práctica: Footjob", "Práctica: BDSM", "Práctica: Bondage", "Práctica: Sumisión", "Práctica: Dominación", "Fetiche: Látex", "Fetiche: Cuero (Leather)", "Fetiche: Tacones (Heels)", "Fetiche: Lencería", "Rol: Madrastra/Padrastro", "Rol: Hermanastra/o", "Rol: Profesora/Estudiante", "Rol: Jefa/Empleado", "Rol: Doctora/Enfermera", "Escenario: Público", "Escenario: Oficina", "Escenario: Casting/Entrevista", "Escenario: Masaje", "Escenario: Fiesta", "Escenario: Cámara Espía (Spycam)", "Parodia: Cosplay", "Estilo: Amateur / Casero", "Estilo: POV (Punto de Vista)",
]
INTENSITY_LEVELS = ("Neutral", "Coqueto", "Sumisa", "Dominante", "Fetichista")
DM_SCENARIOS = ("Mensaje de Bienvenida (Nuevo Fan)", "Oferta Especial (Venta de PPV)", "Anuncio de Live Stream", "Reactivación (Fan Inactivo)", "Agradecimiento (Fan Destacado)")
DEFAULT_PERSONA = "Eres una IA que encarna el rol de una experta en psicología sexual y socioemocional, psicología de ventas y estrategia de marketing. Eres una creadora de contenido veterana y exitosa."
LANGUAGE_EMOJI_MAP = {"Español": "🇪🇸", "Inglés": "🇺🇸", "Francés": "🇫🇷", "Portugués": "🇵🇹🇧🇷", "Alemán": "🇩🇪", "Ruso": "🇷🇺", "Neerlandés": "🇳🇱"}
AVAILABLE_LANGUAGES = list(LANGUAGE_EMOJI_MAP.keys())

# ---------- CONFIGURACIÓN PÁGINA ----------
st.set_page_config(page_title="Luminarys AI Assistant", page_icon="✨", layout="wide")

# --- INICIALIZACIÓN DE LA MEMORIA DE SESIÓN ---
if 'profiles' not in st.session_state: st.session_state.profiles = {}
if 'selected_profile_name' not in st.session_state: st.session_state.selected_profile_name = "-- Ninguno --"
if 'last_desc_generation' not in st.session_state: st.session_state.last_desc_generation = []
if 'dm_conversation_history' not in st.session_state: st.session_state.dm_conversation_history = []
if 'dm_context' not in st.session_state: st.session_state.dm_context = {}
if 'dm_reply_suggestions' not in st.session_state: st.session_state.dm_reply_suggestions = []

# ---------- CLAVE GEMINI ----------
try:
    api_key = os.environ['GEMINI_API_KEY']
    genai.configure(api_key=api_key)
except KeyError:
    st.error("No se encontró la clave de API de Gemini. Asegúrate de añadirla a los 'Secrets'.")
    st.stop()

# ==================== FUNCIONES DE CALLBACK ====================
def save_new_profile():
    name = st.session_state.get("profile_name_input", "").strip()
    desc = st.session_state.get("profile_desc_input", "").strip()
    if name and desc:
        st.session_state.profiles[name] = {"description": desc, "tags": st.session_state.get("profile_tags_input", []), "intensity": st.session_state.get("profile_intensity_input", "Coqueto")}
        st.session_state.selected_profile_name = name
        st.toast(f"¡Perfil '{name}' guardado!", icon="✅")
    else:
        st.toast("El nombre y la descripción son obligatorios.", icon="⚠️")

def delete_active_profile():
    active_profile = st.session_state.selected_profile_name
    if active_profile in st.session_state.profiles:
        del st.session_state.profiles[active_profile]
        st.session_state.selected_profile_name = "-- Ninguno --"
        st.toast(f"Perfil '{active_profile}' eliminado.", icon="🗑️")

# ==================== BARRA LATERAL (SIDEBAR) ====================
with st.sidebar:
    st.title("🎭 Gestor de Perfiles")
    profile_names = ["-- Ninguno --"] + list(st.session_state.profiles.keys())
    st.selectbox("Cargar Perfil", options=profile_names, key='selected_profile_name')
    st.markdown("---")
    with st.expander("➕ Crear Nuevo Perfil"):
        with st.form("new_profile_form"):
            st.text_input("Nombre del Perfil*", key="profile_name_input")
            st.text_area("Descripción de la Personalidad*", height=200, key="profile_desc_input", placeholder="Ej: Eres una diosa dominante...")
            profile_tags_input = st.multiselect("Etiquetas Predeterminadas", options=ALL_TAGS, key="profile_tags_input")
            st.caption(f"Seleccionadas: {len(profile_tags_input)}")
            st.selectbox("Intensidad Predeterminada", options=INTENSITY_LEVELS, index=1, key="profile_intensity_input")
            st.form_submit_button("Guardar Perfil", on_click=save_new_profile)

    if st.session_state.selected_profile_name != "-- Ninguno --":
        st.markdown("---")
        st.button(f"🗑️ Eliminar Perfil '{st.session_state.selected_profile_name}'", on_click=delete_active_profile, use_container_width=True, type="primary")

# ==================== PÁGINA PRINCIPAL ====================
st.title("💌 AI Content Assistant")
st.markdown("by **Luminarys Production**")

active_profile_data = st.session_state.profiles.get(st.session_state.get('selected_profile_name', '-- Ninguno --'), {})
persona_clause = active_profile_data.get('description', DEFAULT_PERSONA)
default_tags = active_profile_data.get('tags', [])
default_intensity = active_profile_data.get('intensity', 'Coqueto')

tab_desc, tab_dm = st.tabs(["📝 Generador de Descripciones", "💬 Asistente de DMs"])

with tab_desc:
    st.header("Crea Descripciones para tus Posts")
    desc_col1, desc_col2 = st.columns([1, 1.2])
    with desc_col1:
        creator_username = st.text_input("Tu nombre de usuario (ej: @Martinaoff)", key="desc_username")
        desc_physical_features = st.text_input("Tus características físicas (opcional)", placeholder="Ej: pelo rojo, ojos verdes", key="desc_phys")
        
        desc_default_tags = default_tags[:10]
        desc_selected_tags = st.multiselect("Elige de 2 a 10 etiquetas", options=ALL_TAGS, max_selections=10, default=desc_default_tags, key="desc_tags")
        st.caption(f"Seleccionadas: {len(desc_selected_tags)} / 10")

        safe_intensity_index = INTENSITY_LEVELS.index(default_intensity) if default_intensity in INTENSITY_LEVELS else 1
        desc_intensity = st.selectbox("Nivel de intensidad", options=INTENSITY_LEVELS, index=safe_intensity_index, key="desc_intensity")
        
        desc_output_languages = st.multiselect("Idiomas de salida", options=AVAILABLE_LANGUAGES, default=["Español", "Inglés"], key="desc_langs")
        desc_num_messages = st.slider("Cantidad de ideas a generar", 1, 5, 3, key="desc_slider")

        if st.button("🚀 Generar Descripciones", key="gen_desc", use_container_width=True):
            if len(desc_selected_tags) < 2:
                st.warning("Por favor, selecciona al menos 2 etiquetas.")
            elif not desc_output_languages:
                st.error("Por favor, selecciona al menos un idioma de salida.")
            else:
                task_description = f"Tu Misión es generar {desc_num_messages} ideas de descripciones o pies de foto (captions) para un post."
                language_clause = ", ".join(desc_output_languages)
                tags_clause = ", ".join(desc_selected_tags)
                
                prompt = f"""
                **Tu Identidad y Rol:** {persona_clause} Tu personalidad debe ser `{desc_intensity}`. Actúas desde la perspectiva de una persona definida por las etiquetas: `{tags_clause}`. Si se especifican características físicas (`{desc_physical_features or 'No especificadas'}`), incorpóralas de forma auténtica.
                **{task_description}**
                **Manual de Estilo Creativo y Reglas:** 1. **Mostrar, no Decir:** Transforma las etiquetas en acciones y sentimientos, no las listes. 2. **CERO CLICHÉS y CERO HASHTAGS:** Prohibido usar frases genéricas y hashtags (`#`). 3. **ADAPTACIÓN CULTURAL AVANZADA:** La versión en 'Inglés' debe ser una adaptación coloquial (jerga de EE. UU.). 4. **FORMATO JSON ESTRICTO:** Tu única respuesta debe ser un objeto JSON con la clave "messages", que contiene una lista. Cada elemento tiene un "id" y una lista de "outputs" para cada idioma (`{language_clause}`).
                **Ejemplo de formato:** {{"messages": [{{"id": 1, "outputs": [ {{"language": "Español", "text": "..."}}, {{"language": "Inglés", "text": "..."}} ] }}]}}
                Genera el contenido.
                """.strip()
                
                with st.spinner("Creando descripciones..."):
                    try:
                        model = genai.GenerativeModel('gemini-1.5-flash-latest')
                        response = model.generate_content(prompt)
                        raw = response.text.strip().replace("```json", "").replace("```", "")
                        data = json.loads(raw)
                        st.session_state.last_desc_generation = data.get("messages", [])
                    except Exception as e:
                        st.error(f"Error en la generación: {e}")

    with desc_col2:
        st.subheader("Resultados Listos para Copiar")
        if st.session_state.last_desc_generation:
            for item in st.session_state.last_desc_generation:
                st.markdown(f"**Idea #{item.get('id', '?')}**")
                for output in item.get("outputs", []):
                    lang, text = output.get("language", ""), output.get("text", "")
                    emoji = LANGUAGE_EMOJI_MAP.get(lang, "🏳️")
                    display_text = f"{creator_username.strip()}\n\n{text}" if creator_username else text
                    st.text_area(f"{emoji} {lang}", value=display_text, height=150, key=f"desc_output_{item.get('id')}_{lang}")
                st.markdown("---")
        else:
            st.info("Aquí aparecerán las descripciones generadas.")

with tab_dm:
    st.header("Gestiona tus Conversaciones con Fans")
    if not st.session_state.dm_conversation_history:
        st.subheader("Iniciar una Nueva Conversación")
        dm_scenario = st.selectbox("Elige un escenario estratégico", options=DM_SCENARIOS, key="dm_scenario")
        fan_username = st.text_input("Nombre de usuario del fan (opcional)", placeholder="@usuario", key="dm_fan_username")
        dm_default_tags = default_tags[:5]
        dm_tags = st.multiselect("Elige etiquetas para este DM", options=ALL_TAGS, max_selections=5, default=dm_default_tags, key="dm_tags")
        st.caption(f"Seleccionadas: {len(dm_tags)} / 5")
        safe_dm_intensity_index = INTENSITY_LEVELS.index(default_intensity) if default_intensity in INTENSITY_LEVELS else 1
        dm_intensity = st.selectbox("Intensidad del DM", options=INTENSITY_LEVELS, index=safe_dm_intensity_index, key="dm_intensity")
        
        if st.button("✍️ Generar Primer Mensaje"):
            st.session_state.dm_context = {"scenario": dm_scenario, "tags": dm_tags, "intensity": dm_intensity, "username": fan_username, "persona": persona_clause}
            first_message_prompt = f"Tu Rol: {persona_clause}\nTu Misión: Escribe el PRIMER mensaje para iniciar una conversación con un fan en el escenario '{dm_scenario}', con un tono '{dm_intensity}' y usando las etiquetas '{', '.join(dm_tags)}' como inspiración. El fan es '{fan_username if fan_username else 'un nuevo fan'}'. El mensaje debe ser corto, personal y diseñado para obtener una respuesta. Devuelve solo el texto del mensaje."
            with st.spinner("Creando el rompehielos perfecto..."):
                model = genai.GenerativeModel('gemini-1.5-flash-latest')
                response = model.generate_content(first_message_prompt)
                st.session_state.dm_conversation_history.append({"role": "model", "parts": [response.text.strip()]})
                st.rerun()
    else:
        st.subheader("💬 Conversación Activa")
        chat_container = st.container(height=300)
        with chat_container:
            for msg in st.session_state.dm_conversation_history:
                role = "user" if msg["role"] == "user" else "assistant"
                with st.chat_message(role):
                    st.write(msg["parts"][0])
        if st.session_state.dm_reply_suggestions:
            st.markdown("💡 **Sugerencias de Respuesta:**")
            for i, suggestion in enumerate(st.session_state.dm_reply_suggestions):
                st.text_area(f"Opción {i+1}", value=suggestion, height=100, key=f"sugg_{i}")
        
        with st.form("reply_form"):
            fan_reply = st.text_area("Pega aquí la respuesta del fan:", height=150, key="fan_reply_text")
            submitted = st.form_submit_button("💡 Generar Sugerencias de Respuesta")
            if submitted and fan_reply:
                st.session_state.dm_conversation_history.append({"role": "user", "parts": [fan_reply]})
                context = st.session_state.dm_context
                history_for_prompt = "\n".join([f"{'Creadora' if m['role'] == 'model' else 'Fan'}: {m['parts'][0]}" for m in st.session_state.dm_conversation_history])
                reply_prompt = f"Tu Rol: {context['persona']}\nObjetivo de la Conversación: {context['scenario']}\nHistorial: {history_for_prompt}\nTu Misión: Lee el último mensaje del fan y genera 3 opciones de respuesta distintas y creativas para continuar la conversación. Formato: JSON con clave 'suggestions' y una lista de 3 strings."
                with st.spinner("Analizando y creando respuestas..."):
                    model = genai.GenerativeModel('gemini-1.5-flash-latest')
                    response = model.generate_content(reply_prompt)
                    raw_suggestions = response.text.strip().replace("```json", "").replace("```", "")
                    try:
                        suggestion_data = json.loads(raw_suggestions)
                        st.session_state.dm_reply_suggestions = suggestion_data.get("suggestions", [])
                    except Exception as e:
                        st.error(f"No se pudieron generar sugerencias: {e}")
                st.rerun()

        if st.button("❌ Terminar y Empezar Nueva Conversación"):
            st.session_state.dm_conversation_history.clear()
            st.session_state.dm_context.clear()
            st.session_state.dm_reply_suggestions.clear()
            st.rerun()