"""
pages/copa_america.py - Copa América FMMJ (CONMEBOL)
10 CONMEBOL + 6 invitadas (no UEFA)
4 grupos de 4 equipos (16 total)
Campeón → directo. 2do-7mo → playoffs. 1er-3ro playoffs → mundial. 4to → repechaje.
"""
import sys, os as _os
_root = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)
import streamlit as st
import random
from data import CONMEBOL_TEAMS, CONCACAF_TEAMS, AFC_TEAMS, CAF_TEAMS, PLAYOFF_TEAMS, get_flag_url
from state import get_state, update_ranking, RANKING_POINTS
from tournament import (
    display_name, flag_img, team_badge, generate_group_fixtures,
    calculate_standings, match_key, render_standings_table,
    register_scorers, draw_groups
)

TOURNAMENT_KEY = "copa_america"
TORNEO_NAME = "Copa América FMMJ"
GUEST_POOL = CONCACAF_TEAMS + AFC_TEAMS + CAF_TEAMS + PLAYOFF_TEAMS


def show():
    state = get_state()
    ca = state[TOURNAMENT_KEY]

    st.markdown("""
    <style>
    .ca-header {
        background: linear-gradient(135deg, #006b3c 0%, #009b4e 50%, #004d2a 100%);
        border-radius:16px;padding:24px 32px;margin-bottom:24px;
        box-shadow:0 8px 32px rgba(0,107,60,0.4);
    }
    .ca-title {font-size:2rem;font-weight:800;color:#ffd700;margin:0;}
    .ca-subtitle {font-size:.9rem;color:#a0ffcc;margin:4px 0 0;}
    .group-card {background:#0a1f12;border:1px solid #1a4a2a;border-radius:12px;padding:16px;margin-bottom:16px;}
    .group-title {font-size:1.1rem;font-weight:700;color:#ffd700;border-bottom:2px solid #ffd700;padding-bottom:8px;margin-bottom:12px;}
    .knockout-match {background:#071510;border:1px solid #1a4a2a;border-radius:10px;padding:14px;margin-bottom:10px;}
    .winner-tag {color:#ffd700;font-weight:700;}
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class='ca-header'>
        <div>
            <div class='ca-title'>🏆 {TORNEO_NAME}</div>
            <div class='ca-subtitle'>10 CONMEBOL + 6 invitadas · 4 grupos · 4 cupos al FMMJ World Cup</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tabs = st.tabs(["🌎 Invitadas", "🎲 Sorteo", "📊 Fase de Grupos", "⚽ Llaves", "🔄 Playoff", "🌍 Clasificados"])

    # ── INVITADAS ──────────────────────────────────────────────────────────
    with tabs[0]:
        st.markdown("### 🌎 Selección de Equipos Invitados")
        st.caption("Elige 6 invitadas de CONCACAF, AFC, CAF u OFC (no UEFA)")

        if ca.get("guests"):
            st.success(f"✅ Invitadas elegidas: {', '.join([display_name(g) for g in ca['guests']])}")
            if st.button("Cambiar invitadas"):
                ca["guests"] = []
                ca["setup_done"] = False
                st.rerun()
        else:
            selected = []
            st.markdown("**Equipos disponibles:**")
            cols = st.columns(3)
            for idx, team in enumerate(GUEST_POOL):
                with cols[idx % 3]:
                    if st.checkbox(f"{flag_img(team,16,12)}{display_name(team)}", key=f"ca_guest_{team}"):
                        selected.append(team)

            st.markdown(f"**Seleccionados: {len(selected)}/6**")
            if len(selected) == 6:
                if st.button("✅ Confirmar invitadas", type="primary"):
                    ca["guests"] = selected
                    st.rerun()
            elif len(selected) > 6:
                st.error("Máximo 6 invitadas. Deselecciona algunas.")

    # ── SORTEO ─────────────────────────────────────────────────────────────
    with tabs[1]:
        st.markdown("### 🎲 Sorteo de Grupos")
        if not ca.get("guests"):
            st.warning("Primero selecciona las 6 invitadas.")
        elif not ca.get("setup_done"):
            all_teams = CONMEBOL_TEAMS + ca["guests"]
            st.info(f"16 equipos → 4 grupos de 4")
            ranking = state["ranking"]
            teams_sorted = sorted(all_teams, key=lambda t: -ranking.get(t, 0))
            st.markdown("**Equipos participantes:**")
            for i, t in enumerate(teams_sorted):
                st.markdown(f"{flag_img(t,16,12)}{i+1}. **{display_name(t)}** — {ranking.get(t,'?')} pts", unsafe_allow_html=True)
            if st.button("🎯 Realizar Sorteo", type="primary"):
                _setup_ca_groups(state, ca)
                st.rerun()
        else:
            st.success("✅ Sorteo realizado")
            if st.button("🔄 Repetir Sorteo"):
                ca["setup_done"] = False
                st.rerun()
            _show_groups_draw(ca)

    # ── FASE DE GRUPOS ─────────────────────────────────────────────────────
    with tabs[2]:
        if not ca.get("setup_done"):
            st.warning("Primero realiza el sorteo.")
        else:
            _show_group_stage(state, ca)

    # ── LLAVES ─────────────────────────────────────────────────────────────
    with tabs[3]:
        if ca.get("phase") not in ["llaves", "completado"]:
            st.warning("Completa la fase de grupos primero.")
        else:
            _show_knockout(state, ca)

    # ── PLAYOFF ────────────────────────────────────────────────────────────
    with tabs[4]:
        _show_playoff(state, ca)

    # ── CLASIFICADOS ───────────────────────────────────────────────────────
    with tabs[5]:
        _show_qualified(state, ca)


def _setup_ca_groups(state, ca):
    all_teams = CONMEBOL_TEAMS + ca["guests"]
    ranking = state["ranking"]
    teams_sorted = sorted(all_teams, key=lambda t: -ranking.get(t, 0))
    # 4 bombos de 4
    pots = [teams_sorted[i*4:(i+1)*4] for i in range(4)]
    groups = {"A": [], "B": [], "C": [], "D": []}
    group_keys = list(groups.keys())
    for pot in pots:
        shuffled = pot[:]
        random.shuffle(shuffled)
        for i, team in enumerate(shuffled):
            groups[group_keys[i]].append(team)
    ca["groups"] = groups
    ca["group_results"] = {}
    ca["group_standings"] = {}
    ca["phase"] = "grupos"
    ca["setup_done"] = True


def _show_groups_draw(ca):
    groups = ca["groups"]
    cols = st.columns(2)
    for idx, (g, teams) in enumerate(groups.items()):
        with cols[idx % 2]:
            st.markdown(f"<div class='group-card'><div class='group-title'>GRUPO {g}</div>", unsafe_allow_html=True)
            for t in teams:
                st.markdown(f"{flag_img(t,20,15)}&nbsp;**{display_name(t)}**", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)


def _show_group_stage(state, ca):
    groups = ca["groups"]
    results = ca.get("group_results", {})

    st.markdown("### 📊 Fase de Grupos — Copa América FMMJ")
    st.caption("Clasifican **2 primeros** de cada grupo a cuartos de final.")
    all_complete = True

    for g, teams in groups.items():
        fixtures = [(teams[i], teams[j]) for i in range(len(teams)) for j in range(i+1, len(teams))]
        with st.expander(f"📋 GRUPO {g}", expanded=True):
            for home, away in fixtures:
                key = match_key(home, away)
                res = results.get(key, {})
                col1, col2, col3, col4, col5 = st.columns([3,1,1,3,1])
                with col1:
                    st.markdown(f"{flag_img(home)}&nbsp;**{display_name(home)}**", unsafe_allow_html=True)
                with col2:
                    hg = st.number_input("", 0, 20, res.get("home_goals", 0), key=f"ca_hg_{g}_{home}_{away}", label_visibility="collapsed")
                with col3:
                    ag = st.number_input("", 0, 20, res.get("away_goals", 0), key=f"ca_ag_{g}_{home}_{away}", label_visibility="collapsed")
                with col4:
                    st.markdown(f"{flag_img(away)}&nbsp;**{display_name(away)}**", unsafe_allow_html=True)
                with col5:
                    save = st.button("💾", key=f"ca_save_{g}_{home}_{away}")
                col_s1, col_s2 = st.columns(2)
                with col_s1:
                    hs = st.text_input(f"⚽ {display_name(home)}", value=", ".join(res.get("home_scorers", [])), key=f"ca_hs_{g}_{home}_{away}")
                with col_s2:
                    as_ = st.text_input(f"⚽ {display_name(away)}", value=", ".join(res.get("away_scorers", [])), key=f"ca_as_{g}_{home}_{away}")
                if save:
                    ca["group_results"][key] = {
                        "home_goals": hg, "away_goals": ag, "played": True,
                        "home_scorers": [s.strip() for s in hs.split(",") if s.strip()],
                        "away_scorers": [s.strip() for s in as_.split(",") if s.strip()],
                    }
                    register_scorers(hs, home, state, TORNEO_NAME)
                    register_scorers(as_, away, state, TORNEO_NAME)
                    st.rerun()
                if not results.get(key, {}).get("played"):
                    all_complete = False
                st.markdown("---")

            standings = calculate_standings(teams, {k: v for k, v in results.items() if any(t in k for t in teams)})
            ca["group_standings"][g] = standings
            st.markdown(render_standings_table(standings, advancing=2), unsafe_allow_html=True)

    if all_complete or st.checkbox("🔓 Forzar avance a llaves"):
        if ca["phase"] == "grupos":
            if st.button("⚽ Generar Cuartos de Final", type="primary", use_container_width=True):
                _build_knockout(state, ca)
                ca["phase"] = "llaves"
                st.rerun()


def _build_knockout(state, ca):
    standings = ca.get("group_standings", {})
    # Top 2 de cada grupo = 8 equipos → Cuartos
    firsts = []
    seconds = []
    for g in sorted(standings.keys()):
        s = standings[g]
        if s: firsts.append(s[0]["team"])
        if len(s) > 1: seconds.append(s[1]["team"])

    # 1A vs 2B, 1B vs 2A, 1C vs 2D, 1D vs 2C
    qf = [
        (firsts[0], seconds[1]),
        (firsts[1], seconds[0]),
        (firsts[2], seconds[3]),
        (firsts[3], seconds[2]),
    ]
    ca["knockout_bracket"] = {
        "cuartos": [{"home": m[0], "away": m[1], "winner": None} for m in qf],
        "semis": [],
        "tercer_puesto": [],
        "final": [],
    }
    ca["knockout_results"] = {}
    # Para playoff: registrar 3ros y 4tos de grupo
    thirds = []
    fourths = []
    for g in sorted(standings.keys()):
        s = standings[g]
        if len(s) > 2: thirds.append(s[2]["team"])
        if len(s) > 3: fourths.append(s[3]["team"])
    ca["group_thirds"] = thirds
    ca["group_fourths"] = fourths


def _show_knockout(state, ca):
    st.markdown("### ⚽ Fase de Eliminación — Copa América FMMJ")
    bracket = ca.get("knockout_bracket", {})
    results = ca.get("knockout_results", {})
    if not results:
        ca["knockout_results"] = {}
        results = ca["knockout_results"]

    phases = [
        ("cuartos", "🟡 Cuartos de Final", "semis"),
        ("semis", "🟠 Semifinales", "final"),
        ("final", "🏆 Final", None),
    ]

    for phase_key, phase_name, next_phase in phases:
        matches = bracket.get(phase_key, [])
        if not matches:
            continue
        st.markdown(f"#### {phase_name}")
        all_done = True

        for idx, match in enumerate(matches):
            home, away = match["home"], match["away"]
            if not home or not away:
                all_done = False
                continue
            key = f"ca_{phase_key}_{idx}"
            res = results.get(key, {})

            with st.container():
                col1,col2,col3,col4,col5,col6 = st.columns([3,1,1,3,2,1])
                with col1:
                    st.markdown(f"{flag_img(home)}&nbsp;**{display_name(home)}**", unsafe_allow_html=True)
                with col2:
                    hg = st.number_input("", 0, 20, res.get("home_goals", 0), key=f"{key}_hg", label_visibility="collapsed")
                with col3:
                    ag = st.number_input("", 0, 20, res.get("away_goals", 0), key=f"{key}_ag", label_visibility="collapsed")
                with col4:
                    st.markdown(f"{flag_img(away)}&nbsp;**{display_name(away)}**", unsafe_allow_html=True)
                with col5:
                    if hg == ag:
                        pen_opt = [None, home, away]
                        pen_disp = ["— Penales —", display_name(home), display_name(away)]
                        pen_idx = pen_opt.index(res.get("penalty_winner")) if res.get("penalty_winner") in pen_opt else 0
                        pen_sel = st.selectbox("Penales", pen_disp, index=pen_idx, key=f"{key}_pen")
                        pen_winner = pen_opt[pen_disp.index(pen_sel)]
                    else:
                        pen_winner = None
                        st.empty()
                with col6:
                    save = st.button("💾", key=f"{key}_save")

                col_s1, col_s2 = st.columns(2)
                with col_s1:
                    hs = st.text_input(f"⚽ {display_name(home)}", value=", ".join(res.get("home_scorers", [])), key=f"{key}_hs")
                with col_s2:
                    as_ = st.text_input(f"⚽ {display_name(away)}", value=", ".join(res.get("away_scorers", [])), key=f"{key}_as")

                if save:
                    winner = home if hg > ag else (away if ag > hg else pen_winner)
                    results[key] = {"home_goals": hg, "away_goals": ag, "winner": winner,
                                    "penalty_winner": pen_winner,
                                    "home_scorers": [s.strip() for s in hs.split(",") if s.strip()],
                                    "away_scorers": [s.strip() for s in as_.split(",") if s.strip()]}
                    ca["knockout_bracket"][phase_key][idx]["winner"] = winner
                    register_scorers(hs, home, state, TORNEO_NAME)
                    register_scorers(as_, away, state, TORNEO_NAME)
                    st.rerun()

                if res.get("winner"):
                    st.markdown(f"<span class='winner-tag'>✅ Ganador: {flag_img(res['winner'],18,13)}{display_name(res['winner'])}</span>", unsafe_allow_html=True)
                else:
                    all_done = False
                st.markdown("---")

        if all_done and next_phase and not bracket.get(next_phase):
            winners = [results.get(f"ca_{phase_key}_{i}", {}).get("winner") for i in range(len(matches))]
            winners = [w for w in winners if w]
            if phase_key == "semis" and not bracket.get("tercer_puesto"):
                losers = []
                for i, m in enumerate(matches):
                    r = results.get(f"ca_semis_{i}", {})
                    loser = m["home"] if r.get("winner") == m["away"] else m["away"]
                    if loser: losers.append(loser)
                if len(losers) == 2:
                    bracket["tercer_puesto"] = [{"home": losers[0], "away": losers[1], "winner": None}]
            next_m = [(winners[i], winners[i+1]) for i in range(0, len(winners)-1, 2)]
            bracket[next_phase] = [{"home": m[0], "away": m[1], "winner": None} for m in next_m]
            ca["knockout_results"] = results
            st.rerun()

        if all_done and phase_key == "final":
            _determine_ca_qualified(state, ca, results, bracket)

    # Tercer puesto
    if bracket.get("tercer_puesto"):
        st.markdown("#### 🥉 Tercer Puesto")
        for idx, match in enumerate(bracket["tercer_puesto"]):
            home, away = match["home"], match["away"]
            key = f"ca_tercer_{idx}"
            res = results.get(key, {})
            col1,col2,col3,col4,col5,col6 = st.columns([3,1,1,3,2,1])
            with col1: st.markdown(f"{flag_img(home)}&nbsp;**{display_name(home)}**", unsafe_allow_html=True)
            with col2:
                hg = st.number_input("", 0, 20, res.get("home_goals", 0), key=f"{key}_hg", label_visibility="collapsed")
            with col3:
                ag = st.number_input("", 0, 20, res.get("away_goals", 0), key=f"{key}_ag", label_visibility="collapsed")
            with col4: st.markdown(f"{flag_img(away)}&nbsp;**{display_name(away)}**", unsafe_allow_html=True)
            with col5:
                if hg == ag:
                    pen_sel = st.selectbox("Penales", ["— —", display_name(home), display_name(away)], key=f"{key}_pen")
                    pen_winner = home if pen_sel == display_name(home) else (away if pen_sel == display_name(away) else None)
                else:
                    pen_winner = None; st.empty()
            with col6:
                if st.button("💾", key=f"{key}_save"):
                    winner = home if hg > ag else (away if ag > hg else pen_winner)
                    results[key] = {"home_goals": hg, "away_goals": ag, "winner": winner}
                    bracket["tercer_puesto"][idx]["winner"] = winner
                    ca["knockout_results"] = results
                    st.rerun()
            if res.get("winner"):
                st.markdown(f"**🥉 3er Lugar: {display_name(res['winner'])}**")


def _determine_ca_qualified(state, ca, results, bracket):
    if ca.get("qualified"): return
    champion = results.get("ca_final_0", {}).get("winner")
    finalist = None
    for m in bracket.get("final", []):
        if m.get("winner"):
            finalist = m["home"] if m["winner"] == m["away"] else m["away"]
    third = results.get("ca_tercer_0", {}).get("winner")
    semis_losers = []
    for i, m in enumerate(bracket.get("semis", [])):
        r = results.get(f"ca_semis_{i}", {})
        loser = m["home"] if r.get("winner") == m["away"] else m["away"]
        if loser: semis_losers.append(loser)
    qf_losers = []
    for i, m in enumerate(bracket.get("cuartos", [])):
        r = results.get(f"ca_cuartos_{i}", {})
        loser = m["home"] if r.get("winner") == m["away"] else m["away"]
        if loser: qf_losers.append(loser)

    ca["champion"] = champion
    ca["qualified_direct"] = [champion] if champion else []
    # 2do-7mo van al playoff
    playoff_candidates = []
    for t in [finalist, third] + semis_losers + qf_losers:
        if t and t not in playoff_candidates: playoff_candidates.append(t)
    ca["playoff_candidates"] = playoff_candidates[:6]
    ca["phase"] = "playoff"


def _show_playoff(state, ca):
    st.markdown("### 🔄 Playoff CONMEBOL — 3 cupos + 1 repechaje")
    st.caption("Puestos 2do al 7mo de Copa América juegan todos contra todos. Top 3 → Mundial. 4to → Repechaje internacional.")
    if ca.get("phase") not in ["playoff", "completado"]:
        st.info("Esta fase se habilita al concluir la Copa América.")
        return

    candidates = ca.get("playoff_candidates", [])
    if not candidates:
        st.warning("No hay candidatos para el playoff.")
        return

    pb = ca.get("playoff_bracket", {})
    if not pb:
        pb = {"results": {}, "standings": {}}
        ca["playoff_bracket"] = pb

    results = pb.get("results", {})
    fixtures = [(candidates[i], candidates[j]) for i in range(len(candidates)) for j in range(i+1, len(candidates))]
    all_done = True

    st.markdown("**Partidos (todos contra todos):**")
    for home, away in fixtures:
        key = match_key(home, away)
        res = results.get(key, {})
        col1,col2,col3,col4,col5 = st.columns([3,1,1,3,1])
        with col1: st.markdown(f"{flag_img(home)}&nbsp;**{display_name(home)}**", unsafe_allow_html=True)
        with col2:
            hg = st.number_input("", 0, 20, res.get("home_goals", 0), key=f"cap_{home}_{away}_hg", label_visibility="collapsed")
        with col3:
            ag = st.number_input("", 0, 20, res.get("away_goals", 0), key=f"cap_{home}_{away}_ag", label_visibility="collapsed")
        with col4: st.markdown(f"{flag_img(away)}&nbsp;**{display_name(away)}**", unsafe_allow_html=True)
        with col5:
            if st.button("💾", key=f"cap_{home}_{away}_save"):
                results[key] = {"home_goals": hg, "away_goals": ag, "played": True}
                pb["results"] = results
                st.rerun()
        if not results.get(key, {}).get("played"):
            all_done = False

    standings = calculate_standings(candidates, results)
    pb["standings"] = standings
    st.markdown("**Tabla Playoff CONMEBOL:**")
    st.markdown(render_standings_table(standings, advancing=3), unsafe_allow_html=True)
    st.caption("🟢 Top 3 → Mundial | 4to → Repechaje Internacional")

    if all_done:
        if st.button("✅ Confirmar Clasificados CONMEBOL", type="primary"):
            top3 = [s["team"] for s in standings[:3]]
            fourth = standings[3]["team"] if len(standings) > 3 else None
            ca["qualified"] = ca.get("qualified_direct", []) + top3
            if fourth:
                state["playoff_teams"]["conmebol_slot"] = fourth
                st.info(f"🔄 {display_name(fourth)} va al Repechaje Internacional.")
            ca["phase"] = "completado"
            state["world_cup_qualified"] = list(set(state["world_cup_qualified"] + ca["qualified"]))
            st.rerun()


def _show_qualified(state, ca):
    st.markdown("### 🌍 Clasificados CONMEBOL al Mundial FMMJ")
    direct = ca.get("qualified_direct", [])
    playoff_q = [t for t in ca.get("qualified", []) if t not in direct]
    repechaje = state["playoff_teams"].get("conmebol_slot")

    if direct:
        st.markdown("#### ✅ Campeón Copa América (Directo)")
        for t in direct:
            st.markdown(f"{flag_img(t,22,16)}&nbsp;**{display_name(t)}**", unsafe_allow_html=True)
    if playoff_q:
        st.markdown("#### 🔄 Clasificados vía Playoff CONMEBOL")
        for i, t in enumerate(playoff_q, 1):
            st.markdown(f"{i}. {flag_img(t,22,16)}&nbsp;**{display_name(t)}**", unsafe_allow_html=True)
    if repechaje:
        st.markdown(f"#### 🔁 Repechaje Internacional: **{display_name(repechaje)}**")

    total = ca.get("qualified", [])
    if total:
        st.info(f"**Total CONMEBOL clasificados: {len(total)}/4**")
