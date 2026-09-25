
import math
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="Belt Drive Transmission Design Checker",
                   page_icon="⚙️", layout="wide")

st.markdown("""
<style>
.main {background:#f5f7fa}
.title {font-size:36px;font-weight:700;color:#17365d;text-align:center}
.subtitle {text-align:center;color:#666;font-size:17px;margin-bottom:25px}
.result-card {background:white;padding:18px;border-radius:12px;border:1px solid #ddd;
box-shadow:0 2px 8px rgba(0,0,0,.06);text-align:center;margin-bottom:12px}
.result-title{font-size:15px;color:#666}.result-value{font-size:25px;font-weight:700;color:#17365d}
.section-title{color:#17365d;font-size:23px;font-weight:700;margin-top:15px;margin-bottom:10px}
.formula{background:#eef3f8;padding:12px;border-radius:8px;border-left:4px solid #17365d;margin:8px 0}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">⚙️ Belt Drive Transmission Design Checker</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Flat Belt / V-Belt • Engineering Design & Transmission Calculator</div>', unsafe_allow_html=True)

st.sidebar.header("⚙️ Design Inputs")
belt_type = st.sidebar.selectbox("Belt Type", ["Flat Belt", "V-Belt"])
driver_d = st.sidebar.number_input("Driver Pulley Diameter (mm)", min_value=1.0, value=200.0, step=1.0)
follower_d = st.sidebar.number_input("Follower Pulley Diameter (mm)", min_value=1.0, value=400.0, step=1.0)
driver_rpm = st.sidebar.number_input("Driver Speed (RPM)", min_value=1.0, value=1440.0, step=10.0)
center_distance = st.sidebar.number_input("Centre Distance (mm)", min_value=1.0, value=1000.0, step=10.0)
mu = st.sidebar.number_input("Coefficient of Friction (μ)", min_value=0.001, value=0.30, step=0.01, format="%.3f")
belt_mass = st.sidebar.number_input("Belt Mass (kg/m)", min_value=0.001, value=0.20, step=0.01, format="%.3f")
max_tension = st.sidebar.number_input("Maximum Allowable Belt Tension (N)", min_value=1.0, value=1000.0, step=50.0)
groove_angle = 180.0 if belt_type == "Flat Belt" else st.sidebar.number_input("V-Belt Groove Angle (degrees)", min_value=10.0, max_value=60.0, value=40.0, step=1.0)

D, d, C = driver_d/1000, follower_d/1000, center_distance/1000
geometry_valid = C > abs(D-d)/2

if geometry_valid:
    alpha = math.asin(abs(D-d)/(2*C))
    theta_small = math.pi - 2*alpha
    theta_large = math.pi + 2*alpha
    belt_length = 2*C + (math.pi/2)*(D+d) + (D-d)**2/(4*C)
    speed_ratio = follower_d/driver_d
    follower_rpm = driver_rpm*speed_ratio
    belt_speed = math.pi*driver_d*driver_rpm/60000
    centrifugal_tension = belt_mass*belt_speed**2
    effective_max_tension = max_tension - centrifugal_tension
    if effective_max_tension > 0:
        if belt_type == "Flat Belt":
            tension_ratio = math.exp(mu*theta_small)
        else:
            tension_ratio = math.exp(mu*theta_small/math.sin(math.radians(groove_angle)/2))
        T1 = effective_max_tension
        T2 = T1/tension_ratio
        power_watts = (T1-T2)*belt_speed
        power_kw = power_watts/1000
    else:
        tension_ratio=T1=T2=power_watts=power_kw=0
else:
    alpha=theta_small=theta_large=belt_length=speed_ratio=follower_rpm=belt_speed=centrifugal_tension=effective_max_tension=tension_ratio=T1=T2=power_watts=power_kw=0

if not geometry_valid:
    st.error("Invalid geometry: Centre distance must be greater than |Driver Diameter − Follower Diameter| / 2.")
else:
    st.markdown('<div class="section-title">📊 Design Results</div>', unsafe_allow_html=True)
    cols=st.columns(3)
    vals=[("Angle of Lap – Small Pulley",f"{math.degrees(theta_small):.2f}°"),
          ("Belt Length",f"{belt_length:.3f} m"),("Speed Ratio",f"{speed_ratio:.3f}")]
    for c,(t,v) in zip(cols,vals):
        with c: st.markdown(f'<div class="result-card"><div class="result-title">{t}</div><div class="result-value">{v}</div></div>',unsafe_allow_html=True)
    cols=st.columns(3)
    vals=[("Follower Speed",f"{follower_rpm:.1f} RPM"),("Belt Speed",f"{belt_speed:.3f} m/s"),("Maximum Power",f"{power_kw:.3f} kW")]
    for c,(t,v) in zip(cols,vals):
        with c: st.markdown(f'<div class="result-card"><div class="result-title">{t}</div><div class="result-value">{v}</div></div>',unsafe_allow_html=True)

    st.markdown('<div class="section-title">🔩 Belt Tension Analysis</div>',unsafe_allow_html=True)
    a,b,c=st.columns(3)
    a.metric("Maximum Belt Tension",f"{max_tension:.2f} N")
    b.metric("Centrifugal Tension",f"{centrifugal_tension:.2f} N")
    c.metric("Effective Tension",f"{effective_max_tension:.2f} N")
    a,b,c=st.columns(3)
    a.metric("Tight-Side Tension T₁",f"{T1:.2f} N")
    b.metric("Slack-Side Tension T₂",f"{T2:.2f} N")
    c.metric("T₁ / T₂",f"{tension_ratio:.3f}")

    st.markdown('<div class="section-title">📐 Pulley Geometry</div>',unsafe_allow_html=True)
    a,b,c=st.columns(3)
    a.metric("Small Pulley Lap Angle",f"{math.degrees(theta_small):.2f}°")
    b.metric("Large Pulley Lap Angle",f"{math.degrees(theta_large):.2f}°")
    c.metric("Centre Distance",f"{center_distance:.1f} mm")

    st.markdown('<div class="section-title">🎥 Interactive 3D Belt Drive Diagram</div>', unsafe_allow_html=True)

    # Scale the engineering dimensions into a convenient 3D scene.
    scene_scale = max(D, d, C, 1e-9)
    R1 = (D / 2) / scene_scale
    R2 = (d / 2) / scene_scale
    C3 = C / scene_scale

    # Pulley centers lie along the X axis; pulleys rotate about Y.
    x1, x2 = 0.0, C3
    y0, z0 = 0.0, 0.0

    fig3d = go.Figure()

    # Pulley meshes (thin cylinders).
    for x, r, label in [(x1, R1, "Driver Pulley"), (x2, R2, "Follower Pulley")]:
        fig3d.add_trace(go.Mesh3d(
            x=[x-r, x-r, x-r, x-r, x+r, x+r, x+r, x+r],
            y=[-r, -r, r, r, -r, -r, r, r],
            z=[-0.12*r, 0.12*r, -0.12*r, 0.12*r, -0.12*r, 0.12*r, -0.12*r, 0.12*r],
            i=[0, 0, 0, 4, 4, 4, 0, 1, 2, 3],
            j=[1, 2, 4, 5, 6, 7, 4, 5, 6, 7],
            k=[2, 3, 5, 6, 7, 4, 5, 6, 7, 4],
            name=label,
            opacity=0.85,
            hovertemplate=f"{label}<br>Diameter: %{r*2:.3f} (scaled)<extra></extra>"
        ))

        # Pulley rim as a circle in the X-Z plane.
        ang = [2*math.pi*i/100 for i in range(101)]
        fig3d.add_trace(go.Scatter3d(
            x=[x + 0*math.cos(a) for a in ang],
            y=[0 for _ in ang],
            z=[r*math.sin(a) for a in ang],
            mode="lines",
            line=dict(width=7),
            name=f"{label} rim",
            showlegend=False
        ))

    # Open belt: tangent-like upper/lower runs plus semicircular ends.
    # This is a visualization of the calculated open-belt geometry.
    if C3 > abs(R1-R2):
        alpha3 = math.asin(abs(R1-R2)/C3)

        # Upper/lower tangent points.
        t1x = x1 + R1*math.sin(alpha3)
        t1z = R1*math.cos(alpha3)
        t2x = x2 + R2*math.sin(alpha3)
        t2z = R2*math.cos(alpha3)

        belt_x = [t1x, t2x]
        belt_z = [t1z, t2z]

        # Upper straight run.
        fig3d.add_trace(go.Scatter3d(
            x=belt_x, y=[0.0, 0.0], z=belt_z,
            mode="lines", line=dict(width=10),
            name="Belt", showlegend=True
        ))
        # Lower straight run.
        fig3d.add_trace(go.Scatter3d(
            x=[t1x, t2x], y=[0.0, 0.0], z=[-t1z, -t2z],
            mode="lines", line=dict(width=10),
            name="Belt return", showlegend=False
        ))

        # Arc around each pulley.
        a1 = [(-math.pi/2-alpha3) + (math.pi+2*alpha3)*i/80 for i in range(81)]
        a2 = [(math.pi/2+alpha3) + (math.pi-2*alpha3)*i/80 for i in range(81)]

        fig3d.add_trace(go.Scatter3d(
            x=[x1 + R1*math.cos(a) for a in a1],
            y=[0]*len(a1),
            z=[R1*math.sin(a) for a in a1],
            mode="lines", line=dict(width=10),
            name="Driver belt arc", showlegend=False
        ))
        fig3d.add_trace(go.Scatter3d(
            x=[x2 + R2*math.cos(a) for a in a2],
            y=[0]*len(a2),
            z=[R2*math.sin(a) for a in a2],
            mode="lines", line=dict(width=10),
            name="Follower belt arc", showlegend=False
        ))

    # Shaft centerlines.
    fig3d.add_trace(go.Scatter3d(
        x=[x1, x1], y=[-0.35*R1, 0.35*R1], z=[0, 0],
        mode="lines", line=dict(width=5), name="Driver shaft", showlegend=False
    ))
    fig3d.add_trace(go.Scatter3d(
        x=[x2, x2], y=[-0.35*R2, 0.35*R2], z=[0, 0],
        mode="lines", line=dict(width=5), name="Follower shaft", showlegend=False
    ))

    fig3d.update_layout(
        height=650,
        margin=dict(l=0, r=0, t=35, b=0),
        scene=dict(
            xaxis_title="Centre distance direction",
            yaxis_title="Pulley width",
            zaxis_title="Pulley radius direction",
            aspectmode="data",
            camera=dict(eye=dict(x=1.8, y=1.5, z=1.2))
        ),
        legend=dict(orientation="h", y=1.02, x=0)
    )

    st.plotly_chart(fig3d, use_container_width=True, config={
        "displaylogo": False,
        "scrollZoom": True
    })

    st.caption(
        f"3D geometry is driven by the current inputs: driver Ø {driver_d:.1f} mm, "
        f"follower Ø {follower_d:.1f} mm, and centre distance {center_distance:.1f} mm."
    )

    st.markdown('<div class="section-title">🧮 Calculation Details</div>',unsafe_allow_html=True)
    st.latex(r"\theta = \pi - 2\sin^{-1}\left(\frac{|D-d|}{2C}\right)")
    st.write(f"Small pulley angle of lap = **{math.degrees(theta_small):.2f}°**")
    st.latex(r"L=2C+\frac{\pi}{2}(D+d)+\frac{(D-d)^2}{4C}")
    st.write(f"Belt length = **{belt_length:.3f} m**")
    st.latex(r"\frac{N_2}{N_1}=\frac{D_1}{D_2}")
    st.write(f"Follower speed = **{follower_rpm:.2f} RPM**")
    if belt_type=="Flat Belt":
        st.latex(r"\frac{T_1}{T_2}=e^{\mu\theta}")
    else:
        st.latex(r"\frac{T_1}{T_2}=e^{\mu\theta/\sin(\beta/2)}")
    st.write(f"Tension ratio = **{tension_ratio:.3f}**")
    st.latex(r"P=(T_1-T_2)v")
    st.write(f"Maximum power before slipping = **{power_kw:.3f} kW**")

    st.markdown('<div class="section-title">📋 Design Summary</div>',unsafe_allow_html=True)
    import pandas as pd
    df=pd.DataFrame({
        "Parameter":["Belt Type","Driver Diameter","Follower Diameter","Driver Speed","Follower Speed",
                     "Centre Distance","Coefficient of Friction","Angle of Lap","Belt Length","Belt Speed",
                     "Centrifugal Tension","Tight-Side Tension","Slack-Side Tension","T₁/T₂","Maximum Power"],
        "Value":[belt_type,f"{driver_d:.2f} mm",f"{follower_d:.2f} mm",f"{driver_rpm:.2f} RPM",
                 f"{follower_rpm:.2f} RPM",f"{center_distance:.2f} mm",f"{mu:.3f}",
                 f"{math.degrees(theta_small):.2f}°",f"{belt_length:.3f} m",f"{belt_speed:.3f} m/s",
                 f"{centrifugal_tension:.2f} N",f"{T1:.2f} N",f"{T2:.2f} N",f"{tension_ratio:.3f}",f"{power_kw:.3f} kW"]})
    st.dataframe(df,use_container_width=True,hide_index=True)
    st.info("Engineering calculator using standard open-belt geometry and tension-ratio relations. Verify final designs against applicable belt manufacturer data and safety factors.")

st.markdown("---")
st.markdown("<div style='text-align:center;color:#777'>Belt Drive Transmission Design Checker | Streamlit</div>",unsafe_allow_html=True)
