import math
import streamlit as st

st.set_page_config(page_title="Belt Drive Transmission Design Checker", page_icon="⚙️", layout="wide")

st.title("⚙️ Belt Drive Transmission Design Checker")
st.caption("Flat Belt / V-Belt — angle of lap, belt length, speed ratio and maximum power before slipping")

st.subheader("Input Parameters")
c1, c2 = st.columns(2)
with c1:
    belt_type = st.selectbox("Belt Type", ["Flat Belt", "V-Belt"])
    D1 = st.number_input("Driver Pulley Diameter D₁ (mm)", min_value=0.01, value=200.0, step=1.0)
    D2 = st.number_input("Follower Pulley Diameter D₂ (mm)", min_value=0.01, value=400.0, step=1.0)
    N1 = st.number_input("Driver Speed N₁ (RPM)", min_value=0.01, value=1440.0, step=10.0)
    C = st.number_input("Centre Distance C (mm)", min_value=0.01, value=1000.0, step=10.0)
with c2:
    mu = st.number_input("Coefficient of Friction μ", min_value=0.0001, value=0.30, step=0.01, format="%.4f")
    T = st.number_input("Maximum Belt Tension T (N)", min_value=0.01, value=1000.0, step=10.0)
    m = st.number_input("Belt Mass per Unit Length m (kg/m)", min_value=0.0, value=0.50, step=0.05)
    groove_angle = st.number_input("V-Belt Groove Angle (degrees)", min_value=0.1, max_value=179.9, value=40.0, step=1.0, disabled=(belt_type == "Flat Belt"))

def calculate_belt_drive(D1, D2, N1, C, mu, T, m, groove_angle, belt_type):
    if D1 <= 0 or D2 <= 0 or N1 <= 0 or C <= 0: raise ValueError("Pulley diameters, RPM and centre distance must be positive.")
    if mu <= 0: raise ValueError("Coefficient of friction must be positive.")
    if T <= 0: raise ValueError("Maximum belt tension must be positive.")
    if m < 0: raise ValueError("Belt mass per unit length cannot be negative.")
    if belt_type == "V-Belt" and not (0 < groove_angle < 180): raise ValueError("V-Belt groove angle must be between 0° and 180°.")
    x = (D2 - D1) / (2 * C)
    if abs(x) > 1: raise ValueError("Invalid geometry: |(D₂ − D₁)/(2C)| must be ≤ 1.")
    theta = math.pi - 2 * math.asin(x)
    L = math.pi / 2 * (D1 + D2) + 2 * C + (D2 - D1) ** 2 / (4 * C)
    speed_ratio = D1 / D2
    N2 = N1 * D1 / D2
    v = math.pi * (D1 / 1000) * N1 / 60
    Tc = m * v ** 2
    if T <= Tc: raise ValueError(f"Maximum belt tension T = {T:.3f} N must be greater than centrifugal tension Tc = {Tc:.3f} N.")
    if belt_type == "Flat Belt":
        tension_ratio = math.exp(mu * theta)
    else:
        tension_ratio = math.exp((mu * theta) / math.sin(math.radians(groove_angle / 2)))
    T1 = T - Tc
    T2 = T1 / tension_ratio
    power_kw = (T1 - T2) * v / 1000
    return theta, L, speed_ratio, N2, v, Tc, T1, T2, power_kw


def show_3d_pulley_diagram(D1, D2, C, belt_type):
    import plotly.graph_objects as go

    r1 = D1 / 2
    r2 = D2 / 2
    x1, x2 = 0.0, C
    zc = 0.0

    # Scale the drawing so very different pulley diameters remain visible.
    scale = max(C, D1, D2, 1.0)
    s = 1.0 / scale

    fig = go.Figure()

    def add_pulley(x, radius, label):
        # Pulley disc
        u = [2 * math.pi * i / 80 for i in range(81)]
        y = [radius * math.cos(a) * s for a in u]
        z = [radius * math.sin(a) * s for a in u]
        fig.add_trace(go.Scatter3d(
            x=[x*s] * len(u), y=y, z=z,
            mode="lines",
            line=dict(width=12),
            name=label,
            showlegend=False
        ))
        # Hub
        hub_r = radius * 0.14
        fig.add_trace(go.Scatter3d(
            x=[x*s] * len(u),
            y=[hub_r * math.cos(a) * s for a in u],
            z=[hub_r * math.sin(a) * s for a in u],
            mode="lines",
            line=dict(width=9),
            showlegend=False
        ))
        fig.add_annotation(
            x=x*s, y=0, z=radius*s*1.12,
            text=f"<b>{label}</b><br>Ø {2*radius:.0f} mm",
            showarrow=False
        )

    add_pulley(x1, r1, "Driver")
    add_pulley(x2, r2, "Follower")

    # Two straight belt runs (schematic, tangent approximation).
    top1 = r1 * s
    top2 = r2 * s
    bottom1 = -r1 * s
    bottom2 = -r2 * s

    fig.add_trace(go.Scatter3d(
        x=[x1*s, x2*s], y=[0, 0], z=[top1, top2],
        mode="lines", line=dict(width=12), name="Belt", showlegend=False
    ))
    fig.add_trace(go.Scatter3d(
        x=[x1*s, x2*s], y=[0, 0], z=[bottom1, bottom2],
        mode="lines", line=dict(width=12), showlegend=False
    ))

    fig.update_layout(
        height=470,
        margin=dict(l=0, r=0, t=35, b=0),
        title=f"3D Belt Drive — {belt_type}",
        scene=dict(
            xaxis_title="Centre distance direction",
            yaxis_title="Pulley width",
            zaxis_title="Pulley radius",
            aspectmode="auto",
            camera=dict(eye=dict(x=1.6, y=1.5, z=1.1))
        ),
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)


if st.button("Calculate", type="primary", use_container_width=True):
    try:
        theta, L, speed_ratio, N2, v, Tc, T1, T2, power_kw = calculate_belt_drive(D1,D2,N1,C,mu,T,m,groove_angle,belt_type)
        st.success("Calculation completed successfully.")
        st.subheader("Results")
        st.table([
            {"Parameter":"Angle of Lap", "Value":f"{math.degrees(theta):.3f}°"},
            {"Parameter":"Belt Length", "Value":f"{L:.3f} mm"},
            {"Parameter":"Speed Ratio (N₂/N₁)", "Value":f"{speed_ratio:.5f}"},
            {"Parameter":"Follower Speed N₂", "Value":f"{N2:.3f} RPM"},
            {"Parameter":"Belt Speed", "Value":f"{v:.3f} m/s"},
            {"Parameter":"Centrifugal Tension", "Value":f"{Tc:.3f} N"},
            {"Parameter":"Tight-Side Effective Tension", "Value":f"{T1:.3f} N"},
            {"Parameter":"Slack-Side Tension", "Value":f"{T2:.3f} N"},
            {"Parameter":"Maximum Power Before Slip", "Value":f"{power_kw:.3f} kW"},
        ])
        st.subheader("Pulley Schematic")
        show_3d_pulley_diagram(D1, D2, C, belt_type)
        st.subheader("Formulas Used")
        formulas = ["θ = π − 2 sin⁻¹((D₂ − D₁)/(2C))", "L = π/2(D₁ + D₂) + 2C + (D₂ − D₁)²/(4C)", "N₂ = N₁ × D₁ / D₂", "v = πD₁N₁ / 60  (D₁ in metres)", "Tc = mv²"]
        if belt_type == "Flat Belt": formulas.append("T₁/T₂ = e^(μθ)")
        else: formulas.append("T₁/T₂ = e^((μθ)/sin(groove angle/2))")
        formulas.append("Power = (T₁ − T₂)v / 1000  kW")
        for f in formulas: st.code(f)
    except ValueError as e:
        st.error(str(e))
else:
    st.info("Enter the belt-drive parameters and click Calculate.")
