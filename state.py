"""
state.py — Gestión de estado con persistencia JSON para FMMJ World Cup Simulator
"""
import streamlit as st
import json
import os

STATE_FILE = "fmmj_state.json"

from data import (
    INITIAL_FIFA_RANKING, UEFA_TEAMS, CONMEBOL_TEAMS, CAF_TEAMS,
    CONCACAF_TEAMS, AFC_TEAMS, PLAYOFF_TEAMS, CONFEDERATIONS
)

RANKING_POINTS = {
    "champion":      80,
    "runner_up":     65,
    "third":         55,
    "fourth":        50,
    "semis_loss":    47,
    "quarters_win":  45,
    "quarters_loss": 40,
    "group_win":     10,
    "group_draw":     5,
    "group_loss":     0,
    "playoff_win":    8,
    "playoff_draw":   4,
    "playoff_loss":   0,
}


def get_initial_state():
    return {
        "host": "Nigeria",
        "edition": 1,
        "ranking": dict(sorted(INITIAL_FIFA_RANKING.items(), key=lambda x: -x[1])),
        "world_cup_qualified": [],
        "playoff_teams": {
            "conmebol_slot": None,
            "concacaf_slot": None,
            "afc_slot":      None,
            "ofc_slot":      "New Zealand",
        },
        "playoff_results": {},
        "all_scorers": {},
        "euro": {
            "phase": "sorteo",
            "groups": {}, "group_results": {}, "group_standings": {},
            "best_thirds": [], "knockout_bracket": {}, "knockout_results": {},
            "playoff_bracket": {}, "playoff_results": {},
            "direct_qualified": [], "qualified": [], "playoff_pool": [],
            "setup_done": False,
        },
        "copa_america": {
            "phase": "configuracion",
            "guests": [], "groups": {}, "group_results": {}, "group_standings": {},
            "knockout_bracket": {}, "knockout_results": {},
            "playoff_bracket": {}, "playoff_results": {},
            "champion": None, "qualified_direct": [], "qualified": [],
            "playoff_pool": [], "setup_done": False,
        },
        "copa_africa": {
            "phase": "sorteo",
            "groups": {}, "group_results": {}, "group_standings": {},
            "knockout_bracket": {}, "knockout_results": {},
            "playoff_bracket": {}, "playoff_results": {},
            "champion": None, "finalist": None,
            "qualified_direct": [], "qualified": [],
            "playoff_pool": [], "setup_done": False,
        },
        "copa_oro": {
            "phase": "sorteo",
            "groups": {}, "group_results": {}, "group_standings": {},
            "knockout_bracket": {}, "knockout_results": {},
            "playoff_bracket": {}, "playoff_results": {},
            "champion": None, "qualified": [],
            "playoff_pool": [], "setup_done": False,
        },
        "copa_asia": {
            "phase": "sorteo",
            "groups": {}, "group_results": {}, "group_standings": {},
            "knockout_bracket": {}, "knockout_results": {},
            "playoff_bracket": {}, "playoff_results": {},
            "champion": None, "qualified": [],
            "playoff_pool": [], "setup_done": False,
        },
        "world_cup": {
            "phase": "sorteo",
            "pots": {}, "groups": {}, "group_results": {}, "group_standings": {},
            "knockout_bracket": {}, "knockout_results": {},
            "champion": None, "setup_done": False,
        },
    }


def load_state_from_file():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return get_initial_state()


def save_state_to_file(state):
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.toast(f"No se pudo guardar: {e}")


def _migrate_state(state):
    initial = get_initial_state()
    for key, val in initial.items():
        if key not in state:
            state[key] = val
    for tour_key in ["euro", "copa_america", "copa_africa", "copa_oro", "copa_asia", "world_cup"]:
        if tour_key in state and tour_key in initial:
            for k, v in initial[tour_key].items():
                if k not in state[tour_key]:
                    state[tour_key][k] = v


def init_state():
    if "fmmj_state" not in st.session_state:
        st.session_state.fmmj_state = load_state_from_file()
    _migrate_state(st.session_state.fmmj_state)


def get_state():
    init_state()
    return st.session_state.fmmj_state


def save_state():
    if "fmmj_state" in st.session_state:
        save_state_to_file(st.session_state.fmmj_state)


def reset_for_new_edition():
    current_ranking = st.session_state.fmmj_state["ranking"].copy()
    current_edition = st.session_state.fmmj_state.get("edition", 1)
    new_state = get_initial_state()
    new_state["ranking"] = current_ranking
    new_state["edition"] = current_edition + 1
    new_state["host"] = None
    st.session_state.fmmj_state = new_state
    save_state_to_file(new_state)


def update_ranking(team, points, state=None):
    if state is None:
        state = get_state()
    if team and team in state["ranking"]:
        state["ranking"][team] = state["ranking"].get(team, 1000) + points
        state["ranking"] = dict(sorted(state["ranking"].items(), key=lambda x: -x[1]))
    save_state()


def get_team_confederation(team):
    for conf, teams in CONFEDERATIONS.items():
        if team in teams:
            return conf
    return "OFC"
