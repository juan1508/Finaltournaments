"""
pages/eurocopa.py - Eurocopa FMMJ (UEFA)
24 equipos, 6 grupos de 4, fase de grupos + llaves
Clasifican al mundial: campeón al 5to directo + playoffs (16 equipos → 8 clasificados)
Total UEFA al mundial: 13
"""
import sys, os as _os
_root = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)
import streamlit as st
import random
from data import UEFA_TEAMS, get_flag_url, PLAYERS
from state import get_state, update_ranking, RANKING_POINTS
from tournament import (
    display_name, flag_img, team_badge, generate_group_fixtures,
    calculate_standings, match_key, render_standings_table,
    register_scorers, draw_groups
)

TOURNAMENT_KEY = "euro"
TORNEO_NAME = "Eurocopa FMMJ"

# ---------------------------------------------------------------------------
# SORTEO DE GRUPOS EUROCOPA (con restricción de confederación = todos UEFA)
# ---------------------------------------------------------------------------
def setup_euro_groups(state):
    """
    24 equipos UEFA → 6 grupos de 4.
    Se forman 4 bombos de 6 (por ranking). De cada bombo se extrae
    1 equipo por grupo (6 grupos), igual que en la Eurocopa real.
    """
    ranking = state["ranking"]
    teams_sorted = sorted(UEFA_TEAMS, key=lambda t: -ranking.get(t, 0))
    # 4 bombos de 6 equipos (4 bombos × 6 = 24)
    pots = [teams_sorted[i*6:(i+1)*6] for i in range(4)]
    groups = {chr(65+i): [] for i in range(6)}
    group_keys = list(groups.keys())  # ['A','B','C','D','E','F']
    # De cada bombo, repartir 1 equipo a cada grupo
    for pot in pots:
        shuffled = pot[:]
        random.shuffle(shuffled)
        for i, team in enumerate(shuffled):
            groups[group_keys[i]].append(team)
    state[TOURNAMENT_KEY]["groups"] = groups
    state[TOURNAMENT_KEY]["group_results"] = {}
    state[TOURNAMENT_KEY]["group_standings"] = {}
    state[TOURNAMENT_KEY]["phase"] = "grupos"
    state[TOURNAMENT_KEY]["setup_done"] = True

# ---------------------------------------------------------------------------
# PÁGINA PRINCIPAL
# ---------------------------------------------------------------------------
def show():
    state = get_state()
    euro = state[TOURNAMENT_KEY]
    host = state.get("host", "Nigeria")

    st.markdown("""
    <style>
    .euro-header {
        background: linear-gradient(135deg, #003580 0%, #0066cc 50%, #003580 100%);
        border-radius: 16px; padding: 24px 32px; margin-bottom: 24px;
        display: flex; align-items: center; gap: 20px;
        box-shadow: 0 8px 32px rgba(0,53,128,0.4);
    }
    .euro-title {font-size: 2rem; font-weight: 800; color: #ffd700; margin: 0;}
    .euro-subtitle {font-size: 0.9rem; color: #aaccff; margin: 4px 0 0 0;}
    .group-card {
        background: #0d1b3e; border: 1px solid #1a3a6e;
        border-radius: 12px; padding: 16px; margin-bottom: 16px;
    }
    .group-title {
        font-size: 1.1rem; font-weight: 700; color: #ffd700;
        border-bottom: 2px solid #ffd700; padding-bottom: 8px; margin-bottom: 12px;
    }
    .match-input-row {
        background: #111a35; border-radius: 8px; padding: 10px 14px;
        margin-bottom: 8px; border: 1px solid #1e3055;
    }
    .match-label {font-size: 0.85rem; color: #8899cc; margin-bottom: 6px;}
    .qualified-badge {
        display: inline-block; padding: 4px 10px; border-radius: 20px;
        font-size: 0.75rem; font-weight: 600; margin: 2px;
    }
    .direct { background: #0d4f2e; color: #4eff91; }
    .playoff { background: #2a3d0d; color: #aaff44; }
    .eliminated { background: #3d0d0d; color: #ff6666; }
    .phase-badge {
        display: inline-block; background: #003580; color: #ffd700;
        padding: 4px 14px; border-radius: 20px; font-size: 0.8rem;
        font-weight: 700; margin-bottom: 16px;
    }
    .knockout-match {
        background: #0a1628; border: 1px solid #1a3a6e;
        border-radius: 10px; padding: 14px; margin-bottom: 10px;
    }
    .match-teams {font-size: 1rem; color: #fff; font-weight: 600; margin-bottom: 8px;}
    .winner-tag {color: #ffd700; font-weight: 700;}
    </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown(f"""
    <div class='euro-header'>
        <div>
            <div class='euro-title'>🏆 {TORNEO_NAME}</div>
            <div class='euro-subtitle'>24 selecciones UEFA · 6 grupos · 13 cupos al FMMJ World Cup</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Pestañas
    tabs = st.tabs(["🎲 Sorteo", "📊 Fase de Grupos", "⚽ Llaves", "🔄 Playoff UEFA", "🌍 Clasificados"])

    # ── TAB 1: SORTEO ──────────────────────────────────────────────────────
    with tabs[0]:
        st.markdown("### 🎲 Sorteo de Grupos")
        if not euro["setup_done"]:
            st.info("Los 24 equipos se distribuyen en 6 grupos de 4, usando el Ranking FMMJ como referencia para los bombos.")
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown("**Equipos UEFA participantes:**")
                ranking = state["ranking"]
                teams_sorted = sorted(UEFA_TEAMS, key=lambda t: -ranking.get(t, 0))
                for i, t in enumerate(teams_sorted):
                    st.markdown(f"{flag_img(t,16,12)}{i+1}. **{display_name(t)}** — {ranking.get(t,'?')} pts", unsafe_allow_html=True)
            with col2:
                if st.button("🎯 Realizar Sorteo", use_container_width=True, type="primary"):
                    setup_euro_groups(state)
                    st.rerun()
        else:
            st.success("✅ Sorteo realizado")
            if st.button("🔄 Repetir Sorteo", type="secondary"):
                euro["setup_done"] = False
                st.rerun()
            _show_groups_draw(euro)

    # ── TAB 2: FASE DE GRUPOS ──────────────────────────────────────────────
    with tabs[1]:
        if not euro["setup_done"]:
            st.warning("Primero realiza el sorteo en la pestaña **Sorteo**.")
        else:
            _show_group_stage(state, euro)

    # ── TAB 3: LLAVES (Knockout desde Octavos) ────────────────────────────
    with tabs[2]:
        if not euro["setup_done"]:
            st.warning("Primero completa el sorteo.")
        elif euro["phase"] not in ["llaves", "completado"]:
            st.warning("Completa la fase de grupos primero.")
        else:
            _show_knockout(state, euro)

    # ── TAB 4: PLAYOFF UEFA ───────────────────────────────────────────────
    with tabs[3]:
        _show_uefa_playoff(state, euro)

    # ── TAB 5: CLASIFICADOS ───────────────────────────────────────────────
    with tabs[4]:
        _show_qualified(state, euro)


# ---------------------------------------------------------------------------
# SORTEO VISUAL
# ---------------------------------------------------------------------------
def _show_groups_draw(euro):
    groups = euro["groups"]
    cols = st.columns(3)
    for idx, (g, teams) in enumerate(groups.items()):
        with cols[idx % 3]:
            st.markdown(f"<div class='group-card'><div class='group-title'>GRUPO {g}</div>", unsafe_allow_html=True)
            for t in teams:
                st.markdown(f"{flag_img(t,20,15)}&nbsp;**{display_name(t)}**", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# FASE DE GRUPOS
# ---------------------------------------------------------------------------
def _show_group_stage(state, euro):
    groups = euro["groups"]
    results = euro.get("group_results", {})

    st.markdown("### 📊 Fase de Grupos — Eurocopa FMMJ")
    st.caption("Ingresa los resultados de cada partido. Clasifican los **2 primeros** de cada grupo + los **4 mejores terceros** al cuadro de llaves.")

    all_groups_complete = True

    for g, teams in groups.items():
        fixtures = []
        for i in range(len(teams)):
            for j in range(i+1, len(teams)):
                fixtures.append((teams[i], teams[j]))

        with st.expander(f"📋 GRUPO {g}", expanded=True):
            # Ingresar resultados
            st.markdown("**Resultados de partidos:**")
            for home, away in fixtures:
                key = match_key(home, away)
                res = results.get(key, {})
                played = res.get("played", False)

                col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 3, 1])
                with col1:
                    st.markdown(f"{flag_img(home,20,15)}&nbsp;**{display_name(home)}**", unsafe_allow_html=True)
                with col2:
                    hg = st.number_input("", min_value=0, max_value=20,
                                        value=res.get("home_goals", 0),
                                        key=f"euro_hg_{g}_{home}_{away}",
                                        label_visibility="collapsed")
                with col3:
                    ag = st.number_input("", min_value=0, max_value=20,
                                        value=res.get("away_goals", 0),
                                        key=f"euro_ag_{g}_{home}_{away}",
                                        label_visibility="collapsed")
                with col4:
                    st.markdown(f"{flag_img(away,20,15)}&nbsp;**{display_name(away)}**", unsafe_allow_html=True)
                with col5:
                    save = st.button("💾", key=f"euro_save_{g}_{home}_{away}", help="Guardar resultado")

                # Goleadores
                col_sc1, col_sc2 = st.columns(2)
                with col_sc1:
                    hs = st.text_input(f"Goleadores {display_name(home)}", value=", ".join(res.get("home_scorers", [])),
                                      key=f"euro_hs_{g}_{home}_{away}", placeholder="Jugador 2, Jugador2 1")
                with col_sc2:
                    as_ = st.text_input(f"Goleadores {display_name(away)}", value=", ".join(res.get("away_scorers", [])),
                                       key=f"euro_as_{g}_{home}_{away}", placeholder="Jugador 1")

                if save:
                    euro["group_results"][key] = {
                        "home_goals": hg, "away_goals": ag,
                        "home_scorers": [s.strip() for s in hs.split(",") if s.strip()],
                        "away_scorers": [s.strip() for s in as_.split(",") if s.strip()],
                        "played": True
                    }
                    register_scorers(hs, home, state, TORNEO_NAME)
                    register_scorers(as_, away, state, TORNEO_NAME)
                    st.rerun()

                if not results.get(key, {}).get("played"):
                    all_groups_complete = False
                st.markdown("---")

            # Tabla
            st.markdown("**Tabla de posiciones:**")
            standings = calculate_standings(teams, {k: v for k, v in results.items()
                                                     if any(t in k for t in teams)})
            euro["group_standings"][g] = standings
            st.markdown(render_standings_table(standings, advancing=2, show_thirds=True),
                       unsafe_allow_html=True)
            st.caption("🟢 Clasificado directo | 🟡 Posible mejor tercero")

    # Botón para avanzar a llaves
    if all_groups_complete or st.checkbox("🔓 Forzar avance a llaves (aunque falten resultados)"):
        if euro["phase"] == "grupos":
            if st.button("⚽ Generar Llaves — Fase de Eliminación", type="primary", use_container_width=True):
                _build_knockout_bracket(state, euro)
                euro["phase"] = "llaves"
                st.rerun()


# ---------------------------------------------------------------------------
# CONSTRUCCIÓN DEL CUADRO ELIMINATORIO
# ---------------------------------------------------------------------------
def _build_knockout_bracket(state, euro):
    """
    Top 2 de cada grupo (12) + 4 mejores terceros = 16 equipos
    Formato UEFA Euro: Octavos definidos por tabla de mejores terceros
    """
    standings = euro.get("group_standings", {})
    groups_order = sorted(standings.keys())

    firsts = []
    seconds = []
    thirds = []

    for g in groups_order:
        s = standings[g]
        if len(s) >= 1:
            firsts.append(s[0]["team"])
        if len(s) >= 2:
            seconds.append(s[1]["team"])
        if len(s) >= 3:
            thirds.append(s[2])

    # Mejores 4 terceros (por puntos, dg, gf)
    best4_thirds = sorted(thirds, key=lambda x: (-x["pts"], -x["dg"], -x["gf"]))[:4]
    best4_thirds_teams = [x["team"] for x in best4_thirds]
    best4_thirds_groups = [g for g in groups_order
                           if any(standings[g][2]["team"] == t for t in best4_thirds_teams
                                  if len(standings.get(g, [])) > 2)]

    # Emparejamiento octavos de final (simplificado por posición)
    # 1A vs Mejor3(BCDEF), 1C vs 3(DEF), etc. (usamos orden estándar UEFA)
    round_of_16 = []
    # Emparejamiento estándar UEFA Euro 2024:
    # 1A vs 2C, 1B vs 3(ADEF), 1C vs 3(DEF), 1D vs 2B
    # 1E vs 3(ABC), 1F vs 3(ABCD), 2D vs 2E, 2A vs 2F
    # Simplificado: top2 + best4thirds aleatoriamente
    qualified_16 = firsts + seconds
    random.shuffle(best4_thirds_teams)
    qualified_16 = qualified_16[:12] + best4_thirds_teams

    random.shuffle(qualified_16)
    for i in range(0, 16, 2):
        round_of_16.append((qualified_16[i], qualified_16[i+1]))

    euro["knockout_bracket"] = {
        "octavos": [{"home": m[0], "away": m[1], "winner": None} for m in round_of_16],
        "cuartos": [],
        "semis": [],
        "tercer_puesto": [],
        "final": [],
    }
    euro["knockout_results"] = {}


# ---------------------------------------------------------------------------
# LLAVES ELIMINATORIAS
# ---------------------------------------------------------------------------
def _show_knockout(state, euro):
    st.markdown("### ⚽ Fase de Eliminación — Eurocopa FMMJ")
    bracket = euro.get("knockout_bracket", {})
    results = euro.get("knockout_results", {})

    phases = [
        ("octavos", "🔵 Octavos de Final", "cuartos"),
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
            home = match["home"]
            away = match["away"]
            if not home or not away:
                st.markdown(f"*Pendiente de clasificación*")
                all_done = False
                continue

            key = f"euro_{phase_key}_{idx}"
            res = results.get(key, {})

            with st.container():
                st.markdown(f"<div class='knockout-match'>", unsafe_allow_html=True)
                col1, col2, col3, col4, col5, col6 = st.columns([3,1,1,3,2,1])
                with col1:
                    st.markdown(f"{flag_img(home,22,16)}&nbsp;**{display_name(home)}**", unsafe_allow_html=True)
                with col2:
                    hg = st.number_input("", min_value=0, max_value=20,
                                        value=res.get("home_goals", 0),
                                        key=f"{key}_hg", label_visibility="collapsed")
                with col3:
                    ag = st.number_input("", min_value=0, max_value=20,
                                        value=res.get("away_goals", 0),
                                        key=f"{key}_ag", label_visibility="collapsed")
                with col4:
                    st.markdown(f"{flag_img(away,22,16)}&nbsp;**{display_name(away)}**", unsafe_allow_html=True)
                with col5:
                    if hg == ag:
                        pen_opt = [None, home, away]
                        pen_disp = ["— Penales —", display_name(home), display_name(away)]
                        pen_idx = pen_opt.index(res.get("penalty_winner")) if res.get("penalty_winner") in pen_opt else 0
                        pen_sel = st.selectbox("Penales", pen_disp, index=pen_idx, key=f"{key}_pen")
                        pen_winner = pen_opt[pen_disp.index(pen_sel)]
                    else:
                        pen_winner = None
                        st.markdown("")
                with col6:
                    save = st.button("💾", key=f"{key}_save", help="Guardar")

                # Goleadores
                col_s1, col_s2 = st.columns(2)
                with col_s1:
                    hs = st.text_input(f"⚽ Gol. {display_name(home)}", value=", ".join(res.get("home_scorers", [])),
                                      key=f"{key}_hs")
                with col_s2:
                    as_ = st.text_input(f"⚽ Gol. {display_name(away)}", value=", ".join(res.get("away_scorers", [])),
                                       key=f"{key}_as")

                if save:
                    winner = home if hg > ag else (away if ag > hg else pen_winner)
                    results[key] = {
                        "home_goals": hg, "away_goals": ag,
                        "penalty_winner": pen_winner, "winner": winner,
                        "home_scorers": [s.strip() for s in hs.split(",") if s.strip()],
                        "away_scorers": [s.strip() for s in as_.split(",") if s.strip()],
                    }
                    euro["knockout_bracket"][phase_key][idx]["winner"] = winner
                    register_scorers(hs, home, state, TORNEO_NAME)
                    register_scorers(as_, away, state, TORNEO_NAME)
                    st.rerun()

                if res.get("winner"):
                    st.markdown(f"<span class='winner-tag'>✅ Ganador: {flag_img(res['winner'],18,13)}{display_name(res['winner'])}</span>",
                               unsafe_allow_html=True)
                else:
                    all_done = False

                st.markdown("</div>", unsafe_allow_html=True)

        # Avanzar a siguiente fase
        if all_done and next_phase is not None and not bracket.get(next_phase):
            winners = [results.get(f"euro_{phase_key}_{i}", {}).get("winner")
                      for i in range(len(matches))]
            winners = [w for w in winners if w]
            if next_phase == "semis" and phase_key == "cuartos":
                losers = [m.get("winner") for m in bracket.get("cuartos", []) if m.get("winner")]
                # semis toma winners de cuartos
            next_matches = [(winners[i], winners[i+1]) for i in range(0, len(winners)-1, 2)]
            bracket[next_phase] = [{"home": m[0], "away": m[1], "winner": None} for m in next_matches]
            if next_phase == "semis":
                # También preparar el partido por el tercer puesto
                bracket["tercer_puesto"] = []
            euro["knockout_results"] = results
            st.rerun()

        if all_done and phase_key == "semis" and not bracket.get("tercer_puesto"):
            losers = []
            for i, match in enumerate(matches):
                key = f"euro_semis_{i}"
                res = results.get(key, {})
                winner = res.get("winner")
                loser = match["home"] if winner == match["away"] else match["away"]
                if loser:
                    losers.append(loser)
            if len(losers) == 2:
                bracket["tercer_puesto"] = [{"home": losers[0], "away": losers[1], "winner": None}]
                st.rerun()

        # Final y 3er puesto -> clasificados
        if all_done and phase_key == "final":
            _determine_euro_qualified(state, euro, results, bracket)


def _determine_euro_qualified(state, euro, results, bracket):
    if euro.get("qualified"):
        return  # ya calculado

    # Orden knockout: campeón=1, finalista=2, semifinalistas=3-4, cuartos=5-8...
    champion = None
    final_res = results.get("euro_final_0", {})
    if final_res.get("winner"):
        champion = final_res["winner"]

    finalist = None
    for m in bracket.get("final", []):
        if m.get("winner"):
            finalist = m["home"] if m["winner"] == m["away"] else m["away"]

    semifinalists = []
    for i, m in enumerate(bracket.get("semis", [])):
        res_s = results.get(f"euro_semis_{i}", {})
        loser = m["home"] if res_s.get("winner") == m["away"] else m["away"]
        if loser:
            semifinalists.append(loser)

    quarter_losers = []
    for i, m in enumerate(bracket.get("cuartos", [])):
        res_q = results.get(f"euro_cuartos_{i}", {})
        loser = m["home"] if res_q.get("winner") == m["away"] else m["away"]
        if loser:
            quarter_losers.append(loser)

    # Top 5 van al mundial directo
    direct = [champion, finalist] + semifinalists + quarter_losers[:1]
    direct = [t for t in direct if t][:5]

    # Puestos 6-21: van al playoff UEFA (16 equipos, 4 grupos, top2 van al mundial = 8 clasificados)
    all_knockout = [champion, finalist] + semifinalists + quarter_losers
    all_round16 = [m["home"] for m in bracket.get("octavos", [])] + \
                  [m["away"] for m in bracket.get("octavos", [])]

    group_teams_flat = [t for teams in euro["groups"].values() for t in teams]
    # Eliminados en fase de grupos (puestos 3 y 4 sin ser mejores terceros)
    best_thirds = []
    fourth_placed = []
    for g, standings in euro.get("group_standings", {}).items():
        if len(standings) >= 3:
            best_thirds.append(standings[2]["team"])
        if len(standings) >= 4:
            fourth_placed.append(standings[3]["team"])

    playoff_candidates = [t for t in all_round16
                         if t and t not in direct and t not in all_knockout[:6]]
    # Completar con grupos
    for t in fourth_placed + best_thirds:
        if t and t not in direct and t not in playoff_candidates:
            playoff_candidates.append(t)

    playoff_candidates = list(dict.fromkeys(playoff_candidates))[:16]

    euro["qualified_direct"] = direct
    euro["playoff_candidates"] = playoff_candidates
    euro["phase"] = "playoff_uefa"


# ---------------------------------------------------------------------------
# PLAYOFF UEFA (puestos 6-21 → 8 clasificados)
# ---------------------------------------------------------------------------
def _show_uefa_playoff(state, euro):
    st.markdown("### 🔄 Playoff UEFA — 8 cupos al Mundial")
    st.caption("16 equipos eliminados en llaves + mejores grupos compiten en 4 grupos de 4. Los 2 primeros de cada grupo clasifican.")

    if euro["phase"] not in ["playoff_uefa", "completado"]:
        st.info("Esta fase se habilita una vez concluya la Eurocopa.")
        return

    if not euro.get("playoff_bracket"):
        candidates = euro.get("playoff_candidates", [])
        if len(candidates) < 16:
            st.warning(f"Solo hay {len(candidates)} candidatos al playoff. Se necesitan 16.")
            return
        # Sorteo 4 grupos de 4
        random.shuffle(candidates)
        playoff_groups = {f"P{i+1}": candidates[i*4:(i+1)*4] for i in range(4)}
        euro["playoff_bracket"] = {
            "groups": playoff_groups,
            "results": {},
            "standings": {},
        }

    pb = euro["playoff_bracket"]
    playoff_results = pb.get("results", {})
    all_complete = True

    for g, teams in pb["groups"].items():
        with st.expander(f"Grupo Playoff {g}", expanded=True):
            fixtures = [(teams[i], teams[j]) for i in range(len(teams)) for j in range(i+1, len(teams))]
            for home, away in fixtures:
                key = match_key(home, away)
                res = playoff_results.get(key, {})
                col1, col2, col3, col4, col5 = st.columns([3,1,1,3,1])
                with col1:
                    st.markdown(f"{flag_img(home)}&nbsp;**{display_name(home)}**", unsafe_allow_html=True)
                with col2:
                    hg = st.number_input("", 0, 20, res.get("home_goals", 0), key=f"epo_hg_{g}_{home}_{away}", label_visibility="collapsed")
                with col3:
                    ag = st.number_input("", 0, 20, res.get("away_goals", 0), key=f"epo_ag_{g}_{home}_{away}", label_visibility="collapsed")
                with col4:
                    st.markdown(f"{flag_img(away)}&nbsp;**{display_name(away)}**", unsafe_allow_html=True)
                with col5:
                    if st.button("💾", key=f"epo_save_{g}_{home}_{away}"):
                        playoff_results[key] = {"home_goals": hg, "away_goals": ag, "played": True}
                        pb["results"] = playoff_results
                        st.rerun()
                if not playoff_results.get(key, {}).get("played"):
                    all_complete = False

            standings = calculate_standings(teams, {k: v for k, v in playoff_results.items()
                                                     if any(t in k for t in teams)})
            pb["standings"][g] = standings
            st.markdown(render_standings_table(standings, advancing=2), unsafe_allow_html=True)

    if all_complete:
        qualified_playoff = []
        for g, standings in pb["standings"].items():
            for row in standings[:2]:
                qualified_playoff.append(row["team"])

        all_qualified = euro.get("qualified_direct", []) + qualified_playoff
        euro["qualified"] = all_qualified
        euro["phase"] = "completado"

        st.success(f"✅ Playoff completado. {len(qualified_playoff)} equipos adicionales clasificados al Mundial.")


# ---------------------------------------------------------------------------
# CLASIFICADOS
# ---------------------------------------------------------------------------
def _show_qualified(state, euro):
    st.markdown("### 🌍 Clasificados UEFA al Mundial FMMJ")

    direct = euro.get("qualified_direct", [])
    playoff_q = [t for t in euro.get("qualified", []) if t not in direct]

    if direct:
        st.markdown("#### ✅ Clasificados Directos (Top 5 Eurocopa)")
        for i, t in enumerate(direct, 1):
            st.markdown(f"{i}. {flag_img(t,22,16)}&nbsp;**{display_name(t)}**", unsafe_allow_html=True)

    if playoff_q:
        st.markdown("#### 🔄 Clasificados vía Playoff UEFA")
        for i, t in enumerate(playoff_q, 1):
            st.markdown(f"{i}. {flag_img(t,22,16)}&nbsp;**{display_name(t)}**", unsafe_allow_html=True)

    total = euro.get("qualified", [])
    if total:
        st.info(f"**Total UEFA clasificados: {len(total)}/13**")
        # Actualizar en estado global
        state["world_cup_qualified"] = list(set(state["world_cup_qualified"] + total))
    else:
        st.info("Los clasificados aparecerán aquí una vez concluyan ambas fases.")
