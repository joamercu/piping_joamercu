import streamlit as st
from fpdf import FPDF
import io
import traceback

# Conversion functions
def si_to_imperial(value, unit):
    conversions = {
        'pressure': lambda x: x * 145.038,  # MPa to psi
        'length': lambda x: x / 25.4,       # mm to inches
        'stress': lambda x: x * 145.038     # MPa to psi
    }
    return conversions[unit](value)

def imperial_to_si(value, unit):
    conversions = {
        'pressure': lambda x: x / 145.038,  # psi to MPa
        'length': lambda x: x * 25.4,       # inches to mm
        'stress': lambda x: x / 145.038     # psi to MPa
    }
    return conversions[unit](value)

# Calculation functions
def calculate_pipe_thickness(P, D, S, E, Y, C):
    """
    Calculates minimum required pipe thickness according to ASME B31.3.
    P: internal pressure (MPa)
    D: outside diameter (mm)
    S: allowable stress (MPa)
    E: joint efficiency
    Y: material coefficient
    C: corrosion/fabrication tolerance (mm)
    """
    return (P * D) / (2 * (S * E + P * Y)) + C

def calculate_max_pressure(S, E, t, D, Y):
    """
    Calculates maximum allowable pressure for given thickness.
    S: allowable stress (MPa)
    E: joint efficiency
    t: thickness (mm)
    D: outside diameter (mm)
    Y: material coefficient
    """
    return (2 * S * E * t) / (D - 2 * Y * t)

# Dictionary of schedule thicknesses
schedule_thickness = {
    5: { # SCH5S
        "1/2": 1.65, "3/4": 1.65, "1": 1.65, "1 1/4": 1.65, "1 1/2": 1.65,
        "2": 1.65, "2 1/2": 2.11, "3": 2.11, "3 1/2": 2.11, "4": 2.11,
        # ... add remaining sizes
    },
    10: { # SCH10S
        "1/2": 2.11, "3/4": 2.11, "1": 2.77, "1 1/4": 2.77, "1 1/2": 2.77,
        # ... add remaining
    },
    40: { # SCH40
        "1/2": 2.77, "3/4": 2.87, "1": 3.38, "1 1/4": 3.56, "1 1/2": 3.68,
        # ... add remaining
    },
    80: { # SCH80
        "1/2": 3.73, "3/4": 3.91, "1": 4.55, "1 1/4": 4.85, "1 1/2": 5.08,
        # ... add remaining
    },
    160: { # SCH160
        "1/2": 4.78, "3/4": 5.56, "1": 6.35, "1 1/4": 6.35, "1 1/2": 7.14,
        # ... add remaining
    }
}

# Streamlit App
st.set_page_config(page_title="Calculadora de Espesor de Tubería", layout="wide")
st.title("📐 Calculadora de Espesor de Tubería según ASME B31.3")

# Sidebar Inputs
st.sidebar.header("🔧 Parámetros de Entrada")
nominal_size = st.sidebar.selectbox("Tamaño nominal (pulgadas)", list(schedule_thickness[5].keys()))
# Dynamically build schedule options for the selected nominal size
available_schedules = [f"SCH{key}" for key, sizes in schedule_thickness.items() if nominal_size in sizes and sizes[nominal_size] is not None]
schedule_sel = st.sidebar.selectbox("Schedule", available_schedules)

pressure = st.sidebar.number_input("Presión interna", min_value=0.0, value=0.0, step=0.1)
pressure_unit = st.sidebar.selectbox("Unidad de presión", ["MPa", "psi", "bar"] )

diameter = st.sidebar.number_input("Diámetro externo", min_value=0.0, value=0.0, step=0.1)
diameter_unit = st.sidebar.selectbox("Unidad de diámetro", ["mm", "inches"])

stress = st.sidebar.number_input("Esfuerzo máximo permitido", min_value=0.0, value=0.0, step=0.1)
stress_unit = st.sidebar.selectbox("Unidad de esfuerzo", ["MPa", "psi"])

efficiency = st.sidebar.number_input("Factor de eficiencia de la junta (E)", min_value=0.0, max_value=1.0, value=1.0, step=0.05)
y_coeff = st.sidebar.number_input("Coeficiente Y", min_value=0.0, value=0.4, step=0.01)

tolerance = st.sidebar.number_input("Tolerancia (C)", min_value=0.0, value=0.0, step=0.1)
tolerance_unit = st.sidebar.selectbox("Unidad de tolerancia", ["mm", "inches"])

st.sidebar.markdown("---")
st.sidebar.info("Para acero al carbono ASTM A-36, Y=0.4. Para acero inoxidable, Y puede variar de 0.3 a 0.4.")

# Show converted values
st.subheader("🔄 Conversiones de Unidades")
try:
    if pressure_unit == "MPa":
        p_imp = si_to_imperial(pressure, 'pressure')
        st.write(f"Presión: {pressure:.2f} MPa = {p_imp:.2f} psi")
    elif pressure_unit == "psi":
        p_si = imperial_to_si(pressure, 'pressure')
        st.write(f"Presión: {pressure:.2f} psi = {p_si:.2f} MPa")
    elif pressure_unit == "bar":
        p_kpa = pressure * 100  # bar to kPa
        st.write(f"Presión: {pressure:.2f} bar = {p_kpa:.2f} kPa")
except Exception:
    st.write("Presión: --")

# Calculation
if st.button("🔢 Calcular"):
    try:
        # Validate inputs
        if any(val <= 0 for val in [pressure, diameter, stress, efficiency, y_coeff]):
            st.error("Todos los valores numéricos deben ser positivos y E entre 0 y 1.")
        else:
            # Convert to SI
            P = pressure
            if pressure_unit == "psi": P = imperial_to_si(pressure, 'pressure')
            elif pressure_unit == "bar": P = pressure / 10  # bar to MPa

            D = diameter
            if diameter_unit == "inches": D = imperial_to_si(diameter, 'length')

            S = stress
            if stress_unit == "psi": S = imperial_to_si(stress, 'stress')

            C = tolerance
            if tolerance_unit == "inches": C = imperial_to_si(tolerance, 'length')

            # Schedule thickness lookup
            key = int(schedule_sel.replace("SCH", ""))
            t_sch = schedule_thickness[key].get(nominal_size)
            t_sch_imp = si_to_imperial(t_sch, 'length') if t_sch else None

            # Calculations
            t_req = calculate_pipe_thickness(P, D, S, efficiency, y_coeff, C)
            t_req_imp = si_to_imperial(t_req, 'length')
            P_max = calculate_max_pressure(S, efficiency, t_req, D, y_coeff)
            P_max_imp = si_to_imperial(P_max, 'pressure')
            P_sch_max = calculate_max_pressure(S, efficiency, t_sch, D, y_coeff) if t_sch else None
            P_sch_max_imp = si_to_imperial(P_sch_max, 'pressure') if P_sch_max else None
            fs = P_sch_max / P if P_sch_max else None

            # Display results
            st.subheader("📈 Resultados")
            st.write(f"Espesor mínimo requerido: {t_req:.2f} mm / {t_req_imp:.4f} inches")
            if t_sch:
                st.write(f"Espesor {schedule_sel}: {t_sch:.2f} mm / {t_sch_imp:.4f} inches")
                st.write(f"Factor de seguridad: {fs:.2f}")

            # Detailed procedure
            def generate_procedure_text():
                lines = []
                lines.append("=== Procedimiento de Cálculo ===")
                lines.append(f"P = {P:.2f} MPa, D = {D:.2f} mm, S = {S:.2f} MPa")
                lines.append(f"E = {efficiency:.2f}, Y = {y_coeff:.2f}, C = {C:.2f} mm")
                lines.append("")
                lines.append("1. Fórmula t = (P·D)/(2·(S·E + P·Y)) + C")
                lines.append(f"   t = ({P:.2f}·{D:.2f})/(2·({S:.2f}·{efficiency:.2f} + {P:.2f}·{y_coeff:.2f})) + {C:.2f} = {t_req:.4f} mm")
                if t_sch:
                    lines.append(f"2. Comparación con {schedule_sel}: {t_sch:.2f} mm -> {'ADECUADO' if t_req<=t_sch else 'INADECUADO'}")
                lines.append("")
                lines.append("3. P_max = (2·S·E·t)/(D - 2·Y·t)")
                lines.append(f"   P_max = {P_max:.4f} MPa / {P_max_imp:.2f} psi")
                if P_sch_max:
                    lines.append(f"4. P_max_schedule = {P_sch_max:.4f} MPa / {P_sch_max_imp:.2f} psi")
                    lines.append(f"5. Factor de seguridad = {fs:.4f}")
                return "\n".join(lines)

            with st.expander("🔍 Procedimiento Detallado"):
                st.code(generate_procedure_text())

            # PDF generation inside calculate for download later
            def build_pdf():
                buf = io.BytesIO()
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", "B", 14)
                pdf.cell(0, 10, "Calculadora de Tubería - Informe de Resultados", ln=True, align='C')
                pdf.ln(5)
                pdf.set_font("Arial", "", 10)
                pdf.cell(0, 8, f"Presión interna: {pressure:.2f} {pressure_unit}", ln=True)
                pdf.cell(0, 8, f"Diámetro externo: {diameter:.2f} {diameter_unit}", ln=True)
                pdf.cell(0, 8, f"Esfuerzo admisible: {stress:.2f} {stress_unit}", ln=True)
                pdf.cell(0, 8, f"E: {efficiency:.2f}, Y: {y_coeff:.2f}, C: {tolerance:.2f} {tolerance_unit}", ln=True)
                pdf.ln(5)
                pdf.cell(0, 8, f"Espesor requerido: {t_req:.2f} mm / {t_req_imp:.4f} in", ln=True)
                if t_sch:
                    pdf.cell(0, 8, f"Espesor {schedule_sel}: {t_sch:.2f} mm / {t_sch_imp:.4f} in", ln=True)
                    pdf.cell(0, 8, f"Factor de seguridad: {fs:.2f}", ln=True)
                pdf.add_page()
                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 10, "Procedimiento Detallado de Cálculo", ln=True)
                pdf.set_font("Arial", "", 8)
                for line in generate_procedure_text().split("\n"):
                    pdf.multi_cell(0, 5, line)
                pdf.output(buf)
                buf.seek(0)
                return buf

            pdf_buffer = build_pdf()
            st.download_button("📄 Descargar Informe PDF", data=pdf_buffer, file_name="informe_tuberia.pdf", mime="application/pdf")

    except Exception as ex:
        st.error(f"Error inesperado: {ex}")
