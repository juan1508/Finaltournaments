"""
app.py - FMMJ World Cup Simulator
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from state import init_state, get_state, reset_for_new_edition
from utils.tournament import display_name, flag_img

st.set_page_config(
    page_title="FMMJ World Cup Simulator",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Oswald:wght@400;600;700&family=Source+Sans+3:wght@400;600&display=swap');
.stApp { background: #060b18; color: #e0e8ff; font-family: 'Source Sans 3', sans-serif; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #080d1e 0%, #0a1228 100%) !important; border-right: 1px solid #1a2a5a; }
[data-testid="stSidebar"] * { color: #c0cce0 !important; }
[data-testid="stSidebar"] .stRadio label { padding: 8px 12px !important; border-radius: 8px !important; cursor: pointer !important; transition: background 0.2s; display: block; }
[data-testid="stSidebar"] .stRadio label:hover { background: #1a2a5a !important; }
.stSelectbox > div > div, .stTextInput > div > input, .stNumberInput > div > input { background: #111a35 !important; border-color: #1e3055 !important; color: #e0e8ff !important; }
.stTabs [data-baseweb="tab-list"] { background: #0a1020 !important; border-radius: 10px !important; padding: 4px !important; }
.stTabs [data-baseweb="tab"] { background: transparent !important; color: #7090c0 !important; border-radius: 8px !important; font-weight: 600 !important; }
.stTabs [aria-selected="true"] { background: #1a3a80 !important; color: #ffd700 !important; }
.stButton > button[kind="primary"] { background: linear-gradient(135deg, #1a4aff, #0033cc) !important; color: white !important; border: none !important; font-weight: 700 !important; font-family: 'Oswald', sans-serif !important; border-radius: 8px !important; }
.stButton > button { background: #111a35 !important; color: #c0d0f0 !important; border: 1px solid #1e3055 !important; border-radius: 8px !important; }
[data-testid="stExpander"] { background: #0a1020 !important; border: 1px solid #1a2a5a !important; border-radius: 10px !important; }
[data-testid="stExpander"] summary { color: #c8d8f0 !important; font-weight: 600 !important; }
h1, h2, h3 { font-family: 'Oswald', sans-serif !important; }
h1 { color: #ffd700 !important; } h2 { color: #c8d8ff !important; } h3 { color: #a0c0ff !important; }
hr { border-color: #1a2a5a !important; }
::-webkit-scrollbar { width: 6px; } ::-webkit-scrollbar-track { background: #0a1020; } ::-webkit-scrollbar-thumb { background: #1a3a6a; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

init_state()
state = get_state()


def _show_home(state):
    host = state.get("host", "Nigeria")
    edition = state.get("edition", 1)
    qualified = state.get("world_cup_qualified", [])
    from state import get_team_confederation

    st.markdown(f"""
    <div style='background:linear-gradient(135deg,#060b18 0%,#0d1a3a 50%,#060b18 100%);
    border:2px solid #c8a000;border-radius:20px;padding:40px;margin-bottom:32px;text-align:center;'>
        <div style='font-size:3.5rem;font-family:Oswald,sans-serif;font-weight:700;
                    color:#ffd700;letter-spacing:4px;text-shadow:0 0 30px rgba(255,215,0,.6);'>
            🌍 FMMJ WORLD CUP
        </div>
        <div style='font-size:1.1rem;color:#6080aa;letter-spacing:2px;margin-top:8px;'>
            EDICIÓN {edition} · SIMULADOR OFICIAL
        </div>
        <div style='margin-top:20px;font-size:1rem;color:#a0c0e0;'>
            Anfitrión: {flag_img(host,24,18)}&nbsp;<strong>{display_name(host)}</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)

    conf_q = {}
    for t in qualified:
        conf = get_team_confederation(t)
        conf_q[conf] = conf_q.get(conf, 0) + 1

    cupos_info = [
        ("🏆 UEFA", 13, "UEFA", "#003580"),
        ("🌎 CONMEBOL", 4, "CONMEBOL", "#006b3c"),
        ("🌍 CAF", 5, "CAF", "#b8860b"),
        ("⭐ CONCACAF", 3, "CONCACAF", "#8b0000"),
        ("🌏 AFC", 4, "AFC", "#4a0080"),
    ]
    cols = st.columns(5)
    for col, (label, total, conf, color) in zip(cols, cupos_info):
        current = conf_q.get(conf, 0)
        with col:
            st.markdown(f"""
            <div style='background:#0a1020;border:1px solid {color};border-radius:12px;
            padding:16px;text-align:center;'>
                <div style='font-size:0.9rem;font-weight:700;color:#c8d8ff;'>{label}</div>
                <div style='font-size:2rem;font-weight:900;color:{"#00cc66" if current >= total else "#ffd700"};'>
                    {current}/{total}
                </div>
                <div style='font-size:0.7rem;color:#6080aa;'>cupos</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("### 🗺️ Guía de uso")
        st.markdown("""
1. **🏅 Ranking FMMJ** — Consulta el ranking actualizado
2. **🏆 Eurocopa** → 6 grupos + llaves + playoff UEFA (13 cupos)
3. **🌎 Copa América** → Elige invitadas, sortea, juega (4 cupos)
4. **🌍 Copa África** → 10 equipos CAF (5 cupos)
5. **⭐ Copa Oro** → CONCACAF (3 cupos)
6. **🌏 Copa Asia** → AFC (4 cupos)
7. **🔁 Repechaje** → 2 llaves ida y vuelta (2 cupos)
8. **🌍 Sorteo y Mundial** → 32 equipos, 8 grupos, llaves 🏆
        """)
    with col_b:
        if qualified:
            st.markdown("### ✅ Clasificados al Mundial")
            for t in qualified[:16]:
                st.markdown(f"{flag_img(t,20,15)}&nbsp;**{display_name(t)}**", unsafe_allow_html=True)
            if len(qualified) > 16:
                st.caption(f"... y {len(qualified)-16} más")
        else:
            st.info("Ningún equipo clasificado aún. Comienza por la Eurocopa.")
    if len(qualified) == 32:
        st.balloons()
        st.success("🎉 ¡Los 32 equipos están clasificados! Ve al **Sorteo y Mundial**.")


def _show_config(state):
    st.markdown("### ⚙️ Configuración del Simulador FMMJ")
    st.markdown("#### 🏠 Anfitrión del Mundial")
    from data import ALL_TEAMS
    current_host = state.get("host", "Nigeria")
    host_options = sorted(ALL_TEAMS, key=lambda t: display_name(t))
    host_display = [display_name(t) for t in host_options]
    current_idx = host_options.index(current_host) if current_host in host_options else 0
    selected_display = st.selectbox("Selecciona el anfitrión:", host_display, index=current_idx)
    new_host = host_options[host_display.index(selected_display)]
    if new_host != current_host:
        if st.button(f"✅ Confirmar: {display_name(new_host)} como anfitrión", type="primary"):
            state["host"] = new_host
            if new_host not in state["world_cup_qualified"]:
                state["world_cup_qualified"].insert(0, new_host)
            st.success(f"✅ Anfitrión actualizado: {display_name(new_host)}")
            st.rerun()
    st.markdown("---")
    st.markdown("#### 🔄 Nueva Edición del Mundial")
    st.warning("⚠️ Esto borrará todos los resultados de la edición actual pero conservará el ranking.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Iniciar Nueva Edición", type="primary"):
            reset_for_new_edition()
            st.success("✅ Nueva edición iniciada. El ranking se conserva.")
            st.rerun()
    with col2:
        if st.button("🗑️ Reset Completo (incluyendo ranking)"):
            from state import get_initial_state
            st.session_state.fmmj_state = get_initial_state()
            st.success("✅ Reset completo realizado.")
            st.rerun()
    st.markdown("---")
    st.markdown("#### 📊 Estado actual")
    st.json({
        "edicion": state.get("edition"),
        "anfitrion": display_name(state.get("host", "")),
        "clasificados_mundial": len(state.get("world_cup_qualified", [])),
        "fase_eurocopa": state.get("euro", {}).get("phase", "—"),
        "fase_copa_america": state.get("copa_america", {}).get("phase", "—"),
        "fase_copa_africa": state.get("copa_africa", {}).get("phase", "—"),
        "fase_copa_oro": state.get("copa_oro", {}).get("phase", "—"),
        "fase_copa_asia": state.get("copa_asia", {}).get("phase", "—"),
    })


# ---------------------------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:16px 0 8px;'>
        <div style='font-size:2.2rem;font-family:Oswald,sans-serif;font-weight:700;
                    color:#ffd700;letter-spacing:2px;text-shadow:0 0 20px rgba(255,215,0,0.5);'>
            🌍 FMMJ
        </div>
        <div style='font-size:0.7rem;color:#6080aa;letter-spacing:3px;text-transform:uppercase;'>
            World Cup Simulator
        </div>
    </div>
    <hr style='border-color:#1a2a5a;margin:8px 0 16px;'/>
    """, unsafe_allow_html=True)

    host = state.get("host", "Nigeria")
    edition = state.get("edition", 1)
    qualified_count = len(state.get("world_cup_qualified", []))

    st.markdown(f"""
    <div style='background:#0a1530;border:1px solid #1a3a6a;border-radius:10px;padding:12px;margin-bottom:16px;'>
        <div style='font-size:0.75rem;color:#6080aa;text-transform:uppercase;letter-spacing:1px;'>Edición</div>
        <div style='font-size:1.1rem;font-weight:700;color:#ffd700;'>FMMJ {edition}ª Copa</div>
        <div style='margin-top:8px;font-size:0.75rem;color:#6080aa;'>Anfitrión</div>
        <div style='font-size:0.95rem;font-weight:600;color:#e0e8ff;'>
            {flag_img(host,20,15)}&nbsp;{display_name(host)}
        </div>
        <div style='margin-top:8px;font-size:0.75rem;color:#6080aa;'>Clasificados</div>
        <div style='font-size:0.95rem;font-weight:700;color:{"#00cc66" if qualified_count >= 32 else "#ffd700"};'>
            {qualified_count}/32 equipos
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**Navegación:**")
    menu_options = {
        "🏠 Inicio": "inicio",
        "🏅 Ranking FMMJ": "ranking",
        "🏆 Eurocopa (UEFA)": "eurocopa",
        "🌎 Copa América (CONMEBOL)": "copa_america",
        "🌍 Copa África (CAF)": "copa_africa",
        "⭐ Copa Oro (CONCACAF)": "copa_oro",
        "🌏 Copa Asia (AFC)": "copa_asia",
        "🔁 Repechaje Internacional": "repechaje",
        "🌍 Sorteo y Mundial": "mundial",
        "⚙️ Configuración": "config",
    }
    selected = st.radio("", list(menu_options.keys()), label_visibility="collapsed")
    page_key = menu_options[selected]

    st.markdown("<hr style='border-color:#1a2a5a;margin:16px 0;'/>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:0.75rem;color:#6080aa;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;'>Progreso Torneos</div>", unsafe_allow_html=True)

    def phase_icon(tour_key):
        phase = state.get(tour_key, {}).get("phase", "")
        if phase == "completado": return "✅"
        elif phase in ["grupos", "llaves", "playoff", "playoff_uefa", "octavos", "cuartos", "semis"]: return "🔄"
        return "⏳"

    for name, tour_key, ph_key in [
        ("Eurocopa", "euro", "euro"),
        ("Copa América", "copa_america", "copa_america"),
        ("Copa África", "copa_africa", "copa_africa"),
        ("Copa Oro", "copa_oro", "copa_oro"),
        ("Copa Asia", "copa_asia", "copa_asia"),
    ]:
        icon = phase_icon(ph_key)
        phase = state.get(ph_key, {}).get("phase", "—")
        color = "#00cc66" if icon == "✅" else ("#ffd700" if icon == "🔄" else "#6080aa")
        st.markdown(f"<div style='font-size:0.8rem;color:{color};padding:2px 0;'>{icon} {name}: <span style='color:#888;'>{phase}</span></div>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# ROUTING
# ---------------------------------------------------------------------------
if page_key == "inicio":
    _show_home(state)
elif page_key == "ranking":
    from pages.repechaje import show_ranking
    show_ranking()
elif page_key == "eurocopa":
    from pages.eurocopa import show
    show()
elif page_key == "copa_america":
    from pages.copa_america import show
    show()
elif page_key == "copa_africa":
    from pages.confederaciones import show_copa_africa
    show_copa_africa()
elif page_key == "copa_oro":
    from pages.confederaciones import show_copa_oro
    show_copa_oro()
elif page_key == "copa_asia":
    from pages.confederaciones import show_copa_asia
    show_copa_asia()
elif page_key == "repechaje":
    from pages.repechaje import show_repechaje
    show_repechaje()
elif page_key == "mundial":
    from pages.repechaje import show_world_cup_draw
    show_world_cup_draw()
elif page_key == "config":
    _show_config(state)
