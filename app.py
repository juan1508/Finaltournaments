"""
app.py — FMMJ World Cup Simulator
Archivo único con persistencia JSON y todas las competiciones clasificatorias
"""
import streamlit as st
import random
import json
import os

from data import (
    UEFA_TEAMS, CONMEBOL_TEAMS, CAF_TEAMS, CONCACAF_TEAMS, AFC_TEAMS,
    PLAYOFF_TEAMS, COPA_AMERICA_GUESTS_POOL, CONFEDERATIONS,
    INITIAL_FIFA_RANKING, FLAG_MAP, TEAM_DISPLAY_NAMES, get_flag_url, CONF_LOGOS
)
from state import (
    get_state, save_state, init_state, get_initial_state,
    reset_for_new_edition, update_ranking, get_team_confederation, RANKING_POINTS
)
from utils import (
    display_name, get_team_confederation, get_jornadas,
    match_key, calculate_standings, render_standings_table,
    _scorer_input, register_scorers
)
from group_setup import manual_group_setup

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="FMMJ World Cup Simulator",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Barlow:wght@400;500;600;700;800&display=swap');
.stApp { background: #06101e; color: #dce8ff; font-family: 'Barlow', sans-serif; }
[data-testid="stSidebar"] { background: linear-gradient(180deg,#040d18 0%,#06101e 100%) !important; border-right:1px solid #142038; }
[data-testid="stSidebar"] * { color:#b0c8ee !important; }
.stTabs [data-baseweb="tab-list"] { background:#091525 !important; border-radius:10px !important; padding:4px !important; }
.stTabs [data-baseweb="tab"] { background:transparent !important; color:#4070a0 !important; border-radius:8px !important; font-weight:600 !important; }
.stTabs [aria-selected="true"] { background:#163070 !important; color:#ffd700 !important; }
.stButton > button[kind="primary"] { background:linear-gradient(135deg,#1a4aff,#0033cc) !important; color:white !important; border:none !important; font-weight:700 !important; border-radius:8px !important; }
.stButton > button { background:#0b1830 !important; color:#a0c0f0 !important; border:1px solid #1a3055 !important; border-radius:8px !important; }
.stSelectbox > div > div, .stTextInput > div > input, .stNumberInput > div > input { background:#0c1a30 !important; border-color:#1c2e50 !important; color:#dce8ff !important; }
[data-testid="stExpander"] { background:#091525 !important; border:1px solid #18285a !important; border-radius:10px !important; }
h1,h2,h3 { font-family:'Bebas Neue',sans-serif !important; letter-spacing:1px; }
h1 { color:#ffd700 !important; } h2 { color:#c0d0ff !important; } h3 { color:#90b0f0 !important; }
hr { border-color:#182848 !important; }
::-webkit-scrollbar { width:5px; } ::-webkit-scrollbar-track { background:#06101e; } ::-webkit-scrollbar-thumb { background:#183868;border-radius:3px; }
.conf-chip { display:inline-block;padding:2px 8px;border-radius:12px;font-size:0.7rem;font-weight:700;margin-left:6px; }
</style>
""", unsafe_allow_html=True)


def flag_html(team, w=20, h=15):
    from data import get_flag_url
    url = get_flag_url(team, w, h)
    if url:
        return f"<img src='{url}' style='vertical-align:middle;margin-right:4px;border-radius:2px;' width='{w}' height='{h}'>"
    return ""

init_state()
state = get_state()

# ─────────────────────────────────────────────
# HELPER GLOBAL: FILA DE PARTIDO
# ─────────────────────────────────────────────
def show_match_row(home, away, prefix_key, results_dict, torneo_name, state, show_scorers=True):
    from data import get_flag_url
    res = results_dict.get(prefix_key, {})
    c1, c2, c3, c4, c5, c6 = st.columns([3, 1, 1, 3, 2, 1])
    with c1:
        fa, fb = st.columns([1, 5])
        with fa:
            fu = get_flag_url(home, 32, 24)
            if fu: st.image(fu, width=28)
        with fb:
            st.markdown(f"**{display_name(home)}**")
    with c2:
        hg = st.number_input("", 0, 20, int(res.get("home_goals", 0)), key=f"{prefix_key}_hg", label_visibility="collapsed")
    with c3:
        ag = st.number_input("", 0, 20, int(res.get("away_goals", 0)), key=f"{prefix_key}_ag", label_visibility="collapsed")
    with c4:
        fa, fb = st.columns([1, 5])
        with fa:
            fu = get_flag_url(away, 32, 24)
            if fu: st.image(fu, width=28)
        with fb:
            st.markdown(f"**{display_name(away)}**")
    with c5:
        if hg == ag:
            ps = st.selectbox("Penales", ["—", display_name(home), display_name(away)], key=f"{prefix_key}_pen")
            pw = home if ps == display_name(home) else (away if ps == display_name(away) else None)
        else:
            pw = None
            st.empty()
    with c6:
        save = st.button("💾", key=f"{prefix_key}_save")

    hs, as_ = [], []
    if show_scorers:
        cs1, cs2 = st.columns(2)
        with cs1: hs = _scorer_input(home, hg, res.get("home_scorers", []), f"{prefix_key}_hs", state, torneo_name)
        with cs2: as_ = _scorer_input(away, ag, res.get("away_scorers", []), f"{prefix_key}_as", state, torneo_name)

    if save:
        winner = home if hg > ag else (away if ag > hg else pw)
        results_dict[prefix_key] = {
            "home_goals": hg, "away_goals": ag, "winner": winner,
            "penalty_winner": pw, "home_scorers": hs, "away_scorers": as_, "played": True
        }
        if show_scorers:
            register_scorers(hs, home, state, torneo_name)
            register_scorers(as_, away, state, torneo_name)
        save_state()
        st.rerun()

    if res.get("played"):
        pw_tag = f" (pen. {display_name(res.get('penalty_winner',''))})" if res.get("penalty_winner") else ""
        st.markdown(
            f"<small style='color:#507090'>✅ {display_name(home)} **{res.get('home_goals',0)}** - **{res.get('away_goals',0)}** {display_name(away)}{pw_tag}</small>",
            unsafe_allow_html=True
        )
    return res.get("played", False)


def _render_groups_grid(groups, cols_n=3):
    col_list = st.columns(cols_n)
    for idx, (g, teams) in enumerate(groups.items()):
        with col_list[idx % cols_n]:
            html = f"<div style='background:#0b1a35;border:1px solid #1a3560;border-radius:10px;padding:14px;margin-bottom:12px;'>"
            html += f"<div style='font-size:1rem;font-weight:700;color:#ffd700;border-bottom:2px solid #ffd700;padding-bottom:6px;margin-bottom:10px;font-family:Bebas Neue,sans-serif;'>GRUPO {g}</div>"
            for t in teams:
                html += f"<div style='padding:3px 0;'>{flag_html(t)} {display_name(t)}</div>"
            html += "</div>"
            st.markdown(html, unsafe_allow_html=True)


def show_group_jornadas(state, tour, torneo_name, advancing=2):
    groups = tour.get("groups", {})
    results = tour.setdefault("group_results", {})
    standings_all = tour.setdefault("group_standings", {})
    if not groups:
        st.warning("No hay grupos configurados.")
        return False

    all_complete = True
    for g, teams in groups.items():
        with st.expander(f"**GRUPO {g}** — {' · '.join([display_name(t) for t in teams])}", expanded=False):
            jornadas = get_jornadas(teams)
            tab_labels = [f"J{i+1}" for i in range(len(jornadas))] + ["📊 Tabla"]
            jtabs = st.tabs(tab_labels)
            for ji, jornada in enumerate(jornadas):
                with jtabs[ji]:
                    for home, away in jornada:
                        mk = match_key(home, away)
                        prefix = f"{torneo_name[:4]}_{g}_{mk}"
                        played = show_match_row(home, away, prefix, results, torneo_name, state)
                        # normalise to match_key for standings
                        if results.get(prefix, {}).get("played"):
                            results[mk] = results[prefix]
                        st.markdown("<hr style='margin:4px 0;border-color:#0f2040;'>", unsafe_allow_html=True)
            with jtabs[-1]:
                standings = calculate_standings(teams, results)
                standings_all[g] = standings
                render_standings_table(standings, advancing=advancing)

    for g, teams in groups.items():
        for i in range(len(teams)):
            for j in range(i+1, len(teams)):
                mk = match_key(teams[i], teams[j])
                prefix = f"{torneo_name[:4]}_{g}_{mk}"
                if not results.get(mk, {}).get("played") and not results.get(prefix, {}).get("played"):
                    all_complete = False
    return all_complete


def show_knockout_generic(state, tour, torneo_name, phase_configs, pfx):
    bracket = tour.setdefault("knockout_bracket", {})
    results = tour.setdefault("knockout_results", {})

    final_done = False
    for phase_key, phase_name, next_phase in phase_configs:
        matches = bracket.get(phase_key, [])
        if not matches:
            continue
        st.markdown(f"#### {phase_name}")
        all_done = True
        for idx, match in enumerate(matches):
            home, away = match.get("home"), match.get("away")
            if not home or not away:
                st.markdown("*Pendiente de definir*")
                all_done = False
                continue
            key = f"{pfx}_{phase_key}_{idx}"
            show_match_row(home, away, key, results, torneo_name, state)
            res = results.get(key, {})
            if res.get("winner"):
                bracket[phase_key][idx]["winner"] = res["winner"]
            else:
                all_done = False
            st.markdown("<hr style='margin:4px 0;border-color:#0f2040;'>", unsafe_allow_html=True)

        if all_done and next_phase is not None and not bracket.get(next_phase):
            winners = [results.get(f"{pfx}_{phase_key}_{i}", {}).get("winner") for i in range(len(matches))]
            winners = [w for w in winners if w]
            # semis → tercer puesto
            if phase_key == "semis" and len(winners) == 2:
                losers = []
                for i, m in enumerate(matches):
                    r = results.get(f"{pfx}_semis_{i}", {})
                    if r.get("winner"):
                        loser = m["home"] if r["winner"] == m["away"] else m["away"]
                        if loser: losers.append(loser)
                if len(losers) == 2:
                    bracket["tercer_puesto"] = [{"home": losers[0], "away": losers[1], "winner": None}]
                    # Add semis losers to playoff pool if applicable
                    pool = tour.get("playoff_pool", [])
                    for l in losers:
                        if l not in pool: pool.append(l)
                    tour["playoff_pool"] = pool
            if phase_key == "cuartos":
                losers = []
                for i, m in enumerate(matches):
                    r = results.get(f"{pfx}_cuartos_{i}", {})
                    if r.get("winner"):
                        loser = m["home"] if r["winner"] == m["away"] else m["away"]
                        if loser: losers.append(loser)
                pool = tour.get("playoff_pool", [])
                for l in losers:
                    if l not in pool: pool.append(l)
                tour["playoff_pool"] = pool
            nxt = [(winners[i], winners[i+1]) for i in range(0, len(winners)-1, 2)]
            bracket[next_phase] = [{"home": a, "away": b, "winner": None} for a, b in nxt]
            save_state()
            st.rerun()

        if all_done and next_phase is None:
            final_done = True

    # Tercer puesto
    if bracket.get("tercer_puesto"):
        st.markdown("#### 🥉 Tercer Puesto")
        for idx, m in enumerate(bracket["tercer_puesto"]):
            home, away = m["home"], m["away"]
            key = f"{pfx}_tercer_{idx}"
            show_match_row(home, away, key, results, torneo_name, state)
            res = results.get(key, {})
            if res.get("winner"):
                bracket["tercer_puesto"][idx]["winner"] = res["winner"]

    return final_done


# ══════════════════════════════════════════════════════════════
# EUROCOPA UEFA — 24 equipos, 6 grupos de 4
# Cupos: top 5 directos, 6-21 → playoff 4 grupos → 8 más
# Total UEFA = 13
# ══════════════════════════════════════════════════════════════
def show_eurocopa():
    state = get_state()
    euro = state["euro"]

    col_logo, col_title = st.columns([1, 9])
    with col_logo:
        try: st.image("uefa.png", width=72)
        except: st.markdown("🏆")
    with col_title:
        st.markdown("""<div style='background:linear-gradient(135deg,#002060 0%,#0044cc 60%,#002060 100%);
            border-radius:16px;padding:20px 28px;margin-bottom:20px;box-shadow:0 6px 24px rgba(0,68,204,.4);'>
            <div style='font-size:1.9rem;font-weight:900;color:#ffd700;font-family:Bebas Neue,sans-serif;letter-spacing:2px;'>EUROCOPA FMMJ</div>
            <div style='color:#a0c4ff;font-size:.9rem;'>24 selecciones UEFA · 6 grupos de 4 · Top 5 directo + Playoff 4 grupos → 13 cupos al Mundial</div>
        </div>""", unsafe_allow_html=True)

    tabs = st.tabs(["🎲 Grupos", "📊 Fase Grupos", "⚽ Llaves", "🔄 Playoff UEFA", "🌍 Clasificados"])

    with tabs[0]:
        st.markdown("### Armado de Grupos — Eurocopa FMMJ")
        if not euro.get("setup_done"):
            manual_group_setup(state, "euro", UEFA_TEAMS, num_groups=6, teams_per_group=4,
                               confirm_label="Confirmar Grupos Eurocopa")
        else:
            st.success("✅ Grupos confirmados")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("✏️ Editar Grupos", type="secondary"):
                    euro["setup_done"] = False
                    if "draft_euro" in st.session_state: del st.session_state["draft_euro"]
                    save_state(); st.rerun()
            _render_groups_grid(euro["groups"], cols_n=3)

    with tabs[1]:
        if not euro.get("setup_done"):
            st.info("Primero confirma los grupos.")
        else:
            all_done = show_group_jornadas(state, euro, "Euro", advancing=2)
            if all_done or st.checkbox("🔓 Forzar avance a llaves", key="euro_force"):
                if euro["phase"] == "grupos":
                    if st.button("⚽ Generar Llaves Eurocopa", type="primary"):
                        _build_euro_knockout(state, euro)
                        save_state(); st.rerun()

    with tabs[2]:
        if euro["phase"] not in ["llaves", "playoff_uefa", "completado"]:
            st.info("Completa la fase de grupos primero.")
        else:
            _show_euro_knockout(state, euro)

    with tabs[3]:
        _show_euro_playoff(state, euro)

    with tabs[4]:
        _show_euro_classified(state, euro)


def _build_euro_knockout(state, euro):
    """
    Construye octavos de final de la Eurocopa con el formato UEFA oficial.
    Los 4 mejores terceros se enfrentan según la tabla oficial UEFA
    que define los cruces en función de qué grupos aportaron 3eros clasificados.

    Tabla UEFA oficial (grupos A-F):
    Grupos con 3eros | 1B vs | 1C vs | 1E vs | 1F vs
    A B C D          |  3D   |  3A   |  3B   |  3C   ← fila imagen
    A B C E          |  3E   |  3A   |  3B   |  3C
    A B C F          |  3F   |  3A   |  3B   |  3C
    A B D E          |  3E   |  3D   |  3A   |  3B
    A B D F          |  3F   |  3D   |  3A   |  3B  (corregido)  
    A B E F          |  3E   |  3F   |  3B   |  3A  (corregido)
    A C D E          |  3E   |  3D   |  3C   |  3A
    A C D F          |  3F   |  3D   |  3C   |  3A
    A C E F          |  3E   |  3F   |  3C   |  3A
    A D E F          |  3E   |  3F   |  3D   |  3A
    B C D E          |  3E   |  3D   |  3B   |  3C
    B C D F          |  3F   |  3D   |  3C   |  3B
    B C E F          |  3E   |  3F   |  3C   |  3B
    B D E F          |  3F   |  3E   |  3D   |  3B
    C D E F          |  3F   |  3E   |  3D   |  3C

    Cruces fijos de octavos:
    M37: 1A vs 2C
    M38: 2A vs 2B  
    M39: 1F vs 2E
    M40: 1D vs 2F   (o bien corregido: ver UEFA 2024)
    M41: 1B vs T3   (según tabla)
    M42: 1E vs T3
    M43: 1C vs T3
    M44: 1G-or-T3 — se adapta a 6 grupos

    Para FMMJ (grupos A-F, 6 grupos):
    Cruces fijos:
    1A vs 2C  |  1B vs T3  |  1C vs T3  |  1D vs 2F
    2A vs 2B  |  1E vs T3  |  1F vs 2E  |  T3 restante vs T3
    """
    standings = euro.get("group_standings", {})
    groups = sorted(standings.keys())  # ['A','B','C','D','E','F']
    if len(groups) < 6:
        st.error("Faltan standings de grupos.")
        return

    firsts  = {g: standings[g][0]["team"] for g in groups if standings.get(g)}
    seconds = {g: standings[g][1]["team"] for g in groups if len(standings.get(g,[])) > 1}
    thirds_raw = {}
    for g in groups:
        s = standings.get(g, [])
        if len(s) >= 3:
            thirds_raw[g] = {"team": s[2]["team"], "pts": s[2]["pts"], "gd": s[2]["gd"], "gf": s[2]["gf"]}
    fourths = [standings[g][3]["team"] for g in groups if len(standings.get(g,[])) > 3]

    # Seleccionar los 4 mejores terceros
    thirds_sorted = sorted(thirds_raw.items(), key=lambda x: (-x[1]["pts"], -x[1]["gd"], -x[1]["gf"]))
    best4_groups = [g for g, _ in thirds_sorted[:4]]   # ej. ['A','B','D','E']
    worst2_thirds = [thirds_raw[g]["team"] for g, _ in thirds_sorted[4:]]
    best4_key = "".join(sorted(best4_groups))           # ej. 'ABDE'

    # Tabla UEFA oficial: clave = grupos con 3eros clasificados
    # Valor: {receptor: grupo_del_3ero}
    # Receptores: 1B, 1C, 1E, 1F
    UEFA_THIRDS_TABLE = {
        "ABCD": {"1B": "D", "1C": "A", "1E": "B", "1F": "C"},
        "ABCE": {"1B": "E", "1C": "A", "1E": "B", "1F": "C"},
        "ABCF": {"1B": "F", "1C": "A", "1E": "B", "1F": "C"},
        "ABDE": {"1B": "E", "1C": "D", "1E": "A", "1F": "B"},
        "ABDF": {"1B": "F", "1C": "D", "1E": "A", "1F": "B"},
        "ABEF": {"1B": "E", "1C": "F", "1E": "B", "1F": "A"},
        "ACDE": {"1B": "E", "1C": "D", "1E": "C", "1F": "A"},
        "ACDF": {"1B": "F", "1C": "D", "1E": "C", "1F": "A"},
        "ACEF": {"1B": "E", "1C": "F", "1E": "C", "1F": "A"},
        "ADEF": {"1B": "E", "1C": "F", "1E": "D", "1F": "A"},
        "BCDE": {"1B": "E", "1C": "D", "1E": "B", "1F": "C"},
        "BCDF": {"1B": "F", "1C": "D", "1E": "C", "1F": "B"},
        "BCEF": {"1B": "E", "1C": "F", "1E": "C", "1F": "B"},
        "BDEF": {"1B": "F", "1C": "E", "1E": "D", "1F": "B"},
        "CDEF": {"1B": "F", "1C": "E", "1E": "D", "1F": "C"},
    }

    mapping = UEFA_THIRDS_TABLE.get(best4_key, {})
    t3 = {slot: thirds_raw[g]["team"] for slot, g in mapping.items() if g in thirds_raw}

    # Cruces oficiales octavos Eurocopa (adaptado a 6 grupos A-F):
    # M1: 1A vs 2C   M2: 1B vs T3(1B)
    # M3: 1C vs T3(1C) M4: 1D vs 2F
    # M5: 2A vs 2B   M6: 1E vs T3(1E)
    # M7: 1F vs 2E   M8: T3(1F) — en Eurocopa real hay M8 distinto
    # Formato FMMJ 6 grupos:
    octavos = [
        {"home": firsts.get("A"), "away": seconds.get("C"), "winner": None},   # M1
        {"home": firsts.get("D"), "away": seconds.get("F"), "winner": None},   # M2
        {"home": seconds.get("A"), "away": seconds.get("B"), "winner": None},  # M3
        {"home": firsts.get("F"), "away": seconds.get("E"), "winner": None},   # M4
        {"home": firsts.get("B"), "away": t3.get("1B"),    "winner": None},   # M5
        {"home": firsts.get("C"), "away": t3.get("1C"),    "winner": None},   # M6
        {"home": firsts.get("E"), "away": t3.get("1E"),    "winner": None},   # M7
        {"home": t3.get("1F"),   "away": seconds.get("D"), "winner": None},   # M8
    ]
    # Filtrar partidos sin equipos definidos
    octavos = [m for m in octavos if m["home"] and m["away"]]

    euro["best_thirds"] = [thirds_raw[g]["team"] for g in best4_groups]
    euro["best4_groups"] = best4_groups
    euro["thirds_mapping"] = mapping
    euro["knockout_bracket"] = {
        "octavos": octavos, "cuartos": [], "semis": [], "tercer_puesto": [], "final": []
    }
    euro["knockout_results"] = {}
    euro["playoff_pool"] = []
    euro["phase"] = "llaves"
    euro["_fourths"] = fourths
    euro["_worst_thirds"] = worst2_thirds


def _show_euro_knockout(state, euro):
    bracket = euro.setdefault("knockout_bracket", {})
    results = euro.setdefault("knockout_results", {})
    from data import get_flag_url, TEAM_DISPLAY_NAMES

    # ── Botón reset llaves ────────────────────────────────────────────
    col_r, col_i = st.columns([1, 4])
    with col_r:
        if st.button("🔄 Resetear Llaves", type="secondary", key="reset_euro_bracket"):
            euro["knockout_bracket"] = {}
            euro["knockout_results"] = {}
            euro["direct_qualified"] = []
            euro["playoff_pool"] = []
            euro["best4_groups"] = []
            euro["thirds_mapping"] = {}
            euro["phase"] = "grupos"
            save_state()
            st.rerun()

    # ── Info mejores 3eros y tabla aplicada ──────────────────────────
    best4 = euro.get("best4_groups", [])
    mapping = euro.get("thirds_mapping", {})
    if best4:
        standings = euro.get("group_standings", {})
        thirds_teams = {g: standings[g][2]["team"] for g in best4 if len(standings.get(g, [])) > 2}
        clave = "".join(sorted(best4))
        html = (f"<div style='background:#0a1428;border:1px solid #1a3060;border-radius:10px;"
                f"padding:14px 16px;margin-bottom:16px;'>")
        html += (f"<div style='font-size:0.85rem;color:#ffd700;font-weight:700;margin-bottom:10px;'>"
                 f"📋 4 Mejores Terceros — Tabla UEFA: <span style='background:#162a5a;padding:2px 8px;"
                 f"border-radius:6px;'>{clave}</span></div>")
        html += "<div style='display:flex;gap:12px;flex-wrap:wrap;'>"
        for slot, g in sorted(mapping.items()):
            team = thirds_teams.get(g, "")
            if not team:
                continue
            fu = get_flag_url(team, 24, 18)
            tname = TEAM_DISPLAY_NAMES.get(team, team)
            flag_tag = f"<img src='{fu}' style='vertical-align:middle;margin-right:5px;border-radius:2px;' width='24' height='18'>" if fu else ""
            html += (f"<div style='background:#0d1f3c;border:1px solid #1a3560;padding:8px 12px;"
                     f"border-radius:8px;min-width:140px;'>"
                     f"<div style='color:#5090c0;font-size:0.72rem;text-transform:uppercase;margin-bottom:4px;'>{slot}</div>"
                     f"<div style='color:#dce8ff;font-size:0.85rem;font-weight:600;'>"
                     f"{flag_tag}{tname}</div>"
                     f"<div style='color:#406080;font-size:0.7rem;margin-top:2px;'>3ro Grupo {g}</div>"
                     f"</div>")
        html += "</div></div>"
        st.markdown(html, unsafe_allow_html=True)

    # ── Bracket visual ────────────────────────────────────────────────
    _render_euro_bracket(euro, bracket, results)

    # ── Partidos jugables ─────────────────────────────────────────────
    phases = [
        ("octavos", "🔵 Octavos de Final", "cuartos"),
        ("cuartos", "🟡 Cuartos de Final",  "semis"),
        ("semis",   "🟠 Semifinales",        "final"),
        ("final",   "🏆 GRAN FINAL",         None),
    ]
    final_done = show_knockout_generic(state, euro, "Eurocopa FMMJ", phases, "euro")
    if final_done:
        _determine_euro_classified(state, euro, results, bracket)


def _render_euro_bracket(euro, bracket, results):
    """Bracket visual de 8 octavos → 4 cuartos → 2 semis → final"""
    from data import get_flag_url, TEAM_DISPLAY_NAMES

    def team_cell(team, is_winner=False, score=None):
        if not team:
            return "<div style='height:36px;background:#0b1830;border-radius:6px;margin:2px 0;display:flex;align-items:center;padding:0 8px;color:#304060;font-size:0.78rem;'>Por definir</div>"
        fu = get_flag_url(team, 20, 15)
        flag_tag = f"<img src='{fu}' style='vertical-align:middle;margin-right:6px;border-radius:2px;' width='20' height='15'>" if fu else ""
        tname = TEAM_DISPLAY_NAMES.get(team, team)
        bg = "#0d3a20" if is_winner else "#0b1830"
        border = "border-left:3px solid #ffd700;" if is_winner else ""
        score_tag = f"<span style='margin-left:auto;font-weight:700;color:#ffd700;'>{score}</span>" if score is not None else ""
        return (f"<div style='height:36px;background:{bg};{border}border-radius:6px;margin:2px 0;"
                f"display:flex;align-items:center;padding:0 8px;font-size:0.82rem;color:#dce8ff;'>"
                f"{flag_tag}{tname}{score_tag}</div>")

    def match_card(match, result, phase_label=""):
        home = match.get("home", "")
        away = match.get("away", "")
        winner = result.get("winner", "")
        hg = result.get("home_goals")
        ag = result.get("away_goals")
        played = result.get("played", False)
        h_score = hg if played else None
        a_score = ag if played else None
        h_win = winner == home and played
        a_win = winner == away and played
        html = "<div style='background:#091525;border:1px solid #1a2a4a;border-radius:8px;padding:6px 8px;margin-bottom:6px;min-width:200px;'>"
        if phase_label:
            html += f"<div style='font-size:0.65rem;color:#406080;text-transform:uppercase;margin-bottom:4px;'>{phase_label}</div>"
        html += team_cell(home, h_win, h_score)
        html += team_cell(away, a_win, a_score)
        html += "</div>"
        return html

    octavos = bracket.get("octavos", [])
    cuartos = bracket.get("cuartos", [])
    semis   = bracket.get("semis", [])
    final   = bracket.get("final", [])

    if not octavos:
        return

    html = "<div style='overflow-x:auto;padding-bottom:8px;'>"
    html += "<div style='display:flex;gap:16px;align-items:flex-start;min-width:800px;'>"

    # ── Octavos (columna izq y der) ──────────────────────────────────
    html += "<div style='flex:0 0 220px;'>"
    html += "<div style='font-size:0.7rem;color:#406080;text-transform:uppercase;margin-bottom:6px;letter-spacing:1px;'>Octavos</div>"
    for i, m in enumerate(octavos[:4]):
        r = results.get(f"euro_octavos_{i}", {})
        html += match_card(m, r, f"M{i+1}")
    html += "</div>"

    # ── Cuartos izq ─────────────────────────────────────────────────
    html += "<div style='flex:0 0 220px;margin-top:44px;'>"
    html += "<div style='font-size:0.7rem;color:#406080;text-transform:uppercase;margin-bottom:6px;letter-spacing:1px;'>Cuartos</div>"
    for i, m in enumerate(cuartos[:2]):
        r = results.get(f"euro_cuartos_{i}", {})
        html += match_card(m, r)
    html += "</div>"

    # ── Semis ────────────────────────────────────────────────────────
    html += "<div style='flex:0 0 220px;margin-top:88px;'>"
    html += "<div style='font-size:0.7rem;color:#406080;text-transform:uppercase;margin-bottom:6px;letter-spacing:1px;'>Semis</div>"
    for i, m in enumerate(semis[:2]):
        r = results.get(f"euro_semis_{i}", {})
        html += match_card(m, r)
    html += "</div>"

    # ── Final ────────────────────────────────────────────────────────
    html += "<div style='flex:0 0 220px;margin-top:132px;'>"
    html += "<div style='font-size:0.7rem;color:#ffd700;text-transform:uppercase;margin-bottom:6px;letter-spacing:1px;font-weight:700;'>🏆 Final</div>"
    for i, m in enumerate(final[:1]):
        r = results.get(f"euro_final_{i}", {})
        html += match_card(m, r, "Gran Final")
    html += "</div>"

    # ── Cuartos der ──────────────────────────────────────────────────
    html += "<div style='flex:0 0 220px;margin-top:44px;'>"
    html += "<div style='font-size:0.7rem;color:#406080;text-transform:uppercase;margin-bottom:6px;letter-spacing:1px;'>Cuartos</div>"
    for i, m in enumerate(cuartos[2:4]):
        r = results.get(f"euro_cuartos_{i+2}", {})
        html += match_card(m, r)
    html += "</div>"

    # ── Octavos der ─────────────────────────────────────────────────
    html += "<div style='flex:0 0 220px;'>"
    html += "<div style='font-size:0.7rem;color:#406080;text-transform:uppercase;margin-bottom:6px;letter-spacing:1px;'>Octavos</div>"
    for i, m in enumerate(octavos[4:8]):
        r = results.get(f"euro_octavos_{i+4}", {})
        html += match_card(m, r, f"M{i+5}")
    html += "</div>"

    html += "</div></div>"

    # Campeón si existe
    winner_final = results.get("euro_final_0", {}).get("winner")
    if winner_final:
        from data import TEAM_DISPLAY_NAMES
        fu = get_flag_url(winner_final, 32, 24)
        flag_tag = f"<img src='{fu}' style='vertical-align:middle;margin-right:8px;border-radius:3px;' width='32' height='24'>" if fu else ""
        tname = TEAM_DISPLAY_NAMES.get(winner_final, winner_final)
        html += (f"<div style='background:linear-gradient(135deg,#1a1300,#2a2000);border:2px solid #ffd700;"
                 f"border-radius:12px;padding:16px 20px;margin-top:16px;text-align:center;'>"
                 f"<div style='font-size:1.6rem;font-family:Bebas Neue,sans-serif;color:#ffd700;letter-spacing:2px;'>"
                 f"🏆 CAMPEÓN EUROCOPA FMMJ</div>"
                 f"<div style='font-size:1.2rem;color:#fff;margin-top:6px;font-weight:700;'>{flag_tag}{tname}</div>"
                 f"</div>")

    st.markdown(html, unsafe_allow_html=True)
    st.markdown("---")


def _determine_euro_classified(state, euro, results, bracket):
    if euro.get("direct_qualified"):
        return  # already computed

    champion = results.get("euro_final_0", {}).get("winner")
    runner_up = None
    for m in bracket.get("final", []):
        if m.get("winner"):
            runner_up = m["home"] if m["winner"] == m["away"] else m["away"]

    semi_losers = []
    for i, m in enumerate(bracket.get("semis", [])):
        r = results.get(f"euro_semis_{i}", {})
        if r.get("winner"):
            loser = m["home"] if r["winner"] == m["away"] else m["away"]
            if loser and loser not in semi_losers: semi_losers.append(loser)

    third = results.get("euro_tercer_0", {}).get("winner")

    direct = [t for t in [champion, runner_up, third] + semi_losers if t]
    direct = list(dict.fromkeys(direct))[:5]
    euro["direct_qualified"] = direct

    # Build playoff pool: cuartos losers + octavos losers + 4tos de grupo + 2 peores terceros
    cuartos_losers = []
    for i, m in enumerate(bracket.get("cuartos", [])):
        r = results.get(f"euro_cuartos_{i}", {})
        if r.get("winner"):
            loser = m["home"] if r["winner"] == m["away"] else m["away"]
            if loser: cuartos_losers.append(loser)

    octavos_losers = []
    for i, m in enumerate(bracket.get("octavos", [])):
        r = results.get(f"euro_octavos_{i}", {})
        if r.get("winner"):
            loser = m["home"] if r["winner"] == m["away"] else m["away"]
            if loser: octavos_losers.append(loser)

    fourths = euro.get("_fourths", [])
    worst_thirds = euro.get("_worst_thirds", [])

    pool = cuartos_losers + octavos_losers + worst_thirds + fourths
    pool = [t for t in pool if t and t not in direct]
    pool = list(dict.fromkeys(pool))[:16]
    euro["playoff_pool"] = pool
    euro["phase"] = "playoff_uefa"

    if champion: update_ranking(champion, RANKING_POINTS["champion"], state)
    if runner_up: update_ranking(runner_up, RANKING_POINTS["runner_up"], state)
    if third: update_ranking(third, RANKING_POINTS["third"], state)
    save_state()
    st.rerun()


def _show_euro_playoff(state, euro):
    st.markdown("### 🔄 Playoff UEFA — 8 cupos adicionales")
    st.caption("Puestos 6–21: 4 grupos de 4, todos contra todos. Top 2 de cada grupo → Mundial.")

    if euro["phase"] not in ["playoff_uefa", "completado"]:
        st.info("Se habilita al finalizar las llaves de la Eurocopa.")
        return

    pb = euro.setdefault("playoff_bracket", {})
    pool = euro.get("playoff_pool", [])

    if not pool:
        st.warning("No hay equipos para el playoff.")
        return

    if not pb.get("groups"):
        st.markdown("#### Sorteo Playoff UEFA (4 grupos de 4)")
        manual_group_setup(state, "_euro_playoff_tmp", pool[:16], num_groups=4, teams_per_group=4,
                           confirm_label="Confirmar Grupos Playoff UEFA")
        tmp = state.get("_euro_playoff_tmp", {})
        if tmp.get("setup_done"):
            pb["groups"] = tmp["groups"]
            del state["_euro_playoff_tmp"]
            if "_euro_playoff_tmp" in st.session_state:
                del st.session_state["_euro_playoff_tmp"]
            save_state(); st.rerun()
        return

    groups = pb["groups"]
    results = pb.setdefault("results", {})
    standings_all = pb.setdefault("standings", {})
    all_complete = True

    for g, teams in groups.items():
        with st.expander(f"Grupo Playoff {g} — {' · '.join([display_name(t) for t in teams])}", expanded=False):
            jornadas = get_jornadas(teams)
            jtabs = st.tabs([f"J{i+1}" for i in range(len(jornadas))] + ["📊 Tabla"])
            for ji, jornada in enumerate(jornadas):
                with jtabs[ji]:
                    for home, away in jornada:
                        mk = match_key(home, away)
                        pkey = f"eupb_{g}_{mk}"
                        show_match_row(home, away, pkey, results, "Playoff UEFA", state, show_scorers=False)
                        if results.get(pkey, {}).get("played"):
                            results[mk] = results[pkey]
                        elif not results.get(mk, {}).get("played"):
                            all_complete = False
            with jtabs[-1]:
                standings = calculate_standings(teams, results)
                standings_all[g] = standings
                render_standings_table(standings, advancing=2)

    if all_complete or st.checkbox("🔓 Forzar clasificados playoff UEFA"):
        if st.button("✅ Confirmar Clasificados Playoff UEFA", type="primary"):
            top2 = []
            for g, stds in standings_all.items():
                top2 += [s["team"] for s in stds[:2]]
            euro["qualified"] = list(dict.fromkeys(euro.get("direct_qualified", []) + top2))[:13]
            euro["phase"] = "completado"
            for t in euro["qualified"]:
                if t not in state["world_cup_qualified"]:
                    state["world_cup_qualified"].append(t)
            save_state(); st.rerun()


def _show_euro_classified(state, euro):
    st.markdown("### 🌍 Clasificados UEFA al Mundial FMMJ")
    direct = euro.get("direct_qualified", [])
    qualified = euro.get("qualified", [])
    playoff_q = [t for t in qualified if t not in direct]

    medals = ["🥇","🥈","🥉","4️⃣","5️⃣"]
    if direct:
        st.markdown("#### ✅ Cupos Directos (Top 5)")
        for i, t in enumerate(direct):
            st.markdown(f"{medals[i] if i < 5 else '✅'} {flag_html(t)} **{display_name(t)}**", unsafe_allow_html=True)
    if playoff_q:
        st.markdown("#### 🔄 Vía Playoff UEFA (8 cupos)")
        for t in playoff_q:
            st.markdown(f"✅ {flag_html(t)} **{display_name(t)}**", unsafe_allow_html=True)
    st.info(f"**Total UEFA: {len(qualified)}/13**")


# ══════════════════════════════════════════════════════════════
# COPA AMERICA — 10 CONMEBOL + 6 invitadas
# 4 grupos de 4 → Cuartos → Semis → Final
# Campeón directo. 2do-7mo → playoff todos contra todos.
# Top 3 → mundial. 4to → repechaje.
# ══════════════════════════════════════════════════════════════
def show_copa_america():
    state = get_state()
    ca = state["copa_america"]

    col_logo, col_title = st.columns([1, 9])
    with col_logo:
        try: st.image("conmebol.png", width=72)
        except: st.markdown("🌎")
    with col_title:
        st.markdown("""<div style='background:linear-gradient(135deg,#004020 0%,#008844 60%,#004020 100%);
            border-radius:16px;padding:20px 28px;margin-bottom:20px;'>
            <div style='font-size:1.9rem;font-weight:900;color:#ffd700;font-family:Bebas Neue,sans-serif;letter-spacing:2px;'>COPA AMÉRICA FMMJ</div>
            <div style='color:#90ffcc;font-size:.9rem;'>10 CONMEBOL + 6 invitadas · 4 grupos de 4 · Campeón directo + Playoff → 4 cupos al Mundial</div>
        </div>""", unsafe_allow_html=True)

    tabs = st.tabs(["🌎 Invitadas", "🎲 Sorteo", "📊 Grupos", "⚽ Llaves", "🔄 Playoff", "🌍 Clasificados"])

    with tabs[0]:
        _ca_guest_selection(state, ca)

    with tabs[1]:
        if not ca.get("guests"):
            st.info("Primero selecciona las 6 invitadas.")
        elif not ca.get("setup_done"):
            all_teams = CONMEBOL_TEAMS + ca["guests"]
            manual_group_setup(state, "copa_america", all_teams, num_groups=4, teams_per_group=4,
                               confirm_label="Confirmar Grupos Copa América")
        else:
            st.success("✅ Grupos confirmados")
            if st.button("✏️ Editar Grupos", type="secondary"):
                ca["setup_done"] = False
                if "draft_copa_america" in st.session_state: del st.session_state["draft_copa_america"]
                save_state(); st.rerun()
            _render_groups_grid(ca["groups"], cols_n=2)

    with tabs[2]:
        if not ca.get("setup_done"):
            st.info("Confirma los grupos primero.")
        else:
            all_done = show_group_jornadas(state, ca, "Copa", advancing=2)
            if all_done or st.checkbox("🔓 Forzar avance", key="ca_force"):
                if ca["phase"] == "grupos":
                    if st.button("⚽ Generar Llaves Copa América", type="primary"):
                        _build_ca_knockout(state, ca)
                        save_state(); st.rerun()

    with tabs[3]:
        if ca["phase"] not in ["llaves", "playoff", "completado"]:
            st.info("Completa la fase de grupos primero.")
        else:
            _show_ca_knockout(state, ca)

    with tabs[4]:
        _show_ca_playoff(state, ca)

    with tabs[5]:
        _show_ca_classified(state, ca)


def _ca_guest_selection(state, ca):
    st.markdown("### 🌎 Selección de Equipos Invitados")
    st.caption("Elige exactamente 6 selecciones de CONCACAF, AFC, CAF u OFC (no UEFA)")

    if ca.get("guests"):
        st.success(f"✅ Invitadas: {', '.join([display_name(g) for g in ca['guests']])}")
        if st.button("🔄 Cambiar invitadas"):
            ca["guests"] = []
            ca["setup_done"] = False
            save_state(); st.rerun()
        return

    available = COPA_AMERICA_GUESTS_POOL
    selected = []
    cols = st.columns(3)
    for idx, team in enumerate(available):
        with cols[idx % 3]:
            if st.checkbox(f"{display_name(team)}", key=f"ca_guest_{team}"):
                selected.append(team)

    st.markdown(f"**Seleccionadas: {len(selected)}/6**")
    if len(selected) > 6:
        st.error("Máximo 6 invitadas.")
    elif len(selected) == 6:
        if st.button("✅ Confirmar Invitadas", type="primary"):
            ca["guests"] = selected
            save_state(); st.rerun()


def _build_ca_knockout(state, ca):
    standings = ca.get("group_standings", {})
    groups = sorted(standings.keys())
    firsts  = [standings[g][0]["team"] for g in groups if standings.get(g)]
    seconds = [standings[g][1]["team"] for g in groups if len(standings.get(g,[])) > 1]
    thirds  = [standings[g][2]["team"] for g in groups if len(standings.get(g,[])) > 2]
    fourths = [standings[g][3]["team"] for g in groups if len(standings.get(g,[])) > 3]

    qf = [
        (firsts[0], seconds[1]),
        (firsts[1], seconds[0]),
        (firsts[2], seconds[3]) if len(firsts)>2 and len(seconds)>3 else (firsts[2], seconds[2]),
        (firsts[3], seconds[2]) if len(firsts)>3 else (seconds[3], thirds[0] if thirds else ""),
    ]
    ca["knockout_bracket"] = {
        "cuartos": [{"home": a, "away": b, "winner": None} for a, b in qf if a and b],
        "semis": [], "tercer_puesto": [], "final": []
    }
    ca["knockout_results"] = {}
    ca["playoff_pool"] = thirds + fourths
    ca["phase"] = "llaves"


def _show_ca_knockout(state, ca):
    bracket = ca.setdefault("knockout_bracket", {})
    results = ca.setdefault("knockout_results", {})
    phases = [
        ("cuartos", "🟡 Cuartos de Final", "semis"),
        ("semis",   "🟠 Semifinales",       "final"),
        ("final",   "🏆 GRAN FINAL Copa América", None),
    ]
    final_done = show_knockout_generic(state, ca, "Copa América FMMJ", phases, "ca")
    if final_done:
        champion = results.get("ca_final_0", {}).get("winner")
        if champion and not ca.get("champion"):
            ca["champion"] = champion
            ca["qualified_direct"] = [champion]
            # Add finalist + semi losers to playoff pool
            for m in bracket.get("final", []):
                if m.get("winner"):
                    runner = m["home"] if m["winner"] == m["away"] else m["away"]
                    pool = ca.get("playoff_pool", [])
                    if runner and runner not in pool: pool.insert(0, runner)
                    ca["playoff_pool"] = pool
            ca["phase"] = "playoff"
            update_ranking(champion, RANKING_POINTS["champion"], state)
            save_state(); st.rerun()


def _show_ca_playoff(state, ca):
    st.markdown("### 🔄 Playoff CONMEBOL — 3 cupos + 1 repechaje")
    st.caption("2do–7mo Copa América: todos contra todos. Top 3 → Mundial. 4to → Repechaje Internacional.")

    if ca["phase"] not in ["playoff", "completado"]:
        st.info("Se habilita al terminar las llaves.")
        return

    pool = ca.get("playoff_pool", [])
    if not pool:
        st.warning("No hay candidatos.")
        return

    pb = ca.setdefault("playoff_bracket", {})
    results = pb.setdefault("results", {})
    all_done = True
    pfx = "capb"

    fixtures = [(pool[i], pool[j]) for i in range(len(pool)) for j in range(i+1, len(pool))]
    st.markdown(f"**Participantes:** {', '.join([display_name(t) for t in pool])}")
    for home, away in fixtures:
        mk = match_key(home, away)
        key = f"{pfx}_{mk}"
        show_match_row(home, away, key, results, "Playoff CONMEBOL", state, show_scorers=False)
        if results.get(key, {}).get("played"):
            results[mk] = results[key]
        elif not results.get(mk, {}).get("played"):
            all_done = False

    standings = calculate_standings(pool, results)
    pb["standings"] = standings
    render_standings_table(standings, advancing=3, show_thirds=True)

    if all_done or st.checkbox("🔓 Forzar clasificados CONMEBOL"):
        if st.button("✅ Confirmar Clasificados CONMEBOL", type="primary"):
            champion = ca.get("champion")
            top3 = [s["team"] for s in standings[:3]]
            repechaje = standings[3]["team"] if len(standings) > 3 else None
            ca["qualified"] = ([champion] if champion else []) + top3
            ca["phase"] = "completado"
            if repechaje:
                state["playoff_teams"]["conmebol_slot"] = repechaje
            for t in ca["qualified"]:
                if t not in state["world_cup_qualified"]:
                    state["world_cup_qualified"].append(t)
            save_state(); st.rerun()


def _show_ca_classified(state, ca):
    st.markdown("### 🌍 Clasificados CONMEBOL al Mundial FMMJ")
    champion = ca.get("champion")
    if champion:
        st.markdown(f"🏆 **Campeón (Directo):** {flag_html(champion)} **{display_name(champion)}**", unsafe_allow_html=True)
    for t in ca.get("qualified", []):
        if t != champion:
            st.markdown(f"✅ {flag_html(t)} **{display_name(t)}**", unsafe_allow_html=True)
    rep = state["playoff_teams"].get("conmebol_slot")
    if rep:
        st.markdown(f"🔁 **Repechaje:** {flag_html(rep)} **{display_name(rep)}**", unsafe_allow_html=True)
    st.info(f"**Total CONMEBOL: {len(ca.get('qualified',[]))}/4**")


# ══════════════════════════════════════════════════════════════
# COPA AFRICA — CAF 10 equipos, 2 grupos de 5
# Campeón + Subcampeón directos.
# 3ro-7mo → playoff todos contra todos → top 3 → mundial.
# ══════════════════════════════════════════════════════════════
def show_copa_africa():
    state = get_state()
    tour = state["copa_africa"]

    col_logo, col_title = st.columns([1, 9])
    with col_logo:
        try: st.image("caf.png", width=72)
        except: st.markdown("🌍")
    with col_title:
        st.markdown("""<div style='background:linear-gradient(135deg,#6a3800 0%,#c07000 60%,#6a3800 100%);
            border-radius:16px;padding:20px 28px;margin-bottom:20px;'>
            <div style='font-size:1.9rem;font-weight:900;color:#fff;font-family:Bebas Neue,sans-serif;letter-spacing:2px;'>COPA ÁFRICA FMMJ</div>
            <div style='color:#ffd088;font-size:.9rem;'>10 selecciones CAF · 2 grupos de 5 · Campeón + Subcampeón directos + Playoff → 5 cupos</div>
        </div>""", unsafe_allow_html=True)

    tabs = st.tabs(["🎲 Grupos", "📊 Fase Grupos", "⚽ Llaves", "🔄 Playoff CAF", "🌍 Clasificados"])

    with tabs[0]:
        if not tour.get("setup_done"):
            manual_group_setup(state, "copa_africa", CAF_TEAMS, num_groups=2, teams_per_group=5,
                               confirm_label="Confirmar Grupos Copa África")
        else:
            st.success("✅ Grupos confirmados")
            if st.button("✏️ Editar", type="secondary"):
                tour["setup_done"] = False
                if "draft_copa_africa" in st.session_state: del st.session_state["draft_copa_africa"]
                save_state(); st.rerun()
            _render_groups_grid(tour["groups"], cols_n=2)

    with tabs[1]:
        if not tour.get("setup_done"):
            st.info("Confirma los grupos primero.")
        else:
            all_done = show_group_jornadas(state, tour, "CAF", advancing=2)
            if all_done or st.checkbox("🔓 Forzar avance", key="caf_force"):
                if tour["phase"] == "grupos":
                    if st.button("⚽ Generar Cuartos CAF", type="primary"):
                        _build_caf_knockout(state, tour)
                        save_state(); st.rerun()

    with tabs[2]:
        if tour["phase"] not in ["llaves", "playoff", "completado"]:
            st.info("Completa la fase de grupos primero.")
        else:
            _show_caf_knockout(state, tour)

    with tabs[3]:
        _show_caf_playoff(state, tour)

    with tabs[4]:
        _show_caf_classified(state, tour)


def _build_caf_knockout(state, tour):
    standings = tour.get("group_standings", {})
    groups = sorted(standings.keys())
    top2, thirds, rest = [], [], []
    for g in groups:
        s = standings.get(g, [])
        if len(s) >= 1: top2.append(s[0]["team"])
        if len(s) >= 2: top2.append(s[1]["team"])
        if len(s) >= 3: thirds.append(s[2]["team"])
        for row in s[3:]: rest.append(row["team"])

    # Semifinales: 1A vs 2B, 2A vs 1B
    semis = [
        {"home": top2[0], "away": top2[3], "winner": None},
        {"home": top2[2], "away": top2[1], "winner": None},
    ] if len(top2) >= 4 else []

    tour["knockout_bracket"] = {
        "semis": semis, "tercer_puesto": [], "final": []
    }
    tour["knockout_results"] = {}
    tour["playoff_pool"] = thirds + rest
    tour["phase"] = "llaves"


def _show_caf_knockout(state, tour):
    bracket = tour.setdefault("knockout_bracket", {})
    results = tour.setdefault("knockout_results", {})
    phases = [
        ("semis", "🟠 Semifinales", "final"),
        ("final", "🏆 GRAN FINAL Copa África", None),
    ]
    final_done = show_knockout_generic(state, tour, "Copa África FMMJ", phases, "caf")
    if final_done:
        res_f = results.get("caf_final_0", {})
        if res_f.get("winner") and not tour.get("champion"):
            champ = res_f["winner"]
            runner = None
            for m in bracket.get("final", []):
                if m.get("winner"):
                    runner = m["home"] if m["winner"] == m["away"] else m["away"]
            tour["champion"] = champ
            tour["finalist"] = runner
            tour["qualified_direct"] = [t for t in [champ, runner] if t]
            # Add semi losers to playoff pool
            for i, m in enumerate(bracket.get("semis", [])):
                r = results.get(f"caf_semis_{i}", {})
                if r.get("winner"):
                    loser = m["home"] if r["winner"] == m["away"] else m["away"]
                    if loser and loser not in tour["playoff_pool"]:
                        tour["playoff_pool"].append(loser)
            tour["phase"] = "playoff"
            update_ranking(champ, RANKING_POINTS["champion"], state)
            if runner: update_ranking(runner, RANKING_POINTS["runner_up"], state)
            save_state(); st.rerun()


def _show_caf_playoff(state, tour):
    st.markdown("### 🔄 Playoff CAF — 3 cupos adicionales")
    st.caption("3ro–7mo: todos contra todos. Top 3 → Mundial.")
    if tour["phase"] not in ["playoff", "completado"]:
        st.info("Se habilita al terminar las llaves.")
        return

    pool = tour.get("playoff_pool", [])
    if not pool:
        st.warning("No hay candidatos.")
        return

    pb = tour.setdefault("playoff_bracket", {})
    results = pb.setdefault("results", {})
    all_done = True

    fixtures = [(pool[i], pool[j]) for i in range(len(pool)) for j in range(i+1, len(pool))]
    for home, away in fixtures:
        mk = match_key(home, away)
        key = f"cafpb_{mk}"
        show_match_row(home, away, key, results, "Playoff CAF", state, show_scorers=False)
        if results.get(key, {}).get("played"):
            results[mk] = results[key]
        elif not results.get(mk, {}).get("played"):
            all_done = False

    standings = calculate_standings(pool, results)
    pb["standings"] = standings
    render_standings_table(standings, advancing=3)

    if all_done or st.checkbox("🔓 Forzar clasificados CAF"):
        if st.button("✅ Confirmar Clasificados CAF", type="primary"):
            top3 = [s["team"] for s in standings[:3]]
            tour["qualified"] = list(dict.fromkeys(tour.get("qualified_direct", []) + top3))
            tour["phase"] = "completado"
            for t in tour["qualified"]:
                if t not in state["world_cup_qualified"]:
                    state["world_cup_qualified"].append(t)
            save_state(); st.rerun()


def _show_caf_classified(state, tour):
    st.markdown("### 🌍 Clasificados CAF al Mundial FMMJ")
    direct = tour.get("qualified_direct", [])
    if direct:
        st.markdown("#### ✅ Campeón y Subcampeón (Directos)")
        for t in direct:
            st.markdown(f"✅ {flag_html(t)} **{display_name(t)}**", unsafe_allow_html=True)
    playoff_q = [t for t in tour.get("qualified", []) if t not in direct]
    if playoff_q:
        st.markdown("#### 🔄 Vía Playoff CAF")
        for t in playoff_q:
            st.markdown(f"✅ {flag_html(t)} **{display_name(t)}**", unsafe_allow_html=True)
    st.info(f"**Total CAF: {len(tour.get('qualified',[]))}/5**")


# ══════════════════════════════════════════════════════════════
# TORNEOS 6 EQUIPOS: Copa Oro (CONCACAF) y Copa Asia (AFC)
# 2 grupos de 3 → Semis → Final
# CONCACAF: campeón directo, 2do-4to playoff → top 2 + 3ro repechaje
# AFC:      campeón directo, 2do-5to playoff → top 3 + 4to repechaje
# ══════════════════════════════════════════════════════════════
def _show_6team_tournament(state, tour_key, torneo_name, teams, direct_spots,
                            playoff_spots, repechaje_slot_key, header_html):
    tour = state[tour_key]

    st.markdown(header_html, unsafe_allow_html=True)
    tabs = st.tabs(["🎲 Grupos", "📊 Fase Grupos", "⚽ Llaves", "🔄 Playoff", "🌍 Clasificados"])

    with tabs[0]:
        if not tour.get("setup_done"):
            manual_group_setup(state, tour_key, teams, num_groups=2, teams_per_group=3,
                               confirm_label=f"Confirmar Grupos {torneo_name}")
        else:
            st.success("✅ Grupos confirmados")
            if st.button("✏️ Editar", type="secondary", key=f"edit_{tour_key}"):
                tour["setup_done"] = False
                if f"draft_{tour_key}" in st.session_state: del st.session_state[f"draft_{tour_key}"]
                save_state(); st.rerun()
            _render_groups_grid(tour["groups"], cols_n=2)

    with tabs[1]:
        if not tour.get("setup_done"):
            st.info("Confirma los grupos primero.")
        else:
            all_done = show_group_jornadas(state, tour, torneo_name[:4], advancing=2)
            if all_done or st.checkbox(f"🔓 Forzar avance", key=f"force_{tour_key}"):
                if tour["phase"] == "grupos":
                    if st.button(f"⚽ Generar Semis {torneo_name}", type="primary", key=f"gen_{tour_key}"):
                        _build_6team_knockout(state, tour)
                        save_state(); st.rerun()

    with tabs[2]:
        if tour["phase"] not in ["llaves", "playoff", "completado"]:
            st.info("Completa grupos primero.")
        else:
            _show_6team_knockout(state, tour, torneo_name, tour_key)

    with tabs[3]:
        _show_6team_playoff(state, tour, torneo_name, tour_key, playoff_spots, repechaje_slot_key)

    with tabs[4]:
        _show_6team_classified(state, tour, torneo_name, repechaje_slot_key)


def _build_6team_knockout(state, tour):
    standings = tour.get("group_standings", {})
    groups = sorted(standings.keys())
    top2, thirds = [], []
    for g in groups:
        s = standings.get(g, [])
        if len(s) >= 1: top2.append(s[0]["team"])
        if len(s) >= 2: top2.append(s[1]["team"])
        if len(s) >= 3: thirds.append(s[2]["team"])

    semis = []
    if len(top2) >= 4:
        semis = [
            {"home": top2[0], "away": top2[3], "winner": None},
            {"home": top2[2], "away": top2[1], "winner": None},
        ]
    tour["knockout_bracket"] = {"semis": semis, "tercer_puesto": [], "final": []}
    tour["knockout_results"] = {}
    tour["playoff_pool"] = thirds[:]
    tour["phase"] = "llaves"


def _show_6team_knockout(state, tour, torneo_name, tour_key):
    bracket = tour.setdefault("knockout_bracket", {})
    results = tour.setdefault("knockout_results", {})
    pfx = tour_key[:4]
    phases = [
        ("semis", "🟠 Semifinales", "final"),
        ("final", "🏆 GRAN FINAL", None),
    ]
    final_done = show_knockout_generic(state, tour, torneo_name, phases, pfx)
    if final_done:
        champ = results.get(f"{pfx}_final_0", {}).get("winner")
        if champ and not tour.get("champion"):
            tour["champion"] = champ
            # Add runner up + semi losers to playoff pool
            for m in bracket.get("final", []):
                if m.get("winner"):
                    runner = m["home"] if m["winner"] == m["away"] else m["away"]
                    pool = tour.get("playoff_pool", [])
                    if runner and runner not in pool: pool.insert(0, runner)
                    tour["playoff_pool"] = pool
            for i, m in enumerate(bracket.get("semis", [])):
                r = results.get(f"{pfx}_semis_{i}", {})
                if r.get("winner"):
                    loser = m["home"] if r["winner"] == m["away"] else m["away"]
                    pool = tour.get("playoff_pool", [])
                    if loser and loser not in pool: pool.append(loser)
                    tour["playoff_pool"] = pool
            tour["phase"] = "playoff"
            update_ranking(champ, RANKING_POINTS["champion"], state)
            save_state(); st.rerun()


def _show_6team_playoff(state, tour, torneo_name, tour_key, playoff_spots, repechaje_slot_key):
    st.markdown(f"### 🔄 Playoff {torneo_name}")
    st.caption(f"2do–5to: todos contra todos. Top {playoff_spots} → Mundial.{' El siguiente → Repechaje.' if repechaje_slot_key else ''}")
    if tour["phase"] not in ["playoff", "completado"]:
        st.info("Se habilita al terminar las llaves.")
        return

    pool = tour.get("playoff_pool", [])
    if not pool:
        st.warning("No hay candidatos.")
        return

    pb = tour.setdefault("playoff_bracket", {})
    results = pb.setdefault("results", {})
    all_done = True
    pfx = f"{tour_key[:4]}pb"

    fixtures = [(pool[i], pool[j]) for i in range(len(pool)) for j in range(i+1, len(pool))]
    for home, away in fixtures:
        mk = match_key(home, away)
        key = f"{pfx}_{mk}"
        show_match_row(home, away, key, results, f"Playoff {torneo_name}", state, show_scorers=False)
        if results.get(key, {}).get("played"):
            results[mk] = results[key]
        elif not results.get(mk, {}).get("played"):
            all_done = False

    standings = calculate_standings(pool, results)
    pb["standings"] = standings
    render_standings_table(standings, advancing=playoff_spots)

    if all_done or st.checkbox(f"🔓 Forzar resultado {torneo_name}", key=f"force_pb_{tour_key}"):
        if st.button(f"✅ Confirmar Clasificados {torneo_name}", type="primary", key=f"confirm_{tour_key}"):
            champion = tour.get("champion")
            top_n = [s["team"] for s in standings[:playoff_spots]]
            repechaje = standings[playoff_spots]["team"] if len(standings) > playoff_spots else None
            tour["qualified"] = ([champion] if champion else []) + top_n
            tour["phase"] = "completado"
            if repechaje and repechaje_slot_key:
                state["playoff_teams"][repechaje_slot_key] = repechaje
            for t in tour["qualified"]:
                if t not in state["world_cup_qualified"]:
                    state["world_cup_qualified"].append(t)
            save_state(); st.rerun()


def _show_6team_classified(state, tour, torneo_name, repechaje_slot_key):
    st.markdown(f"### 🌍 Clasificados {torneo_name}")
    champion = tour.get("champion")
    if champion:
        st.markdown(f"🏆 **Campeón (Directo):** {flag_html(champion)} **{display_name(champion)}**", unsafe_allow_html=True)
    for t in tour.get("qualified", []):
        if t != champion:
            st.markdown(f"✅ {flag_html(t)} **{display_name(t)}**", unsafe_allow_html=True)
    if repechaje_slot_key:
        rep = state["playoff_teams"].get(repechaje_slot_key)
        if rep:
            st.markdown(f"🔁 **Repechaje:** {flag_html(rep)} **{display_name(rep)}**", unsafe_allow_html=True)
    st.info(f"**Total {torneo_name}: {len(tour.get('qualified',[]))} clasificados**")


def show_copa_oro():
    state = get_state()
    col_logo, col_title = st.columns([1, 9])
    with col_logo:
        try: st.image("concacaf.png", width=72)
        except: st.markdown("⭐")
    header = """<div style='background:linear-gradient(135deg,#600000 0%,#cc0000 60%,#600000 100%);
        border-radius:16px;padding:20px 28px;margin-bottom:20px;'>
        <div style='font-size:1.9rem;font-weight:900;color:#ffd700;font-family:Bebas Neue,sans-serif;letter-spacing:2px;'>COPA ORO FMMJ</div>
        <div style='color:#ffaaaa;font-size:.9rem;'>6 selecciones CONCACAF · 2 grupos de 3 · Campeón directo + Playoff → 3 cupos | 4to → Repechaje</div>
    </div>"""
    with col_title:
        pass
    _show_6team_tournament(state, "copa_oro", "Copa Oro FMMJ", CONCACAF_TEAMS,
                            direct_spots=1, playoff_spots=2,
                            repechaje_slot_key="concacaf_slot",
                            header_html=header)


def show_copa_asia():
    state = get_state()
    col_logo, col_title = st.columns([1, 9])
    with col_logo:
        try: st.image("afc.png", width=72)
        except: st.markdown("🌏")
    header = """<div style='background:linear-gradient(135deg,#350060 0%,#6600cc 60%,#350060 100%);
        border-radius:16px;padding:20px 28px;margin-bottom:20px;'>
        <div style='font-size:1.9rem;font-weight:900;color:#ffd700;font-family:Bebas Neue,sans-serif;letter-spacing:2px;'>COPA ASIA FMMJ</div>
        <div style='color:#ddaaff;font-size:.9rem;'>6 selecciones AFC · 2 grupos de 3 · Campeón directo + Playoff → 4 cupos | 5to → Repechaje</div>
    </div>"""
    with col_title:
        pass
    _show_6team_tournament(state, "copa_asia", "Copa Asia FMMJ", AFC_TEAMS,
                            direct_spots=1, playoff_spots=3,
                            repechaje_slot_key="afc_slot",
                            header_html=header)


# ══════════════════════════════════════════════════════════════
# REPECHAJE INTERNACIONAL
# CONMEBOL vs New Zealand — CONCACAF vs AFC
# Ida y vuelta — ganadores = últimos 2 cupos
# ══════════════════════════════════════════════════════════════
def show_repechaje():
    state = get_state()
    playoff = state["playoff_teams"]
    pr = state.setdefault("playoff_results", {})

    st.markdown("""<div style='background:linear-gradient(135deg,#181818 0%,#282828 50%,#181818 100%);
        border:2px solid #ffd700;border-radius:16px;padding:22px 30px;margin-bottom:20px;'>
        <div style='font-size:1.9rem;font-weight:900;color:#ffd700;font-family:Bebas Neue,sans-serif;letter-spacing:2px;'>🔁 REPECHAJE INTERNACIONAL FMMJ</div>
        <div style='color:#aaa;font-size:.9rem;'>2 llaves ida y vuelta · Los ganadores obtienen los últimos 2 cupos al Mundial</div>
    </div>""", unsafe_allow_html=True)

    conmebol_team = playoff.get("conmebol_slot")
    ofc_team = "New Zealand"
    concacaf_team = playoff.get("concacaf_slot")
    afc_team = playoff.get("afc_slot")

    tabs = st.tabs(["🌎 Llave 1: CONMEBOL vs OFC", "🌏 Llave 2: CONCACAF vs AFC", "✅ Resultados"])

    with tabs[0]:
        st.markdown("### 🌎 Llave 1: CONMEBOL vs OFC")
        if not conmebol_team:
            st.warning("⏳ Esperando 4to CONMEBOL (Playoff Copa América).")
        else:
            _show_tie(state, "llave1", conmebol_team, ofc_team, "slot1", pr)

    with tabs[1]:
        st.markdown("### 🌏 Llave 2: CONCACAF vs AFC")
        if not concacaf_team:
            st.warning("⏳ Esperando 3er Copa Oro (Playoff CONCACAF).")
        elif not afc_team:
            st.warning("⏳ Esperando 4to Copa Asia (Playoff AFC).")
        else:
            _show_tie(state, "llave2", concacaf_team, afc_team, "slot2", pr)

    with tabs[2]:
        st.markdown("### ✅ Clasificados vía Repechaje")
        slot1 = pr.get("slot1")
        slot2 = pr.get("slot2")
        for slot, label in [(slot1, "Llave 1 (CONMEBOL/OFC)"), (slot2, "Llave 2 (CONCACAF/AFC)")]:
            if slot:
                st.markdown(
                    f"<div style='background:#0d4f2e;border-radius:8px;padding:10px;color:#4eff91;font-weight:700;margin-bottom:8px;'>"
                    f"🎉 {label}: {flag_html(slot)} {display_name(slot)}</div>",
                    unsafe_allow_html=True
                )
                if slot not in state["world_cup_qualified"]:
                    state["world_cup_qualified"].append(slot)
                    save_state()
        if slot1 and slot2:
            st.balloons()
            st.success("✅ ¡Los 32 clasificados están completos! Procede al Sorteo del Mundial.")


def _show_tie(state, tie_key, home_team, away_team, slot_key, pr):
    st.info(f"**{display_name(home_team)}** vs **{display_name(away_team)}** — Ida y Vuelta")
    for leg, leg_name, h, a in [
        ("ida",    "⚽ Partido de Ida",    home_team, away_team),
        ("vuelta", "⚽ Partido de Vuelta", away_team, home_team),
    ]:
        st.markdown(f"#### {leg_name}")
        key = f"rep_{tie_key}_{leg}"
        res = pr.get(key, {})
        c1, c2, c3, c4, c5 = st.columns([3, 1, 1, 3, 1])
        with c1: st.markdown(f"{flag_html(h)} **{display_name(h)}**", unsafe_allow_html=True)
        with c2:
            hg = st.number_input("", 0, 20, int(res.get("home_goals", 0)), key=f"{key}_hg", label_visibility="collapsed")
        with c3:
            ag = st.number_input("", 0, 20, int(res.get("away_goals", 0)), key=f"{key}_ag", label_visibility="collapsed")
        with c4: st.markdown(f"{flag_html(a)} **{display_name(a)}**", unsafe_allow_html=True)
        with c5:
            if st.button("💾", key=f"{key}_save"):
                pr[key] = {"home": h, "away": a, "home_goals": hg, "away_goals": ag, "played": True}
                save_state(); st.rerun()
        if res.get("played"):
            st.markdown(f"<small style='color:#507090'>✅ {display_name(h)} {res.get('home_goals',0)} - {res.get('away_goals',0)} {display_name(a)}</small>", unsafe_allow_html=True)

    ida    = pr.get(f"rep_{tie_key}_ida", {})
    vuelta = pr.get(f"rep_{tie_key}_vuelta", {})
    if ida.get("played") and vuelta.get("played"):
        ht = int(ida.get("home_goals", 0)) + int(vuelta.get("away_goals", 0))
        at = int(ida.get("away_goals", 0)) + int(vuelta.get("home_goals", 0))
        st.markdown(f"---\n**Global:** {display_name(home_team)} **{ht}** – **{at}** {display_name(away_team)}")
        if ht != at:
            winner = home_team if ht > at else away_team
            st.success(f"🎉 **Clasificado: {display_name(winner)}**")
            pr[slot_key] = winner
            save_state()
        else:
            st.warning("⚠️ Empate global → Definición por penales")
            opts = ["— Elige —", display_name(home_team), display_name(away_team)]
            sel = st.selectbox("Ganador en penales:", opts, key=f"rep_{tie_key}_pen")
            if sel != "— Elige —":
                winner = home_team if sel == display_name(home_team) else away_team
                if st.button(f"✅ Confirmar: {display_name(winner)}", key=f"rep_{tie_key}_pen_btn"):
                    pr[slot_key] = winner
                    save_state(); st.rerun()


# ══════════════════════════════════════════════════════════════
# RANKING FMMJ
# ══════════════════════════════════════════════════════════════
def show_ranking():
    state = get_state()
    ranking = state["ranking"]

    st.markdown("""<div style='background:linear-gradient(135deg,#06101e 0%,#0c1e3a 50%,#06101e 100%);
        border:2px solid #b89000;border-radius:16px;padding:22px 30px;margin-bottom:20px;'>
        <div style='font-size:1.9rem;font-weight:900;color:#c8a000;font-family:Bebas Neue,sans-serif;letter-spacing:2px;'>🏅 RANKING FMMJ</div>
        <div style='color:#888;font-size:.85rem;'>Puntuación dinámica actualizada con resultados de cada torneo clasificatorio</div>
    </div>""", unsafe_allow_html=True)

    sorted_ranking = sorted(ranking.items(), key=lambda x: -x[1])
    c1, c2, c3 = st.columns(3)
    with c1: conf_filter = st.selectbox("Confederación", ["Todas","UEFA","CONMEBOL","CAF","CONCACAF","AFC","OFC"])
    with c2: search = st.text_input("🔍 Buscar", placeholder="Nombre del país...")
    with c3: show_pts = st.checkbox("Mostrar puntos", value=True)

    conf_colors = {
        "UEFA":"#003580","CONMEBOL":"#006b3c","CAF":"#5a3000",
        "CONCACAF":"#5a0000","AFC":"#3a0060","OFC":"#1a3a1a"
    }

    html = """<table style='width:100%;border-collapse:collapse;font-size:0.84rem;margin-top:12px;'>
    <tr style='background:#091525;color:#5070a0;font-size:0.72rem;text-transform:uppercase;border-bottom:2px solid #182848;'>
        <th style='padding:8px;text-align:center;width:36px;'>#</th>
        <th style='padding:8px;text-align:left;'>Selección</th>
        <th style='padding:8px;text-align:center;'>Conf.</th>"""
    if show_pts: html += "<th style='padding:8px;text-align:center;'>Puntos</th>"
    html += "<th style='padding:8px;text-align:center;'>Estado</th></tr>"

    pos_real = 0
    for pos, (team, pts) in enumerate(sorted_ranking, 1):
        conf = get_team_confederation(team)
        if conf_filter != "Todas" and conf != conf_filter: continue
        if search and search.lower() not in display_name(team).lower() and search.lower() not in team.lower(): continue
        pos_real += 1
        qualified = team in state["world_cup_qualified"]
        status_color = "#00cc66" if qualified else "#506080"
        status = "✅ Clasificado" if qualified else "⏳"
        row_bg = "#0c3a22" if qualified else ("#091525" if pos_real % 2 == 0 else "#06101e")
        html += f"""<tr style='background:{row_bg};border-bottom:1px solid #101e38;'>
            <td style='padding:8px;text-align:center;color:#555;font-weight:700;'>{pos}</td>
            <td style='padding:8px;'>{flag_html(team)} <span style='font-weight:600;color:#dce8ff;'>{display_name(team)}</span></td>
            <td style='padding:8px;text-align:center;'>
                <span class='conf-chip' style='background:{conf_colors.get(conf,"#222")};color:#fff;'>{conf}</span>
            </td>"""
        if show_pts:
            html += f"<td style='padding:8px;text-align:center;color:#ffd700;font-weight:800;font-size:0.95rem;'>{pts}</td>"
        html += f"<td style='padding:8px;text-align:center;color:{status_color};font-size:0.8rem;'>{status}</td></tr>"
    html += "</table>"
    st.markdown(html, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# GOLEADORES
# ══════════════════════════════════════════════════════════════
def show_goleadores():
    state = get_state()
    st.markdown("""<div style='background:linear-gradient(135deg,#180028 0%,#360058 50%,#180028 100%);
        border:2px solid #ffd700;border-radius:16px;padding:22px 30px;margin-bottom:20px;'>
        <div style='font-size:1.9rem;font-weight:900;color:#ffd700;font-family:Bebas Neue,sans-serif;letter-spacing:2px;'>⚽ TABLA DE GOLEADORES FMMJ</div>
    </div>""", unsafe_allow_html=True)

    all_scorers = state.get("all_scorers", {})
    if not all_scorers:
        st.info("Sin goles registrados aún.")
        return

    rows = [
        {"name": d.get("name",""), "team": d.get("team",""), "goals": d.get("goals",0), "torneos": d.get("torneos",{})}
        for d in all_scorers.values() if d.get("goals",0) > 0
    ]
    rows.sort(key=lambda x: -x["goals"])

    c1, c2 = st.columns(2)
    with c1:
        torneos_list = sorted(set(t for r in rows for t in r["torneos"].keys()))
        torneo_filter = st.selectbox("🏆 Torneo", ["Todos"] + torneos_list)
    with c2:
        top_n = st.selectbox("Top", [10, 20, 50, "Todos"])

    filtered = []
    for r in rows:
        g = r["torneos"].get(torneo_filter, 0) if torneo_filter != "Todos" else r["goals"]
        if g > 0:
            filtered.append({**r, "goles_f": g})
    filtered.sort(key=lambda x: -x["goles_f"])
    if top_n != "Todos":
        filtered = filtered[:int(top_n)]

    if not filtered:
        st.info("Sin resultados.")
        return

    if len(filtered) >= 3:
        st.markdown("### 🥇 Podio")
        cols = st.columns(3)
        for i, (col, medal, color) in enumerate(zip(cols, ["🥇","🥈","🥉"], ["#ffd700","#c0c0c0","#cd7f32"])):
            if i < len(filtered):
                r = filtered[i]
                with col:
                    st.markdown(f"""<div style='background:#0a1020;border:2px solid {color};border-radius:12px;
                        padding:16px;text-align:center;'>
                        <div style='font-size:2rem;'>{medal}</div>
                        <div style='font-size:1rem;font-weight:700;color:#fff;'>{r['name']}</div>
                        <div style='font-size:0.8rem;color:#aaa;'>{flag_html(r['team'])} {display_name(r['team'])}</div>
                        <div style='font-size:2rem;font-weight:900;color:{color};'>{r['goles_f']}</div>
                    </div>""", unsafe_allow_html=True)

    st.markdown("### 📊 Tabla")
    import pandas as pd
    table = [{"#": pos, "Jugador": r["name"], "Selección": display_name(r["team"]),
              "Goles": r["goles_f"],
              "Torneos": " · ".join([f"{t}: {g}⚽" for t, g in r["torneos"].items()])}
             for pos, r in enumerate(filtered, 1)]
    st.dataframe(pd.DataFrame(table), use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════
# SORTEO Y MUNDIAL
# ══════════════════════════════════════════════════════════════
def show_world_cup_draw():
    state = get_state()
    wc = state["world_cup"]
    qualified = state["world_cup_qualified"]
    host = state.get("host", "Nigeria")

    if host and host not in qualified:
        qualified.insert(0, host)
        state["world_cup_qualified"] = qualified

    st.markdown(f"""<div style='background:linear-gradient(135deg,#b89000 0%,#ffd700 40%,#b89000 100%);
        border-radius:16px;padding:24px 32px;margin-bottom:20px;box-shadow:0 8px 32px rgba(200,160,0,.4);'>
        <div style='font-size:2.2rem;font-weight:900;color:#06101e;font-family:Bebas Neue,sans-serif;letter-spacing:3px;'>🌍 FMMJ WORLD CUP</div>
        <div style='font-size:.95rem;color:#333;margin-top:4px;'>32 selecciones · 8 grupos de 4 · Anfitrión: {flag_html(host)} {display_name(host)}</div>
    </div>""", unsafe_allow_html=True)

    tabs = st.tabs(["🏅 Clasificados","🎲 Bombos","🎯 Sorteo","📊 Grupos","⚽ Llaves"])
    with tabs[0]: _show_wc_classified(state, qualified)
    with tabs[1]: _show_wc_pots(state, wc, qualified)
    with tabs[2]: _show_wc_draw(state, wc, qualified)
    with tabs[3]: _show_wc_groups(state, wc)
    with tabs[4]: _show_wc_knockout(state, wc)


def _show_wc_classified(state, qualified):
    st.markdown("### 🏅 Las 32 Selecciones del FMMJ World Cup")
    cupos = {"UEFA":13,"CONMEBOL":4,"CAF":5,"CONCACAF":3,"AFC":4,"OFC":1}
    conf_groups = {}
    for t in qualified:
        c = get_team_confederation(t)
        conf_groups.setdefault(c, []).append(t)

    cols = st.columns(3)
    for i, (conf, teams) in enumerate(conf_groups.items()):
        with cols[i % 3]:
            total = cupos.get(conf, 0)
            html = f"<div style='background:#091525;border:1px solid #1a2a5a;border-radius:10px;padding:14px;margin-bottom:12px;'>"
            html += f"<div style='font-weight:700;color:#ffd700;margin-bottom:8px;font-family:Bebas Neue,sans-serif;'>{conf} — {len(teams)}/{total}</div>"
            for t in teams:
                html += f"<div style='padding:3px 0;'>{flag_html(t)} {display_name(t)}</div>"
            html += "</div>"
            st.markdown(html, unsafe_allow_html=True)
    st.info(f"**Total: {len(qualified)}/32**")
    if len(qualified) < 32:
        st.warning(f"Faltan {32 - len(qualified)} equipos por clasificar.")


def _show_wc_pots(state, wc, qualified):
    st.markdown("### 🎲 Bombos del Sorteo FMMJ World Cup")
    st.caption("4 bombos de 8 equipos por ranking FMMJ. El anfitrión encabeza el Bombo 1.")
    if len(qualified) < 32:
        st.warning(f"Aún no están los 32 equipos ({len(qualified)}/32).")
        return

    host = state.get("host")
    ranking = state["ranking"]
    teams_sorted = sorted(qualified, key=lambda t: -ranking.get(t, 0))
    if host and host in teams_sorted:
        teams_sorted.remove(host)
        teams_sorted.insert(0, host)

    pots = {i+1: teams_sorted[i*8:(i+1)*8] for i in range(4)}
    wc["pots"] = {str(k): v for k, v in pots.items()}

    pot_styles = [
        ("🟡 BOMBO 1","#1a1300","#ffd700"),
        ("🟢 BOMBO 2","#001a0d","#00cc66"),
        ("🔵 BOMBO 3","#00001a","#3388ff"),
        ("🔴 BOMBO 4","#1a000d","#ff6699"),
    ]
    cols = st.columns(2)
    for i, (label, bg, color) in enumerate(pot_styles):
        with cols[i % 2]:
            html = f"<div style='background:{bg};border:2px solid {color};border-radius:10px;padding:14px;margin-bottom:12px;'>"
            html += f"<div style='font-weight:800;color:{color};margin-bottom:10px;font-family:Bebas Neue,sans-serif;font-size:1.1rem;'>{label}</div>"
            for t in pots.get(i+1, []):
                h_tag = " 🏠" if t == host else ""
                html += f"<div style='padding:3px 0;'>{flag_html(t)} {display_name(t)}{h_tag}</div>"
            html += "</div>"
            st.markdown(html, unsafe_allow_html=True)


def _show_wc_draw(state, wc, qualified):
    st.markdown("### 🎯 Sorteo del FMMJ World Cup")
    st.caption("Regla: máx. 2 equipos UEFA por grupo. Sin 2 equipos de la misma confederación (excl. UEFA).")
    if len(qualified) < 32:
        st.warning("Aún no están los 32 clasificados.")
        return

    if wc.get("groups") and wc.get("setup_done"):
        st.success("✅ Sorteo realizado.")
        _render_wc_groups(wc)
        if st.button("🔄 Repetir Sorteo", type="secondary"):
            wc["groups"] = {}
            wc["setup_done"] = False
            if "draft_world_cup" in st.session_state: del st.session_state["draft_world_cup"]
            save_state(); st.rerun()
        if wc["phase"] == "sorteo" and st.button("▶️ Iniciar Fase de Grupos", type="primary"):
            wc["phase"] = "grupos"
            save_state(); st.rerun()
        return

    manual_group_setup(state, "world_cup", qualified, num_groups=8, teams_per_group=4,
                       confirm_label="Confirmar Grupos del Mundial FMMJ")


def _render_wc_groups(wc):
    groups = wc.get("groups", {})
    cols = st.columns(4)
    for idx, (g, teams) in enumerate(groups.items()):
        with cols[idx % 4]:
            html = f"<div style='background:#091020;border:1px solid #1a2860;border-radius:10px;padding:12px;margin-bottom:10px;'>"
            html += f"<div style='color:#ffd700;font-weight:700;border-bottom:1px solid #ffd700;padding-bottom:4px;margin-bottom:8px;font-family:Bebas Neue,sans-serif;'>GRUPO {g}</div>"
            for t in teams:
                html += f"<div style='padding:3px 0;font-size:0.85rem;'>{flag_html(t)} {display_name(t)}</div>"
            html += "</div>"
            st.markdown(html, unsafe_allow_html=True)


def _show_wc_groups(state, wc):
    if not wc.get("groups"):
        st.warning("Realiza el sorteo primero.")
        return
    st.markdown("### 📊 Fase de Grupos — FMMJ World Cup")
    all_done = show_group_jornadas(state, wc, "FMMJ", advancing=2)
    if all_done or st.checkbox("🔓 Forzar avance Mundial"):
        if wc["phase"] == "grupos":
            if st.button("⚽ Generar Octavos de Final", type="primary"):
                _build_wc_knockout(state, wc)
                save_state(); st.rerun()


def _build_wc_knockout(state, wc):
    standings = wc.get("group_standings", {})
    groups = sorted(standings.keys())
    pairs = [(groups[i], groups[i+1]) for i in range(0, len(groups)-1, 2)]
    octavos = []
    for ga, gb in pairs:
        f_a = standings[ga][0]["team"] if standings.get(ga) else None
        s_b = standings[gb][1]["team"] if len(standings.get(gb,[])) > 1 else None
        f_b = standings[gb][0]["team"] if standings.get(gb) else None
        s_a = standings[ga][1]["team"] if len(standings.get(ga,[])) > 1 else None
        if f_a and s_b: octavos.append({"home": f_a, "away": s_b, "winner": None})
        if f_b and s_a: octavos.append({"home": f_b, "away": s_a, "winner": None})
    wc["knockout_bracket"] = {
        "octavos": octavos, "cuartos": [], "semis": [], "tercer_puesto": [], "final": []
    }
    wc["knockout_results"] = {}
    wc["phase"] = "octavos"


def _show_wc_knockout(state, wc):
    st.markdown("### ⚽ Fase Eliminatoria — FMMJ World Cup")
    bracket = wc.get("knockout_bracket", {})
    if not bracket:
        st.info("Completa la fase de grupos primero.")
        return
    results = wc.setdefault("knockout_results", {})
    phases = [
        ("octavos", "🔵 Octavos de Final", "cuartos"),
        ("cuartos", "🟡 Cuartos de Final",  "semis"),
        ("semis",   "🟠 Semifinales",        "final"),
        ("final",   "🏆 GRAN FINAL FMMJ",    None),
    ]
    final_done = show_knockout_generic(state, wc, "FMMJ World Cup", phases, "wc")
    if final_done:
        champ = results.get("wc_final_0", {}).get("winner")
        if champ and not wc.get("champion"):
            wc["champion"] = champ
            wc["phase"] = "completado"
            st.balloons()
            st.markdown(f"""<div style='background:linear-gradient(135deg,#ffd700,#c8a000);border-radius:16px;
                padding:28px;text-align:center;margin-top:20px;'>
                <div style='font-size:3rem;'>🏆</div>
                <div style='font-size:2.2rem;font-weight:900;color:#06101e;font-family:Bebas Neue,sans-serif;'>{display_name(champ)}</div>
                <div style='font-size:1rem;color:#333;'>¡CAMPEÓN DEL FMMJ WORLD CUP!</div>
            </div>""", unsafe_allow_html=True)
            save_state()


# ══════════════════════════════════════════════════════════════
# HOME
# ══════════════════════════════════════════════════════════════
def show_home(state):
    host = state.get("host", "Nigeria")
    qualified = state.get("world_cup_qualified", [])

    st.markdown(f"""<div style='background:linear-gradient(135deg,#06101e 0%,#0c1e3a 50%,#06101e 100%);
        border:2px solid #c8a000;border-radius:20px;padding:40px;margin-bottom:28px;text-align:center;'>
        <div style='font-size:3.5rem;font-family:Bebas Neue,sans-serif;font-weight:700;
                    color:#ffd700;letter-spacing:5px;text-shadow:0 0 40px rgba(255,215,0,.6);'>
            🌍 FMMJ WORLD CUP
        </div>
        <div style='font-size:1rem;color:#406080;letter-spacing:3px;margin-top:6px;'>
            SIMULADOR OFICIAL FMMJ · {state.get('edition',1)}ª EDICIÓN
        </div>
        <div style='margin-top:16px;font-size:1rem;color:#90b0d0;'>
            Anfitrión: {flag_html(host)} <strong>{display_name(host)}</strong>
        </div>
    </div>""", unsafe_allow_html=True)

    cupos_info = [
        ("🏆 UEFA",13,"UEFA","#003580"),
        ("🌎 CONMEBOL",4,"CONMEBOL","#006b3c"),
        ("🌍 CAF",5,"CAF","#7a4500"),
        ("⭐ CONCACAF",3,"CONCACAF","#6a0000"),
        ("🌏 AFC",4,"AFC","#3a0060"),
        ("🔁 OFC/Rep.",2,"OFC","#1a3a1a"),
    ]
    cols = st.columns(6)
    conf_q = {}
    for t in qualified:
        c = get_team_confederation(t)
        conf_q[c] = conf_q.get(c, 0) + 1

    for col, (label, total, conf, color) in zip(cols, cupos_info):
        current = conf_q.get(conf, 0)
        done = current >= total
        with col:
            st.markdown(f"""<div style='background:#091525;border:1px solid {color};border-radius:12px;
                padding:14px;text-align:center;'>
                <div style='font-size:0.8rem;font-weight:700;color:#c0d0f0;'>{label}</div>
                <div style='font-size:1.8rem;font-weight:900;color:{"#00cc66" if done else "#ffd700"};'>{current}/{total}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown(f"<br><div style='text-align:center;font-size:1rem;color:#8090a8;margin-bottom:10px;'>{len(qualified)}/32 clasificados al FMMJ World Cup</div>", unsafe_allow_html=True)
    st.progress(len(qualified) / 32)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 🗺️ Guía del Simulador")
        st.markdown("""
1. **🏅 Ranking FMMJ** — Ranking dinámico
2. **🏆 Eurocopa** — 24 equipos UEFA → 13 cupos
3. **🌎 Copa América** — 10 + 6 invitadas → 4 cupos
4. **🌍 Copa África** — 10 equipos CAF → 5 cupos
5. **⭐ Copa Oro** — 6 CONCACAF → 3 cupos
6. **🌏 Copa Asia** — 6 AFC → 4 cupos
7. **🔁 Repechaje** — 2 llaves → 2 cupos
8. **🌍 Sorteo y Mundial** — 32 equipos 🏆
        """)
    with c2:
        st.markdown("### ✅ Últimos Clasificados")
        if qualified:
            for t in reversed(qualified[-10:]):
                st.markdown(f"{flag_html(t)} {display_name(t)}", unsafe_allow_html=True)
        else:
            st.info("Ninguno clasificado aún.")


def show_config(state):
    st.markdown("### ⚙️ Configuración del Simulador FMMJ")
    st.markdown("#### 🏠 Anfitrión del Mundial")
    all_teams_list = sorted(
        UEFA_TEAMS + CONMEBOL_TEAMS + CAF_TEAMS + CONCACAF_TEAMS + AFC_TEAMS + PLAYOFF_TEAMS,
        key=lambda t: display_name(t)
    )
    host_display = [display_name(t) for t in all_teams_list]
    current_host = state.get("host", "Nigeria")
    current_idx = all_teams_list.index(current_host) if current_host in all_teams_list else 0
    sel = st.selectbox("Seleccionar anfitrión:", host_display, index=current_idx)
    new_host = all_teams_list[host_display.index(sel)]
    if new_host != current_host:
        if st.button(f"✅ Confirmar: {display_name(new_host)}", type="primary"):
            state["host"] = new_host
            save_state(); st.rerun()

    st.markdown("---")
    st.markdown("#### 💾 Gestión de Datos")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🔄 Nueva Edición", type="primary"):
            reset_for_new_edition()
            st.success("✅ Nueva edición iniciada.")
            st.rerun()
    with c2:
        if st.button("🗑️ Reset Completo"):
            if os.path.exists("fmmj_state.json"):
                os.remove("fmmj_state.json")
            st.session_state.fmmj_state = get_initial_state()
            st.success("✅ Reset completo."); st.rerun()
    with c3:
        state_json = json.dumps(state, ensure_ascii=False, indent=2)
        st.download_button("⬇️ Descargar Estado", state_json, "fmmj_state.json", "application/json")

    st.markdown("---")
    st.markdown("#### 📊 Estado Actual")
    st.json({
        "edicion": state.get("edition"),
        "anfitrion": display_name(state.get("host","")),
        "clasificados": len(state.get("world_cup_qualified",[])),
        "eurocopa": state.get("euro",{}).get("phase"),
        "copa_america": state.get("copa_america",{}).get("phase"),
        "copa_africa": state.get("copa_africa",{}).get("phase"),
        "copa_oro": state.get("copa_oro",{}).get("phase"),
        "copa_asia": state.get("copa_asia",{}).get("phase"),
    })


# ══════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:16px 0 8px;'>
        <div style='font-size:2.6rem;font-family:Bebas Neue,sans-serif;color:#ffd700;letter-spacing:3px;text-shadow:0 0 20px rgba(255,215,0,0.5);'>FMMJ</div>
        <div style='font-size:0.62rem;color:#406080;letter-spacing:4px;text-transform:uppercase;'>World Cup Simulator</div>
    </div>
    <hr style='border-color:#142038;margin:8px 0 14px;'/>
    """, unsafe_allow_html=True)

    host = state.get("host", "Nigeria")
    edition = state.get("edition", 1)
    qc = len(state.get("world_cup_qualified", []))

    st.markdown(f"""<div style='background:#091525;border:1px solid #1a3a6a;border-radius:10px;padding:12px;margin-bottom:14px;'>
        <div style='font-size:0.68rem;color:#406080;text-transform:uppercase;'>Edición</div>
        <div style='font-size:1rem;font-weight:700;color:#ffd700;font-family:Bebas Neue,sans-serif;'>FMMJ {edition}ª Copa</div>
        <div style='margin-top:5px;font-size:0.68rem;color:#406080;'>Anfitrión</div>
        <div style='font-size:0.9rem;font-weight:600;color:#dce8ff;'>{flag_html(host)} {display_name(host)}</div>
        <div style='margin-top:5px;font-size:0.68rem;color:#406080;'>Clasificados</div>
        <div style='font-size:1rem;font-weight:700;color:{"#00cc66" if qc >= 32 else "#ffd700"};'>{qc}/32</div>
    </div>""", unsafe_allow_html=True)

    menu_options = {
        "🏠 Inicio": "inicio",
        "🏅 Ranking FMMJ": "ranking",
        "⚽ Goleadores": "goleadores",
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

    st.markdown("<hr style='border-color:#142038;margin:14px 0;'/>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:0.68rem;color:#406080;text-transform:uppercase;margin-bottom:6px;'>Progreso Torneos</div>", unsafe_allow_html=True)
    for name, ph_key in [("Eurocopa","euro"),("Copa América","copa_america"),("Copa África","copa_africa"),("Copa Oro","copa_oro"),("Copa Asia","copa_asia")]:
        phase = state.get(ph_key, {}).get("phase", "—")
        icon = "✅" if phase == "completado" else ("🔄" if phase not in ["—","sorteo","configuracion"] else "⏳")
        color = "#00cc66" if icon == "✅" else ("#ffd700" if icon == "🔄" else "#406080")
        st.markdown(f"<div style='font-size:0.78rem;color:{color};padding:2px 0;'>{icon} {name}</div>", unsafe_allow_html=True)

    save_state()


# ══════════════════════════════════════════════════════════════
# ROUTING
# ══════════════════════════════════════════════════════════════
if page_key == "inicio":        show_home(state)
elif page_key == "ranking":     show_ranking()
elif page_key == "goleadores":  show_goleadores()
elif page_key == "eurocopa":    show_eurocopa()
elif page_key == "copa_america":show_copa_america()
elif page_key == "copa_africa": show_copa_africa()
elif page_key == "copa_oro":    show_copa_oro()
elif page_key == "copa_asia":   show_copa_asia()
elif page_key == "repechaje":   show_repechaje()
elif page_key == "mundial":     show_world_cup_draw()
elif page_key == "config":      show_config(state)
