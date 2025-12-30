import streamlit as st
import pandas as pd
import google.generativeai as genai

# --- CONFIGURACIÓN DIRECTA ---
# Pega tu clave real aquí abajo (la que empieza con AIza...)
API_KEY = "AIzaSyAn230zYeBakpJ_EsGN4PuuXOhcRrBE5uw" 

# Configurar Gemini
if API_KEY and API_KEY.startswith("AIza"):
    genai.configure(api_key=API_KEY)
    
    # CORRECCIÓN: Usamos el modelo vigente en Diciembre 2025
    NOMBRE_DEL_MODELO = 'gemini-2.5-flash' 
    
    model = genai.GenerativeModel(NOMBRE_DEL_MODELO)
else:
    model = None

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
        
        # Mapeo de columnas de calificaciones
        def limpiar_nota(col_idx):
            if col_idx < len(df.columns):
                return pd.to_numeric(df[df.columns[col_idx]], errors='coerce').fillna(0)
            return 0.0

        df['promedio_final'] = limpiar_nota(11)
        df['participacion'] = limpiar_nota(12)
        df['tareas'] = limpiar_nota(13)
        df['proyecto'] = limpiar_nota(14)
        df['examen'] = limpiar_nota(15)
        return df
    except Exception as e:
        st.error(f"⚠️ Error CSV: {e}")
        return None

# --- INTERFAZ ---
st.set_page_config(page_title="Calificaciones Estadística", page_icon="🦁")
st.title("🦁 Consulta de Calificaciones")
st.subheader("Periodo 2: Estadística y Probabilidad")

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
                # Datos
                row = alumno.iloc[0]
                
                # --- FEEDBACK IA ---
                mensaje = ""
                try:
                    if model is None:
                         mensaje = "⚠️ Error: Falta pegar la API KEY en la línea 6."
                    else:
                        prompt = f"Actúa como un profesor amable, no des muchos rodeos. Alumno: {nombre_real}. Nota: {row['promedio_final']} Resalta la calificación obtenida en el periodo. Motívalo brevemente. Firma como 'Atentamente: Marco'."
                        response = model.generate_content(prompt)
                        mensaje = response.text
                except Exception as e:
                    mensaje = f"⚠️ Error Técnico: {str(e)}"

                # Mostrar
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




