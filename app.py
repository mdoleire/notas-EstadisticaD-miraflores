import streamlit as st
import pandas as pd
import google.generativeai as genai

# --- CONFIGURACIÓN SEGURA ---
# El código buscará la llave en la caja fuerte de Streamlit
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("⚠️ No se detectó la API Key en los Secrets de Streamlit.")
    st.stop()

# Configurar Gemini (Usamos el modelo estándar actual)
if API_KEY:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')

# --- FUNCIÓN PARA CARGAR DATOS ---
def cargar_datos():
    archivo_nombre = "calificaciones 6D-Copia.csv"
    try:
        df = pd.read_csv(archivo_nombre)
        
        # Limpieza básica
        if len(df.columns) > 1:
            rename_map = {df.columns[0]: 'numero_lista', df.columns[1]: 'nombre'}
            df = df.rename(columns=rename_map)
        
        df = df[pd.to_numeric(df['numero_lista'], errors='coerce').notna()]
        df['numero_lista'] = df['numero_lista'].astype(float).astype(int).astype(str)
        
        # Mapeo de columnas (Ajustado a tu duda anterior: Indice = Excel - 1)
        def limpiar_nota(col_idx):
            if col_idx < len(df.columns):
                return pd.to_numeric(df[df.columns[col_idx]], errors='coerce').fillna(0)
            return 0.0

        # Ajusta estos índices si cambiaste columnas en el Excel
        # Recuerda: Columna 17 en Excel es índice 16 en Python
        df['promedio_final'] = limpiar_nota(11) 
        df['participacion'] = limpiar_nota(12)
        df['tareas'] = limpiar_nota(13)
        df['proyecto'] = limpiar_nota(14)
        df['examen'] = limpiar_nota(15)
        return df
    except Exception as e:
        st.error(f"⚠️ Error al leer CSV: {e}")
        return None

# --- INTERFAZ ---
st.set_page_config(page_title="Calificaciones Estadística - Miraflores", page_icon="🦁")
st.title("🦁 Consulta de Calificaciones")
st.subheader("Periodo 2: Estadística y Probabilidad 6° D")

col1, col2 = st.columns(2)
num = col1.text_input("Número de Lista:")
nom = col2.text_input("Primer Nombre:")

if st.button("Ver Resultados"):
    df = cargar_datos()
    if df is not None and num and nom:
        alumno = df[df['numero_lista'] == num.strip()]
        if not alumno.empty:
            nombre_real = alumno.iloc[0]['nombre']
            if isinstance(nombre_real, str) and nom.lower().strip() in nombre_real.lower():
                row = alumno.iloc[0]
                
                # --- FEEDBACK IA ---
                mensaje = ""
                try:
                    prompt = f"Actúa como un profesor amable, no des muchos rodeos. Alumno: {nombre_real}. Nota: {row['promedio_final']} Resalta la calificación obtenida en el periodo. 
                    Motívalo brevemente, una buena calificación va de 85 para arriba, una calificación media de 70 a 85 y una calificación mala de 70 69 para abajo, aunque la aprobatoria 
                    es 60 hay que motivarlos. Firma como 'Atentamente: Marco'."
                    with st.spinner('Analizando desempeño...'):
                        response = model.generate_content(prompt)
                        mensaje = response.text
                except Exception as e:
                    mensaje = f"Buen esfuerzo. (El sistema de IA está descansando: {str(e)})"

                st.success(f"Alumno: {nombre_real}")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Part (20%)", row['participacion'])
                c2.metric("Tareas (30%)", row['tareas'])
                c3.metric("Proy (15%)", row['proyecto'])
                c4.metric("Examen (35%)", row['examen'])
                st.markdown("---")
                st.metric("🎓 FINAL", row['promedio_final'])
                st.info(f"**Comentario del Profe:** {mensaje}")
            else:
                st.error("Nombre incorrecto.")
        else:
            st.error("Lista no encontrada.")



