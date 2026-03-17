"""
utils.py — Helpers compartidos para FMMJ World Cup Simulator
"""
import streamlit as st
import random
from data import FLAG_MAP, TEAM_DISPLAY_NAMES, get_flag_url, CONFEDERATIONS, PLAYERS


def display_name(team):
    return TEAM_DISPLAY_NAMES.get(team, team)


def flag_img(team, w=20, h=15):
    """HTML con bandera — usar SOLO en st.markdown(unsafe_allow_html=True)."""
    url = get_flag_url(team, w, h)
    if url:
        return f"<img src='{url}' style='vertical-align:middle;margin-right:4px;border-radius:2px;' width='{w}' height='{h}'>"
    return ""


def tlabel(team):
    """Label con nombre para widgets Streamlit."""
    return TEAM_DISPLAY_NAMES.get(team, team)


def get_team_confederation(team):
    for conf, teams in CONFEDERATIONS.items():
        if team in teams:
            return conf
    return "OFC"


def match_key(t1, t2):
    return f"{min(t1,t2)}||{max(t1,t2)}"


def get_jornadas(teams):
    """
    Genera jornadas round-robin con localía alternada.
    Cada jornada tiene floor(n/2) partidos y cada equipo juega exactamente una vez por jornada.
    Algoritmo de rueda (circle method) estándar para torneos.
    """
    n = len(teams)

    # Casos hardcodeados para 3 y 4 (grupos de Copa)
    if n == 3:
        return [
            [(teams[0], teams[1])],
            [(teams[0], teams[2])],
            [(teams[1], teams[2])],
        ]

    if n == 4:
        return [
            [(teams[0], teams[1]), (teams[2], teams[3])],
            [(teams[0], teams[2]), (teams[1], teams[3])],
            [(teams[0], teams[3]), (teams[1], teams[2])],
        ]

    # Para 5, 6 o cualquier otro número: algoritmo de rueda (circle method)
    # Si n es impar, añadimos un "bye" fantasma para hacer n par
    lst = list(teams)
    if n % 2 == 1:
        lst.append(None)  # bye
    m = len(lst)  # m es par
    num_rounds = m - 1
    matches_per_round = m // 2

    jornadas = []
    # El primer equipo es el "fijo", el resto rota
    fixed = lst[0]
    rotating = lst[1:]

    for ronda in range(num_rounds):
        pairs = []
        # Par del equipo fijo con el primero de la rueda
        opp = rotating[0]
        if fixed is not None and opp is not None:
            # Alternar localía: ronda par → fijo es local, impar → fijo es visitante
            if ronda % 2 == 0:
                pairs.append((fixed, opp))
            else:
                pairs.append((opp, fixed))

        # Resto de pares de la rueda
        for i in range(1, matches_per_round):
            a = rotating[i]
            b = rotating[m - 1 - i]
            if a is not None and b is not None:
                # Alternar localía según posición de ronda
                if (ronda + i) % 2 == 0:
                    pairs.append((a, b))
                else:
                    pairs.append((b, a))

        if pairs:
            jornadas.append(pairs)

        # Rotar: el último de rotating va al frente
        rotating = [rotating[-1]] + rotating[:-1]

    return jornadas


def calculate_standings(group_teams, results, prefix=""):
    """
    Calcula la tabla de posiciones.
    Usa home_team/away_team guardados en el resultado para asignar goles
    correctamente sin importar el orden alfabético de match_key.
    Si no existen esos campos (retrocompatibilidad), asume que t1=home, t2=away.
    """
    table = {t: {"team": t, "pts": 0, "gf": 0, "ga": 0, "gd": 0,
                 "pj": 0, "pg": 0, "pe": 0, "pp": 0} for t in group_teams}
    for i, t1 in enumerate(group_teams):
        for j, t2 in enumerate(group_teams):
            if i >= j:
                continue
            mk = match_key(t1, t2)
            # Buscar con prefijo primero; si no, con key pura (retrocompatibilidad)
            if prefix:
                res = results.get(f"{prefix}{mk}", results.get(mk, {}))
            else:
                res = results.get(mk, {})
            if not res.get("played"):
                continue
            hg = int(res.get("home_goals", 0))
            ag = int(res.get("away_goals", 0))
            # Usar home_team/away_team guardados para asignar goles correctamente.
            # match_key ordena alfabéticamente, pero home_goals pertenece al
            # equipo que era LOCAL cuando se jugó el partido.
            real_home = res.get("home_team")
            real_away = res.get("away_team")
            if real_home and real_away and real_home in table and real_away in table:
                # Tenemos info exacta de localía
                h, a = real_home, real_away
            else:
                # Retrocompatibilidad: asumir t1=home, t2=away
                h, a = t1, t2
            table[h]["pj"] += 1; table[a]["pj"] += 1
            table[h]["gf"] += hg; table[h]["ga"] += ag
            table[a]["gf"] += ag; table[a]["ga"] += hg
            if hg > ag:
                table[h]["pts"] += 3; table[h]["pg"] += 1; table[a]["pp"] += 1
            elif hg < ag:
                table[a]["pts"] += 3; table[a]["pg"] += 1; table[h]["pp"] += 1
            else:
                table[h]["pts"] += 1; table[a]["pts"] += 1
                table[h]["pe"] += 1; table[a]["pe"] += 1
    for t in table.values():
        t["gd"] = t["gf"] - t["ga"]
    return sorted(table.values(), key=lambda x: (-x["pts"], -x["gd"], -x["gf"]))


def render_standings_table(standings, advancing=2, show_thirds=False):
    html = """<table style='width:100%;border-collapse:collapse;font-size:0.83rem;margin-top:8px;'>
    <tr style='background:#0a1530;color:#7090c0;font-size:0.72rem;text-transform:uppercase;border-bottom:2px solid #1a2a5a;'>"""
    for h in ["", "#", "Selección", "PJ", "PG", "PE", "PP", "GF", "GA", "DG", "Pts"]:
        align = "left" if h == "Selección" else "center"
        html += f"<th style='padding:7px 8px;text-align:{align};'>{h}</th>"
    html += "</tr>"
    for i, row in enumerate(standings):
        if i < advancing:          badge, bg = "🟢", "#0d3a20"
        elif show_thirds and i == advancing: badge, bg = "🟡", "#2a2a00"
        else:                      badge, bg = "🔴", "#0a0a1a"
        html += f"<tr style='background:{bg};border-bottom:1px solid #111e35;'>"
        html += f"<td style='padding:7px 8px;text-align:center;'>{badge}</td>"
        html += f"<td style='padding:7px 8px;text-align:center;color:#666;font-weight:700;'>{i+1}</td>"
        fu = get_flag_url(row["team"], 20, 15)
        flag_cell = (f"<img src='{fu}' style='vertical-align:middle;margin-right:5px;"
                     f"border-radius:2px;border:1px solid #1a2a4a;' width='20' height='15'>") if fu else ""
        html += (f"<td style='padding:7px 8px;text-align:left;color:#e0e8ff;'>"
                 f"{flag_cell}{display_name(row['team'])}</td>")
        for k in ["pj","pg","pe","pp","gf","ga","gd"]:
            color = "#ffd700" if k == "gd" else "#e0e8ff"
            html += f"<td style='padding:7px 8px;text-align:center;color:{color};'>{row[k]}</td>"
        html += f"<td style='padding:7px 8px;text-align:center;color:#ffd700;font-weight:800;font-size:0.95rem;'>{row['pts']}</td>"
        html += "</tr>"
    html += "</table>"
    st.markdown(html, unsafe_allow_html=True)


def _scorer_input(team, num_goals, existing_scorers, widget_key, state, torneo):
    players_data = PLAYERS.get(team, [])
    if num_goals == 0:
        return []
    scorers = []
    if players_data:
        player_names = [p["name"] for p in players_data]
        for i in range(num_goals):
            default_idx = 0
            if i < len(existing_scorers) and existing_scorers[i] in player_names:
                default_idx = player_names.index(existing_scorers[i])
            sel = st.selectbox(
                f"Gol {i+1} — {tlabel(team)}",
                player_names,
                index=default_idx,
                key=f"{widget_key}_{i}"
            )
            scorers.append(sel)
    else:
        val = st.text_input(
            f"Goleadores {tlabel(team)}",
            value=", ".join(existing_scorers),
            key=f"{widget_key}_free"
        )
        scorers = [s.strip() for s in val.split(",") if s.strip()]
    return scorers


def register_scorers(scorers_list, team, state, torneo_name):
    if not scorers_list:
        return
    if "all_scorers" not in state:
        state["all_scorers"] = {}
    for name in scorers_list:
        if not name:
            continue
        key = f"{name}||{team}"
        if key not in state["all_scorers"]:
            state["all_scorers"][key] = {"name": name, "team": team, "goals": 0, "torneos": {}}
        state["all_scorers"][key]["goals"] += 1
        state["all_scorers"][key]["torneos"][torneo_name] = \
            state["all_scorers"][key]["torneos"].get(torneo_name, 0) + 1


def manual_group_setup(state, tour_key, teams, num_groups, teams_per_group, confirm_label="Confirmar grupos"):
    tour = state[tour_key]
    ranking = state["ranking"]
    teams_sorted = sorted(teams, key=lambda t: -ranking.get(t, 0))
    group_keys = [chr(65 + i) for i in range(num_groups)]

    sk = f"draft_{tour_key}"
    if sk not in st.session_state or set(st.session_state[sk].keys()) != set(group_keys):
        st.session_state[sk] = {g: [] for g in group_keys}
    dg = st.session_state[sk]

    assigned = [t for lst in dg.values() for t in lst]
    unassigned = [t for t in teams_sorted if t not in assigned]

    # ── Equipos disponibles ───────────────────────────────────────────
    if unassigned:
        st.markdown("**Equipos disponibles (por Ranking FMMJ):**")
        cols_un = st.columns(4)
        for idx, team in enumerate(unassigned):
            with cols_un[idx % 4]:
                opts = ["— Grupo —"] + [f"Grupo {g}" for g in group_keys]
                sel = st.selectbox(
                    tlabel(team),
                    opts,
                    key=f"assign_{tour_key}_{team}",
                )
                if sel != "— Grupo —":
                    g = sel.split()[-1]
                    if len(dg.get(g, [])) < teams_per_group and team not in dg[g]:
                        dg[g].append(team)
                        st.rerun()

    # ── Grupos actuales ───────────────────────────────────────────────
    st.markdown("---")
    st.markdown("**Grupos actuales:**")
    cols_per_row = min(num_groups, 4)
    gkeys_rows = [group_keys[i:i+cols_per_row] for i in range(0, num_groups, cols_per_row)]
    for row_keys in gkeys_rows:
        cols = st.columns(len(row_keys))
        for col, g in zip(cols, row_keys):
            with col:
                count = len(dg.get(g, []))
                color = "#00cc66" if count == teams_per_group else "#ffd700"
                st.markdown(
                    f"<div style='font-weight:700;color:{color};margin-bottom:6px;"
                    f"font-family:Bebas Neue,sans-serif;font-size:1rem;'>GRUPO {g} ({count}/{teams_per_group})</div>",
                    unsafe_allow_html=True
                )
                for t in list(dg.get(g, [])):
                    c1, c2 = st.columns([5, 1])
                    with c1:
                        st.markdown(
                            f"<div style='padding:2px 0;font-size:0.9rem;'>"
                            f"<img src='{get_flag_url(t,16,11)}' style='vertical-align:middle;margin-right:4px;border-radius:2px;' width='16' height='11'>&nbsp;{display_name(t)}</div>",
                            unsafe_allow_html=True
                        )
                    with c2:
                        if st.button("✕", key=f"rm_{tour_key}_{g}_{t}", help="Quitar"):
                            dg[g].remove(t)
                            st.rerun()

    # ── Acciones ──────────────────────────────────────────────────────
    total_assigned = sum(len(v) for v in dg.values())
    all_correct = total_assigned == len(teams) and all(len(dg[g]) == teams_per_group for g in group_keys)

    col_auto, col_confirm = st.columns(2)
    with col_auto:
        if st.button("🎲 Sorteo Automático", type="secondary", key=f"auto_{tour_key}"):
            ts = sorted(teams, key=lambda t: -ranking.get(t, 0))
            pot_size = len(ts) // num_groups
            remainder = len(ts) % num_groups
            pots, idx_ = [], 0
            for i in range(num_groups):
                size = pot_size + (1 if i < remainder else 0)
                pots.append(ts[idx_:idx_+size])
                idx_ += size
            new_dg = {g: [] for g in group_keys}
            for pot in pots:
                shuffled = pot[:]
                random.shuffle(shuffled)
                for i, t in enumerate(shuffled):
                    new_dg[group_keys[i % num_groups]].append(t)
            st.session_state[sk] = new_dg
            st.rerun()

    with col_confirm:
        if all_correct:
            if st.button(f"✅ {confirm_label}", type="primary", key=f"confirm_{tour_key}"):
                tour["groups"] = {g: list(v) for g, v in dg.items()}
                tour["group_results"] = {}
                tour["group_standings"] = {}
                tour["phase"] = "grupos"
                tour["setup_done"] = True
                if sk in st.session_state:
                    del st.session_state[sk]
                from state import save_state
                save_state()
                st.rerun()
        else:
            missing = len(teams) - total_assigned
            st.warning(f"Faltan {missing} equipos por asignar ({total_assigned}/{len(teams)})")
