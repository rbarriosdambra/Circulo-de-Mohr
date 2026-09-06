
import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Aplicación Círculo de Mohr",
    layout="wide"
)

st.markdown("""
<style>
    .block-container {
        padding-top: 0.7rem;
        padding-bottom: 0.5rem;
        max-width: 1550px;
    }

    h1 { margin-bottom: 0.12rem !important; }

    [data-testid="stSidebar"] .block-container {
        padding-top: 0.7rem;
    }

    /* Campos de entrada más compactos */
    [data-testid="stNumberInput"] input {
        font-size: 0.95rem !important;
        min-height: 2.25rem !important;
        padding-top: 0.25rem !important;
        padding-bottom: 0.25rem !important;
    }

    /* Adaptación específica para celular */
    @media (max-width: 768px) {
        .block-container {
            padding-left: 0.55rem;
            padding-right: 0.55rem;
            padding-top: 0.45rem;
        }

        h1 {
            font-size: 1.75rem !important;
            line-height: 1.15 !important;
        }

        [data-testid="stSidebar"] {
            min-width: 260px !important;
            max-width: 285px !important;
        }

        [data-testid="stSidebar"] h2 {
            font-size: 1.15rem !important;
        }

        [data-testid="stNumberInput"] label,
        [data-testid="stSlider"] label {
            font-size: 0.88rem !important;
        }

        [data-testid="stNumberInput"] input {
            font-size: 0.88rem !important;
            min-height: 2.0rem !important;
        }

        /* Evita márgenes excesivos alrededor de gráficos */
        [data-testid="stImage"] img,
        [data-testid="stPlotlyChart"],
        [data-testid="stPyplotGlobalUse"] {
            width: 100% !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# FUNCIONES DE CÁLCULO
# ============================================================

def stress_transform(sx, sy, txy, alpha_deg):
    a = math.radians(alpha_deg)
    sm = 0.5 * (sx + sy)
    d = 0.5 * (sx - sy)

    sa = sm + d * math.cos(2*a) - txy * math.sin(2*a)
    ta = d * math.sin(2*a) + txy * math.cos(2*a)
    return sa, ta


def principal_data(sx, sy, txy):
    sm = 0.5 * (sx + sy)
    R = math.sqrt((0.5 * (sx - sy))**2 + txy**2)

    smax = sm + R
    smin = sm - R

    two_as = math.atan2(-2.0 * txy, sx - sy)
    a1 = 0.5 * math.degrees(two_as)
    a2 = a1 + 90.0

    s1, _ = stress_transform(sx, sy, txy, a1)
    s2, _ = stress_transform(sx, sy, txy, a2)

    if s1 >= s2:
        a_smax, a_smin = a1, a2
    else:
        a_smax, a_smin = a2, a1

    return sm, R, smax, smin, a_smax, a_smin


def shear_data(sx, sy, txy):
    _, R, _, _, _, _ = principal_data(sx, sy, txy)

    taumax = R
    taumin = -R

    two_at = math.atan2(sx - sy, 2.0 * txy)
    a1 = 0.5 * math.degrees(two_at)
    a2 = a1 + 90.0

    _, t1 = stress_transform(sx, sy, txy, a1)
    _, t2 = stress_transform(sx, sy, txy, a2)

    if t1 >= t2:
        a_tmax, a_tmin = a1, a2
    else:
        a_tmax, a_tmin = a2, a1

    return taumax, taumin, a_tmax, a_tmin


def place_nonoverlap_labels(ax, labels, center_x):
    left_labels = []
    right_labels = []

    for item in labels:
        side = item.get("side")
        if side is None:
            side = "right" if item["xy"][0] >= center_x else "left"

        if side == "right":
            right_labels.append(item)
        else:
            left_labels.append(item)

    def draw_group(group, side):
        if not group:
            return

        group.sort(key=lambda it: it["xy"][1], reverse=True)
        n = len(group)
        y_fracs = [0.88] if n == 1 else np.linspace(0.91, 0.10, n)

        if side == "right":
            x_frac = 0.965
            ha = "right"
        else:
            x_frac = 0.035
            ha = "left"

        for item, yf in zip(group, y_fracs):
            ax.annotate(
                item["text"],
                xy=item["xy"],
                xycoords="data",
                xytext=(x_frac, float(yf)),
                textcoords="axes fraction",
                ha=ha,
                va="center",
                fontsize=8.2,
                color=item["color"],
                bbox=dict(
                    boxstyle="round,pad=0.22",
                    fc="white",
                    ec=item["color"],
                    alpha=0.90,
                    linewidth=0.7
                ),
                arrowprops=dict(
                    arrowstyle="-",
                    color=item["color"],
                    linewidth=0.8,
                    alpha=0.75
                ),
                annotation_clip=False,
                zorder=20
            )

    draw_group(left_labels, "left")
    draw_group(right_labels, "right")


def vec(ax, p, v, color="blue"):
    p = np.array(p, dtype=float)
    v = np.array(v, dtype=float)

    if np.linalg.norm(v) < 1e-12:
        return p

    ax.arrow(
        p[0], p[1], v[0], v[1],
        head_width=0.065,
        head_length=0.095,
        length_includes_head=True,
        linewidth=1.4,
        color=color
    )
    return p + v


def draw_element(ax, sx, sy, txy, alpha, sa, ta):
    ax.set_title("Elemento diferencial rotado", fontsize=10.5)
    ax.set_aspect("equal")
    ax.axis("off")

    h = 1.0
    corners = np.array([
        [-h, -h],
        [ h, -h],
        [ h,  h],
        [-h,  h],
        [-h, -h]
    ], dtype=float)

    ang = math.radians(alpha)

    Rm = np.array([
        [math.cos(ang), -math.sin(ang)],
        [math.sin(ang),  math.cos(ang)]
    ])

    rc = corners @ Rm.T
    ax.plot(rc[:, 0], rc[:, 1], color="black", linewidth=2)

    # ejes globales
    ax.arrow(
        -1.72, -1.57, 0.72, 0,
        head_width=0.07,
        length_includes_head=True,
        color="black"
    )
    ax.text(-0.94, -1.66, "x")

    ax.arrow(
        -1.72, -1.57, 0, 0.72,
        head_width=0.07,
        length_includes_head=True,
        color="black"
    )
    ax.text(-1.82, -0.78, "y")

    sb, tb = stress_transform(sx, sy, txy, alpha + 90.0)

    maxv = max(
        abs(sx), abs(sy), abs(txy),
        abs(sa), abs(ta), abs(sb), abs(tb), 1.0
    )

    scale = 0.70 / maxv

    ex = Rm @ np.array([1.0, 0.0])
    ey = Rm @ np.array([0.0, 1.0])

    gap = 0.20
    elem_labels = []

    # Cara derecha (+x')
    q_sigma = vec(ax, ex*h, ex*(sa*scale))
    q_tau = vec(ax, ex*(h+gap), -ey*(ta*scale))
    elem_labels.append((q_sigma, f"σ = {sa:.3g}", "blue"))
    elem_labels.append((q_tau, f"τ = {ta:.3g}", "blue"))

    # Cara izquierda (-x')
    vec(ax, -ex*h, -ex*(sa*scale))
    vec(ax, -ex*(h+gap), ey*(ta*scale))

    # Cara superior (+y')
    q_sigma90 = vec(ax, ey*h, ey*(sb*scale))
    q_tau90 = vec(ax, ey*(h+gap), ex*(tb*scale))
    elem_labels.append((q_sigma90, f"σ90 = {sb:.3g}", "blue"))
    elem_labels.append((q_tau90, f"τ90 = {tb:.3g}", "blue"))

    # Cara inferior (-y')
    vec(ax, -ey*h, -ey*(sb*scale))
    vec(ax, -ey*(h+gap), -ex*(tb*scale))

    # vertical de referencia
    ax.plot([0, 0], [0, 1.68], linestyle="--", linewidth=1, color="gray")

    # arco alfa
    rr = 1.46
    angs = np.linspace(
        math.pi / 2,
        math.pi / 2 + math.radians(alpha),
        200
    )
    ax.plot(
        rr * np.cos(angs),
        rr * np.sin(angs),
        color="purple",
        linewidth=1.2
    )
    ax.text(0.08, 1.53, f"α={alpha:.1f}°", color="purple")

    # leyendas visibles dentro del gráfico
    y_positions = [0.76, 0.61, 0.46, 0.31]

    for (q, label, color), yf in zip(elem_labels, y_positions):
        ax.annotate(
            label,
            xy=(q[0], q[1]),
            xycoords="data",
            xytext=(0.94, yf),
            textcoords="axes fraction",
            ha="right",
            va="center",
            fontsize=8.0,
            color=color,
            bbox=dict(
                boxstyle="round,pad=0.18",
                fc="white",
                ec=color,
                alpha=0.92,
                linewidth=0.7
            ),
            arrowprops=dict(
                arrowstyle="-",
                color=color,
                linewidth=0.8,
                alpha=0.75
            ),
            annotation_clip=True,
            zorder=20
        )

    ax.set_xlim(-2.30, 2.85)
    ax.set_ylim(-2.10, 2.10)


# ============================================================
# INTERFAZ WEB
# ============================================================

st.title("Aplicación Círculo de Mohr")

st.caption(
    "Convención: σ positiva = tracción. "
    "τxy positiva = tendencia de giro horario. "
    "τyx = −τxy. "
    "α positivo medido desde la vertical en sentido antihorario."
)

with st.sidebar:
    st.header("Datos de entrada")

    sx = st.number_input("σx", value=100.0, step=1.0, format="%.4f")
    sy = st.number_input("σy", value=20.0, step=1.0, format="%.4f")
    txy = st.number_input("τxy", value=30.0, step=1.0, format="%.4f")

    st.divider()

    alpha = st.slider(
        "Ángulo α (°)",
        min_value=0.0,
        max_value=360.0,
        value=0.0,
        step=1.0
    )

tyx = -txy

sm, R, smax, smin, a_smax, a_smin = principal_data(sx, sy, txy)
taumax, taumin, a_tmax, a_tmin = shear_data(sx, sy, txy)

sa, ta = stress_transform(sx, sy, txy, alpha)
sa90, ta90 = stress_transform(sx, sy, txy, alpha + 90.0)

X = np.array([sx, txy])
Y = np.array([sy, tyx])
C = np.array([sm, 0.0])

# Punto principal P según construcción geométrica solicitada:
P = np.array([sx, tyx])

# ============================================================
# RESULTADOS
# ============================================================

st.markdown(
    f"""
    <style>
        .mohr-metrics {{
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 0.55rem;
            margin: 0.15rem 0 0.45rem 0;
        }}

        .mohr-metric-card {{
            padding: 0.30rem 0.45rem 0.28rem 0.45rem;
            border-radius: 0.45rem;
            line-height: 1.05;
        }}

        .mohr-metric-title {{
            font-size: 0.90rem;
            line-height: 1.05;
            margin: 0;
            opacity: 0.90;
        }}

        .mohr-metric-value {{
            font-size: 1.65rem;
            line-height: 1.00;
            margin: 0.10rem 0 0.08rem 0;
            font-weight: 500;
        }}

        .mohr-metric-angle {{
            font-size: 0.78rem;
            line-height: 1.00;
            margin: 0;
            opacity: 0.72;
        }}

        @media (max-width: 768px) {{
            .mohr-metrics {{
                grid-template-columns: repeat(4, minmax(0, 1fr));
                gap: 0.18rem;
                margin-top: 0.05rem;
                margin-bottom: 0.25rem;
            }}

            .mohr-metric-card {{
                padding: 0.18rem 0.10rem 0.16rem 0.10rem;
            }}

            .mohr-metric-title {{
                font-size: 0.68rem;
                line-height: 1.0;
            }}

            .mohr-metric-value {{
                font-size: 1.05rem;
                line-height: 1.0;
                margin: 0.05rem 0 0.04rem 0;
            }}

            .mohr-metric-angle {{
                font-size: 0.58rem;
                line-height: 1.0;
            }}
        }}
    </style>

    <div class="mohr-metrics">
        <div class="mohr-metric-card">
            <div class="mohr-metric-title">σmáx</div>
            <div class="mohr-metric-value">{smax:.4g}</div>
            <div class="mohr-metric-angle">α = {a_smax:.2f}°</div>
        </div>

        <div class="mohr-metric-card">
            <div class="mohr-metric-title">σmín</div>
            <div class="mohr-metric-value">{smin:.4g}</div>
            <div class="mohr-metric-angle">α = {a_smin:.2f}°</div>
        </div>

        <div class="mohr-metric-card">
            <div class="mohr-metric-title">τmáx</div>
            <div class="mohr-metric-value">{taumax:.4g}</div>
            <div class="mohr-metric-angle">α = {a_tmax:.2f}°</div>
        </div>

        <div class="mohr-metric-card">
            <div class="mohr-metric-title">τmín</div>
            <div class="mohr-metric-value">{taumin:.4g}</div>
            <div class="mohr-metric-angle">α = {a_tmin:.2f}°</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ============================================================
# GRÁFICOS
# ============================================================

# En la versión web usamos dos figuras separadas.
# En computadora se muestran lado a lado; en celular Streamlit las apila,
# por lo que el Círculo de Mohr aprovecha prácticamente todo el ancho.

col_mohr, col_elem = st.columns([2.15, 1.0], gap="small")

# ------------------------------------------------------------
# CÍRCULO DE MOHR
# ------------------------------------------------------------
fig_mohr, ax_mohr = plt.subplots(figsize=(8.6, 7.2), dpi=115)

th = np.linspace(0, 2*np.pi, 720)
xx = sm + R*np.cos(th)
yy = R*np.sin(th)

ax_mohr.plot(xx, yy, color="black", linewidth=1.8)
ax_mohr.axhline(0, color="gray", linewidth=0.8)
ax_mohr.axvline(0, color="gray", linewidth=0.8)

ax_mohr.scatter([C[0]], [C[1]], color="black", s=35, zorder=6)

ax_mohr.scatter(
    [X[0], Y[0]],
    [X[1], Y[1]],
    color="black",
    s=45,
    zorder=7
)

# Construcción geométrica de P
ax_mohr.plot(
    [X[0], P[0]],
    [X[1], P[1]],
    color="gray",
    linestyle="--",
    linewidth=1.3
)
ax_mohr.plot(
    [Y[0], P[0]],
    [Y[1], P[1]],
    color="gray",
    linestyle="--",
    linewidth=1.3
)

ax_mohr.scatter(
    [P[0]], [P[1]],
    color="darkorange",
    s=70,
    zorder=8
)

# Planos alfa y alfa+90
ax_mohr.plot([P[0], sa], [P[1], ta], color="blue", linewidth=2.1)
ax_mohr.plot([P[0], sa90], [P[1], ta90], color="blue", linewidth=2.1)
ax_mohr.scatter([sa, sa90], [ta, ta90], color="blue", s=48, zorder=8)

principal_plot_data = []
for ang, sig, label in [
    (a_smax, smax, "σmáx"),
    (a_smin, smin, "σmín")
]:
    ss, tt = stress_transform(sx, sy, txy, ang)
    ax_mohr.plot([P[0], ss], [P[1], tt], color="red", linewidth=1.9)
    ax_mohr.scatter([ss], [tt], color="red", s=48, zorder=8)
    principal_plot_data.append((ss, tt, ang, sig, label))

shear_plot_data = []
for ang, tauv, label in [
    (a_tmax, taumax, "τmáx"),
    (a_tmin, taumin, "τmín")
]:
    ss, tt = stress_transform(sx, sy, txy, ang)
    ax_mohr.plot([P[0], ss], [P[1], tt], color="green", linewidth=1.9)
    ax_mohr.scatter([ss], [tt], color="green", s=48, zorder=8)
    shear_plot_data.append((ss, tt, ang, tauv, label))

all_x = [sm-R, sm+R, P[0], X[0], Y[0], sa, sa90]
all_y = [-R, R, P[1], X[1], Y[1], ta, ta90]

xmin, xmax = min(all_x), max(all_x)
ymin, ymax = min(all_y), max(all_y)

span = max(xmax-xmin, ymax-ymin, 1.0)
pad = 0.23 * span

ax_mohr.set_xlim(xmin-pad, xmax+pad)
ax_mohr.set_ylim(ymin-pad, ymax+pad)
ax_mohr.set_aspect("equal", adjustable="box")
ax_mohr.grid(True, alpha=0.20)

ax_mohr.set_title(
    "Círculo de Mohr y trazas de planos desde P",
    fontsize=11
)
ax_mohr.set_xlabel("σ")
ax_mohr.set_ylabel("τ")

labels = [
    {
        "xy": tuple(X),
        "text": f"X\nσx = {sx:.3g}\nτxy = {txy:.3g}",
        "color": "black"
    },
    {
        "xy": tuple(Y),
        "text": f"Y\nσy = {sy:.3g}\nτyx = {tyx:.3g}",
        "color": "black"
    },
    {
        "xy": tuple(P),
        "text": f"P\n({P[0]:.3g}, {P[1]:.3g})",
        "color": "darkorange"
    },
    {
        "xy": tuple(C),
        "text": f"C\n({C[0]:.3g}, 0)",
        "color": "black"
    },
    {
        "xy": (sa, ta),
        "text": f"Plano α = {alpha:.1f}°\nσα = {sa:.3g}\nτα = {ta:.3g}",
        "color": "blue"
    },
    {
        "xy": (sa90, ta90),
        "text": f"Plano α+90°\nσ = {sa90:.3g}\nτ = {ta90:.3g}",
        "color": "blue"
    }
]

for ss, tt, ang, sig, label in principal_plot_data:
    labels.append({
        "xy": (ss, tt),
        "text": f"{label} = {sig:.3g}\nα = {ang:.2f}°",
        "color": "red"
    })

for ss, tt, ang, tauv, label in shear_plot_data:
    labels.append({
        "xy": (ss, tt),
        "text": f"{label} = {tauv:.3g}\nα = {ang:.2f}°",
        "color": "green"
    })

place_nonoverlap_labels(ax_mohr, labels, center_x=sm)
fig_mohr.tight_layout(pad=0.8)

with col_mohr:
    st.pyplot(fig_mohr, use_container_width=True)
plt.close(fig_mohr)

# ------------------------------------------------------------
# ELEMENTO DIFERENCIAL
# ------------------------------------------------------------
fig_elem, ax_elem = plt.subplots(figsize=(5.2, 5.7), dpi=115)
draw_element(ax_elem, sx, sy, txy, alpha, sa, ta)
fig_elem.tight_layout(pad=0.6)

with col_elem:
    st.pyplot(fig_elem, use_container_width=True)
plt.close(fig_elem)

# Pie institucional: en escritorio queda hacia la derecha.
# En celular se adapta naturalmente al ancho disponible.
st.markdown(
    """
    <div style="
        margin-top:-0.35rem;
        margin-left:auto;
        width:max-content;
        max-width:100%;
        text-align:left;
        line-height:1.28;
    ">
        <div style="font-family:Arial;font-size:12px;">Aplicación Circulo de Mohr</div>
        <div style="font-family:Arial;font-size:12px;">Material didáctico Estabilidad 2 – F.I. – UNNE</div>
        <div style="font-family:Arial;font-size:8px;">Ing. Ricardo Barrios D’Ambra</div>
    </div>
    """,
    unsafe_allow_html=True
)

# ============================================================
# DETALLE NUMÉRICO
# ============================================================

with st.expander("Ver resultados numéricos completos"):
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("**Punto principal de Mohr**")
        st.write(f"τyx = {tyx:.6g}")
        st.write(f"P = ({sx:.6g}, {tyx:.6g})")

        st.markdown("**Centro del círculo**")
        st.write(f"C = ({sm:.6g}, 0)")
        st.write(f"R = {R:.6g}")

        st.markdown("**Plano variable**")
        st.write(f"α = {alpha:.3f}°")
        st.write(f"σα = {sa:.6g}")
        st.write(f"τα = {ta:.6g}")
        st.write(f"σ(α+90) = {sa90:.6g}")
        st.write(f"τ(α+90) = {ta90:.6g}")

    with c2:
        st.markdown("**Tensiones principales**")
        st.write(f"σmáx = {smax:.6g}")
        st.write(f"α(σmáx) = {a_smax:.3f}°")
        st.write(f"σmín = {smin:.6g}")
        st.write(f"α(σmín) = {a_smin:.3f}°")

        st.markdown("**Tensiones tangenciales extremas**")
        st.write(f"τmáx = {taumax:.6g}")
        st.write(f"α(τmáx) = {a_tmax:.3f}°")
        st.write(f"τmín = {taumin:.6g}")
        st.write(f"α(τmín) = {a_tmin:.3f}°")
