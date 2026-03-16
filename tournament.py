"""
utils/tournament.py - Lógica compartida para todos los torneos FMMJ
"""
import random
import streamlit as st
from data import INITIAL_FIFA_RANKING, FLAG_MAP, TEAM_DISPLAY_NAMES, get_flag_url

# ---------------------------------------------------------------------------
# NOMBRE PARA MOSTRAR
# ---------------------------------------------------------------------------
def display_name(team):
    return TEAM_DISPLAY_NAMES.get(team, team)

def flag_img(team, w=20, h=15):
    url = get_flag_url(team, w, h)
    if url:
        return f'<img src="{url}" style="height:{h}px;vertical-align:middle;margin-right:4px;border-radius:2px;">'
    return ""

def team_badge(team, size=20):
    return f'{flag_img(team, size, int(size*0.75))}{display_name(team)}'

# ---------------------------------------------------------------------------
# SORTEO DE GRUPOS GENÉRICO
# ---------------------------------------------------------------------------
def draw_groups(teams, num_groups, seeded_teams=None, ranking=None):
    """
    Distribuye teams en num_groups grupos.
    Si seeded_teams está dado, un cabeza de serie por grupo.
    Resto aleatorio respetando confederaciones (máx 1 por grupo excepto UEFA: máx 2).
    """
    if ranking:
        teams_sorted = sorted(teams, key=lambda t: -ranking.get(t, 0))
    else:
        teams_sorted = sorted(teams, key=lambda t: -INITIAL_FIFA_RANKING.get(t, 0))

    groups = {chr(65+i): [] for i in range(num_groups)}

    if seeded_teams:
        seeds = seeded_teams[:num_groups]
    else:
        seeds = teams_sorted[:num_groups]

    for i, seed in enumerate(seeds):
        groups[chr(65+i)].append(seed)

    remaining = [t for t in teams_sorted if t not in seeds]
    random.shuffle(remaining)

    for team in remaining:
        # Buscar grupo disponible
        placed = False
        random_groups = list(groups.keys())
        random.shuffle(random_groups)
        for g in random_groups:
            current = groups[g]
            if len(current) < (len(teams) // num_groups):
                groups[g].append(team)
                placed = True
                break
        if not placed:
            for g in groups:
                groups[g].append(team)
                break

    return groups

# ---------------------------------------------------------------------------
# GENERAR CALENDARIO DE GRUPO (Round Robin)
# ---------------------------------------------------------------------------
def generate_group_fixtures(groups):
    """Genera todos los partidos de grupos {grupo: [(t1, t2), ...]}"""
    fixtures = {}
    for g, teams in groups.items():
        matches = []
        for i in range(len(teams)):
            for j in range(i+1, len(teams)):
                matches.append((teams[i], teams[j]))
        fixtures[g] = matches
    return fixtures

# ---------------------------------------------------------------------------
# TABLA DE GRUPO
# ---------------------------------------------------------------------------
def calculate_standings(group_teams, results):
    """
    results: {match_key: {"home_goals": int, "away_goals": int, "home_scorers": [], "away_scorers": []}}
    match_key: "T1 vs T2"
    Retorna lista de dicts ordenada
    """
    table = {t: {"team": t, "pj": 0, "pg": 0, "pe": 0, "pp": 0,
                 "gf": 0, "gc": 0, "dg": 0, "pts": 0} for t in group_teams}

    for key, res in results.items():
        parts = key.split(" vs ")
        if len(parts) != 2:
            continue
        home, away = parts[0], parts[1]
        if home not in table or away not in table:
            continue
        hg = res.get("home_goals", 0)
        ag = res.get("away_goals", 0)

        table[home]["pj"] += 1
        table[away]["pj"] += 1
        table[home]["gf"] += hg
        table[home]["gc"] += ag
        table[away]["gf"] += ag
        table[away]["gc"] += hg

        if hg > ag:
            table[home]["pg"] += 1
            table[home]["pts"] += 3
            table[away]["pp"] += 1
        elif hg < ag:
            table[away]["pg"] += 1
            table[away]["pts"] += 3
            table[home]["pp"] += 1
        else:
            table[home]["pe"] += 1
            table[home]["pts"] += 1
            table[away]["pe"] += 1
            table[away]["pts"] += 1

    for t in table:
        table[t]["dg"] = table[t]["gf"] - table[t]["gc"]

    standings = sorted(table.values(),
                       key=lambda x: (-x["pts"], -x["dg"], -x["gf"]))
    for i, row in enumerate(standings):
        row["pos"] = i + 1
    return standings

# ---------------------------------------------------------------------------
# MATCH KEY
# ---------------------------------------------------------------------------
def match_key(t1, t2):
    return f"{t1} vs {t2}"

# ---------------------------------------------------------------------------
# PARTIDO FORMATO DISPLAY
# ---------------------------------------------------------------------------
def format_result(home, away, hg, ag):
    return f"{display_name(home)} {hg} - {ag} {display_name(away)}"

# ---------------------------------------------------------------------------
# COLORES DE CONFEDERACIÓN
# ---------------------------------------------------------------------------
CONF_COLORS = {
    "UEFA":     "#003580",
    "CONMEBOL": "#006b3c",
    "CAF":      "#b8860b",
    "CONCACAF": "#8b0000",
    "AFC":      "#4a0080",
    "OFC":      "#006080",
    "FMMJ":     "#c8a000",
}

def conf_color(team):
    from state import get_team_confederation
    conf = get_team_confederation(team)
    return CONF_COLORS.get(conf, "#333")

# ---------------------------------------------------------------------------
# GOLEADORES
# ---------------------------------------------------------------------------
def register_scorers(scorers_list, team, state, torneo):
    """
    scorers_list: "Messi 2, Neymar 1" o lista
    """
    if not scorers_list:
        return
    if isinstance(scorers_list, str):
        entries = [s.strip() for s in scorers_list.split(",") if s.strip()]
    else:
        entries = scorers_list

    for entry in entries:
        parts = entry.rsplit(" ", 1)
        if len(parts) == 2:
            name, goals_str = parts
            try:
                goals = int(goals_str)
            except:
                goals = 1
        else:
            name = entry
            goals = 1

        key = f"{name} ({display_name(team)})"
        if "all_scorers" not in state:
            state["all_scorers"] = {}
        if key not in state["all_scorers"]:
            state["all_scorers"][key] = {"team": team, "goals": 0, "torneos": {}}
        state["all_scorers"][key]["goals"] += goals
        state["all_scorers"][key]["torneos"][torneo] = \
            state["all_scorers"][key]["torneos"].get(torneo, 0) + goals

# ---------------------------------------------------------------------------
# RENDER TABLA DE POSICIONES
# ---------------------------------------------------------------------------
def render_standings_table(standings, advancing=2, show_thirds=False):
    """Renderiza tabla HTML con colores de clasificación"""
    html = """
    <style>
    .standings-table {width:100%;border-collapse:collapse;font-size:13px;font-family:'Segoe UI',sans-serif;}
    .standings-table th {background:#1a1a2e;color:#ffd700;padding:6px 8px;text-align:center;font-weight:600;}
    .standings-table td {padding:5px 8px;text-align:center;border-bottom:1px solid #2a2a4a;}
    .standings-table tr:hover td {background:#ffffff15;}
    .pos-direct {background:#0d4f2e;}
    .pos-playoff {background:#2a4a0d;}
    .pos-out {background:#1a1a2e;}
    .team-cell {text-align:left!important;}
    </style>
    <table class='standings-table'>
    <tr>
      <th>#</th><th class='team-cell'>Selección</th>
      <th>PJ</th><th>PG</th><th>PE</th><th>PP</th>
      <th>GF</th><th>GC</th><th>DG</th><th>PTS</th>
    </tr>
    """
    for row in standings:
        pos = row["pos"]
        if pos <= advancing:
            css = "pos-direct"
        elif pos <= advancing + 2 and show_thirds:
            css = "pos-playoff"
        else:
            css = "pos-out"

        flag = flag_img(row["team"], 18, 13)
        name = display_name(row["team"])
        html += f"""
        <tr class='{css}'>
          <td><b>{pos}</b></td>
          <td class='team-cell'>{flag}{name}</td>
          <td>{row['pj']}</td><td>{row['pg']}</td><td>{row['pe']}</td><td>{row['pp']}</td>
          <td>{row['gf']}</td><td>{row['gc']}</td>
          <td>{'+' if row['dg']>0 else ''}{row['dg']}</td>
          <td><b>{row['pts']}</b></td>
        </tr>
        """
    html += "</table>"
    return html
