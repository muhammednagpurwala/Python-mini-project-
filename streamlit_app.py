import math
import streamlit as st

st.set_page_config(
    page_title="Belt Drive Transmission Design Checker",
    page_icon="⚙️",
    layout="wide",
)

st.markdown("""
<style>
body { background-color: #f4f6f8; }
.block-container { max-width: 1000px; padding-top: 2rem; }
.card {
    background: white; padding: 1.25rem; border-radius: 12px;
    box-shadow: 0 3px 12px rgba(0,0,0,.08); margin-bottom: 1rem;
}
.result-table { width:100%; border-collapse:collapse; }
.result-table th,.result-table td {
    padding:10px; border-bottom:1px solid #ddd; text-align:left;
}
.result-table th { background:#f0f0f0; }
.formula {
    background:#f7f7f7; padding:10px; border-radius:7px;
    margin:8px 0; font-family:monospace; overflow:auto;
}
</style>
""", unsafe_allow_html=True)

st.title("Belt Drive Transmission Design Checker")
st.markdown("<p style='text-align:center;color:#666;'>Flat Belt / V-Belt Design Calculator</p>",
            unsafe_allow_html=True)

with st.container():
    st.subheader("Input Parameters")
    c1, c2 = st.columns(2)

    with c1:
        belt_type = st.selectbox("Belt Type", ["Flat Belt", "V-Belt"])
        D1 = st.number_input("Driver Pulley Diameter (mm)", min_value=0.0, value=200.0)
        D2 = st.number_input("Follower Pulley Diameter (mm)", min_value=0.0, value=400.0)
        N1 = st.number_input("Driver Speed (RPM)", min_value=0.0, value=1440.0)
        C = st.number_input("Centre Distance (mm)", min_value=0.0, value=800.0)

    with c2:
        mu = st.number_input("Coefficient of Friction (μ)", min_value=0.0, value=0.30, step=0.01)
        T = st.number_input("Maximum Belt Tension (N)", min_value=0.0, value=1000.0)
        m = st.number_input("Belt Mass per Unit Length (kg/m)", min_value=0.0, value=0.80, step=0.01)
        groove = 40.0
        if belt_type == "V-Belt":
            groove = st.number_input("V-Belt Groove Angle (degrees)",
                                     min_value=1.0, max_value=179.0, value=40.0)

    calculate = st.button("Calculate", type="primary", use_container_width=True)

if calculate:
    errors = []

    if D1 <= 0 or D2 <= 0:
        errors.append("Pulley diameters must be greater than zero.")
    if N1 <= 0:
        errors.append("Driver RPM must be greater than zero.")
    if C <= 0:
        errors.append("Centre distance must be greater than zero.")
    if mu <= 0:
        errors.append("Coefficient of friction must be greater than zero.")
    if T <= 0:
        errors.append("Maximum belt tension must be greater than zero.")
    if m < 0:
        errors.append("Belt mass cannot be negative.")

    if belt_type == "V-Belt" and not (0 < groove < 180):
        errors.append("V-belt groove angle must be between 0° and 180°.")

    if not errors:
        small, large = min(D1, D2), max(D1, D2)
        a = (large - small) / (2 * C)

        if abs(a) > 1:
            errors.append("Invalid geometry: centre distance is too small.")

    if errors:
        for e in errors:
            st.error(e)
    else:
        theta = math.pi - 2 * math.asin(a)
        belt_length = (
            math.pi / 2 * (D1 + D2)
            + 2 * C
            + (D2 - D1) ** 2 / (4 * C)
        )
        ratio = D2 / D1
        N2 = N1 * D1 / D2
        v = math.pi * (D1 / 1000) * N1 / 60
        Tc = m * v * v

        if T <= Tc:
            st.error("Maximum belt tension must be greater than centrifugal tension.")
        else:
            T1 = T - Tc

            if belt_type == "Flat Belt":
                tension_ratio = math.exp(mu * theta)
            else:
                tension_ratio = math.exp(
                    (mu * theta) / math.sin(math.radians(groove) / 2)
                )

            T2 = T1 / tension_ratio
            power = (T1 - T2) * v / 1000

            st.success("Calculation completed successfully.")

            results = [
                ("Angle of Lap", f"{math.degrees(theta):.2f}", "degrees"),
                ("Belt Length", f"{belt_length:.2f}", "mm"),
                ("Speed Ratio", f"{ratio:.3f}", "—"),
                ("Follower Speed", f"{N2:.2f}", "RPM"),
                ("Belt Speed", f"{v:.3f}", "m/s"),
                ("Centrifugal Tension", f"{Tc:.2f}", "N"),
                ("Tight-Side Effective Tension", f"{T1:.2f}", "N"),
                ("Slack-Side Tension", f"{T2:.2f}", "N"),
                ("Maximum Power Before Slip", f"{power:.3f}", "kW"),
            ]

            st.subheader("Results")
            st.table({
                "Parameter": [r[0] for r in results],
                "Result": [r[1] for r in results],
                "Unit": [r[2] for r in results],
            })

            # Simple schematic using Streamlit HTML/CSS.
            st.subheader("3D Belt Drive Diagram")
            st.caption("Interactive-style schematic — pulley sizes follow your inputs.")
            s1 = max(145, min(245, D1 * min(1, 300 / max(D1, D2))))
            s2 = max(145, min(245, D2 * min(1, 300 / max(D1, D2))))

            st.markdown(f"""
            <div style="
                display:flex;justify-content:center;align-items:center;
                min-height:300px;border-radius:10px;
                background:linear-gradient(145deg,#eef1f4,#dfe4e8);
                overflow:hidden;">
              <div style="display:flex;align-items:center;gap:70px;">
                <div style="width:{s1}px;height:{s1}px;border-radius:50%;
                    background:radial-gradient(circle at 38% 34%,#fafafa 0 9%,#9aa1a8 10% 13%,#42484e 14% 20%,#c9ced2 21% 32%,#555b61 33% 39%,#aeb4b9 40% 70%,#353a3e 71% 100%);
                    border:5px solid #2d3237;display:flex;align-items:center;
                    justify-content:center;color:white;font-weight:bold;
                    text-shadow:0 1px 3px #000;">Driver</div>
                <div style="font-size:42px;font-weight:bold;">↻</div>
                <div style="width:{s2}px;height:{s2}px;border-radius:50%;
                    background:radial-gradient(circle at 38% 34%,#fafafa 0 9%,#9aa1a8 10% 13%,#42484e 14% 20%,#c9ced2 21% 32%,#555b61 33% 39%,#aeb4b9 40% 70%,#353a3e 71% 100%);
                    border:5px solid #2d3237;display:flex;align-items:center;
                    justify-content:center;color:white;font-weight:bold;
                    text-shadow:0 1px 3px #000;">Follower</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

st.subheader("Formulas Used")
formulas = [
    "θ = π − 2 sin⁻¹((D₂ − D₁)/(2C))",
    "L = π/2(D₁ + D₂) + 2C + (D₂ − D₁)²/(4C)",
    "N₂ = N₁ × D₁ / D₂",
    "v = πD₁N₁ / 60",
    "T₁/T₂ = e^(μθ)",
    "Tᶜ = mv²",
    "P = (T₁ − T₂)v",
]
for f in formulas:
    st.markdown(f"<div class='formula'>{f}</div>", unsafe_allow_html=True)
