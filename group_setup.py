"""
group_setup.py — Sorteo de grupos con banderas reales via st.components
La bandera se muestra encima del selectbox usando st.image de CDN
"""
import streamlit as st
import random
from data import TEAM_DISPLAY_NAMES, get_flag_url, CONFEDERATIONS


def display_name(team):
    return TEAM_DISPLAY_NAMES.get(team, team)


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

    # ── Botón sorteo automático arriba ───────────────────────────────
    col_auto, col_info = st.columns([1, 3])
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
    with col_info:
        total_assigned = sum(len(v) for v in dg.values())
        st.markdown(f"<div style='padding:8px 0;color:#a0b8d8;font-size:0.9rem;'>Asignados: <b>{total_assigned}/{len(teams)}</b></div>", unsafe_allow_html=True)

    st.markdown("---")

    # ── Equipos disponibles con BANDERA REAL ─────────────────────────
    if unassigned:
        st.markdown("**Asigna cada equipo a un grupo:**")
        opts_group = ["— Grupo —"] + [f"Grupo {g}" for g in group_keys]

        cols_n = 4
        rows = [unassigned[i:i+cols_n] for i in range(0, len(unassigned), cols_n)]
        for row in rows:
            cols = st.columns(cols_n)
            for col_idx, team in enumerate(row):
                with cols[col_idx]:
                    # BANDERA REAL con st.image (funciona siempre)
                    flag_url = get_flag_url(team, 40, 30)
                    if flag_url:
                        st.image(flag_url, width=36)
                    # Nombre del equipo como caption
                    st.caption(display_name(team))
                    # Selectbox con texto plano (sin HTML)
                    sel = st.selectbox(
                        ".",
                        opts_group,
                        key=f"assign_{tour_key}_{team}",
                        label_visibility="collapsed",
                    )
                    if sel != "— Grupo —":
                        g = sel.split()[-1]
                        if len(dg.get(g, [])) < teams_per_group and team not in dg[g]:
                            dg[g].append(team)
                            st.rerun()

    # ── Grupos actuales con banderas ──────────────────────────────────
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
                    f"font-family:Bebas Neue,sans-serif;font-size:1rem;'>"
                    f"GRUPO {g} ({count}/{teams_per_group})</div>",
                    unsafe_allow_html=True
                )
                for t in list(dg.get(g, [])):
                    c1, c2, c3 = st.columns([1, 4, 1])
                    with c1:
                        flag_url = get_flag_url(t, 28, 21)
                        if flag_url:
                            st.image(flag_url, width=24)
                    with c2:
                        st.markdown(
                            f"<div style='padding-top:4px;font-size:0.85rem;color:#dce8ff;'>{display_name(t)}</div>",
                            unsafe_allow_html=True
                        )
                    with c3:
                        if st.button("✕", key=f"rm_{tour_key}_{g}_{t}", help="Quitar"):
                            dg[g].remove(t)
                            st.rerun()

    # ── Confirmar ────────────────────────────────────────────────────
    st.markdown("---")
    total_assigned = sum(len(v) for v in dg.values())
    all_correct = total_assigned == len(teams) and all(len(dg[g]) == teams_per_group for g in group_keys)

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
