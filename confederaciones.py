"""
pages/confederaciones.py - Copa África (CAF), Copa Oro (CONCACAF), Copa Asia (AFC)
"""
import streamlit as st
import random
from data import CAF_TEAMS, CONCACAF_TEAMS, AFC_TEAMS
from state import get_state
from utils.tournament import (
    display_name, flag_img, calculate_standings,
    match_key, render_standings_table, register_scorers
)

# ---------------------------------------------------------------------------
# FUNCIÓN GENÉRICA PARA TORNEOS DE 6 EQUIPOS (2 GRUPOS DE 3)
# ---------------------------------------------------------------------------

def _generic_6team_tournament(state, tournament_key, torneo_name, teams,
                               direct_spots, playoff_spots, repechaje_slot_key):
    """
    6 equipos, 2 grupos de 3.
    Campeón → directo.
    2do-5to → playoff todos contra todos.
    """
    tour = state[tournament_key]

    if not tour.get("setup_done"):
        st.info(f"**Equipos ({len(teams)}):**")
        ranking = state["ranking"]
        teams_sorted = sorted(teams, key=lambda t: -ranking.get(t, 0))
        for i, t in enumerate(teams_sorted):
            st.markdown(f"{flag_img(t,16,12)}&nbsp;{i+1}. **{display_name(t)}** — {ranking.get(t,'?')} pts", unsafe_allow_html=True)
        if st.button("🎯 Realizar Sorteo y Comenzar", type="primary"):
            _setup_6team_groups(state, tour, teams)
            st.rerun()
        return

    tabs = st.tabs(["📊 Fase de Grupos", "⚽ Llaves", "🔄 Playoff", "🌍 Clasificados"])

    with tabs[0]:
        _show_6team_groups(state, tour, torneo_name)
    with tabs[1]:
        _show_6team_knockout(state, tour, torneo_name)
    with tabs[2]:
        _show_6team_playoff(state, tour, torneo_name, direct_spots, playoff_spots, repechaje_slot_key)
    with tabs[3]:
        _show_6team_qualified(state, tour, torneo_name, repechaje_slot_key)


def _setup_6team_groups(state, tour, teams):
    ranking = state["ranking"]
    teams_sorted = sorted(teams, key=lambda t: -ranking.get(t, 0))
    random.shuffle(teams_sorted)
    groups = {"A": teams_sorted[:3], "B": teams_sorted[3:6]}
    tour["groups"] = groups
    tour["group_results"] = {}
    tour["group_standings"] = {}
    tour["phase"] = "grupos"
    tour["setup_done"] = True


def _show_6team_groups(state, tour, torneo_name):
    st.markdown("### 📊 Fase de Grupos")
    groups = tour["groups"]
    results = tour.get("group_results", {})
    all_complete = True

    for g, teams in groups.items():
        fixtures = [(teams[i], teams[j]) for i in range(len(teams)) for j in range(i+1, len(teams))]
        with st.expander(f"📋 GRUPO {g}", expanded=True):
            for home, away in fixtures:
                key = match_key(home, away)
                res = results.get(key, {})
                col1,col2,col3,col4,col5 = st.columns([3,1,1,3,1])
                with col1: st.markdown(f"{flag_img(home)}&nbsp;**{display_name(home)}**", unsafe_allow_html=True)
                with col2:
                    hg = st.number_input("", 0, 20, res.get("home_goals", 0), key=f"{torneo_name[:3]}_hg_{g}_{home}_{away}", label_visibility="collapsed")
                with col3:
                    ag = st.number_input("", 0, 20, res.get("away_goals", 0), key=f"{torneo_name[:3]}_ag_{g}_{home}_{away}", label_visibility="collapsed")
                with col4: st.markdown(f"{flag_img(away)}&nbsp;**{display_name(away)}**", unsafe_allow_html=True)
                with col5:
                    save = st.button("💾", key=f"{torneo_name[:3]}_save_{g}_{home}_{away}")
                col_s1, col_s2 = st.columns(2)
                with col_s1:
                    hs = st.text_input(f"⚽ {display_name(home)}", value=", ".join(res.get("home_scorers", [])), key=f"{torneo_name[:3]}_hs_{g}_{home}_{away}")
                with col_s2:
                    as_ = st.text_input(f"⚽ {display_name(away)}", value=", ".join(res.get("away_scorers", [])), key=f"{torneo_name[:3]}_as_{g}_{home}_{away}")
                if save:
                    tour["group_results"][key] = {
                        "home_goals": hg, "away_goals": ag, "played": True,
                        "home_scorers": [s.strip() for s in hs.split(",") if s.strip()],
                        "away_scorers": [s.strip() for s in as_.split(",") if s.strip()],
                    }
                    register_scorers(hs, home, state, torneo_name)
                    register_scorers(as_, away, state, torneo_name)
                    st.rerun()
                if not results.get(key, {}).get("played"):
                    all_complete = False
                st.markdown("---")

            standings = calculate_standings(teams, {k: v for k, v in results.items() if any(t in k for t in teams)})
            tour["group_standings"][g] = standings
            st.markdown(render_standings_table(standings, advancing=1), unsafe_allow_html=True)
            st.caption("🟢 1ro → Semifinales")

    if all_complete or st.checkbox(f"🔓 Forzar avance a semis ({torneo_name[:5]})", key=f"force_{torneo_name[:5]}"):
        if tour["phase"] == "grupos":
            if st.button("⚽ Generar Semifinales", type="primary", use_container_width=True, key=f"gen_sf_{torneo_name[:5]}"):
                _build_6team_knockout(state, tour)
                tour["phase"] = "llaves"
                st.rerun()


def _build_6team_knockout(state, tour):
    standings = tour.get("group_standings", {})
    groups = sorted(standings.keys())
    first_A = standings[groups[0]][0]["team"] if standings.get(groups[0]) else None
    second_A = standings[groups[0]][1]["team"] if len(standings.get(groups[0], [])) > 1 else None
    first_B = standings[groups[1]][0]["team"] if standings.get(groups[1]) else None
    second_B = standings[groups[1]][1]["team"] if len(standings.get(groups[1], [])) > 1 else None
    third_A = standings[groups[0]][2]["team"] if len(standings.get(groups[0], [])) > 2 else None
    third_B = standings[groups[1]][2]["team"] if len(standings.get(groups[1], [])) > 2 else None

    # Semifinales: 1A vs 2B, 1B vs 2A
    tour["knockout_bracket"] = {
        "semis": [
            {"home": first_A, "away": second_B, "winner": None},
            {"home": first_B, "away": second_A, "winner": None},
        ],
        "tercer_puesto": [],
        "final": [],
    }
    tour["knockout_results"] = {}
    # Playoff: los eliminados en semis + 3ros de grupo
    tour["playoff_pool"] = [second_A, second_B, third_A, third_B]
    tour["playoff_pool"] = [t for t in tour["playoff_pool"] if t]


def _show_6team_knockout(state, tour, torneo_name):
    st.markdown("### ⚽ Fase de Eliminación")
    bracket = tour.get("knockout_bracket", {})
    if not bracket:
        st.info("Completa la fase de grupos primero.")
        return
    results = tour.get("knockout_results", {})
    if results is None:
        tour["knockout_results"] = {}
        results = tour["knockout_results"]

    phases = [("semis", "🟠 Semifinales", "final"), ("final", "🏆 Final", None)]

    for phase_key, phase_name, next_phase in phases:
        matches = bracket.get(phase_key, [])
        if not matches: continue
        st.markdown(f"#### {phase_name}")
        all_done = True

        for idx, match in enumerate(matches):
            home, away = match["home"], match["away"]
            if not home or not away: continue
            key = f"{torneo_name[:3]}_{phase_key}_{idx}"
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
                    pen_sel = st.selectbox("Penales", ["—", display_name(home), display_name(away)], key=f"{key}_pen")
                    pen_winner = home if pen_sel == display_name(home) else (away if pen_sel == display_name(away) else None)
                else:
                    pen_winner = None; st.empty()
            with col6:
                save = st.button("💾", key=f"{key}_save")

            col_s1, col_s2 = st.columns(2)
            with col_s1:
                hs = st.text_input(f"⚽ {display_name(home)}", value=", ".join(res.get("home_scorers", [])), key=f"{key}_hs")
            with col_s2:
                as_ = st.text_input(f"⚽ {display_name(away)}", value=", ".join(res.get("away_scorers", [])), key=f"{key}_as")

            if save:
                winner = home if hg > ag else (away if ag > hg else pen_winner)
                results[key] = {"home_goals": hg, "away_goals": ag, "winner": winner, "penalty_winner": pen_winner,
                                "home_scorers": [s.strip() for s in hs.split(",") if s.strip()],
                                "away_scorers": [s.strip() for s in as_.split(",") if s.strip()]}
                tour["knockout_bracket"][phase_key][idx]["winner"] = winner
                register_scorers(hs, home, state, torneo_name)
                register_scorers(as_, away, state, torneo_name)
                st.rerun()

            if res.get("winner"):
                st.markdown(f"**✅ Ganador: {flag_img(res['winner'],18,13)}{display_name(res['winner'])}**", unsafe_allow_html=True)
            else:
                all_done = False
            st.markdown("---")

        if all_done and next_phase and not bracket.get(next_phase):
            winners = [results.get(f"{torneo_name[:3]}_{phase_key}_{i}", {}).get("winner") for i in range(len(matches))]
            winners = [w for w in winners if w]
            if phase_key == "semis":
                losers = []
                for i, m in enumerate(matches):
                    r = results.get(f"{torneo_name[:3]}_semis_{i}", {})
                    loser = m["home"] if r.get("winner") == m["away"] else m["away"]
                    if loser: losers.append(loser)
                bracket["tercer_puesto"] = [{"home": losers[0], "away": losers[1], "winner": None}] if len(losers) == 2 else []
                # Agregar losers al playoff pool
                existing = tour.get("playoff_pool", [])
                for l in losers:
                    if l and l not in existing:
                        existing.append(l)
                tour["playoff_pool"] = existing
            bracket[next_phase] = [{"home": winners[i], "away": winners[i+1], "winner": None} for i in range(0, len(winners)-1, 2)]
            tour["knockout_results"] = results
            st.rerun()

        if all_done and phase_key == "final":
            champion = results.get(f"{torneo_name[:3]}_final_0", {}).get("winner")
            if champion:
                tour["champion"] = champion
                tour["qualified_direct"] = [champion]
                tour["phase"] = "playoff"

    # Tercer puesto
    if bracket.get("tercer_puesto"):
        st.markdown("#### 🥉 Tercer Puesto")
        for idx, m in enumerate(bracket["tercer_puesto"]):
            home, away = m["home"], m["away"]
            key = f"{torneo_name[:3]}_tercer_{idx}"
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
                    p = st.selectbox("Penales", ["—", display_name(home), display_name(away)], key=f"{key}_pen")
                    pw = home if p == display_name(home) else (away if p == display_name(away) else None)
                else:
                    pw = None; st.empty()
            with col6:
                if st.button("💾", key=f"{key}_save"):
                    winner = home if hg > ag else (away if ag > hg else pw)
                    results[key] = {"home_goals": hg, "away_goals": ag, "winner": winner}
                    bracket["tercer_puesto"][idx]["winner"] = winner
                    tour["knockout_results"] = results
                    st.rerun()
            if res.get("winner"):
                st.markdown(f"**🥉 3er Lugar: {display_name(res['winner'])}**")


def _show_6team_playoff(state, tour, torneo_name, direct_spots, playoff_spots, repechaje_slot_key):
    st.markdown("### 🔄 Playoff")
    if tour.get("phase") not in ["playoff", "completado"]:
        st.info("Esta fase se habilita al concluir las llaves.")
        return

    candidates = tour.get("playoff_pool", [])
    if not candidates:
        st.warning("No hay candidatos.")
        return

    pb = tour.get("playoff_bracket", {})
    if not pb:
        pb = {"results": {}, "standings": {}}
        tour["playoff_bracket"] = pb

    results = pb.get("results", {})
    fixtures = [(candidates[i], candidates[j]) for i in range(len(candidates)) for j in range(i+1, len(candidates))]
    all_done = True

    for home, away in fixtures:
        key = match_key(home, away)
        res = results.get(key, {})
        col1,col2,col3,col4,col5 = st.columns([3,1,1,3,1])
        with col1: st.markdown(f"{flag_img(home)}&nbsp;**{display_name(home)}**", unsafe_allow_html=True)
        with col2:
            hg = st.number_input("", 0, 20, res.get("home_goals", 0), key=f"pb_{torneo_name[:3]}_{home}_{away}_hg", label_visibility="collapsed")
        with col3:
            ag = st.number_input("", 0, 20, res.get("away_goals", 0), key=f"pb_{torneo_name[:3]}_{home}_{away}_ag", label_visibility="collapsed")
        with col4: st.markdown(f"{flag_img(away)}&nbsp;**{display_name(away)}**", unsafe_allow_html=True)
        with col5:
            if st.button("💾", key=f"pb_{torneo_name[:3]}_{home}_{away}_save"):
                results[key] = {"home_goals": hg, "away_goals": ag, "played": True}
                pb["results"] = results
                st.rerun()
        if not results.get(key, {}).get("played"):
            all_done = False

    standings = calculate_standings(candidates, results)
    pb["standings"] = standings
    st.markdown(render_standings_table(standings, advancing=playoff_spots), unsafe_allow_html=True)

    if all_done:
        repechaje_idx = playoff_spots
        st.markdown(f"🟢 Top {playoff_spots} → Mundial | Pos {playoff_spots+1} → Repechaje")
        if st.button(f"✅ Confirmar Clasificados {torneo_name[:10]}", type="primary", key=f"confirm_{torneo_name[:5]}"):
            top_n = [s["team"] for s in standings[:playoff_spots]]
            repechaje = standings[repechaje_idx]["team"] if len(standings) > repechaje_idx else None
            tour["qualified"] = tour.get("qualified_direct", []) + top_n
            if repechaje and repechaje_slot_key:
                state["playoff_teams"][repechaje_slot_key] = repechaje
            tour["phase"] = "completado"
            state["world_cup_qualified"] = list(set(state["world_cup_qualified"] + tour["qualified"]))
            st.rerun()


def _show_6team_qualified(state, tour, torneo_name, repechaje_slot_key):
    st.markdown(f"### 🌍 Clasificados al Mundial — {torneo_name}")
    direct = tour.get("qualified_direct", [])
    playoff_q = [t for t in tour.get("qualified", []) if t not in direct]
    repechaje = state["playoff_teams"].get(repechaje_slot_key) if repechaje_slot_key else None

    if direct:
        st.markdown("#### ✅ Campeón (Directo)")
        for t in direct:
            st.markdown(f"{flag_img(t,22,16)}&nbsp;**{display_name(t)}**", unsafe_allow_html=True)
    if playoff_q:
        st.markdown("#### 🔄 Playoff")
        for i, t in enumerate(playoff_q, 1):
            st.markdown(f"{i}. {flag_img(t,22,16)}&nbsp;**{display_name(t)}**", unsafe_allow_html=True)
    if repechaje:
        st.markdown(f"#### 🔁 Repechaje: **{display_name(repechaje)}**")

    total = tour.get("qualified", [])
    if total:
        st.info(f"**Clasificados: {len(total)}**")


# ---------------------------------------------------------------------------
# COPA ÁFRICA (CAF) - 10 equipos, 2 grupos de 5
# ---------------------------------------------------------------------------
def show_copa_africa():
    state = get_state()
    tour = state["copa_africa"]
    host = state.get("host", "Nigeria")

    st.markdown("""
    <style>
    .caf-header {background:linear-gradient(135deg,#b8860b 0%,#daa520 50%,#8b6914 100%);
    border-radius:16px;padding:24px 32px;margin-bottom:24px;box-shadow:0 8px 32px rgba(184,134,11,.4);}
    .caf-title {font-size:2rem;font-weight:800;color:#fff;margin:0;}
    .caf-subtitle {font-size:.9rem;color:#fff3a0;margin:4px 0 0;}
    </style>
    """, unsafe_allow_html=True)
    n_teams = len(CAF_TEAMS)
    subtitle_caf = f"{n_teams} selecciones CAF · 2 grupos de 5 · 5 cupos al Mundial"
    st.markdown(f"""<div class='caf-header'>
        <div><div class='caf-title'>🏆 Copa África FMMJ</div>
        <div class='caf-subtitle'>{subtitle_caf}</div></div>
    </div>""", unsafe_allow_html=True)

    # El anfitrión participa normalmente pero si clasifica cede su cupo al siguiente
    if host in CAF_TEAMS:
        st.info(
            f"🏠 **{display_name(host)}** es el anfitrión del Mundial y participa en la Copa África normalmente. "
            f"Si clasifica entre los 5 primeros, su cupo pasa al siguiente en la tabla."
        )

    _show_10team_caf_tournament(state, tour, CAF_TEAMS)


def _show_10team_caf_tournament(state, tour, teams):
    """Copa África: 10 equipos, 2 grupos de 5"""
    TORNEO_NAME = "Copa África FMMJ"

    if not tour.get("setup_done"):
        st.info(f"**Equipos participantes CAF ({len(teams)}):**")
        ranking = state["ranking"]
        for i, t in enumerate(sorted(teams, key=lambda x: -ranking.get(x, 0))):
            st.markdown(f"{flag_img(t,16,12)}&nbsp;{i+1}. **{display_name(t)}**", unsafe_allow_html=True)
        if st.button("🎯 Sortear Grupos Copa África", type="primary"):
            _setup_caf_groups(state, tour, teams)
            st.rerun()
        return

    tabs = st.tabs(["📊 Grupos", "⚽ Llaves", "🔄 Playoff CAF", "🌍 Clasificados"])
    with tabs[0]: _show_caf_groups(state, tour, TORNEO_NAME)
    with tabs[1]: _show_caf_knockout(state, tour, TORNEO_NAME)
    with tabs[2]: _show_caf_playoff(state, tour, TORNEO_NAME)
    with tabs[3]: _show_caf_qualified(state, tour)


def _setup_caf_groups(state, tour, teams):
    """
    CAF puede tener 10 equipos (2 grupos de 5) o 9 equipos si el anfitrión
    es de CAF (grupos de 5 y 4). El cuadro de llaves se arma con top 2 de
    cada grupo en ambos casos.
    """
    ranking = state["ranking"]
    teams_sorted = sorted(teams, key=lambda t: -ranking.get(t, 0))
    random.shuffle(teams_sorted)
    n = len(teams_sorted)
    mid = (n + 1) // 2   # 5 si n=9 o 10; grupo A siempre igual o mayor
    groups = {"A": teams_sorted[:mid], "B": teams_sorted[mid:n]}
    tour["groups"] = groups
    tour["group_results"] = {}
    tour["group_standings"] = {}
    tour["phase"] = "grupos"
    tour["setup_done"] = True


def _show_caf_groups(state, tour, torneo_name):
    st.markdown("### 📊 Fase de Grupos — Copa África")
    groups = tour["groups"]
    results = tour.get("group_results", {})
    all_complete = True

    for g, teams in groups.items():
        fixtures = [(teams[i], teams[j]) for i in range(len(teams)) for j in range(i+1, len(teams))]
        with st.expander(f"📋 GRUPO {g}", expanded=True):
            for home, away in fixtures:
                key = match_key(home, away)
                res = results.get(key, {})
                col1,col2,col3,col4,col5 = st.columns([3,1,1,3,1])
                with col1: st.markdown(f"{flag_img(home)}&nbsp;**{display_name(home)}**", unsafe_allow_html=True)
                with col2:
                    hg = st.number_input("", 0, 20, res.get("home_goals", 0), key=f"caf_hg_{g}_{home}_{away}", label_visibility="collapsed")
                with col3:
                    ag = st.number_input("", 0, 20, res.get("away_goals", 0), key=f"caf_ag_{g}_{home}_{away}", label_visibility="collapsed")
                with col4: st.markdown(f"{flag_img(away)}&nbsp;**{display_name(away)}**", unsafe_allow_html=True)
                with col5:
                    save = st.button("💾", key=f"caf_save_{g}_{home}_{away}")
                col_s1, col_s2 = st.columns(2)
                with col_s1:
                    hs = st.text_input(f"⚽ {display_name(home)}", value=", ".join(res.get("home_scorers", [])), key=f"caf_hs_{g}_{home}_{away}")
                with col_s2:
                    as_ = st.text_input(f"⚽ {display_name(away)}", value=", ".join(res.get("away_scorers", [])), key=f"caf_as_{g}_{home}_{away}")
                if save:
                    tour["group_results"][key] = {
                        "home_goals": hg, "away_goals": ag, "played": True,
                        "home_scorers": [s.strip() for s in hs.split(",") if s.strip()],
                        "away_scorers": [s.strip() for s in as_.split(",") if s.strip()],
                    }
                    register_scorers(hs, home, state, torneo_name)
                    register_scorers(as_, away, state, torneo_name)
                    st.rerun()
                if not results.get(key, {}).get("played"):
                    all_complete = False
                st.markdown("---")

            standings = calculate_standings(teams, {k: v for k, v in results.items() if any(t in k for t in teams)})
            tour["group_standings"][g] = standings
            st.markdown(render_standings_table(standings, advancing=2), unsafe_allow_html=True)
            st.caption("🟢 Top 2 → Cuartos de Final")

    if all_complete or st.checkbox("🔓 Forzar avance Copa África"):
        if tour["phase"] == "grupos":
            if st.button("⚽ Generar Cuartos de Final CAF", type="primary", use_container_width=True):
                _build_caf_knockout(state, tour)
                tour["phase"] = "llaves"
                st.rerun()


def _build_caf_knockout(state, tour):
    standings = tour.get("group_standings", {})
    groups = sorted(standings.keys())
    top4 = []
    thirds = []
    rest = []
    for g in groups:
        s = standings[g]
        if len(s) >= 1: top4.append(s[0]["team"])
        if len(s) >= 2: top4.append(s[1]["team"])
        if len(s) >= 3: thirds.append(s[2]["team"])
        for t in s[3:]:
            rest.append(t["team"])

    # Cuartos: 1A vs 2B, 1B vs 2A
    qf = [(top4[0], top4[3]), (top4[1], top4[2])]
    tour["knockout_bracket"] = {
        "cuartos": [{"home": m[0], "away": m[1], "winner": None} for m in qf],
        "semis": [],
        "tercer_puesto": [],
        "final": [],
    }
    tour["knockout_results"] = {}
    tour["playoff_pool"] = thirds + rest


def _show_caf_knockout(state, tour, torneo_name):
    st.markdown("### ⚽ Fase de Eliminación — Copa África")
    bracket = tour.get("knockout_bracket", {})
    if not bracket:
        st.info("Completa grupos primero.")
        return
    results = tour.get("knockout_results", {})
    if results is None:
        tour["knockout_results"] = {}
        results = tour["knockout_results"]

    phases = [("cuartos", "🟡 Cuartos de Final", "semis"), ("semis", "🟠 Semifinales", "final"), ("final", "🏆 Final", None)]

    for phase_key, phase_name, next_phase in phases:
        matches = bracket.get(phase_key, [])
        if not matches: continue
        st.markdown(f"#### {phase_name}")
        all_done = True

        for idx, match in enumerate(matches):
            home, away = match["home"], match["away"]
            if not home or not away: all_done = False; continue
            key = f"caf_{phase_key}_{idx}"
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
                    ps = st.selectbox("Penales", ["—", display_name(home), display_name(away)], key=f"{key}_pen")
                    pw = home if ps == display_name(home) else (away if ps == display_name(away) else None)
                else:
                    pw = None; st.empty()
            with col6:
                save = st.button("💾", key=f"{key}_save")

            col_s1, col_s2 = st.columns(2)
            with col_s1:
                hs = st.text_input(f"⚽ {display_name(home)}", value=", ".join(res.get("home_scorers", [])), key=f"{key}_hs")
            with col_s2:
                as_ = st.text_input(f"⚽ {display_name(away)}", value=", ".join(res.get("away_scorers", [])), key=f"{key}_as")

            if save:
                winner = home if hg > ag else (away if ag > hg else pw)
                results[key] = {"home_goals": hg, "away_goals": ag, "winner": winner, "penalty_winner": pw,
                                "home_scorers": [s.strip() for s in hs.split(",") if s.strip()],
                                "away_scorers": [s.strip() for s in as_.split(",") if s.strip()]}
                tour["knockout_bracket"][phase_key][idx]["winner"] = winner
                register_scorers(hs, home, state, torneo_name)
                register_scorers(as_, away, state, torneo_name)
                st.rerun()

            if res.get("winner"):
                st.markdown(f"**✅ {display_name(res['winner'])}**")
            else:
                all_done = False
            st.markdown("---")

        if all_done and next_phase and not bracket.get(next_phase):
            winners = [results.get(f"caf_{phase_key}_{i}", {}).get("winner") for i in range(len(matches))]
            winners = [w for w in winners if w]
            if phase_key == "semis":
                losers = []
                for i, m in enumerate(matches):
                    r = results.get(f"caf_semis_{i}", {})
                    loser = m["home"] if r.get("winner") == m["away"] else m["away"]
                    if loser: losers.append(loser)
                bracket["tercer_puesto"] = [{"home": losers[0], "away": losers[1], "winner": None}] if len(losers) == 2 else []
                pool = tour.get("playoff_pool", [])
                for l in losers:
                    if l not in pool: pool.append(l)
                tour["playoff_pool"] = pool
            if phase_key == "cuartos":
                losers_qf = []
                for i, m in enumerate(matches):
                    r = results.get(f"caf_cuartos_{i}", {})
                    loser = m["home"] if r.get("winner") == m["away"] else m["away"]
                    if loser: losers_qf.append(loser)
                pool = tour.get("playoff_pool", [])
                for l in losers_qf:
                    if l not in pool: pool.append(l)
                tour["playoff_pool"] = pool
            nxt = [(winners[i], winners[i+1]) for i in range(0, len(winners)-1, 2)]
            bracket[next_phase] = [{"home": m[0], "away": m[1], "winner": None} for m in nxt]
            tour["knockout_results"] = results
            st.rerun()

        if all_done and phase_key == "final":
            res_final = results.get("caf_final_0", {})
            finalist_winner = res_final.get("winner")
            finalist_loser = None
            for m in bracket.get("final", []):
                if m.get("winner"):
                    finalist_loser = m["home"] if m["winner"] == m["away"] else m["away"]
            if finalist_winner:
                tour["champion"] = finalist_winner
                tour["finalist"] = finalist_loser
                tour["qualified_direct"] = [finalist_winner, finalist_loser] if finalist_loser else [finalist_winner]
                tour["phase"] = "playoff"

    # Tercer puesto
    if bracket.get("tercer_puesto"):
        st.markdown("#### 🥉 Tercer Puesto")
        for idx, m in enumerate(bracket["tercer_puesto"]):
            home, away = m["home"], m["away"]
            key = f"caf_tercer_{idx}"
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
                    p = st.selectbox("Penales", ["—", display_name(home), display_name(away)], key=f"{key}_pen")
                    pw = home if p == display_name(home) else (away if p == display_name(away) else None)
                else:
                    pw = None; st.empty()
            with col6:
                if st.button("💾", key=f"{key}_save"):
                    winner = home if hg > ag else (away if ag > hg else pw)
                    results[key] = {"home_goals": hg, "away_goals": ag, "winner": winner}
                    bracket["tercer_puesto"][idx]["winner"] = winner
                    tour["knockout_results"] = results
                    st.rerun()
            if res.get("winner"):
                st.markdown(f"**🥉 3er Lugar: {display_name(res['winner'])}**")


def _show_caf_playoff(state, tour, torneo_name):
    st.markdown("### 🔄 Playoff CAF — 3 cupos adicionales")
    st.caption("3ro-7mo Copa África: todos contra todos. Top 3 → Mundial.")
    if tour.get("phase") not in ["playoff", "completado"]:
        st.info("Se habilita al terminar las llaves.")
        return

    candidates = tour.get("playoff_pool", [])
    if not candidates:
        st.warning("No hay candidatos.")
        return

    pb = tour.get("playoff_bracket", {})
    if not pb:
        pb = {"results": {}, "standings": {}}
        tour["playoff_bracket"] = pb

    results = pb.get("results", {})
    fixtures = [(candidates[i], candidates[j]) for i in range(len(candidates)) for j in range(i+1, len(candidates))]
    all_done = True

    for home, away in fixtures:
        key = match_key(home, away)
        res = results.get(key, {})
        col1,col2,col3,col4,col5 = st.columns([3,1,1,3,1])
        with col1: st.markdown(f"{flag_img(home)}&nbsp;**{display_name(home)}**", unsafe_allow_html=True)
        with col2:
            hg = st.number_input("", 0, 20, res.get("home_goals", 0), key=f"cafp_{home}_{away}_hg", label_visibility="collapsed")
        with col3:
            ag = st.number_input("", 0, 20, res.get("away_goals", 0), key=f"cafp_{home}_{away}_ag", label_visibility="collapsed")
        with col4: st.markdown(f"{flag_img(away)}&nbsp;**{display_name(away)}**", unsafe_allow_html=True)
        with col5:
            if st.button("💾", key=f"cafp_{home}_{away}_save"):
                results[key] = {"home_goals": hg, "away_goals": ag, "played": True}
                pb["results"] = results
                st.rerun()
        if not results.get(key, {}).get("played"):
            all_done = False

    standings = calculate_standings(candidates, results)
    pb["standings"] = standings
    st.markdown(render_standings_table(standings, advancing=3), unsafe_allow_html=True)

    if all_done:
        if st.button("✅ Confirmar Clasificados CAF", type="primary"):
            top3 = [s["team"] for s in standings[:3]]
            tour["qualified"] = tour.get("qualified_direct", []) + top3
            tour["phase"] = "completado"
            state["world_cup_qualified"] = list(set(state["world_cup_qualified"] + tour["qualified"]))
            st.rerun()


def _show_caf_qualified(state, tour):
    st.markdown("### 🌍 Clasificados CAF al Mundial FMMJ")
    host = state.get("host", "Nigeria")
    if host in CAF_TEAMS:
        st.markdown(f"🏠 **{display_name(host)}** — Anfitrión (clasificado directo)")

    direct = tour.get("qualified_direct", [])
    playoff_q = [t for t in tour.get("qualified", []) if t not in direct]

    if direct:
        st.markdown("#### ✅ Campeón y Subcampeón (Directos)")
        for t in direct:
            st.markdown(f"{flag_img(t,22,16)}&nbsp;**{display_name(t)}**", unsafe_allow_html=True)
    if playoff_q:
        st.markdown("#### 🔄 Playoff CAF")
        for i, t in enumerate(playoff_q, 1):
            st.markdown(f"{i}. {flag_img(t,22,16)}&nbsp;**{display_name(t)}**", unsafe_allow_html=True)

    total = tour.get("qualified", [])
    host_count = 1 if host in CAF_TEAMS else 0
    st.info(f"**Total CAF al Mundial: {len(total) + host_count}/5** (incluyendo anfitrión)" if host in CAF_TEAMS
            else f"**Total CAF: {len(total)}/5**")


# ---------------------------------------------------------------------------
# COPA ORO — CONCACAF
# ---------------------------------------------------------------------------
def show_copa_oro():
    state = get_state()
    tour = state["copa_oro"]

    st.markdown("""
    <style>
    .concacaf-header {background:linear-gradient(135deg,#8b0000 0%,#cc2200 50%,#6b0000 100%);
    border-radius:16px;padding:24px 32px;margin-bottom:24px;box-shadow:0 8px 32px rgba(139,0,0,.4);}
    .concacaf-title {font-size:2rem;font-weight:800;color:#ffd700;margin:0;}
    .concacaf-subtitle {font-size:.9rem;color:#ffaaaa;margin:4px 0 0;}
    </style>""", unsafe_allow_html=True)
    st.markdown(f"""<div class='concacaf-header'>
        <div><div class='concacaf-title'>🏆 Copa Oro FMMJ</div>
        <div class='concacaf-subtitle'>6 selecciones CONCACAF · 2 grupos de 3 · 3 cupos al Mundial</div></div>
    </div>""", unsafe_allow_html=True)

    st.caption("Campeón → directo. 2do-5to → playoff todos contra todos. Top 2 playoff → Mundial. 3ro → Repechaje.")
    _generic_6team_tournament(state, "copa_oro", "Copa Oro FMMJ", CONCACAF_TEAMS,
                              direct_spots=1, playoff_spots=2, repechaje_slot_key="concacaf_slot")


# ---------------------------------------------------------------------------
# COPA ASIA — AFC
# ---------------------------------------------------------------------------
def show_copa_asia():
    state = get_state()
    tour = state["copa_asia"]

    st.markdown("""
    <style>
    .afc-header {background:linear-gradient(135deg,#4a0080 0%,#7700cc 50%,#330060 100%);
    border-radius:16px;padding:24px 32px;margin-bottom:24px;box-shadow:0 8px 32px rgba(74,0,128,.4);}
    .afc-title {font-size:2rem;font-weight:800;color:#ffd700;margin:0;}
    .afc-subtitle {font-size:.9rem;color:#ddaaff;margin:4px 0 0;}
    </style>""", unsafe_allow_html=True)
    st.markdown(f"""<div class='afc-header'>
        <div><div class='afc-title'>🏆 Copa Asia FMMJ</div>
        <div class='afc-subtitle'>6 selecciones AFC · 2 grupos de 3 · 4 cupos al Mundial</div></div>
    </div>""", unsafe_allow_html=True)

    st.caption("Campeón → directo. 2do-5to → playoff todos contra todos. Top 3 playoff → Mundial. 4to → Repechaje.")
    _generic_6team_tournament(state, "copa_asia", "Copa Asia FMMJ", AFC_TEAMS,
                              direct_spots=1, playoff_spots=3, repechaje_slot_key="afc_slot")
