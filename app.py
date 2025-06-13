# ---------------- streamlit_app.py (Versión 7.1 - Corrección de Sintaxis) ----------------

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
if 'favorites' not in st.session_state: st.session_state.favorites = []
if 'last_generation' not in st.session_state: st.session_state.last_generation = []
if 'profiles' not in st.session_state: st.session_state.profiles = {}
if 'active_profile_name' not in st.session_state: st.session_state.active_profile_name = "-- Ninguno --"

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
    
    st.session_state.active_profile_name = st.selectbox(
        "Cargar Perfil",
        options=profile_names,
        index=profile_names.index(st.session_state.active_profile_name)
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
                    st.session_state.active_profile_name = new_profile_name
                    st.success(f"¡Perfil '{new_profile_name}' guardado!")
                    st.rerun()
                else:
                    st.error("El nombre y la descripción del perfil son obligatorios.")

    if st.session_state.active_profile_name != "-- Ninguno --":
        st.markdown("---")
        if st.button(f"🗑️ Eliminar Perfil '{st.session_state.active_profile_name}'", use_container_width=True):
            del st.session_state.profiles[st.session_state.active_profile_name]
            st.session_state.active_profile_name = "-- Ninguno --"
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
            st.markdown(f"**Favorito #{i+1}**")
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

# Cargar configuración del perfil activo
active_profile = st.session_state.profiles.get(st.session_state.active_profile_name, {})
default_tags = active_profile.get('tags', [])
try:
    default_intensity_index = INTENSITY_LEVELS.index(active_profile.get('intensity', 'Coqueto'))
except ValueError:
    default_intensity_index = 1

col1, col2 = st.columns([1, 1])

with col1:
    st.header("1. Define tu Contenido")
    generation_type = st.selectbox("¿Qué quieres generar?", ("Descripción para Post", "DM para Fans"))
    dm_type = st.radio("🎯 Propósito del DM", ("Mass DM Free (Atraer)", "Mass DM $ (Vender)", "Mass Sub (Retener)")) if generation_type == "DM para Fans" else ""
    physical_features = st.text_input