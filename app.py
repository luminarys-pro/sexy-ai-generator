# ---------------- streamlit_app.py (Versión de Re-estabilización) ----------------

import streamlit as st
import google.generativeai as genai
import json
import os

# ---------- CONFIGURACIÓN PÁGINA ----------
st.set_page_config(page_title="AI Text Generator - Base Estable", page_icon="🔩", layout="centered")

# ---------- CLAVE GEMINI ----------
try:
    api_key = os.environ['GEMINI_API_KEY']
    genai.configure(api_key=api_key)
except KeyError:
    st.error("ERROR: No se encontró la clave de API de Gemini en los 'Secrets'. La aplicación no puede funcionar.")
    st.stop()

# ==================== PÁGINA PRINCIPAL ====================
st.title("🔩 Generador de Texto - Base Estable")
st.markdown("Esta es una versión simplificada para garantizar el funcionamiento del núcleo de la IA.")

# --- Formulario de Entrada ---
with st.form("generation_form"):
    st.header("1. Define tu Petición")
    
    prompt_text = st.text_area(
        "Introduce las instrucciones para la IA:",
        height=200,
        value="Eres un experto en marketing. Escribe 3 descripciones de post coquetas y misteriosas para una creadora de contenido latina con tatuajes."
    )
    
    submitted = st.form_submit_button("🚀 Generar Texto")

# --- Lógica de Generación y Visualización ---
if submitted:
    if not prompt_text:
        st.warning("Por favor, introduce un prompt para la IA.")
    else:
        st.markdown("---")
        st.subheader("2. Respuesta de la IA")
        
        with st.spinner("Contactando a la IA..."):
            try:
                model = genai.GenerativeModel('gemini-1.5-flash-latest')
                response = model.generate_content(prompt_text)
                
                # CÓDIGO DEFENSIVO: Se comprueba la respuesta antes de mostrarla
                if hasattr(response, 'text') and response.text:
                    st.success("¡Respuesta recibida con éxito!")
                    st.markdown(response.text)
                else:
                    st.error("La IA devolvió una respuesta vacía. Esto puede ser por los filtros de seguridad del modelo. Intenta con un prompt diferente.")
            
            except Exception as e:
                st.error("Ocurrió un error durante la comunicación con la IA.")
                st.exception(e) # Muestra el error técnico completo para depuración