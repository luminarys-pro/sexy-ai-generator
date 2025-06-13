# ---------------- streamlit_app.py (Versión Base Estable) ----------------

from __future__ import annotations
import streamlit as st
import google.generativeai as genai
import json
import os

# ---------- LISTAS DE OPCIONES Y CONSTANTES ----------
ALL_TAGS = [
    "Edad: Teen (18+)", "Edad: Joven (20-29)", "Edad: MILF (30-45)", "Edad: Madura/Cougar (45+)", "Cuerpo: Petite/Delgada", "Cuerpo: Curvy/Gruesa (Thick)", "Cuerpo: BBW/Talla Grande", "Cuerpo: Atlético/Fitness", "Cuerpo: Musculosa", "Cabello: Rubia", "Cabello: Morena", "Cabello: Pelirroja", "Cabello: Pelo Negro", "Etnia: Latina", "Etnia: Asiática", "Etnia: Ébano (Ebony)", "Etnia: India", "Etnia: Blanca/Caucásica", "Rasgos: Tatuajes", "Rasgos: Piercings", "Rasgos: Busto Generoso", "Rasgos: Busto Pequeño", "Rasgos: Pechos Naturales", "Rasgos: Trasero Grande", "Participantes: Solo (Chica)", "Participantes: Pareja (Chica/Chico)", "Participantes: Pareja (Chica/Chica)", "Práctica: Sexo Anal", "Práctica: Sexo Oral", "Práctica: Doble Penetración", "Práctica: Creampie", "Práctica: Squirt", "Práctica: Masturbación", "Práctica: BDSM", "Práctica: Bondage", "Práctica: Sumisión", "Práctica: Dominación", "Fetiche: Látex", "Fetiche: Cuero (Leather)", "Fetiche: Tacones (Heels)", "Fetiche: Lencería", "Rol: Madrastra/Padrastro", "Rol: Hermanastra/o", "Rol: Profesora/Estudiante", "Rol: Jefa/Empleado", "Rol: Doctora/Enfermera", "Escenario: Público", "Escenario: Oficina", "Escenario: Casting/Entrevista", "Escenario: Masaje", "Escenario: Fiesta", "Escenario: Cámara Espía (Spycam)", "Parodia: Cosplay", "Estilo: Amateur / Casero", "Estilo: POV (Punto de Vista)",
]
INTENSITY_LEVELS = ("Neutral", "Coqueto", "Sumisa", "Dominante", "Fetichista")
DEFAULT_PERSONA = "Eres una IA que encarna el rol de una experta en psicología sexual y socioemocional, psicología de ventas y estrategia de marketing. Eres una creadora de contenido veterana y exitosa."
LANGUAGE_EMOJI_MAP = {"Español": "🇪🇸", "Inglés": "🇺🇸", "Francés": "🇫🇷", "Portugués": "🇵🇹🇧🇷", "Alemán": "🇩🇪", "Ruso": "🇷🇺", "Neerlandés": "🇳🇱"}
AVAILABLE_LANGUAGES = list(LANGUAGE_EMOJI_MAP.keys())

# ---------- CONFIGURACIÓN PÁGINA ----------
st.set_page_config(page_title="Luminarys AI Assistant", page_icon="✨", layout="wide")

# --- INICIALIZACIÓN DE LA MEMORIA DE SESIÓN ---
if 'last_desc_generation' not in st.session_state:
    st.session_state.last_desc_generation = []

# ---------- CLAVE GEMINI ----------
try:
    api_key = os.environ['GEMINI_API_KEY']
    genai.configure(api_key=api_key)
except KeyError:
    st.error("No se encontró la clave de API de Gemini. Asegúrate de añadirla a los 'Secrets'.")
    st.stop()

# ==================== FUNCIÓN DE LÓGICA CENTRAL ====================
def get_model_response(prompt_text):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        response = model.generate_content(prompt_text, generation_config=genai.types.GenerationConfig(temperature=1.0))
        
        # Código defensivo para manejar respuestas vacías o inválidas de la IA
        if hasattr(response, 'text') and response.text:
            raw_text = response.text.strip().replace("```json", "").replace("```", "")
            return json.loads(raw_text)
        else:
            st.warning("⚠️ La IA no generó una respuesta, probablemente por filtros de seguridad. Intenta con una combinación de etiquetas diferente.", icon="🤖")
            return None
    except json.JSONDecodeError:
        st.error("La IA devolvió un formato de texto inválido. No se pudo interpretar.")
        if 'response' in locals() and hasattr(response, 'text'):
            st.code(response.text, language="text")
        return None
    except Exception as e:
        st.error(f"Error en la comunicación con la IA: {e}")
        return None

# ==================== PÁGINA PRINCIPAL ====================
st.title("💌 AI Content Assistant")
st.markdown("by **Luminarys Production**")
st.header("Crea Descripciones para tus Posts")

desc_col1, desc_col2 = st.columns([1, 1.2])

# --- COLUMNA DE CONTROLES ---
with desc_col1:
    creator_username = st.text_input("Tu nombre de usuario (ej: @Martinaoff)", key="desc_username")
    desc_physical_features = st.text_input("Tus características físicas (opcional)", placeholder="Ej: pelo rojo, ojos verdes", key="desc_phys")
    
    desc_selected_tags = st.multiselect("Elige de 2 a 10 etiquetas", options=ALL_TAGS, max_selections=10, key="desc_tags")
    st.caption(f"Seleccionadas: {len(desc_selected_tags)} / 10")

    desc_intensity = st.selectbox("Nivel de intensidad", options=INTENSITY_LEVELS, index=1, key="desc_intensity")
    desc_output_languages = st.multiselect("Idiomas de salida", options=AVAILABLE_LANGUAGES, default=["Español", "Inglés"], key="desc_langs")
    desc_num_messages = st.slider("Cantidad de ideas a generar", 1, 5, 3, key="desc_slider")

    if st.button("🚀 Generar Descripciones", key="gen_desc", use_container_width=True):
        if len(desc_selected_tags) < 2:
            st.warning("Por favor, selecciona al menos 2 etiquetas.")
        elif not desc_output_languages:
            st.error("Por favor, selecciona al menos un idioma de salida.")
        else:
            language_clause = ", ".join(desc_output_languages)
            tags_clause = ", ".join(desc_selected_tags)
            prompt = f"**REGLA MÁXIMA: Eres un modelo de LENGUAJE. NO generas imágenes. Tu ÚNICA función es generar TEXTO en el formato JSON especificado.**\n\n**Tu Identidad y Rol:** {DEFAULT_PERSONA} Tu personalidad debe ser `{desc_intensity}`. Actúas desde la perspectiva de una persona definida por las etiquetas: `{tags_clause}`. Si se especifican características físicas (`{desc_physical_features or 'No especificadas'}`), incorpóralas de forma auténtica.\n**Tu Misión:** Genera {desc_num_messages} ideas de descripciones para un post.\n**Instrucción Clave:** Cada vez que generes, produce un lote de ideas COMPLETAMENTE NUEVO.\n**Manual de Estilo:** 1. **Mostrar, no Decir**. 2. **CERO CLICHÉS y CERO HASHTAGS**. 3. **ADAPTACIÓN CULTURAL AVANZADA** para el inglés. 4. **FORMATO JSON ESTRICTO:** Tu única respuesta debe ser un objeto JSON con la clave 'messages' (lista de ideas, cada una con 'id' y lista de 'outputs' por idioma).\nGenera el contenido."
            with st.spinner("Creando descripciones únicas..."):
                data = get_model_response(prompt)
                if data and isinstance(data, dict):
                    st.session_state.last_desc_generation = data.get("messages", [])
                else:
                    # Si la respuesta es None o no es un diccionario, limpia la generación anterior
                    st.session_state.last_desc_generation = []

# --- COLUMNA DE RESULTADOS ---
with desc_col2:
    st.subheader("Resultados Listos para Copiar")
    if not st.session_state.last_desc_generation:
        st.info("Aquí aparecerán las descripciones generadas.")
    
    for item in st.session_state.last_desc_generation:
        if isinstance(item, dict):
            unique_id = item.get('id', os.urandom(4).hex())
            st.markdown(f"**Idea #{unique_id}**")
            
            outputs = item.get("outputs", [])
            if isinstance(outputs, list):
                for output in outputs:
                    if isinstance(output, dict):
                        lang = output.get("language", "")
                        text = output.get("text", "")
                        emoji = LANGUAGE_EMOJI_MAP.get(lang, "🏳️")
                        display_text = f"{creator_username.strip()}\n\n{text}" if creator_username else text
                        st.text_area(f"{emoji} {lang}", value=display_text, height=150, key=f"desc_output_{unique_id}_{lang}")
            st.markdown("---")