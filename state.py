"""
state.py - Gestión del estado global del simulador FMMJ
Maneja la sesión de Streamlit y la persistencia del estado
"""
import streamlit as st
import json
import copy
from data import INITIAL_FIFA_RANKING, UEFA_TEAMS, CONMEBOL_TEAMS, CAF_TEAMS, CONCACAF_TEAMS, AFC_TEAMS, PLAYOFF_TEAMS

# ---------------------------------------------------------------------------
# ESTADO INICIAL
# ---------------------------------------------------------------------------
def get_initial_state():
    return {
        # Meta
        "host": "Nigeria",
        "edition": 1,

        # Ranking FMMJ (puntos actualizados durante los torneos)
        "ranking": dict(sorted(INITIAL_FIFA_RANKING.items(), key=lambda x: -x[1])),

        # Clasificados al mundial
        "world_cup_qualified": [],

        # Repechaje
        "playoff_teams": {
            "conmebol_slot": None,   # 4to Copa América
            "concacaf_slot": None,   # 3er Copa Oro
            "afc_slot": None,        # 4to Copa Asia
            "ofc_slot": "New Zealand",
        },
        "playoff_results": {},

        # EUROCOPA
        "euro": {
            "phase": "grupos",  # grupos | eliminatorias_playoff | llaves | completado
            "groups": {},       # {A: [equipos], B: [...], ...}
            "group_results": {},   # resultados partidos de grupos
            "group_standings": {}, # tabla por grupo
            "best_thirds": [],      # mejores terceros
            "knockout_bracket": {}, # octavos, cuartos, semis, final
            "knockout_results": {},
            "playoff_bracket": {},  # playoff UEFA (puestos 6-21)
            "playoff_results": {},
            "qualified": [],        # clasificados UEFA al mundial (13)
            "top_scorers": {},
            "setup_done": False,
        },

        # COPA AMÉRICA
        "copa_america": {
            "phase": "configuracion",  # configuracion | grupos | eliminatorias_playoff | llaves | completado
            "guests": [],           # 6 invitadas elegidas
            "groups": {},
            "group_results": {},
            "group_standings": {},
            "knockout_bracket": {},
            "knockout_results": {},
            "playoff_bracket": {},
            "playoff_results": {},
            "qualified": [],        # clasificados CONMEBOL (4: 1 directo + 3 de playoff)
            "top_scorers": {},
            "setup_done": False,
        },

        # COPA ÁFRICA
        "copa_africa": {
            "phase": "grupos",
            "groups": {},
            "group_results": {},
            "group_standings": {},
            "knockout_bracket": {},
            "knockout_results": {},
            "playoff_bracket": {},
            "playoff_results": {},
            "qualified": [],        # clasificados CAF (5: 2 directos + 3 de playoff)
            "top_scorers": {},
            "setup_done": False,
        },

        # COPA ORO (CONCACAF)
        "copa_oro": {
            "phase": "grupos",
            "groups": {},
            "group_results": {},
            "group_standings": {},
            "knockout_bracket": {},
            "knockout_results": {},
            "playoff_bracket": {},
            "playoff_results": {},
            "qualified": [],        # clasificados CONCACAF (3: 1 directo + 2 de playoff)
            "top_scorers": {},
            "setup_done": False,
        },

        # COPA ASIA (AFC)
        "copa_asia": {
            "phase": "grupos",
            "groups": {},
            "group_results": {},
            "group_standings": {},
            "knockout_bracket": {},
            "knockout_results": {},
            "playoff_bracket": {},
            "playoff_results": {},
            "qualified": [],        # clasificados AFC (4: 1 directo + 3 de playoff)
            "top_scorers": {},
            "setup_done": False,
        },

        # MUNDIAL
        "world_cup": {
            "phase": "sorteo",  # sorteo | grupos | octavos | cuartos | semis | final | completado
            "pots": {1: [], 2: [], 3: [], 4: []},
            "groups": {},
            "group_results": {},
            "group_standings": {},
            "knockout_bracket": {},
            "knockout_results": {},
            "champion": None,
            "top_scorers": {},
            "setup_done": False,
        },

        # Goleadores globales
        "all_scorers": {},  # {jugador: {equipo, goles, torneo}}
    }

# ---------------------------------------------------------------------------
# INICIALIZAR ESTADO EN SESIÓN
# ---------------------------------------------------------------------------
def init_state():
    if "fmmj_state" not in st.session_state:
        st.session_state.fmmj_state = get_initial_state()

def get_state():
    init_state()
    return st.session_state.fmmj_state

def save_state():
    """No hace nada especial – streamlit ya persiste session_state"""
    pass

def reset_for_new_edition():
    """Resetea torneos pero mantiene ranking"""
    current_ranking = st.session_state.fmmj_state["ranking"].copy()
    current_edition = st.session_state.fmmj_state["edition"]
    new_state = get_initial_state()
    new_state["ranking"] = current_ranking
    new_state["edition"] = current_edition + 1
    new_state["host"] = None  # Se elige nuevo anfitrión
    st.session_state.fmmj_state = new_state

# ---------------------------------------------------------------------------
# HELPER: ACTUALIZAR RANKING DESPUÉS DE UN TORNEO
# ---------------------------------------------------------------------------
RANKING_POINTS = {
    # victoria, empate, derrota en cada fase
    "group_win": 3,
    "group_draw": 1,
    "group_loss": 0,
    "knockout_win": 5,
    "knockout_draw_win": 4,   # ganó en penales/prórroga
    "knockout_loss": 1,
    "champion_bonus": 20,
    "finalist_bonus": 12,
    "semifinal_bonus": 6,
    "quarterfinal_bonus": 3,
}

def update_ranking(team, points, state=None):
    if state is None:
        state = get_state()
    if team in state["ranking"]:
        state["ranking"][team] = state["ranking"].get(team, 1000) + points
    # Reordenar
    state["ranking"] = dict(sorted(state["ranking"].items(), key=lambda x: -x[1]))

def get_team_confederation(team):
    if team in UEFA_TEAMS:
        return "UEFA"
    elif team in CONMEBOL_TEAMS:
        return "CONMEBOL"
    elif team in CAF_TEAMS:
        return "CAF"
    elif team in CONCACAF_TEAMS:
        return "CONCACAF"
    elif team in AFC_TEAMS:
        return "AFC"
    elif team in PLAYOFF_TEAMS:
        return "OFC"
    return "UNKNOWN"
