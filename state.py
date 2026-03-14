"""
state.py — Gestión de estado + persistencia JSON via GitHub API
Orden correcto: load_state() PRIMERO, luego init_state() llena solo lo que falta.
"""
import streamlit as st
import json
import base64
import ast
import requests
from data import INITIAL_FIFA_RANKING, FLAG_MAP


# ══════════════════════════════════════════════════════
# CLAVES PERSISTIBLES
# ══════════════════════════════════════════════════════
PERSIST_KEYS = [
    "season", "season_history", "fifa_ranking", "top_scorers",
    "locked_euro","locked_ca","locked_af","locked_co",
    "locked_as","locked_wc","locked_euro_playoff",
    "wc_qualified","wc_champion","wc_host","wc_groups","wc_matches",
    "wc_standings","wc_r16","wc_r16_results","wc_qf","wc_qf_results",
    "wc_sf","wc_sf_results","wc_final","wc_final_result","wc_third","wc_third_result",
    "euro_teams","euro_groups","euro_matches","euro_standings",
    "euro_r16","euro_r16_results","euro_qf","euro_qf_results",
    "euro_sf","euro_sf_results","euro_final","euro_final_result",
    "euro_champion","euro_final_standings",
    "euro_playoff_groups","euro_playoff_matches","euro_playoff_standings","euro_playoff_qualified",
    "ca_teams","ca_groups","ca_matches","ca_standings",
    "ca_r16","ca_r16_results","ca_sf","ca_sf_results",
    "ca_final","ca_final_result","ca_champion","ca_final_standings",
    "conmebol_playoff_teams","conmebol_playoff_matches","conmebol_playoff_standings",
    "conmebol_playoff_qualified","conmebol_playoff_repechaje",
    "af_teams","af_groups","af_matches","af_standings",
    "af_sf","af_sf_results","af_final","af_final_result","af_champion","af_final_standings",
    "caf_playoff_teams","caf_playoff_matches","caf_playoff_standings","caf_playoff_qualified",
    "co_teams","co_groups","co_matches","co_standings",
    "co_sf","co_sf_results","co_final","co_final_result","co_champion","co_final_standings",
    "concacaf_playoff_teams","concacaf_playoff_matches","concacaf_playoff_standings",
    "concacaf_playoff_qualified","concacaf_playoff_repechaje",
    "as_teams","as_groups","as_matches","as_standings",
    "as_sf","as_sf_results","as_final","as_final_result","as_champion","as_final_standings",
    "afc_playoff_teams","afc_playoff_matches","afc_playoff_standings",
    "afc_playoff_qualified","afc_playoff_repechaje",
    "int_playoff_match1","int_playoff_match2","int_playoff_qualified",
]


# ══════════════════════════════════════════════════════
# SERIALIZACIÓN
# ══════════════════════════════════════════════════════
def _serialize(obj):
    if isinstance(obj, dict):
        return {str(k): _serialize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_serialize(i) for i in obj]
    if isinstance(obj, tuple):
        return list(obj)
    return obj


def _deserialize(key, obj):
    if obj is None:
        return obj
    # Matches: claves tupla
    if key.endswith("_matches") or key.endswith("_results"):
        if isinstance(obj, dict):
            result = {}
            for k, v in obj.items():
                if isinstance(k, str) and k.startswith("('"):
                    try:
                        real_k = ast.literal_eval(k)
                    except Exception:
                        real_k = k
                else:
                    real_k = k
                result[real_k] = v
            return result
    # Listas de pares KO → lista de tuplas
    if any(key.endswith(s) for s in ("_r16","_qf","_sf")):
        if isinstance(obj, list):
            out = []
            for item in obj:
                if isinstance(item, list) and len(item) == 2:
                    out.append(tuple(item))
                else:
                    out.append(item)
            return out
    # Par final → tupla
    if key.endswith("_final") and isinstance(obj, list) and len(obj) == 2:
        return tuple(obj)
    return obj


# ══════════════════════════════════════════════════════
# GITHUB API
# ══════════════════════════════════════════════════════
def _gh_headers():
    token = st.secrets.get("GITHUB_TOKEN", "")
    return {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}

def _gh_coords():
    owner = st.secrets.get("GITHUB_OWNER", "")
    repo  = st.secrets.get("GITHUB_REPO",  "")
    path  = st.secrets.get("GITHUB_STATE_PATH", "fmmj_state.json")
    return owner, repo, path


def load_state():
    owner, repo, path = _gh_coords()
    if not owner or not repo:
        return False
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    try:
        r = requests.get(url, headers=_gh_headers(), timeout=10)
        if r.status_code != 200:
            return False
        data  = r.json()
        saved = json.loads(base64.b64decode(data["content"]).decode("utf-8"))
        st.session_state["_gh_sha"] = data.get("sha", "")
        for key in PERSIST_KEYS:
            if key in saved:
                st.session_state[key] = _deserialize(key, saved[key])
        return True
    except Exception:
        return False


def save_state():
    owner, repo, path = _gh_coords()
    if not owner or not repo:
        return
    token = st.secrets.get("GITHUB_TOKEN", "")
    if not token:
        return
    snapshot    = {key: _serialize(st.session_state.get(key)) for key in PERSIST_KEYS}
    content_b64 = base64.b64encode(
        json.dumps(snapshot, ensure_ascii=False, indent=2).encode("utf-8")
    ).decode("utf-8")
    sha     = st.session_state.get("_gh_sha", "")
    payload = {"message": f"fmmj s{st.session_state.get('season',1)}", "content": content_b64}
    if sha:
        payload["sha"] = sha
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    try:
        r = requests.put(url, headers=_gh_headers(), json=payload, timeout=12)
        if r.status_code in (200, 201):
            st.session_state["_gh_sha"] = r.json()["content"]["sha"]
    except Exception:
        pass


# ══════════════════════════════════════════════════════
# DEFAULTS
# ══════════════════════════════════════════════════════
DEFAULTS = {
    "active_page": "🏠 Inicio", "season": 1, "season_history": [],
    "fifa_ranking": dict(INITIAL_FIFA_RANKING), "top_scorers": {},
    "_gh_sha": "", "_state_loaded": False,
    # Bloqueos
    "locked_euro": False, "locked_ca": False, "locked_af": False,
    "locked_co": False, "locked_as": False, "locked_wc": False,
    "locked_euro_playoff": False,
    # Mundial
    "wc_qualified":[],"wc_champion":None,"wc_host":"USA",
    "wc_groups":{},"wc_matches":{},"wc_standings":{},
    "wc_r16":[],"wc_r16_results":{},"wc_qf":[],"wc_qf_results":{},
    "wc_sf":[],"wc_sf_results":{},"wc_final":None,"wc_final_result":None,
    "wc_third":None,"wc_third_result":None,
    # Eurocopa
    "euro_teams":[],"euro_groups":{},"euro_matches":{},"euro_standings":{},
    "euro_r16":[],"euro_r16_results":{},"euro_qf":[],"euro_qf_results":{},
    "euro_sf":[],"euro_sf_results":{},"euro_final":None,"euro_final_result":None,
    "euro_champion":None,"euro_final_standings":[],
    # Playoffs UEFA
    "euro_playoff_groups":{},"euro_playoff_matches":{},"euro_playoff_standings":{},"euro_playoff_qualified":[],
    # Copa América
    "ca_teams":[],"ca_groups":{},"ca_matches":{},"ca_standings":{},
    "ca_r16":[],"ca_r16_results":{},"ca_sf":[],"ca_sf_results":{},
    "ca_final":None,"ca_final_result":None,"ca_champion":None,"ca_final_standings":[],
    # Playoffs CONMEBOL
    "conmebol_playoff_teams":[],"conmebol_playoff_matches":{},"conmebol_playoff_standings":[],
    "conmebol_playoff_qualified":[],"conmebol_playoff_repechaje":None,
    # Copa África
    "af_teams":[],"af_groups":{},"af_matches":{},"af_standings":{},
    "af_sf":[],"af_sf_results":{},"af_final":None,"af_final_result":None,
    "af_champion":None,"af_final_standings":[],
    # Playoffs CAF
    "caf_playoff_teams":[],"caf_playoff_matches":{},"caf_playoff_standings":[],"caf_playoff_qualified":[],
    # Copa Oro
    "co_teams":[],"co_groups":{},"co_matches":{},"co_standings":{},
    "co_sf":[],"co_sf_results":{},"co_final":None,"co_final_result":None,
    "co_champion":None,"co_final_standings":[],
    # Playoffs CONCACAF
    "concacaf_playoff_teams":[],"concacaf_playoff_matches":{},"concacaf_playoff_standings":[],
    "concacaf_playoff_qualified":[],"concacaf_playoff_repechaje":None,
    # Copa Asia
    "as_teams":[],"as_groups":{},"as_matches":{},"as_standings":{},
    "as_sf":[],"as_sf_results":{},"as_final":None,"as_final_result":None,
    "as_champion":None,"as_final_standings":[],
    # Playoffs AFC
    "afc_playoff_teams":[],"afc_playoff_matches":{},"afc_playoff_standings":[],
    "afc_playoff_qualified":[],"afc_playoff_repechaje":None,
    # Repechaje
    "int_playoff_match1":None,"int_playoff_match2":None,"int_playoff_qualified":[],
}

SEASON_RESET_KEYS = [k for k in PERSIST_KEYS if k not in
                     ("season","season_history","fifa_ranking","top_scorers")]


# ══════════════════════════════════════════════════════
# INIT STATE
# ══════════════════════════════════════════════════════
def init_state():
    # 1. Cargar desde GitHub PRIMERO (una vez por sesión)
    if not st.session_state.get("_state_loaded", False):
        load_state()
        st.session_state["_state_loaded"] = True
    # 2. Rellenar solo lo que no vino de GitHub
    for key, val in DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = val


def reset_season():
    """Resetea datos de torneo, conserva ranking e historial."""
    for key in SEASON_RESET_KEYS:
        default = DEFAULTS.get(key)
        if isinstance(default, dict):
            st.session_state[key] = {}
        elif isinstance(default, list):
            st.session_state[key] = []
        else:
            st.session_state[key] = default
    save_state()


# ══════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════
def flag(team):       return FLAG_MAP.get(team, "")
def flag_url(team, w=20, h=15):
    c = FLAG_MAP.get(team, "")
    return f"https://flagcdn.com/{w}x{h}/{c}.png" if c else ""
def flag_img(team, width=20):
    c = FLAG_MAP.get(team, "")
    if not c: return ""
    h = int(width * 0.75)
    return f'<img src="https://flagcdn.com/{width}x{h}/{c}.png" style="vertical-align:middle;border-radius:2px;margin-right:5px;">'

def generate_group_matches(teams):
    from itertools import combinations
    return {(t1, t2): None for t1, t2 in combinations(teams, 2)}

def get_match_result(matches, t1, t2):
    return matches.get((t1, t2)) or matches.get((t2, t1))

def compute_standings(teams, matches):
    stats = {t: {"pts":0,"played":0,"w":0,"d":0,"l":0,"gf":0,"ga":0,"gd":0} for t in teams}
    for (t1, t2), res in matches.items():
        if res is None or t1 not in stats or t2 not in stats: continue
        hg, ag = res.get("hg",0), res.get("ag",0)
        stats[t1]["played"]+=1; stats[t2]["played"]+=1
        stats[t1]["gf"]+=hg; stats[t1]["ga"]+=ag
        stats[t2]["gf"]+=ag; stats[t2]["ga"]+=hg
        stats[t1]["gd"]=stats[t1]["gf"]-stats[t1]["ga"]
        stats[t2]["gd"]=stats[t2]["gf"]-stats[t2]["ga"]
        if hg>ag:   stats[t1]["pts"]+=3;stats[t1]["w"]+=1;stats[t2]["l"]+=1
        elif ag>hg: stats[t2]["pts"]+=3;stats[t2]["w"]+=1;stats[t1]["l"]+=1
        else:       stats[t1]["pts"]+=1;stats[t2]["pts"]+=1;stats[t1]["d"]+=1;stats[t2]["d"]+=1
    return [{"pos":p,"team":t,**stats[t]}
            for p,t in enumerate(sorted(teams,key=lambda t:(stats[t]["pts"],stats[t]["gd"],stats[t]["gf"]),reverse=True),1)]

def update_scorer(player_name, team, goals, prefix=""):
    if not player_name: return
    k = f"{prefix}{player_name}|{team}"
    st.session_state.top_scorers[k] = st.session_state.top_scorers.get(k,0) + goals

def update_ranking_from_standings(final_standings, base_points, decay):
    for e in final_standings:
        pts = max(base_points-(e["pos"]-1)*decay, 0)
        if pts>0:
            st.session_state.fifa_ranking[e["team"]] = st.session_state.fifa_ranking.get(e["team"],0)+pts
