import streamlit as st
import pandas as pd
from io import BytesIO

from modules.costos_materiales import calcular_costos_materiales
from modules.costos_mano_obra import calcular_costos_mano_obra
from modules.costos_totales import calcular_costo_total

# Función para exportar resultados a un archivo Excel
def exportar_excel(materiales, mano_obra, total):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')

    # Guardar cada sección en una hoja diferente
    pd.DataFrame.from_dict(materiales, orient='index', columns=["Costo"]).to_excel(
        writer, sheet_name="Materiales")
    pd.DataFrame.from_dict(mano_obra, orient='index', columns=["Costo"]).to_excel(
        writer, sheet_name="Fabricación")
    pd.DataFrame.from_dict(total, orient='index', columns=["Costo"]).to_excel(
        writer, sheet_name="Resumen Total")

    writer.close()
    output.seek(0)
    return output

# Configuración de la página
st.set_page_config(
    page_title="Calculadora Escaleras Metálicas",
    page_icon="🛠️",
    layout="centered"
)

# Título principal
st.title("🪜 Calculadora de Costos para Escaleras Metálicas")
st.markdown("Llena los campos y presiona el botón para calcular y exportar tu presupuesto.")

# 👇 Parámetros del proyecto (sidebar)
st.sidebar.header("🔧 Parámetros del Proyecto")
longitud_escalera = st.sidebar.number_input(
    "📏 Longitud total de la escalera (m)", min_value=0.1, value=10.0
)
tiempo_entrega = st.sidebar.number_input(
    "⏱️ Tiempo de entrega (días)", min_value=1, value=7
)

# 💰 Costos de Materia Prima
st.markdown("### 💰 Costos de Materia Prima (por metro lineal)")
col1, col2 = st.columns(2)
with col1:
    precio_escalon = st.number_input(
        "🪚 Escalones metálicos (COP/m)", value=150000
    )
    precio_pasamanos = st.number_input(
        "🪤 Pasamanos metálico (COP/m)", value=46000
    )
with col2:
    precio_baranda = st.number_input(
        "🧱 Barandas metálicas (COP/m)", value=50000
    )
    precio_antideslizante = st.number_input(
        "🟫 Antideslizante (COP/m)", value=20000
    )

# 🛠️ Costos de Fabricación
st.markdown("### 🛠️ Costos de Fabricación")
col3, col4 = st.columns(2)
with col3:
    precio_consumibles = st.number_input(
        "🔩 Consumibles metalmecánica (COP/m)", value=25000
    )
with col4:
    horas_hombre = st.number_input(
        "👷‍♂️ Horas hombre requeridas", min_value=1, value=8
    )
    costo_hora_hombre = st.number_input(
        "💼 Costo hora hombre (COP)", min_value=10000, value=20000
    )

# Botón de cálculo y exportación
def main():
    if st.button("🧮 Calcular y exportar Excel"):
        # Cálculo de costos
        materiales = calcular_costos_materiales(
            longitud_escalera,
            precio_escalon,
            precio_baranda,
            precio_pasamanos,
            precio_antideslizante
        )
        mano_obra = calcular_costos_mano_obra(
            longitud_escalera,
            precio_consumibles,
            horas_hombre,
            costo_hora_hombre
        )
        total = calcular_costo_total(
            materiales,
            mano_obra,
            tiempo_entrega
        )

        # Mostrar resultados en pantalla
        st.markdown("### 📊 Resumen de Costos")
        st.write("#### 🧱 Materiales")
        st.table(materiales)
        st.write("#### 🧰 Fabricación")
        st.table(mano_obra)
        st.write("#### 🚚 Logística y Total")
        st.table(total)

        st.success(
            f"💵 Costo Total del Proyecto: ${total['Costo Total Proyecto (COP)']:,.2f} COP"
        )

        # Generar y descargar Excel
        excel_bytes = exportar_excel(materiales, mano_obra, total)
        st.download_button(
            label="📥 Descargar Excel con el Presupuesto",
            data=excel_bytes,
            file_name="Presupuesto_Escaleras.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

if __name__ == "__main__":
    main()
