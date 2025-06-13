# ---------------- streamlit_app.py (Versión 10.1 - Corrección de Sintaxis) ----------------

from __future__ import annotations
import streamlit as st
import google.generativeai as genai
import json
from typing import List, Dict
import os

# --- (Las listas de opciones y constantes no cambian) ---
ALL_TAGS = [
    "Edad: Teen (18+)", "Edad: Joven (20-29)", "Edad: MILF (30-45)", "Edad: Madura/Cougar (45+)", "Cuerpo: Petite/Delgada", "Cuerpo: Curvy/Gruesa (Thick)", "Cuerpo: BBW/Talla Grande", "Cuerpo: Atlético/Fitness", "Cuerpo: Musculosa", "Cabello: Rubia", "Cabello: Morena", "Cabello: Pelirroja", "Cabello: Pelo Negro", "Etnia: Latina", "Etnia: Asiática", "Etnia: Ébano (Ebony)", "Etnia: India", "Etnia: Blanca/Caucásica", "Rasgos: Tatuajes", "Rasgos: Piercings", "Rasgos: Pechos Grandes", "Rasgos: Pechos Pequeños", "Rasgos: Pechos Naturales", "Rasgos: Trasero Grande (Big Ass)", "Participantes: Solo (Chica)", "Participantes: Pareja (Chica/Chico)", "Participantes: Pareja (Chica/Chica)", "Práctica: Anal", "Práctica: Oral (Blowjob/Deepthroat)", "Práctica: Doble Penetración", "Práctica: Creampie", "Práctica: Squirt", "Práctica: Handjob", "Práctica: Footjob", "Práctica: BDSM", "Práctica: Bondage", "Práctica: Sumisión", "Práctica: Dominación", "Fetiche: Látex", "Fetiche: Cuero (Leather)", "Fetiche: Tacones (Heels)", "Fetiche: Lencería", "Rol: Madrastra/Padrastro", "Rol: Hermanastra/o", "Rol: Profesora/Estudiante", "Rol: Jefa/Empleado", "Rol: Doctora/Enfermera", "Escenario: Público", "Escenario: Oficina", "Escenario: Casting/Entrevista", "Escenario: Masaje", "Escenario: Fiesta", "Escenario: Cámara Espía (Spycam)", "Parodia: Cosplay", "Estilo: Amateur / Casero", "Estilo: POV (Punto de Vista)",
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
                    st.session_state.profiles[new_profile_name] = {"description": new_profile_desc, "tags": new_profile_tags, "intensity": new_profile_intensity}
                    st.session_state.selected_profile_name = new_profile_name
                    st.success(f"¡Perfil '{new_profile_name}' guardado!")
                else:
                    st.error("El nombre y la descripción del perfil son obligatorios.")

    if active_profile_name != "-- Ninguno --":
        st.markdown("---")
        if st.button(f"🗑️ Eliminar Perfil '{active_profile_name}'", use_container_width=True):
            del st.session_state.profiles[active_profile_name]
            st.session_state.selected_profile_name = "-- Ninguno --"
            st.rerun()

# ==================== PÁGINA PRINCIPAL ====================