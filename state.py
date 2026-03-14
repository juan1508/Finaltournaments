"""
state.py — Gestión de estado de sesión para FMMJ Nations
"""
import streamlit as st
from data import INITIAL_FIFA_RANKING, FLAG_MAP


# ──────────────────────────────────────────────
# INIT STATE — inicializa todas las keys
# ──────────────────────────────────────────────
def init_state():
    defaults = {
        # General
        "active_page":   "🏠 Inicio",
        "season":        1,
        "season_history": [],
        "fifa_ranking":  dict(INITIAL_FIFA_RANKING),
        "top_scorers":   {},

        # Mundial
        "wc_qualified":     [],
        "wc_champion":      None,
        "wc_host":          "USA",
        "wc_groups":        {},
        "wc_matches":       {},
        "wc_standings":     {},
        "wc_r16":           [],
        "wc_r16_results":   {},
        "wc_qf":            [],
        "wc_qf_results":    {},
        "wc_sf":            [],
        "wc_sf_results":    {},
        "wc_final":         None,
        "wc_final_result":  None,
        "wc_third":         None,
        "wc_third_result":  None,

        # Eurocopa
        "euro_teams":            [],
        "euro_groups":           {},
        "euro_matches":          {},
        "euro_standings":        {},
        "euro_r16":              [],
        "euro_r16_results":      {},
        "euro_qf":               [],
        "euro_qf_results":       {},
        "euro_sf":               [],
        "euro_sf_results":       {},
        "euro_final":            None,
        "euro_final_result":     None,
        "euro_champion":         None,
        "euro_final_standings":  [],

        # Playoffs UEFA
        "euro_playoff_groups":    {},
        "euro_playoff_matches":   {},
        "euro_playoff_standings": {},
        "euro_playoff_qualified": [],

        # Copa América
        "ca_teams":           [],
        "ca_groups":          {},
        "ca_matches":         {},
        "ca_standings":       {},
        "ca_r16":             [],
        "ca_r16_results":     {},
        "ca_sf":              [],
        "ca_sf_results":      {},
        "ca_final":           None,
        "ca_final_result":    None,
        "ca_champion":        None,
        "ca_final_standings": [],

        # Playoffs CONMEBOL
        "conmebol_playoff_teams":      [],
        "conmebol_playoff_matches":    {},
        "conmebol_playoff_standings":  [],
        "conmebol_playoff_qualified":  [],
        "conmebol_playoff_repechaje":  None,

        # Copa África
        "af_teams":           [],
        "af_groups":          {},
        "af_matches":         {},
        "af_standings":       {},
        "af_sf":              [],
        "af_sf_results":      {},
        "af_final":           None,
        "af_final_result":    None,
        "af_champion":        None,
        "af_final_standings": [],

        # Playoffs CAF
        "caf_playoff_teams":      [],
        "caf_playoff_matches":    {},
        "caf_playoff_standings":  [],
        "caf_playoff_qualified":  [],

        # Copa Oro
        "co_teams":           [],
        "co_groups":          {},
        "co_matches":         {},
        "co_standings":       {},
        "co_sf":              [],
        "co_sf_results":      {},
        "co_final":           None,
        "co_final_result":    None,
        "co_champion":        None,
        "co_final_standings": [],

        # Playoffs CONCACAF
        "concacaf_playoff_teams":      [],
        "concacaf_playoff_matches":    {},
        "concacaf_playoff_standings":  [],
        "concacaf_playoff_qualified":  [],
        "concacaf_playoff_repechaje":  None,

        # Copa Asia
        "as_teams":           [],
        "as_groups":          {},
        "as_matches":         {},
        "as_standings":       {},
        "as_sf":              [],
        "as_sf_results":      {},
        "as_final":           None,
        "as_final_result":    None,
        "as_champion":        None,
        "as_final_standings": [],

        # Playoffs AFC
        "afc_playoff_teams":      [],
        "afc_playoff_matches":    {},
        "afc_playoff_standings":  [],
        "afc_playoff_qualified":  [],
        "afc_playoff_repechaje":  None,

        # Repechaje Internacional
        "int_playoff_match1":   None,
        "int_playoff_match2":   None,
        "int_playoff_qualified": [],
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


# ──────────────────────────────────────────────
# HELPERS DE BANDERA (compatibilidad con app.py)
# ──────────────────────────────────────────────
def flag(team):
    """Devuelve el código ISO del país."""
    return FLAG_MAP.get(team, "")

def flag_url(team, width=20, height=15):
    code = FLAG_MAP.get(team, "")
    if code:
        return f"https://flagcdn.com/{width}x{height}/{code}.png"
    return ""

def flag_img(team, width=20):
    """Devuelve tag <img> con la bandera."""
    code = FLAG_MAP.get(team, "")
    if not code:
        return ""
    h = int(width * 0.75)
    return f'<img src="https://flagcdn.com/{width}x{h}/{code}.png" style="vertical-align:middle;border-radius:2px;margin-right:5px;">'


# ──────────────────────────────────────────────
# GENERACIÓN DE PARTIDOS DE GRUPO
# ──────────────────────────────────────────────
def generate_group_matches(teams):
    """Genera todos los enfrentamientos posibles entre los equipos de un grupo."""
    from itertools import combinations
    matches = {}
    for t1, t2 in combinations(teams, 2):
        matches[(t1, t2)] = None
    return matches


# ──────────────────────────────────────────────
# OBTENER RESULTADO DE UN PARTIDO
# ──────────────────────────────────────────────
def get_match_result(matches, t1, t2):
    """Busca el resultado de un partido en el dict de matches."""
    if (t1, t2) in matches:
        return matches[(t1, t2)]
    if (t2, t1) in matches:
        return matches[(t2, t1)]
    return None


# ──────────────────────────────────────────────
# CÁLCULO DE POSICIONES / STANDINGS
# ──────────────────────────────────────────────
def compute_standings(teams, matches):
    """
    Calcula la tabla de posiciones de un grupo.
    matches: dict {(t1,t2): {"hg":int,"ag":int,...} | None}
    Retorna lista de dicts ordenada por pts, gd, gf.
    """
    stats = {t: {"pts":0,"played":0,"w":0,"d":0,"l":0,"gf":0,"ga":0,"gd":0} for t in teams}

    for (t1, t2), res in matches.items():
        if res is None:
            continue
        hg = res.get("hg", 0)
        ag = res.get("ag", 0)

        # Solo procesar si ambos equipos están en el grupo
        if t1 not in stats or t2 not in stats:
            continue

        stats[t1]["played"] += 1
        stats[t2]["played"] += 1
        stats[t1]["gf"] += hg
        stats[t1]["ga"] += ag
        stats[t2]["gf"] += ag
        stats[t2]["ga"] += hg
        stats[t1]["gd"] = stats[t1]["gf"] - stats[t1]["ga"]
        stats[t2]["gd"] = stats[t2]["gf"] - stats[t2]["ga"]

        if hg > ag:
            stats[t1]["pts"] += 3
            stats[t1]["w"]   += 1
            stats[t2]["l"]   += 1
        elif ag > hg:
            stats[t2]["pts"] += 3
            stats[t2]["w"]   += 1
            stats[t1]["l"]   += 1
        else:
            stats[t1]["pts"] += 1
            stats[t2]["pts"] += 1
            stats[t1]["d"]   += 1
            stats[t2]["d"]   += 1

    # Ordenar: puntos → diferencia de goles → goles a favor
    sorted_teams = sorted(
        teams,
        key=lambda t: (stats[t]["pts"], stats[t]["gd"], stats[t]["gf"]),
        reverse=True
    )

    result = []
    for pos, team in enumerate(sorted_teams, 1):
        result.append({
            "pos":    pos,
            "team":   team,
            "pts":    stats[team]["pts"],
            "played": stats[team]["played"],
            "w":      stats[team]["w"],
            "d":      stats[team]["d"],
            "l":      stats[team]["l"],
            "gf":     stats[team]["gf"],
            "ga":     stats[team]["ga"],
            "gd":     stats[team]["gd"],
        })
    return result


# ──────────────────────────────────────────────
# ACTUALIZAR GOLEADORES
# ──────────────────────────────────────────────
def update_scorer(player_name, team, goals, prefix=""):
    """Registra goles de un jugador en top_scorers."""
    if not player_name:
        return
    key = f"{prefix}{player_name}|{team}"
    if key not in st.session_state.top_scorers:
        st.session_state.top_scorers[key] = 0
    st.session_state.top_scorers[key] += goals


# ──────────────────────────────────────────────
# ACTUALIZAR RANKING FIFA
# ──────────────────────────────────────────────
def update_ranking_from_standings(final_standings, base_points, decay):
    """
    Actualiza el ranking FIFA según el resultado de un torneo.
    final_standings: lista de {"pos": int, "team": str}
    base_points: puntos para el campeón
    decay: reducción de puntos por posición
    """
    for entry in final_standings:
        team = entry["team"]
        pos  = entry["pos"]
        pts  = max(base_points - (pos - 1) * decay, 0)
        if pts > 0 and team in st.session_state.fifa_ranking:
            st.session_state.fifa_ranking[team] = (
                st.session_state.fifa_ranking[team] + pts
            )
        elif pts > 0:
            st.session_state.fifa_ranking[team] = pts
