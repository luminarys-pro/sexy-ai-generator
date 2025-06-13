# ---------------- streamlit_app.py (Versión de Diagnóstico) ----------------

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
DEFAULT_PERSONA = "Eres una IA que encarna el rol de una experta en psicología sexual y socioemocional, psicología de ventas y estrategia de marketing. Eres una creadora de contenido veterana y exitosa."
AVAILABLE_LANGUAGES = ("Español", "Inglés", "Francés", "Portugués", "Alemán", "Ruso", "Neerlandés")


# ---------- CONFIGURACIÓN PÁGINA ----------
st.set_page_config(page_title="Luminarys AI Assistant - MODO DIAGNÓSTICO", page_icon="⚙️", layout="wide")

# ---------- CLAVE GEMINI ----------
try:
    api_key = os.environ['GEMINI_API_KEY']
    genai.configure(api_key=api_key)
except KeyError:
    st.error("No se encontró la clave de API de Gemini.")
    st.stop()

# ==================== PÁGINA PRINCIPAL ====================
st.title("⚙️ AI Content Assistant (Modo Diagnóstico)")
st.warning("Esta es una versión simplificada para encontrar un error. Algunas funciones están desactivadas.")

# --- Controles simplificados para la prueba ---
st.header("Prueba de Generación de Descripciones")
desc_selected_tags = st.multiselect("Elige algunas etiquetas de prueba", options=ALL_TAGS, max_selections=5)
desc_intensity = st.selectbox("Nivel de intensidad", options=INTENSITY_LEVELS)
desc_output_languages = st.multiselect("Idiomas de salida", options=AVAILABLE_LANGUAGES, default=["Español", "Inglés"])

if st.button("🚀 Ejecutar Prueba de Generación", use_container_width=True):
    if not desc_selected_tags or not desc_output_languages:
        st.warning("Por favor, selecciona etiquetas e idiomas para la prueba.")
    else:
        language_clause = ", ".join(desc_output_languages)
        tags_clause = ", ".join(desc_selected_tags)
        
        prompt = f"""
        **Tu Identidad y Rol:** {DEFAULT_PERSONA} Tu personalidad debe ser `{desc_intensity}`. Actúas desde la perspectiva de una persona definida por las etiquetas: `{tags_clause}`.
        **Tu Misión:** Genera 2 ideas de descripciones para un post.
        **Manual de Estilo:** 1. **Mostrar, no Decir**. 2. **CERO CLICHÉS y CERO HASHTAGS**. 3. **ADAPTACIÓN CULTURAL AVANZADA** para el inglés. 4. **FORMATO JSON ESTRICTO:** Tu única respuesta debe ser un objeto JSON con la clave 'messages' (lista de ideas, cada una con 'id' y lista de 'outputs' por idioma).
        Genera el contenido.
        """
        
        st.markdown("---")
        st.subheader("1. Prompt Enviado a la IA:")
        st.code(prompt, language="markdown")

        with st.spinner("Esperando respuesta de la IA..."):
            try:
                model = genai.GenerativeModel('gemini-1.5-flash-latest')
                response = model.generate_content(prompt)
                raw = response.text.strip()
                
                st.markdown("---")
                st.subheader("2. Respuesta Cruda Recibida de la IA:")
                st.code(raw, language="text")

                st.markdown("---")
                st.subheader("3. Intentando interpretar como JSON:")
                
                # Limpieza del texto antes de parsear
                if raw.startswith("```json"):
                    raw = raw.replace("```json", "").replace("```", "")
                
                data = json.loads(raw)
                st.success("¡Interpretación JSON exitosa!")
                st.json(data) # Muestra el JSON interpretado de forma bonita

            except Exception as e:
                st.error("¡FALLÓ LA COMUNICACIÓN O LA INTERPRETACIÓN!")
                st.exception(e) # Muestra el error de Python completo