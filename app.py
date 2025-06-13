# ---------------- streamlit_app.py (Versión 5.0 - Sistema de Favoritos) ----------------

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
    "Práctica: Anal", "Práctica: Oral (Blowjob/Deepthroat)", "Práctica: Doble Penetración", "Práctica: Creampie",
    "Práctica: Squirt", "Práctica: Handjob", "Práctica: Footjob", "Práctica: Bukkake / Gangbang",
    "Práctica: BDSM", "Práctica: Bondage", "Práctica: Sumisión", "Práctica: Dominación",
    "Fetiche: Látex", "Fetiche: Cuero (Leather)", "Fetiche: Tacones (Heels)", "Fetiche: Lencería",
    "Rol: Madrastra/Padrastro", "Rol: Hermanastra/o", "Rol: Profesora/Estudiante", "Rol: Jefa/Empleado", "Rol: Doctora/Enfermera",
    "Escenario: Público", "Escenario: Oficina", "Escenario: Casting/Entrevista", "Escenario: Masaje", "Escenario: Fiesta", "Escenario: Cámara Espía (Spycam)",
    "Parodia: Dibujos Animados / Anime", "Parodia: Cosplay",
    "Estilo: Amateur / Casero", "Estilo: POV (Punto de Vista)",
]
INTENSITY_LEVELS = ("Neutral", "Coqueto", "Sumisa", "Dominante", "Fetichista")
AVAILABLE_LANGUAGES = ("Español", "Inglés", "Francés", "Portugués", "Alemán", "Ruso", "Neerlandés")
LANGUAGE_EMOJI_MAP = {
    "Español": "🇪🇸", "Inglés": "🇺🇸", "Francés": "🇫🇷", "Portugués": "🇵🇹🇧🇷",
    "Alemán": "🇩🇪", "Ruso": "🇷🇺", "Neerlandés": "🇳🇱",
}

# ---------- CONFIGURACIÓN PÁGINA ----------
st.set_page_config(page_title="Sexy AI Message Generator", page_icon="✨", layout="centered")

# --- INICIALIZACIÓN DE LA MEMORIA DE SESIÓN (FAVORITOS) ---
if 'favorites' not in st.session_state:
    st.session_state.favorites = []

# ---------- CLAVE GEMINI ----------
try:
    api_key = os.environ['GEMINI_API_KEY']
    genai.configure(api_key=api_key)
except KeyError:
    st.error("No se encontró la clave de API de Gemini. Asegúrate de añadirla a los 'Secrets'.")
    st.stop()

# ---------- CABECERA Y BRANDING ----------
st.title("💌 Sexy AI Message Generator")
st.markdown("by **Luminarys Production**")

# --- SECCIÓN PARA MOSTRAR FAVORITOS GUARDADOS ---
if st.session_state.favorites:
    st.write("---")
    st.subheader("⭐ Mis Contenidos Favoritos")
    for i, fav_item in enumerate(st.session_state.favorites):
        # Usamos un expander para que no ocupe tanto espacio
        with st.expander(f"Favorito #{i+1}: {fav_item['outputs'][0]['text'][:50]}..."):
            idea_id = fav_item.get("id", i)
            outputs = fav_item.get("outputs", [])
            if outputs:
                for output in outputs:
                    lang = output.get("language", "Desconocido")
                    text = output.get("text", "No generado.")
                    emoji = LANGUAGE_EMOJI_MAP.get(lang, "🏳️")
                    st.markdown(f"{emoji} **{lang}:** {text}")
            
            # Botón para eliminar el favorito de la lista
            if st.button(f"🗑️ Eliminar Favorito", key=f"delete_fav_{i}"):
                st.session_state.favorites.pop(i)
                st.rerun() # Re-ejecuta la app para refrescar la lista inmediatamente
    st.write("---")
else:
    st.info("💡 Consejo: Cuando generes contenido que te guste, ¡guárdalo como favorito para acceder a él rápidamente!")


# ---------- CONTROLES DE LA APP ----------
st.header("Generador de Contenido")
generation_type = st.selectbox("1. ¿Qué quieres generar?", ("Descripción para Post", "DM para Fans"))

dm_type = ""
physical_features = ""
if generation_type == "DM para Fans":
    dm_type = st.radio("🎯 Propósito del DM", ("Mass DM Free (Atraer)", "Mass DM $ (Vender)", "Mass Sub (Retener)"), index=0)
else:
    physical_features = st.text_input("✨ Tus 3 características físicas principales (opcional)", placeholder="Ej: pelo rojo, ojos verdes, tatuajes", help="Describe 3 rasgos para que la IA se inspire y los incorpore.")

selected_tags = st.multiselect(
    "2. Elige de 2 a 10 etiquetas para definir el contenido",
    options=ALL_TAGS,
    max_selections=10,
)

intensity = st.selectbox("3. Nivel de intensidad", options=INTENSITY_LEVELS, index=1)
output_languages = st.multiselect("4. Idiomas de salida", options=AVAILABLE_LANGUAGES, default=["Español", "Inglés"])
num_messages = st.slider("5. Cantidad de ideas a generar", 1, 10, 3)

st.write("---")

# ================= BOTÓN =================
if st.button("🚀 Generar Contenido"):
    if len(selected_tags) < 2:
        st.warning("Por favor, selecciona al menos 2 etiquetas para obtener mejores resultados.")
    elif not output_languages:
        st.error("Por favor, selecciona al menos un idioma de salida.")
    else:
        # (El prompt y la lógica de la IA no cambian en esta actualización)
        language_clause = ", ".join(output_languages)
        tags_clause = ", ".join(selected_tags)
        task_description = ""
        if generation_type == "DM para Fans":
            task_description = f"Tu Misión es generar {num_messages} ideas de mensajes directos (DM) para fans con el propósito de: `{dm_type}`."
        else:
            task_description = f"Tu Misión es generar {num_messages} ideas de descripciones o pies de foto (captions) para un post en una red social."

        prompt = f"""
        **Tu Identidad Secreta (El Personaje que Debes Encarnar):**
        Eres una creadora de contenido experta. Tu personalidad y tono verbal deben ser `{intensity}`.
        Actúas DESDE la perspectiva de una persona definida por las siguientes etiquetas: `{tags_clause}`.
        Si se especifican características físicas adicionales (`{physical_features if physical_features else 'No especificadas'}`), estas son TUS características. Habla en primera persona sobre ellas.
        Tu conocimiento base es el de una experta en psicología sexual y de ventas, y marketing digital para creadores.

        **{task_description}**

        **Manual de Estilo Creativo (Reglas Obligatorias):**
        1.  **Mostrar, no Decir:** No LISTES las etiquetas. TRANSFÓRMALAS en acciones, sentimientos y descripciones. Si la etiqueta es "Rasgos: Tatuajes", no digas "tengo tatuajes", di "siente la tinta de mi piel contra la tuya...". Encarna el arquetipo, no lo anuncies.
        2.  **CERO CLICHÉS:** PROHIBIDO usar frases genéricas como "suscríbete", "contenido exclusivo", "no te lo pierdas". El llamado a la acción debe ser implícito y seductor.
        3.  **PROHIBIDO HASHTAGS:** No generes NUNCA hashtags (`#`).
        4.  **ADAPTACIÓN CULTURAL AVANZADA:** Para CADA idea, genera una versión en los idiomas solicitados: `{language_clause}`. La versión en 'Inglés' DEBE ser una adaptación coloquial (jerga de EE. UU.). *Ejemplo de adaptación:* Español (poético): "Mis ojos oscuros guardan secretos." -> Inglés (directo): "Bet you can't handle the secrets in my eyes."
        5.  **FORMATO DE SALIDA (JSON ESTRICTO):** Tu única respuesta debe ser un objeto JSON válido.
            *Ejemplo de formato:*
            {{
              "messages": [
                {{ "id": 1, "outputs": [ {{ "language": "Español", "text": "..." }}, {{ "language": "Inglés", "text": "..." }} ] }}
              ]
            }}

        Ahora, encarna tu rol y genera el contenido.
        """.strip()

        # ---------- LLAMADA A GEMINI ----------
        with st.spinner("🧠 Perfeccionando el arte de la seducción..."):
            try:
                model = genai.GenerativeModel('gemini-1.5-flash-latest')
                generation_config = genai.types.GenerationConfig(temperature=1.0)
                response = model.generate_content(prompt, generation_config=generation_config)
                raw = response.text.strip()
                
                # Parseo y visualización de resultados generados
                st.subheader("💡 Contenido Recién Generado")
                if raw.startswith("```json"):
                    raw = raw.replace("```json", "").replace("```", "").strip()
                data = json.loads(raw)
                msgs = data.get("messages", [])
                
                if not msgs:
                    st.error("La respuesta de la IA no contenía mensajes. Intenta de nuevo.")
                else:
                    for i, item in enumerate(msgs):
                        st.markdown(f"---")
                        idea_id = item.get("id", i)
                        outputs = item.get("outputs", [])
                        
                        # Crear un ID único para el item para evitar duplicados en favoritos
                        item['unique_id'] = hash(frozenset(o['text'] for o in outputs))

                        # Mostrar los textos generados
                        st.markdown(f"#### Idea de Contenido #{idea_id}")
                        if outputs:
                            for output in outputs:
                                lang = output.get("language", "Desconocido")
                                text = output.get("text", "No generado.")
                                emoji = LANGUAGE_EMOJI_MAP.get(lang, "🏳️")
                                st.markdown(f"{emoji} **{lang}:** {text}")
                        
                        # Lógica para el botón de Guardar
                        is_favorited = any(fav.get('unique_id') == item['unique_id'] for fav in st.session_state.favorites)
                        if is_favorited:
                            st.success("✔️ Guardado en Favoritos")
                        else:
                            if st.button(f"⭐ Guardar Idea #{idea_id}", key=f"save_{i}"):
                                st.session_state.favorites.append(item)
                                st.rerun()

            except json.JSONDecodeError:
                st.error("❌ La IA devolvió un formato de JSON inválido. Revisa la respuesta bruta:")
                st.code(raw, language="text")
            except Exception as exc:
                st.error(f"❌ Error con la API de Gemini: {exc}")

# ---------- PIE ----------
st.markdown("<div style='text-align:center;font-size:0.8em; margin-top: 2em;'>Powered by Google Gemini</div>", unsafe_allow_html=True)