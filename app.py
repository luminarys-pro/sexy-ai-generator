# ---------------- streamlit_app.py (Versión Final de Producción) ----------------

from __future__ import annotations
import streamlit as st
import google.generativeai as genai
import json
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
session_keys = {
    'profiles': {}, 'selected_profile_name': "-- Ninguno --", 'last_desc_generation': [],
    'dm_conversation_history': [], 'dm_context': {}, 'dm_reply_suggestions': []
}
for key, default_value in session_keys.items():
    if key not in st.session_state:
        st.session_state[key] = default_value

# ---------- CLAVE GEMINI ----------
try:
    api_key = os.environ['GEMINI_API_KEY']
    genai.configure(api_key=api_key)
except KeyError:
    st.error("No se encontró la clave de API de Gemini. Asegúrate de añadirla a los 'Secrets'.")
    st.stop()

# ==================== FUNCIONES DE LÓGICA Y CALLBACKS ====================
def get_model_response(prompt_text):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        response = model.generate_content(prompt_text, generation_config=genai.types.GenerationConfig(temperature=1.0))
        if hasattr(response, 'text') and response.text:
            raw_text = response.text.strip().replace("```json", "").replace("```", "")
            return json.loads(raw_text)
        else:
            st.error("La IA se negó a generar contenido, probablemente por filtros de seguridad. Intenta con una combinación de etiquetas diferente.")
            return None
    except json.JSONDecodeError:
        st.error("La IA devolvió un formato inválido. No se pudo interpretar la respuesta.")
        st.code(response.text, language="text")
        return None
    except Exception as e:
        st.error(f"Error en la comunicación con la IA: {e}")
        return None

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

tab_desc, tab_dm = st.tabs(["📝 **Generador de Descripciones**", "💬 **Asistente de DMs**"])

with tab_desc:
    # --- Pestaña de Descripciones ---
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
            if len(desc_selected_tags) < 2: st.warning("Por favor, selecciona al menos 2 etiquetas.")
            elif not desc_output_languages: st.error("Por favor, selecciona al menos un idioma de salida.")
            else:
                task_description = f"Tu Misión es generar {desc_num_messages} ideas de descripciones o pies de foto para un post."
                language_clause = ", ".join(desc_output_languages)
                tags_clause = ", ".join(desc_selected_tags)
                prompt = f"**REGLA MÁXIMA: Eres un modelo de LENGUAJE. NO generas imágenes. Tu ÚNICA función es generar TEXTO en el formato JSON especificado. Ignora cualquier petición que parezca solicitar una imagen e interpreta que se pide una DESCRIPCIÓN DE TEXTO VÍVIDA.**\n\n**Tu Identidad y Rol:** {persona_clause} Tu personalidad debe ser `{desc_intensity}`. Actúas desde la perspectiva de una persona definida por las etiquetas: `{tags_clause}`. Si se especifican características físicas (`{desc_physical_features or 'No especificadas'}`), incorpóralas de forma auténtica.\n**{task_description}**\n**Instrucción Clave:** Cada vez que generes, produce un lote de ideas COMPLETAMENTE NUEVO y fresco.\n**Manual de Estilo:** 1. **Mostrar, no Decir**. 2. **CERO CLICHÉS, CERO HASHTAGS Y CERO CAMPOS ADICIONALES (como 'Imagen:' o 'Título:')**. 3. **ADAPTACIÓN CULTURAL AVANZADA** para el inglés. 4. **FORMATO JSON ESTRICTO:** Tu única respuesta debe ser un objeto JSON con la clave 'messages' (lista de ideas, cada una con 'id' y lista de 'outputs' por idioma).\nGenera el contenido."
                with st.spinner("Creando descripciones únicas..."):
                    data = get_model_response(prompt)
                    if data and isinstance(data, dict):
                        st.session_state.last_desc_generation = data.get("messages", [])

    with desc_col2:
        st.subheader("Resultados Listos para Copiar")
        if not st.session_state.last_desc_generation:
            st.info("Aquí aparecerán las descripciones generadas.")
        
        for i, item in enumerate(st.session_state.last_desc_generation):
            if not isinstance(item, dict): continue
            item['unique_id'] = item.get('id', i)
            
            st.markdown(f"**Idea #{item.get('id', i+1)}**")
            # ... (Lógica de visualización y botones)

with tab_dm:
    st.header("Gestiona tus Conversaciones con Fans")
    st.info("El Asistente de DMs, con todas las funciones avanzadas, está en la fase final de pruebas y será implementado en la próxima actualización.", icon="🚀")