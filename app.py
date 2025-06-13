# ---------------- streamlit_app.py (Versión 10.0 - Plataforma Completa con Asistente de DMs) ----------------

from __future__ import annotations
import streamlit as st
import google.generativeai as genai
import json
from typing import List, Dict
import os

# ---------- LISTAS DE OPCIONES Y CONSTANTES ----------
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
DM_SCENARIOS = ("Mensaje de Bienvenida (Nuevo Fan)", "Oferta Especial (Venta de PPV)", "Anuncio de Live Stream", "Reactivación (Fan Inactivo)", "Agradecimiento (Fan Destacado)")
DEFAULT_PERSONA = "Eres una IA que encarna el rol de una experta en psicología sexual y socioemocional, psicología de ventas y estrategia de marketing. Eres una creadora de contenido veterana y exitosa."

# ---------- CONFIGURACIÓN PÁGINA ----------
st.set_page_config(page_title="Luminarys AI Assistant", page_icon="✨", layout="wide")

# --- INICIALIZACIÓN DE LA MEMORIA DE SESIÓN ---
if 'favorites' not in st.session_state: st.session_state.favorites = []
if 'profiles' not in st.session_state: st.session_state.profiles = {}
if 'selected_profile_name' not in st.session_state: st.session_state.selected_profile_name = "-- Ninguno --"
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

# ==================== BARRA LATERAL (SIDEBAR) PARA PERFILES ====================
with st.sidebar:
    st.title("🎭 Gestor de Perfiles")
    st.markdown("Crea y guarda diferentes personalidades para la IA.")

    profile_names = ["-- Ninguno --"] + list(st.session_state.profiles.keys())
    active_profile_name = st.selectbox("Cargar Perfil", options=profile_names, key='selected_profile_name')

    with st.expander("➕ Crear Nuevo Perfil"):
        with st.form("new_profile_form", clear_on_submit=True):
            # ... (Formulario de creación de perfil sin cambios)
            new_profile_name = st.text_input("Nombre del Perfil*")
            new_profile_desc = st.text_area("Descripción de la Personalidad*", height=200, placeholder="Ej: Eres una diosa dominante y juguetona...")
            new_profile_tags = st.multiselect("Etiquetas Predeterminadas", options=ALL_TAGS)
            new_profile_intensity = st.selectbox("Intensidad Predeterminada", options=INTENSITY_LEVELS, index=1)
            submitted = st.form_submit_button("Guardar Perfil")
            if submitted and new_profile_name and new_profile_desc:
                st.session_state.profiles[new_profile_name] = {"description": new_profile_desc, "tags": new_profile_tags, "intensity": new_profile_intensity}
                st.session_state.selected_profile_name = new_profile_name
                st.rerun()

    if active_profile_name != "-- Ninguno --":
        if st.button(f"🗑️ Eliminar Perfil '{active_profile_name}'", use_container_width=True):
            del st.session_state.profiles[active_profile_name]
            st.session_state.selected_profile_name = "-- Ninguno --"
            st.rerun()

# ==================== PÁGINA PRINCIPAL ====================
st.title("💌 AI Content Assistant")
st.markdown("by **Luminarys Production**")

# --- LÓGICA DE CARGA DE PERFIL ---
active_profile_data = st.session_state.profiles.get(st.session_state.get('selected_profile_name', '-- Ninguno --'), {})
persona_clause = active_profile_data.get('description', DEFAULT_PERSONA)
default_tags = active_profile_data.get('tags', [])
default_intensity = active_profile_data.get('intensity', 'Coqueto')

# --- DEFINICIÓN DE PESTAÑAS ---
tab_desc, tab_dm = st.tabs(["📝 Generador de Descripciones", "💬 Asistente de DMs"])

# ==================== PESTAÑA 1: GENERADOR DE DESCRIPCIONES ====================
with tab_desc:
    st.header("Crea Descripciones para tus Posts")
    
    # --- SECCIÓN DE FAVORITOS (SOLO PARA DESCRIPCIONES) ---
    if st.session_state.favorites:
        with st.expander("⭐ Mis Descripciones Favoritas Guardadas"):
            for i, fav_item in enumerate(st.session_state.favorites):
                st.markdown(f"**Favorito #{i+1}**")
                text = fav_item.get("text", "N/A")
                st.markdown(text)
                if st.button(f"🗑️ Eliminar", key=f"delete_fav_desc_{i}"):
                    st.session_state.favorites.pop(i)
                    st.rerun()
                st.markdown("---")
    
    # --- CONTROLES PARA DESCRIPCIONES ---
    desc_physical_features = st.text_input("✨ Tus características físicas (opcional)", placeholder="Ej: pelo rojo, ojos verdes, tatuajes")
    desc_selected_tags = st.multiselect("Elige de 2 a 10 etiquetas", options=ALL_TAGS, max_selections=10, default=default_tags, key="desc_tags")
    desc_intensity = st.selectbox("Nivel de intensidad", options=INTENSITY_LEVELS, index=INTENSITY_LEVELS.index(default_intensity), key="desc_intensity")
    
    if st.button("🚀 Generar Descripciones", key="gen_desc"):
        # Lógica para generar descripciones (similar a versiones anteriores)
        # Se omite por brevedad pero sería la lógica de generación de texto para posts
        st.success("Función de descripciones ejecutada.")


# ==================== PESTAÑA 2: ASISTENTE DE DMs ====================
with tab_dm:
    st.header("Gestiona tus Conversaciones con Fans")

    # --- INICIAR UNA NUEVA CONVERSACIÓN ---
    if not st.session_state.dm_conversation_history:
        st.subheader("Iniciar una Nueva Conversación")
        dm_scenario = st.selectbox("Elige un escenario estratégico", options=DM_SCENARIOS)
        fan_username = st.text_input("Nombre de usuario del fan (opcional)", placeholder="@usuario")
        dm_tags = st.multiselect("Elige etiquetas para este DM", options=ALL_TAGS, max_selections=5, default=default_tags, key="dm_tags")
        dm_intensity = st.selectbox("Intensidad del DM", options=INTENSITY_LEVELS, index=INTENSITY_LEVELS.index(default_intensity), key="dm_intensity")
        
        if st.button("✍️ Generar Primer Mensaje"):
            st.session_state.dm_context = {"scenario": dm_scenario, "tags": dm_tags, "intensity": dm_intensity, "username": fan_username}
            
            # Prompt para el primer mensaje
            first_message_prompt = f"""
            **Tu Rol:** {persona_clause}
            **Tu Misión:** Escribe el PRIMER mensaje para iniciar una conversación con un fan.
            **Contexto:**
            - Escenario: {dm_scenario}
            - Nombre del Fan: {fan_username if fan_username else "No especificado"}
            - Tono/Intensidad: {dm_intensity}
            - Etiquetas para inspirarte: {", ".join(dm_tags)}
            **Reglas:**
            - Si hay un nombre de usuario, intégralo de forma natural.
            - El mensaje debe ser corto, directo y diseñado para obtener una respuesta.
            - Prohibido hashtags o clichés.
            - Devuelve un solo string con el texto del mensaje.
            """
            with st.spinner("Creando el rompehielos perfecto..."):
                # Simulación de llamada a API para el primer mensaje
                model = genai.GenerativeModel('gemini-1.5-flash-latest')
                response = model.generate_content(first_message_prompt)
                first_message_text = response.text.strip()
                
                st.session_state.dm_conversation_history.append({"role": "model", "parts": [first_message_text]})
                st.rerun()

    # --- CONTINUAR UNA CONVERSACIÓN EXISTENTE ---
    else:
        st.subheader("💬 Conversación Activa")

        # Mostrar historial de chat
        for msg in st.session_state.dm_conversation_history:
            with st.chat_message("user" if msg["role"] == "user" else "assistant"):
                st.write(msg["parts"][0])

        # Mostrar sugerencias de respuesta si existen
        if st.session_state.dm_reply_suggestions:
            st.markdown("💡 **Sugerencias de Respuesta:**")
            for i, suggestion in enumerate(st.session_state.dm_reply_suggestions):
                st.text_area(f"Opción {i+1}", value=suggestion, height=100, key=f"sugg_{i}")
        
        # Formulario para la respuesta del fan
        with st.form("reply_form"):
            fan_reply = st.text_area("Pega aquí la respuesta del fan:", height=150)
            submitted = st.form_submit_button("💡 Generar Sugerencias de Respuesta")

            if submitted and fan_reply:
                st.session_state.dm_conversation_history.append({"role": "user", "parts": [fan_reply]})
                
                # Prompt para generar respuestas
                context = st.session_state.dm_context
                history_text = "\n".join([f"{msg['role']}: {msg['parts'][0]}" for msg in st.session_state.dm_conversation_history])

                reply_prompt = f"""
                **Tu Rol:** Eres un asistente de chat para una creadora de contenido. Responde como si fueras ella, manteniendo la personalidad de su perfil activo: "{persona_clause}" y un tono '{context['intensity']}'.
                **Objetivo Original de la Conversación:** {context['scenario']}
                **Historial de la Conversación hasta ahora:**
                {history_text}
                **Tu Misión:** Lee el último mensaje del fan y genera 3 opciones de respuesta distintas y creativas para continuar la conversación y guiarla hacia el objetivo original.
                **Formato de Salida:** Un JSON con una clave "suggestions" que contiene una lista de 3 strings. Ejemplo: {{"suggestions": ["Respuesta 1", "Respuesta 2", "Respuesta 3"]}}
                """
                
                with st.spinner("Analizando la conversación y creando respuestas..."):
                    # Simulación de llamada a API para sugerencias
                    model = genai.GenerativeModel('gemini-1.5-flash-latest')
                    response = model.generate_content(reply_prompt)
                    raw_suggestions = response.text.strip()

                    try: