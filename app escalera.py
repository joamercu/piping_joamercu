import streamlit as st
from modules.costos_materiales import calcular_costos_materiales
from modules.costos_mano_obra import calcular_costos_mano_obra
from modules.costos_totales import calcular_costo_total
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Calculadora Escaleras Metálicas", page_icon="🛠️", layout="centered")
st.title("🪜 Calculadora de Costos para Escaleras Metálicas")

st.sidebar.header("🔧 Parámetros del Proyecto")
longitud_escalera = st.sidebar.number_input("📏 Longitud total de la escalera (m)", min_value=0.1, value=10.0)
tiempo_entrega = st.sidebar.number_input("⏱️ Tiempo de entrega (días)", min_value=1, value=7)

st.markdown("### 💰 Costos de Materia Prima (por metro lineal)")
col1, col2 = st.columns(2)
with col1:
    precio_escalon = st.number_input("🪚 Escalones metálicos (COP/m)", value=150000)
    precio_pasamanos = st.number_input("🪤 Pasamanos metálico (COP/m)", value=46000)
with col2:
    precio_baranda = st.number_input("🧱 Barandas metálicas (COP/m)", value=50000)
    precio_antideslizante = st.number_input("🟫 Antideslizante (COP/m)", value=20000)

st.markdown("### 🛠️ Costos de Fabricación")
col3, col4 = st.columns(2)
with col3:
    precio_consumibles = st.number_input("🔩 Consumibles metalmecánica (COP/m)", value=25000)
with col4:
    horas_hombre = st.number_input("👷‍♂️ Horas hombre requeridas", min_value=1, value=8)
    costo_hora_hombre = st.number_input("💼 Costo hora hombre (COP)", min_value=10000, value=20000)

# Calcular y mostrar resultados
if st.button("🧮 Calcular presupuesto total"):
    materiales = calcular_costos_materiales(
        longitud_escalera, precio_escalon, precio_baranda, precio_pasamanos, precio_antideslizante
    )
    mano_obra = calcular_costos_mano_obra(
        longitud_escalera, precio_consumibles, horas_hombre, costo_hora_hombre
    )
    total = calcular_costo_total(materiales, mano_obra, tiempo_entrega)

    st.markdown("### 📊 **Resumen de Costos**")
    st.write("#### 🧱 Materiales")
    st.table(materiales)
    st.write("#### 🧰 Fabricación")
    st.table(mano_obra)
    st.write("#### 🚚 Logística y Total")
    st.table(total)

    st.success(f"💵 **Costo Total del Proyecto:** ${total['Costo Total Proyecto (COP)']:,.2f} COP")

    # Exportar a Excel
    def exportar_excel(materiales, mano_obra, total):
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='openpyxl')

        pd.DataFrame.from_dict(materiales, orient='index', columns=["Costo"]).to_excel(writer, sheet_name="Materiales")
        pd.DataFrame.from_dict(mano_obra, orient='index', columns=["Costo"]).to_excel(writer, sheet_name="Fabricación")
        pd.DataFrame.from_dict(total, orient='index', columns=["Costo"]).to_excel(writer, sheet_name="Resumen Total")

        writer.close()
        output.seek(0)
        return output

    excel_bytes = exportar_excel(materiales, mano_obra, total)

    st.download_button(
        label="📥 Descargar Excel con el Presupuesto",
        data=excel_bytes,
        file_name="Presupuesto_Escaleras.xlsx",
        mime