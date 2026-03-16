"""
pages/repechaje.py - Repechaje Internacional + Sorteo y Mundial FMMJ
"""
import sys, os as _os
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
import streamlit as st
import random
from data import INITIAL_FIFA_RANKING, FLAG_MAP
from state import get_state, get_team_confederation
from utils.tournament import (
    display_name, flag_img, calculate_standings,
    match_key, render_standings_table, register_scorers, CONF_COLORS
)

# ---------------------------------------------------------------------------
# REPECHAJE INTERNACIONAL
# ---------------------------------------------------------------------------
def show_repechaje():
    state = get_state()
    playoff = state["playoff_teams"]

    st.markdown("""
    <style>
    .rep-header {background:linear-gradient(135deg,#1a1a1a 0%,#333 50%,#1a1a1a 100%);
    border:2px solid #ffd700;border-radius:16px;padding:24px 32px;margin-bottom:24px;}
    .rep-title {font-size:1.8rem;font-weight:800;color:#ffd700;}
    .rep-subtitle {color:#aaa;font-size:.9rem;}
    .playoff-card {background:#111;border:1px solid #333;border-radius:12px;padding:16px;margin-bottom:12px;}
    .playoff-title {font-size:1rem;font-weight:700;color:#ffd700;margin-bottom:10px;}
    .winner-announce {background:#0d4f2e;border-radius:8px;padding:10px;color:#4eff91;font-weight:700;font-size:1rem;}
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""<div class='rep-header'>
        <div class='rep-title'>🔁 Repechaje Internacional FMMJ</div>
        <div class='rep-subtitle'>2 llaves de ida y vuelta · 2 cupos al Mundial</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("""
    **Sistema de Repechaje:**
    - 🌎 **Llave 1:** CONMEBOL vs OFC (Nueva Zelanda)
    - 🌏 **Llave 2:** CONCACAF vs AFC
    - Partidos de ida y vuelta. El global define al clasificado.
    """)

    conmebol_team = playoff.get("conmebol_slot")
    ofc_team = playoff.get("ofc_slot", "New Zealand")
    concacaf_team = playoff.get("concacaf_slot")
    afc_team = playoff.get("afc_slot")

    tabs = st.tabs(["🌎 Llave 1: CONMEBOL vs OFC", "🌏 Llave 2: CONCACAF vs AFC", "✅ Resultados"])

    # ── LLAVE 1 ────────────────────────────────────────────────────────────
    with tabs[0]:
        st.markdown("### 🌎 Llave 1: CONMEBOL vs OFC")
        if not conmebol_team:
            st.warning("⏳ Esperando clasificado CONMEBOL del Playoff Copa América (4to lugar).")
            st.info(f"OFC: **{display_name(ofc_team)}** ✅")
        else:
            st.info(f"**{display_name(conmebol_team)}** (CONMEBOL) vs **{display_name(ofc_team)}** (OFC/Nueva Zelanda)")
            _show_playoff_tie(state, "llave1", conmebol_team, ofc_team, "mundial_slot_1")

    # ── LLAVE 2 ────────────────────────────────────────────────────────────
    with tabs[1]:
        st.markdown("### 🌏 Llave 2: CONCACAF vs AFC")
        if not concacaf_team:
            st.warning("⏳ Esperando clasificado CONCACAF del Playoff Copa Oro (3er lugar).")
        elif not afc_team:
            st.warning("⏳ Esperando clasificado AFC del Playoff Copa Asia (4to lugar).")
        else:
            st.info(f"**{display_name(concacaf_team)}** (CONCACAF) vs **{display_name(afc_team)}** (AFC)")
            _show_playoff_tie(state, "llave2", concacaf_team, afc_team, "mundial_slot_2")

    # ── RESULTADOS ─────────────────────────────────────────────────────────
    with tabs[2]:
        st.markdown("### ✅ Clasificados vía Repechaje")
        slot1 = state["playoff_results"].get("mundial_slot_1")
        slot2 = state["playoff_results"].get("mundial_slot_2")

        if slot1:
            st.markdown(f"<div class='winner-announce'>🎉 Clasificado Llave 1: {flag_img(slot1,24,18)}&nbsp;{display_name(slot1)}</div>", unsafe_allow_html=True)
        else:
            st.markdown("⏳ Llave 1 pendiente")

        if slot2:
            st.markdown(f"<div class='winner-announce'>🎉 Clasificado Llave 2: {flag_img(slot2,24,18)}&nbsp;{display_name(slot2)}</div>", unsafe_allow_html=True)
        else:
            st.markdown("⏳ Llave 2 pendiente")

        if slot1 and slot2:
            st.balloons()
            st.success("✅ ¡Todos los clasificados al Mundial FMMJ están definidos!")
            # Añadir a clasificados
            for t in [slot1, slot2]:
                if t and t not in state["world_cup_qualified"]:
                    state["world_cup_qualified"].append(t)


def _show_playoff_tie(state, tie_key, home_team, away_team, slot_key):
    """Partidos de ida y vuelta"""
    pr = state.get("playoff_results", {})
    if not pr:
        state["playoff_results"] = {}
        pr = state["playoff_results"]

    for leg, leg_name in [("ida", "⚽ Partido de Ida"), ("vuelta", "⚽ Partido de Vuelta")]:
        st.markdown(f"#### {leg_name}")
        if leg == "ida":
            h, a = home_team, away_team
        else:
            h, a = away_team, home_team

        key = f"{tie_key}_{leg}"
        res = pr.get(key, {})

        col1,col2,col3,col4,col5 = st.columns([3,1,1,3,1])
        with col1: st.markdown(f"{flag_img(h)}&nbsp;**{display_name(h)}**", unsafe_allow_html=True)
        with col2:
            hg = st.number_input("", 0, 20, res.get("home_goals", 0), key=f"rep_{key}_hg", label_visibility="collapsed")
        with col3:
            ag = st.number_input("", 0, 20, res.get("away_goals", 0), key=f"rep_{key}_ag", label_visibility="collapsed")
        with col4: st.markdown(f"{flag_img(a)}&nbsp;**{display_name(a)}**", unsafe_allow_html=True)
        with col5:
            save = st.button("💾", key=f"rep_{key}_save")

        col_s1, col_s2 = st.columns(2)
        with col_s1:
            hs_v = st.text_input(f"⚽ {display_name(h)}", value=", ".join(res.get("home_scorers", [])), key=f"rep_{key}_hs")
        with col_s2:
            as_v = st.text_input(f"⚽ {display_name(a)}", value=", ".join(res.get("away_scorers", [])), key=f"rep_{key}_as")

        if save:
            pr[key] = {
                "home": h, "away": a,
                "home_goals": hg, "away_goals": ag, "played": True,
                "home_scorers": [s.strip() for s in hs_v.split(",") if s.strip()],
                "away_scorers": [s.strip() for s in as_v.split(",") if s.strip()],
            }
            state["playoff_results"] = pr
            st.rerun()

        if res.get("played"):
            st.markdown(f"*Resultado: {display_name(h)} {res['home_goals']} - {res['away_goals']} {display_name(a)}*")

    # Calcular global
    ida = pr.get(f"{tie_key}_ida", {})
    vuelta = pr.get(f"{tie_key}_vuelta", {})

    if ida.get("played") and vuelta.get("played"):
        # home_team goles totales
        home_total = ida.get("home_goals", 0) + vuelta.get("away_goals", 0)
        away_total = ida.get("away_goals", 0) + vuelta.get("home_goals", 0)

        st.markdown(f"""
        ---
        **Global:** {flag_img(home_team)}{display_name(home_team)} **{home_total}** - **{away_total}** {display_name(away_team)}{flag_img(away_team)}
        """, unsafe_allow_html=True)

        if home_total != away_total:
            winner = home_team if home_total > away_total else away_team
            st.success(f"🎉 **Clasificado: {display_name(winner)}**")
            pr[slot_key] = winner
            state["playoff_results"] = pr
        else:
            # Penales
            st.warning("⚠️ Empate en el global → Penales en la vuelta")
            pen_opts = ["— Elegir —", display_name(home_team), display_name(away_team)]
            pen_sel = st.selectbox("Ganador en penales:", pen_opts, key=f"rep_{tie_key}_pen_global")
            if pen_sel != "— Elegir —":
                winner = home_team if pen_sel == display_name(home_team) else away_team
                if st.button(f"✅ Confirmar: {display_name(winner)}", key=f"rep_{tie_key}_pen_confirm"):
                    pr[slot_key] = winner
                    state["playoff_results"] = pr
                    st.rerun()


# ---------------------------------------------------------------------------
# RANKING FMMJ
# ---------------------------------------------------------------------------
def show_ranking():
    state = get_state()

    st.markdown("""
    <style>
    .ranking-header {background:linear-gradient(135deg,#0a0a1a 0%,#1a1a3e 100%);
    border:2px solid #c8a000;border-radius:16px;padding:20px 28px;margin-bottom:24px;}
    .ranking-title {font-size:1.8rem;font-weight:800;color:#c8a000;}
    .ranking-row {display:flex;align-items:center;padding:8px 12px;border-radius:8px;margin-bottom:4px;}
    .ranking-pos {width:40px;font-weight:700;color:#888;}
    .ranking-team {flex:1;font-weight:600;}
    .ranking-pts {color:#ffd700;font-weight:700;font-size:0.9rem;}
    .conf-badge {display:inline-block;padding:2px 8px;border-radius:10px;font-size:0.7rem;font-weight:700;margin-left:8px;}
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""<div class='ranking-header'>
        <div class='ranking-title'>🏅 Ranking FMMJ</div>
        <div style='color:#888;font-size:.85rem;'>Ranking actualizado con puntos de los torneos clasificatorios</div>
    </div>""", unsafe_allow_html=True)

    ranking = state["ranking"]
    sorted_ranking = sorted(ranking.items(), key=lambda x: -x[1])

    # Filtros
    col1, col2 = st.columns([1, 3])
    with col1:
        conf_filter = st.selectbox("Confederación", ["Todas", "UEFA", "CONMEBOL", "CAF", "CONCACAF", "AFC", "OFC"])
    with col2:
        search = st.text_input("🔍 Buscar selección", placeholder="Escribe el nombre...")

    # Tabla
    html = """
    <style>
    .rank-table {width:100%;border-collapse:collapse;font-size:13px;font-family:'Segoe UI',sans-serif;}
    .rank-table th {background:#0a0a2e;color:#c8a000;padding:8px;text-align:center;position:sticky;top:0;}
    .rank-table td {padding:7px 10px;border-bottom:1px solid #1a1a3a;text-align:center;}
    .rank-table tr:hover td {background:#ffffff08;}
    .rank-1 td {background:#1a1500!important;}
    .rank-top5 td {background:#0d1500!important;}
    .team-cell-rank {text-align:left!important;font-weight:600;}
    </style>
    <table class='rank-table'>
    <tr>
      <th>#</th><th class='team-cell-rank'>Selección</th><th>Conf.</th><th>Puntos</th>
    </tr>
    """
    conf_colors_map = {
        "UEFA": "#003580", "CONMEBOL": "#006b3c", "CAF": "#8b6914",
        "CONCACAF": "#8b0000", "AFC": "#4a0080", "OFC": "#006080"
    }

    for pos, (team, pts) in enumerate(sorted_ranking, 1):
        conf = get_team_confederation(team)
        if conf_filter != "Todas" and conf != conf_filter:
            continue
        if search and search.lower() not in display_name(team).lower() and search.lower() not in team.lower():
            continue

        row_class = "rank-1" if pos == 1 else ("rank-top5" if pos <= 5 else "")
        flag = flag_img(team, 18, 13)
        color = conf_colors_map.get(conf, "#333")
        badge = f"<span style='background:{color};color:#fff;padding:2px 7px;border-radius:10px;font-size:0.7rem;font-weight:700;'>{conf}</span>"

        html += f"""
        <tr class='{row_class}'>
          <td><b>{pos}</b></td>
          <td class='team-cell-rank'>{flag}{display_name(team)}</td>
          <td>{badge}</td>
          <td><b>{pts}</b></td>
        </tr>"""

    html += "</table>"
    st.markdown(html, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# SORTEO MUNDIAL
# ---------------------------------------------------------------------------
def show_world_cup_draw():
    state = get_state()
    wc = state["world_cup"]
    qualified = state["world_cup_qualified"]
    host = state.get("host", "Nigeria")

    st.markdown("""
    <style>
    .wc-header {
        background:linear-gradient(135deg,#c8a000 0%,#ffd700 40%,#c8a000 100%);
        border-radius:16px;padding:24px 32px;margin-bottom:24px;
        box-shadow:0 8px 32px rgba(200,160,0,.4);
    }
    .wc-title {font-size:2rem;font-weight:800;color:#0a0a1a;margin:0;}
    .wc-subtitle {font-size:.9rem;color:#333;margin:4px 0 0;}
    .pot-card {border-radius:12px;padding:16px;margin-bottom:16px;}
    .pot1 {background:#1a1500;border:2px solid #ffd700;}
    .pot2 {background:#001a0d;border:2px solid #00cc66;}
    .pot3 {background:#00001a;border:2px solid #3388ff;}
    .pot4 {background:#1a000d;border:2px solid #ff6699;}
    .pot-title {font-weight:800;font-size:1rem;margin-bottom:10px;}
    .group-wc {background:#0a1020;border:1px solid #1a3060;border-radius:10px;padding:14px;}
    .group-wc-title {color:#ffd700;font-weight:700;font-size:1.1rem;border-bottom:1px solid #ffd700;margin-bottom:8px;padding-bottom:4px;}
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""<div class='wc-header'>
        <div><div class='wc-title'>🌍 FMMJ World Cup</div>
        <div class='wc-subtitle'>32 selecciones · 8 grupos de 4 · Anfitrión: {display_name(host)}</div></div>
    </div>""", unsafe_allow_html=True)

    # Asegurar que el anfitrión esté en clasificados
    if host and host not in qualified:
        qualified.insert(0, host)
        state["world_cup_qualified"] = qualified

    tabs = st.tabs(["🏅 Clasificados", "🎲 Bombos", "🎯 Sorteo Grupos", "📊 Fase de Grupos", "⚽ Llaves Mundial"])

    with tabs[0]:
        _show_qualified_32(state, qualified)
    with tabs[1]:
        _show_pots(state, wc, qualified)
    with tabs[2]:
        _show_draw(state, wc)
    with tabs[3]:
        _show_wc_groups(state, wc)
    with tabs[4]:
        _show_wc_knockout(state, wc)


def _show_qualified_32(state, qualified):
    st.markdown("### 🏅 Las 32 Selecciones del FMMJ World Cup")
    host = state.get("host")

    conf_groups = {}
    for t in qualified:
        conf = get_team_confederation(t)
        if conf not in conf_groups:
            conf_groups[conf] = []
        conf_groups[conf].append(t)

    conf_order = ["UEFA", "CONMEBOL", "CAF", "CONCACAF", "AFC", "OFC"]
    cupos = {"UEFA": 13, "CONMEBOL": 4, "CAF": 5, "CONCACAF": 3, "AFC": 4, "OFC": 1}

    for conf in conf_order:
        teams_conf = conf_groups.get(conf, [])
        total = cupos.get(conf, 0)
        with st.expander(f"{conf} — {len(teams_conf)}/{total}", expanded=True):
            for t in teams_conf:
                host_tag = "🏠 **ANFITRIÓN**" if t == host else ""
                st.markdown(f"{flag_img(t,22,16)}&nbsp;**{display_name(t)}** {host_tag}", unsafe_allow_html=True)

    st.info(f"**Total clasificados: {len(qualified)}/32**")
    if len(qualified) < 32:
        st.warning(f"Faltan {32 - len(qualified)} equipos por clasificar.")


def _show_pots(state, wc, qualified):
    st.markdown("### 🏅 Bombos para el Sorteo")
    st.caption("Los equipos se distribuyen en 4 bombos de 8 según ranking FMMJ. El anfitrión es cabeza de serie en Bombo 1.")

    if len(qualified) < 32:
        st.warning(f"Aún no están los 32 clasificados. Hay {len(qualified)} equipos.")
    
    host = state.get("host")
    ranking = state["ranking"]
    teams_sorted = sorted(qualified, key=lambda t: -ranking.get(t, 0))

    # Anfitrión siempre en bombo 1
    if host in teams_sorted:
        teams_sorted.remove(host)
        teams_sorted.insert(0, host)

    pot_size = 8
    pots = {i+1: teams_sorted[i*pot_size:(i+1)*pot_size] for i in range(4)}
    wc["pots"] = pots

    pot_styles = ["pot1", "pot2", "pot3", "pot4"]
    pot_colors = ["🟡", "🟢", "🔵", "🔴"]
    cols = st.columns(2)
    for pot_num, teams in pots.items():
        with cols[(pot_num-1) % 2]:
            st.markdown(f"<div class='{pot_styles[pot_num-1]}'><div class='pot-title'>{pot_colors[pot_num-1]} BOMBO {pot_num}</div>", unsafe_allow_html=True)
            for t in teams:
                h_tag = "🏠" if t == host else ""
                st.markdown(f"{flag_img(t,18,13)}&nbsp;{display_name(t)} {h_tag}", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)


def _show_draw(state, wc):
    st.markdown("### 🎯 Sorteo del Mundial FMMJ")
    st.caption("Regla: máx. 2 equipos UEFA por grupo. No puede haber 2 equipos de misma confederación excepto UEFA.")

    pots = wc.get("pots", {})
    if not pots or not pots.get(1):
        st.warning("Primero genera los bombos en la pestaña anterior.")
        return

    if wc.get("groups") and wc["phase"] != "sorteo":
        st.success("✅ Sorteo ya realizado.")
        _display_wc_groups_draw(wc)
        if st.button("🔄 Repetir Sorteo", type="secondary"):
            wc["groups"] = {}
            wc["phase"] = "sorteo"
            st.rerun()
        return

    if st.button("🎯 ¡Realizar Sorteo del Mundial!", type="primary", use_container_width=True):
        groups = _do_world_cup_draw(pots, state)
        wc["groups"] = groups
        wc["group_results"] = {}
        wc["group_standings"] = {}
        wc["phase"] = "grupos"
        st.rerun()

    if wc.get("groups"):
        _display_wc_groups_draw(wc)


def _do_world_cup_draw(pots, state):
    """Sorteo con restricción de confederaciones"""
    groups = {chr(65+i): [] for i in range(8)}
    host = state.get("host")

    # Pot 1: un equipo por grupo (anfitrión al Grupo A)
    pot1 = list(pots[1])
    if host in pot1:
        pot1.remove(host)
        groups["A"].append(host)
        random.shuffle(pot1)
        for i, t in enumerate(pot1):
            key = chr(65 + i + 1)
            groups[key].append(t)
    else:
        random.shuffle(pot1)
        for i, t in enumerate(pot1):
            groups[chr(65+i)].append(t)

    # Pots 2-4: respetar restricciones de confederación
    for pot_num in [2, 3, 4]:
        pot = list(pots.get(pot_num, []))
        random.shuffle(pot)
        for team in pot:
            conf = get_team_confederation(team)
            placed = False
            group_order = list(groups.keys())
            random.shuffle(group_order)
            for g in group_order:
                current = groups[g]
                if len(current) >= 4:
                    continue
                conf_count = sum(1 for t in current if get_team_confederation(t) == conf)
                if conf == "UEFA" and conf_count >= 2:
                    continue
                elif conf != "UEFA" and conf_count >= 1:
                    continue
                groups[g].append(team)
                placed = True
                break
            if not placed:
                # Forzar colocación ignorando restricción de confederación
                for g in groups:
                    if len(groups[g]) < 4:
                        groups[g].append(team)
                        break
    return groups


def _display_wc_groups_draw(wc):
    groups = wc.get("groups", {})
    cols = st.columns(4)
    for idx, (g, teams) in enumerate(groups.items()):
        with cols[idx % 4]:
            st.markdown(f"<div class='group-wc'><div class='group-wc-title'>GRUPO {g}</div>", unsafe_allow_html=True)
            for t in teams:
                st.markdown(f"{flag_img(t,20,15)}&nbsp;**{display_name(t)}**", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)


def _show_wc_groups(state, wc):
    if not wc.get("groups"):
        st.warning("Realiza el sorteo primero.")
        return

    groups = wc["groups"]
    results = wc.get("group_results", {})
    st.markdown("### 📊 Fase de Grupos — FMMJ World Cup")
    all_complete = True

    for g, teams in groups.items():
        fixtures = [(teams[i], teams[j]) for i in range(len(teams)) for j in range(i+1, len(teams))]
        with st.expander(f"📋 GRUPO {g}", expanded=False):
            for home, away in fixtures:
                key = match_key(home, away)
                res = results.get(key, {})
                col1,col2,col3,col4,col5 = st.columns([3,1,1,3,1])
                with col1: st.markdown(f"{flag_img(home)}&nbsp;**{display_name(home)}**", unsafe_allow_html=True)
                with col2:
                    hg = st.number_input("", 0, 20, res.get("home_goals", 0), key=f"wc_hg_{g}_{home}_{away}", label_visibility="collapsed")
                with col3:
                    ag = st.number_input("", 0, 20, res.get("away_goals", 0), key=f"wc_ag_{g}_{home}_{away}", label_visibility="collapsed")
                with col4: st.markdown(f"{flag_img(away)}&nbsp;**{display_name(away)}**", unsafe_allow_html=True)
                with col5:
                    save = st.button("💾", key=f"wc_save_{g}_{home}_{away}")
                col_s1, col_s2 = st.columns(2)
                with col_s1:
                    hs = st.text_input(f"⚽ {display_name(home)}", value=", ".join(res.get("home_scorers", [])), key=f"wc_hs_{g}_{home}_{away}")
                with col_s2:
                    as_ = st.text_input(f"⚽ {display_name(away)}", value=", ".join(res.get("away_scorers", [])), key=f"wc_as_{g}_{home}_{away}")
                if save:
                    wc["group_results"][key] = {
                        "home_goals": hg, "away_goals": ag, "played": True,
                        "home_scorers": [s.strip() for s in hs.split(",") if s.strip()],
                        "away_scorers": [s.strip() for s in as_.split(",") if s.strip()],
                    }
                    register_scorers(hs, home, state, "FMMJ World Cup")
                    register_scorers(as_, away, state, "FMMJ World Cup")
                    st.rerun()
                if not results.get(key, {}).get("played"):
                    all_complete = False
                st.markdown("---")

            standings = calculate_standings(teams, {k: v for k, v in results.items() if any(t in k for t in teams)})
            wc["group_standings"][g] = standings
            st.markdown(render_standings_table(standings, advancing=2), unsafe_allow_html=True)

    if all_complete or st.checkbox("🔓 Forzar avance a octavos"):
        if wc["phase"] == "grupos":
            if st.button("⚽ Generar Octavos de Final", type="primary", use_container_width=True):
                _build_wc_knockout(state, wc)
                wc["phase"] = "octavos"
                st.rerun()


def _build_wc_knockout(state, wc):
    standings = wc.get("group_standings", {})
    groups = sorted(standings.keys())
    # Octavos: 1A vs 2B, 1B vs 2A, etc.
    pairs = [
        (groups[0], groups[1]),
        (groups[2], groups[3]),
        (groups[4], groups[5]),
        (groups[6], groups[7]),
    ]
    octavos = []
    for ga, gb in pairs:
        first_a = standings[ga][0]["team"] if standings.get(ga) else None
        second_b = standings[gb][1]["team"] if len(standings.get(gb, [])) > 1 else None
        first_b = standings[gb][0]["team"] if standings.get(gb) else None
        second_a = standings[ga][1]["team"] if len(standings.get(ga, [])) > 1 else None
        octavos.append({"home": first_a, "away": second_b, "winner": None})
        octavos.append({"home": first_b, "away": second_a, "winner": None})

    wc["knockout_bracket"] = {
        "octavos": octavos,
        "cuartos": [],
        "semis": [],
        "tercer_puesto": [],
        "final": [],
    }
    wc["knockout_results"] = {}


def _show_wc_knockout(state, wc):
    st.markdown("### ⚽ Fase de Eliminación — FMMJ World Cup")
    bracket = wc.get("knockout_bracket", {})
    if not bracket:
        st.info("Completa la fase de grupos primero.")
        return
    results = wc.get("knockout_results", {})
    if results is None:
        wc["knockout_results"] = {}
        results = wc["knockout_results"]

    phases = [
        ("octavos", "🔵 Octavos de Final", "cuartos"),
        ("cuartos", "🟡 Cuartos de Final", "semis"),
        ("semis", "🟠 Semifinales", "final"),
        ("final", "🏆 GRAN FINAL", None),
    ]

    for phase_key, phase_name, next_phase in phases:
        matches = bracket.get(phase_key, [])
        if not matches: continue
        st.markdown(f"#### {phase_name}")
        all_done = True

        for idx, match in enumerate(matches):
            home, away = match.get("home"), match.get("away")
            if not home or not away:
                st.markdown("*Pendiente*"); all_done = False; continue

            key = f"wc_{phase_key}_{idx}"
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
                wc["knockout_bracket"][phase_key][idx]["winner"] = winner
                register_scorers(hs, home, state, "FMMJ World Cup")
                register_scorers(as_, away, state, "FMMJ World Cup")
                st.rerun()

            if res.get("winner"):
                st.markdown(f"**✅ {display_name(res['winner'])}** avanza")
            else:
                all_done = False
            st.markdown("---")

        if all_done and next_phase and not bracket.get(next_phase):
            winners = [results.get(f"wc_{phase_key}_{i}", {}).get("winner") for i in range(len(matches))]
            winners = [w for w in winners if w]
            if phase_key == "semis":
                losers = []
                for i, m in enumerate(matches):
                    r = results.get(f"wc_semis_{i}", {})
                    loser = m["home"] if r.get("winner") == m["away"] else m["away"]
                    if loser: losers.append(loser)
                bracket["tercer_puesto"] = [{"home": losers[0], "away": losers[1], "winner": None}] if len(losers) == 2 else []
            nxt = [(winners[i], winners[i+1]) for i in range(0, len(winners)-1, 2)]
            bracket[next_phase] = [{"home": m[0], "away": m[1], "winner": None} for m in nxt]
            wc["knockout_results"] = results
            st.rerun()

        if all_done and phase_key == "final":
            champion = results.get("wc_final_0", {}).get("winner")
            if champion:
                wc["champion"] = champion
                wc["phase"] = "completado"
                st.balloons()
                st.markdown(f"""
                <div style='background:linear-gradient(135deg,#ffd700,#c8a000);border-radius:16px;
                padding:24px;text-align:center;margin-top:20px;'>
                <div style='font-size:2.5rem;'>🏆</div>
                <div style='font-size:1.8rem;font-weight:900;color:#0a0a1a;'>{display_name(champion)}</div>
                <div style='font-size:1rem;color:#333;'>¡CAMPEÓN DEL FMMJ WORLD CUP!</div>
                </div>
                """, unsafe_allow_html=True)

    # 3er puesto
    if bracket.get("tercer_puesto"):
        st.markdown("#### 🥉 Tercer Puesto")
        for idx, m in enumerate(bracket["tercer_puesto"]):
            home, away = m["home"], m["away"]
            key = f"wc_tercer_{idx}"
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
                    wc["knockout_results"] = results
                    st.rerun()
            if res.get("winner"):
                st.markdown(f"**🥉 3er Puesto: {display_name(res['winner'])}**")
