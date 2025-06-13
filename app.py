# ---------------- streamlit_app.py (Versión Final Completa) ----------------

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
if 'desc_favorites' not in st.session_state: st.session_state.desc_favorites = []
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
        st.session_state.profiles[name] = {
            "description": desc,
            "tags": st.session_state.get("profile_tags_input", []),
            "intensity": st.session_state.get("profile_intensity_input", "Coqueto")
        }
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
            st.multiselect("Etiquetas Predeterminadas", options=ALL_TAGS, key="profile_tags_input")
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
    
    # ... (Resto del código de la pestaña