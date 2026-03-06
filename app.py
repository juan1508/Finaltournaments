import streamlit as st
import json
import os
from data import (
    TEAM_COMPOSITIONS, ZONE_TO_CODE, CODE_TO_DISPLAY,
    PLAYER_DATA, POS_COLORS, get_player_photo
)

st.set_page_config(
    page_title="MMJ Tournament Hub",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── PERSISTENCE ──────────────────────────────────────────────────────────────
DATA_FILE = "tournament_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

if "data" not in st.session_state:
    st.session_state.data = load_data()

# ─── TEAM LOOKUPS ─────────────────────────────────────────────────────────────
def get_display(code):
    return CODE_TO_DISPLAY.get(code, code)

def get_logo_url(code):
    return TEAM_COMPOSITIONS.get(code, {}).get("logo", "")

def get_team_players(code):
    return TEAM_COMPOSITIONS.get(code, {}).get("players", [])

def get_full_name(code):
    return TEAM_COMPOSITIONS.get(code, {}).get("name", code)

def logo_img(code, size=32):
    url = get_logo_url(code)
    if url:
        return f'<img src="{url}" width="{size}" height="{size}" style="object-fit:contain;vertical-align:middle;" onerror="this.style.display=\'none\'">'
    return ""

# ─── ZONES ────────────────────────────────────────────────────────────────────
ZONES = {
    "WEST ZONE":     {"teams": ["LAFC","LA","SJ","SDFC","POR","RSL","SEA","COL"],  "format":"groups",    "advance":2},
    "MIDWEST ZONE":  {"teams": ["MIN","SKC","STL","CHI","CIN","CLB"],              "format":"groups",    "advance":2},
    "SOUTH ZONE":    {"teams": ["DAL","ATX","HOU","NHS","CLT","ATL","ORL","MIA"],  "format":"groups",    "advance":2},
    "NORTH ZONE":    {"teams": ["DCU","PHI","NYC","RBNY","NE"],                    "format":"roundrobin","advance":2},
    "CANADIAN ZONE": {"teams": ["MTL","TOR","VAN"],                                "format":"roundrobin","advance":1},
}

ZONE_COLORS = {
    "WEST ZONE":"#E67E22","MIDWEST ZONE":"#3498DB","SOUTH ZONE":"#2ECC71",
    "NORTH ZONE":"#9B59B6","CANADIAN ZONE":"#E74C3C",
}

ALL_CODES = list(TEAM_COMPOSITIONS.keys())

# ─── TEAM COLORS (para Palmarés) ──────────────────────────────────────────────
TEAM_COLORS = {
    "NHS":  {"primary": "#1f183f",  "secondary": "#e8e51d"},
    "ATX":  {"primary": "#000000",  "secondary": "#00B140"},
    "ATL":  {"primary": "#1A1A1A",  "secondary": "#80000A"},
    "LAFC": {"primary": "#000000",  "secondary": "#C39E6D"},
    "TOR":  {"primary": "#313F49",  "secondary": "#AC152A"},
    "NYC":  {"primary": "#00285E",  "secondary": "#6CACE4"},
    "CLB":  {"primary": "#000000",  "secondary": "#FAF200"},
    "MTL":  {"primary": "#c5c8cb",  "secondary": "#003da6"},
    "PHI":  {"primary": "#071B2C",  "secondary": "#B19C6F"},
    "MIA":  {"primary": "#231F20",  "secondary": "#F7B5CD"},
    "MIN":  {"primary": "#9BCDE4",  "secondary": "#e2e2de"},
    "VAN":  {"primary": "#85B2E5",  "secondary": "#00245D"},
    "SEA":  {"primary": "#007A5E",  "secondary": "#5D9741"},
    "POR":  {"primary": "#004812",  "secondary": "#EBE5D8"},
    "LA":   {"primary": "#00245D",  "secondary": "#FFD700"},
    "SJ":   {"primary": "#0067B1",  "secondary": "#000000"},
    "RSL":  {"primary": "#B30838",  "secondary": "#013A81"},
    "COL":  {"primary": "#862633",  "secondary": "#8B9CA7"},
    "SDFC": {"primary": "#003087",  "secondary": "#B1872D"},
    "DAL":  {"primary": "#D11F2B",  "secondary": "#003087"},
    "HOU":  {"primary": "#F4911E",  "secondary": "#101820"},
    "CLT":  {"primary": "#1A85C8",  "secondary": "#C8A95A"},
    "ORL":  {"primary": "#633492",  "secondary": "#FFC222"},
    "SKC":  {"primary": "#002F6C",  "secondary": "#91B0D5"},
    "STL":  {"primary": "#16294E",  "secondary": "#CA3138"},
    "CHI":  {"primary": "#CC2529",  "secondary": "#636466"},
    "CIN":  {"primary": "#F05323",  "secondary": "#263B80"},
    "DCU":  {"primary": "#DD1128",  "secondary": "#101820"},
    "RBNY": {"primary": "#E31937",  "secondary": "#002A5C"},
    "NE":   {"primary": "#C63323",  "secondary": "#003087"},
}

def get_tc(code):
    return TEAM_COLORS.get(code, {"primary": "#F5C518", "secondary": "#1A1A24"})

def hex_to_rgb(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c*2 for c in h)
    return f"{int(h[0:2],16)}, {int(h[2:4],16)}, {int(h[4:6],16)}"

# ─── STYLES ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Barlow:wght@300;400;600;700&family=Barlow+Condensed:wght@600;700&display=swap');
:root{--gold:#F5C518;--gold2:#E8A800;--dark:#0A0A0F;--dark2:#111118;--dark3:#1A1A24;--card:#16161F;--border:#2A2A3A;--text:#E8E8F0;--muted:#8888AA;--green:#2ECC71;--red:#E74C3C;--blue:#3498DB;--purple:#9B59B6;--orange:#E67E22;}
*{font-family:'Barlow',sans-serif;}
.stApp{background:var(--dark);color:var(--text);}
[data-testid="stSidebar"]{background:var(--dark2)!important;border-right:1px solid var(--border);}
[data-testid="stSidebar"] *{color:var(--text)!important;}
.hero-title{font-family:'Bebas Neue',sans-serif;font-size:3.5rem;letter-spacing:4px;background:linear-gradient(135deg,var(--gold),var(--gold2),#fff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;text-align:center;margin:0;line-height:1;}
.hero-sub{font-family:'Barlow Condensed',sans-serif;font-size:0.85rem;letter-spacing:6px;color:var(--muted);text-align:center;text-transform:uppercase;margin-top:4px;}
.section-title{font-family:'Bebas Neue',sans-serif;font-size:2rem;letter-spacing:3px;color:var(--gold);border-bottom:2px solid var(--border);padding-bottom:8px;margin-bottom:20px;}
.match-card{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:16px;margin:8px 0;}
.stats-table{width:100%;border-collapse:collapse;font-size:0.9rem;}
.stats-table th{background:var(--dark3);color:var(--gold);font-family:'Barlow Condensed',sans-serif;font-size:0.8rem;letter-spacing:2px;padding:10px 12px;text-align:left;border-bottom:2px solid var(--border);}
.stats-table td{padding:10px 12px;border-bottom:1px solid var(--border);color:var(--text);}
.stats-table tr:hover td{background:var(--dark3);}
.info-box{background:var(--card);border-left:3px solid var(--gold);border-radius:0 6px 6px 0;padding:12px 16px;margin:8px 0;font-size:0.9rem;color:var(--muted);}
.scorer-chip{display:inline-flex;align-items:center;gap:6px;background:var(--dark3);border:1px solid var(--border);border-radius:20px;padding:4px 10px;margin:3px;font-size:0.82rem;}
.scorer-chip .min{color:var(--gold);font-weight:700;}
.pos-badge{display:inline-block;padding:2px 7px;border-radius:3px;font-size:0.65rem;font-weight:700;font-family:'Barlow Condensed',sans-serif;letter-spacing:1px;}
.stButton>button{background:var(--gold)!important;color:#000!important;font-family:'Barlow Condensed',sans-serif!important;font-weight:700!important;letter-spacing:2px!important;border:none!important;border-radius:4px!important;}
.stButton>button:hover{background:var(--gold2)!important;}
.stTextInput input,.stNumberInput input{background:var(--dark3)!important;color:var(--text)!important;border:1px solid var(--border)!important;}
.stTabs [data-baseweb="tab-list"]{background:var(--dark2)!important;border-bottom:1px solid var(--border)!important;}
.stTabs [data-baseweb="tab"]{background:transparent!important;color:var(--muted)!important;font-family:'Barlow Condensed',sans-serif!important;font-weight:600!important;letter-spacing:1px!important;border-bottom:2px solid transparent!important;}
.stTabs [aria-selected="true"]{color:var(--gold)!important;border-bottom-color:var(--gold)!important;}
div[data-testid="stExpander"]{background:var(--card);border:1px solid var(--border);border-radius:8px;}
hr{border-color:var(--border)!important;}

/* ── Palmarés Premium ── */
@keyframes floatIn {
    from { opacity:0; transform:translateY(16px); }
    to   { opacity:1; transform:translateY(0);    }
}
@keyframes shimmer-pass {
    0%   { transform: translateX(-150%) skewX(-15deg); opacity:0; }
    10%  { opacity:1; }
    90%  { opacity:1; }
    100% { transform: translateX(250%) skewX(-15deg);  opacity:0; }
}
.champ-card {
    position: relative;
    border-radius:14px;
    text-align:center; padding:20px 14px 16px;
    min-width:155px; flex:1; max-width:205px;
    animation: floatIn 0.45s ease both;
    transition: transform 0.22s ease, box-shadow 0.22s ease;
    cursor:default;
    overflow: hidden;
}
.champ-card::after {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 40%;
    height: 100%;
    background: linear-gradient(
        to right,
        rgba(255,255,255,0) 0%,
        rgba(255,255,255,0.13) 50%,
        rgba(255,255,255,0) 100%
    );
    animation: shimmer-pass 4s ease-in-out infinite;
    animation-delay: var(--shimmer-delay, 0ms);
    pointer-events: none;
    border-radius:14px;
}
.champ-card:hover {
    transform: translateY(-7px) scale(1.04);
    box-shadow: 0 12px 40px rgba(255,255,255,0.08);
}
.hof-card {
    position: relative;
    border-radius:16px;
    text-align:center; padding:22px 14px 16px;
    min-width:148px; flex:1; max-width:195px;
    transition: transform 0.22s ease;
    cursor:default;
    overflow: hidden;
}
.hof-card::after {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 40%;
    height: 100%;
    background: linear-gradient(
        to right,
        rgba(255,255,255,0) 0%,
        rgba(255,255,255,0.13) 50%,
        rgba(255,255,255,0) 100%
    );
    animation: shimmer-pass 4s ease-in-out infinite;
    pointer-events: none;
}
.hof-card:hover {
    transform: translateY(-9px) scale(1.04);
}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# CORE HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def gk(tournament, *parts):
    return f"{tournament}__{'__'.join(str(p) for p in parts)}"

def d_get(key, default=None):
    return st.session_state.data.get(key, default)

def d_set(key, value):
    st.session_state.data[key] = value
    save_data(st.session_state.data)

def get_match_winner(match_key, t1, t2):
    r = d_get(match_key, {})
    if not r.get("played"):
        return "TBD"
    return t1 if r.get("g1", 0) >= r.get("g2", 0) else t2


def render_scorers(match_key, t1, t2):
    scorers = d_get(match_key + "__scorers", [])
    st.markdown("**⚽ Registrar Goleador**")

    t1_players = get_team_players(t1)
    t2_players = get_team_players(t2)
    all_players = [""] + t1_players + t2_players

    cols = st.columns([2, 1, 1, 0.6])
    with cols[0]:
        player = st.selectbox("Jugador", all_players, key=match_key + "_sp")
    with cols[1]:
        auto_team = t1 if player in t1_players else (t2 if player in t2_players else t1)
        team_opts = [t1, t2]
        team = st.selectbox("Equipo", team_opts, index=team_opts.index(auto_team), key=match_key + "_st")
    with cols[2]:
        minute = st.number_input("Min", 1, 120, 45, key=match_key + "_sm")
    with cols[3]:
        st.write(""); st.write("")
        if st.button("➕", key=match_key + "_sb"):
            if player:
                scorers.append({"player": player, "team": team, "minute": minute})
                d_set(match_key + "__scorers", scorers)
                st.rerun()

    if scorers:
        html = ""
        for s in scorers:
            pdata = PLAYER_DATA.get(s["player"], {})
            photo = get_player_photo(s["player"], pdata.get("sofifa", 0))
            html += f'<span class="scorer-chip"><img src="{photo}" width="26" height="26" style="border-radius:50%;object-fit:cover;" onerror="this.style.display=\'none\'"> <b>{s["player"]}</b> {logo_img(s["team"],14)} <span class="min">{s["minute"]}\'</span></span>'
        st.markdown(html, unsafe_allow_html=True)

        del_idx = st.selectbox("Eliminar", range(len(scorers)),
                               format_func=lambda i: f"{scorers[i]['player']} {scorers[i]['minute']}'",
                               key=match_key + "_del")
        if st.button("🗑️ Eliminar gol", key=match_key + "_delb"):
            scorers.pop(del_idx)
            d_set(match_key + "__scorers", scorers)
            st.rerun()


def render_match(t1, t2, match_key, label=""):
    result = d_get(match_key, {})
    st.markdown(f"""
    <div class="match-card">
        <div style="font-family:'Barlow Condensed';font-size:0.72rem;letter-spacing:2px;color:var(--muted);margin-bottom:12px">{label}</div>
        <div style="display:flex;align-items:center;justify-content:center;gap:16px">
            <div style="flex:1;text-align:right;display:flex;align-items:center;justify-content:flex-end;gap:10px">
                <span style="font-weight:700;font-size:1rem">{t1}</span>{logo_img(t1,40)}
            </div>
            <span style="font-family:'Bebas Neue';font-size:1.5rem;color:var(--gold);min-width:30px;text-align:center">VS</span>
            <div style="flex:1;text-align:left;display:flex;align-items:center;justify-content:flex-start;gap:10px">
                {logo_img(t2,40)}<span style="font-weight:700;font-size:1rem">{t2}</span>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        g1 = st.number_input(f"⚽ {t1}", 0, 20, result.get("g1", 0), key=match_key + "_g1")
    with c2:
        g2 = st.number_input(f"⚽ {t2}", 0, 20, result.get("g2", 0), key=match_key + "_g2")

    cs, cr = st.columns([1, 1])
    with cs:
        if st.button("💾 Guardar resultado", key=match_key + "_save"):
            d_set(match_key, {"g1": g1, "g2": g2, "played": True, "t1": t1, "t2": t2})
            st.rerun()
    with cr:
        if result.get("played"):
            st.success(f"✅ {t1} {result.get('g1',0)}–{result.get('g2',0)} {t2}")

    render_scorers(match_key, t1, t2)


def compute_standings(teams, prefix):
    table = {t: {"PJ":0,"G":0,"E":0,"P":0,"GF":0,"GC":0,"DG":0,"PTS":0} for t in teams}
    for key, result in st.session_state.data.items():
        if not key.startswith(prefix) or not isinstance(result, dict) or not result.get("played"):
            continue
        t1, t2 = result.get("t1"), result.get("t2")
        if not t1 or not t2 or t1 not in table or t2 not in table:
            continue
        g1, g2 = result["g1"], result["g2"]
        table[t1]["PJ"] += 1; table[t2]["PJ"] += 1
        table[t1]["GF"] += g1; table[t1]["GC"] += g2
        table[t2]["GF"] += g2; table[t2]["GC"] += g1
        table[t1]["DG"] = table[t1]["GF"] - table[t1]["GC"]
        table[t2]["DG"] = table[t2]["GF"] - table[t2]["GC"]
        if g1 > g2:   table[t1]["G"]+=1; table[t1]["PTS"]+=3; table[t2]["P"]+=1
        elif g2 > g1: table[t2]["G"]+=1; table[t2]["PTS"]+=3; table[t1]["P"]+=1
        else:
            table[t1]["E"]+=1; table[t1]["PTS"]+=1
            table[t2]["E"]+=1; table[t2]["PTS"]+=1
    return sorted(table.keys(), key=lambda t: (-table[t]["PTS"],-table[t]["DG"],-table[t]["GF"])), table


def render_standings(teams_sorted, table, highlight=2):
    html = '<table class="stats-table"><thead><tr>'
    for col in ["#","EQUIPO","PJ","G","E","P","GF","GC","DG","PTS"]:
        html += f"<th>{col}</th>"
    html += "</tr></thead><tbody>"
    rcolors = ["var(--gold)","var(--blue)","var(--green)"]
    for i, team in enumerate(teams_sorted):
        s = table[team]
        rc = rcolors[min(i,2)] if i < highlight else "var(--muted)"
        tick = "✓ " if i < highlight else ""
        dg = f"+{s['DG']}" if s["DG"]>0 else str(s["DG"])
        dgc = "var(--green)" if s["DG"]>=0 else "var(--red)"
        html += f"""<tr>
            <td style="color:{rc};font-weight:700">{i+1}</td>
            <td style="font-weight:600">{logo_img(team,22)}&nbsp;{tick}<span style="font-family:'Barlow Condensed';letter-spacing:1px">{team}</span> <span style="font-size:0.78rem;color:var(--muted);font-weight:400">{get_full_name(team)}</span></td>
            <td>{s['PJ']}</td><td>{s['G']}</td><td>{s['E']}</td><td>{s['P']}</td>
            <td>{s['GF']}</td><td>{s['GC']}</td>
            <td style="color:{dgc}">{dg}</td>
            <td style="color:var(--gold);font-weight:700">{s['PTS']}</td>
        </tr>"""
    html += "</tbody></table>"
    st.markdown(html, unsafe_allow_html=True)


def get_all_scorers(tournament):
    agg = {}
    for key, val in st.session_state.data.items():
        if key.startswith(tournament) and key.endswith("__scorers"):
            for s in val:
                k = f"{s['player']}|{s['team']}"
                if k not in agg:
                    agg[k] = {"player":s["player"],"team":s["team"],"goals":0,"minutes":[]}
                agg[k]["goals"] += 1
                agg[k]["minutes"].append(s["minute"])
    return sorted(agg.values(), key=lambda x: -x["goals"])


def render_scorers_table(scorers):
    if not scorers:
        st.info("No hay goleadores registrados aún.")
        return
    html = '<table class="stats-table"><thead><tr><th>#</th><th>FOTO</th><th>JUGADOR</th><th>EQUIPO</th><th>GOLES</th><th>MINUTOS</th></tr></thead><tbody>'
    for i, s in enumerate(scorers):
        pdata = PLAYER_DATA.get(s["player"], {})
        photo = get_player_photo(s["player"], pdata.get("sofifa", 0))
        pos = pdata.get("pos", "")
        poc = POS_COLORS.get(pos, "#888")
        medal = "🥇" if i==0 else ("🥈" if i==1 else ("🥉" if i==2 else str(i+1)))
        mins = ", ".join(str(m)+"'" for m in sorted(s["minutes"]))
        html += f"""<tr>
            <td>{medal}</td>
            <td><img src="{photo}" width="38" height="38" style="border-radius:50%;object-fit:cover;" onerror="this.style.display=\'none\'"></td>
            <td style="font-weight:600">{s['player']}<br><span class="pos-badge" style="background:{poc}22;color:{poc};border:1px solid {poc}44">{pos}</span></td>
            <td>{logo_img(s['team'],22)}&nbsp;{s['team']}</td>
            <td style="color:var(--gold);font-weight:700;font-size:1.2rem">{s['goals']}</td>
            <td style="color:var(--muted);font-size:0.85rem">{mins}</td>
        </tr>"""
    html += "</tbody></table>"
    st.markdown(html, unsafe_allow_html=True)


def big_match_card(t1, t2, subtitle=""):
    return f"""
    <div style="background:linear-gradient(135deg,var(--card),var(--dark3));border:1px solid var(--border);border-radius:12px;padding:28px;text-align:center;margin:12px 0">
        <div style="font-family:'Barlow Condensed';font-size:0.8rem;letter-spacing:4px;color:var(--muted);margin-bottom:16px">{subtitle}</div>
        <div style="display:flex;align-items:center;justify-content:center;gap:40px">
            <div style="text-align:center">
                <div style="margin-bottom:8px">{logo_img(t1,60)}</div>
                <div style="font-family:'Bebas Neue';font-size:1.6rem;letter-spacing:2px">{t1}</div>
                <div style="font-size:0.72rem;color:var(--muted)">{get_full_name(t1)}</div>
            </div>
            <div style="font-family:'Bebas Neue';font-size:1.5rem;color:var(--gold)">VS</div>
            <div style="text-align:center">
                <div style="margin-bottom:8px">{logo_img(t2,60)}</div>
                <div style="font-family:'Bebas Neue';font-size:1.6rem;letter-spacing:2px">{t2}</div>
                <div style="font-size:0.72rem;color:var(--muted)">{get_full_name(t2)}</div>
            </div>
        </div>
    </div>"""


def champion_card(champ, tournament_name):
    return f"""
    <div style="background:linear-gradient(135deg,rgba(245,197,24,0.18),rgba(245,197,24,0.04));border:2px solid var(--gold);border-radius:12px;padding:30px;text-align:center;margin-top:20px">
        <div style="font-size:3rem">🏆</div>
        <div style="font-family:'Bebas Neue';font-size:1rem;letter-spacing:4px;color:var(--muted)">{tournament_name} CHAMPION</div>
        <div style="margin:14px 0">{logo_img(champ,80)}</div>
        <div style="font-family:'Bebas Neue';font-size:3rem;color:var(--gold);letter-spacing:4px">{champ}</div>
        <div style="font-size:0.9rem;color:var(--muted);margin-top:4px">{get_full_name(champ)}</div>
    </div>"""


# ─── PALMARES HELPERS ─────────────────────────────────────────────────────────
def title_color_palmares(title):
    # Lista ordenada: más específicas primero (Midwest antes que West)
    TITLE_COLORS = [
        ("Canadian Zone",    "#E74C3C"),
        ("Midwest Zone",     "#2ECC71"),
        ("North Zone",       "#9B59B6"),
        ("South Zone",       "#3498DB"),
        ("West Zone",        "#E67E22"),
        ("Streamlit League", "#b040f0"),
        ("Emirates Cup",     "#CE3035"),
        ("Cisco Super Cup",  "#eb7c1e"),
        ("Papa Johns",       "#233dff"),
        ("McDonald",         "#fa0d04"),
    ]
    t = title.lower()
    for k, v in TITLE_COLORS:
        if k.lower() in t:
            return v
    return "#888888"
def title_icon_palmares(title):
    t = title.lower()
    if "streamlit league" in t: return "⚽"
    if "emirates" in t:         return "✈️"
    if "cisco" in t:            return "🥤"
    if "papa johns" in t:       return "🏟️"
    if "mcdonald" in t:         return "🍔"
    if "west zone" in t:        return "🌅"
    if "midwest zone" in t:     return "🌾"
    if "south zone" in t:       return "🌶️"
    if "north zone" in t:       return "🗽"
    if "canadian zone" in t:    return "🍁"
    return "🏆"

def make_champ_card(code, title, delay_ms=0):
    pending = (code == "??")
    tc = get_tc(code) if not pending else {"primary": "#2A2A3A", "secondary": "#1A1A24"}
    primary   = tc["primary"]
    secondary = tc["secondary"]
    rgb_p     = hex_to_rgb(primary)
    t_color   = title_color_palmares(title)
    icon      = title_icon_palmares(title)
    title_short = title.replace("Campeón ", "").upper()

    logo_url  = get_logo_url(code) if not pending else ""
    logo_html = (
        f'<img src="{logo_url}" width="50" height="50" style="object-fit:contain;display:block;margin:0 auto;">'
        if logo_url else '<div style="font-size:1.8rem;text-align:center;">❓</div>'
    )
    name_display = get_full_name(code) if not pending else "Por definir"
    code_display = code if not pending else "???"
    text_color   = "#FFFFFF" if not pending else "#555566"
    name_color   = "rgba(255,255,255,0.72)" if not pending else "#444455"
    opacity      = "1" if not pending else "0.5"

    gradient = (
        f"linear-gradient(145deg, {secondary}EE 0%, {primary}FF 52%, {secondary}CC 100%)"
        if not pending else
        "linear-gradient(145deg, #1A1A2A, #22222F)"
    )
    border_color = f"{primary}AA" if not pending else "#2A2A3A"
    shadow = f"0 6px 28px rgba({rgb_p}, 0.38), 0 2px 8px rgba(0,0,0,0.55)" if not pending else "0 2px 10px rgba(0,0,0,0.4)"

    return f"""<div class="champ-card" style="
        background:{gradient};
        border-top:3px solid {t_color};
        border-left:1.5px solid {border_color};
        border-right:1.5px solid {border_color};
        border-bottom:1.5px solid {border_color};
        box-shadow:{shadow};
        opacity:{opacity};
        --shimmer-delay:{delay_ms}ms;
    ">
        <div style="font-family:'Barlow Condensed',sans-serif;font-size:0.58rem;letter-spacing:2.5px;text-transform:uppercase;margin-bottom:10px;font-weight:700;color:{t_color};">{icon} {title_short}</div>
        <div style="margin-bottom:8px;">{logo_html}</div>
        <div style="font-family:'Bebas Neue',sans-serif;font-size:1.55rem;letter-spacing:3px;line-height:1;margin:5px 0 2px;color:{text_color};">{code_display}</div>
        <div style="font-size:0.63rem;color:{name_color};letter-spacing:0.4px;">{name_display}</div>
    </div>"""

def make_hof_card(rank, code, count, medal_colors):
    mc = medal_colors[min(rank, len(medal_colors)-1)]
    tc = get_tc(code)
    primary   = tc["primary"]
    secondary = tc["secondary"]
    rgb_p     = hex_to_rgb(primary)
    logo_url  = get_logo_url(code)
    logo_html = f'<img src="{logo_url}" width="58" height="58" style="object-fit:contain;display:block;margin:0 auto;">' if logo_url else ""
    gradient  = f"linear-gradient(155deg, {secondary}DD 0%, {primary}FF 55%, {secondary}AA 100%)"

    return f"""<div class="hof-card" style="
        background:{gradient};
        border-top:4px solid {mc};
        border-left:2px solid {mc}55;
        border-right:2px solid {mc}55;
        border-bottom:2px solid {mc}55;
        box-shadow:0 8px 30px rgba({rgb_p},0.42);
    ">
        <div style="font-family:'Barlow Condensed',sans-serif;font-size:0.65rem;letter-spacing:2px;color:{mc};margin-bottom:4px;font-weight:700;">#{rank+1}</div>
        <div style="margin-bottom:8px;">{logo_html}</div>
        <div style="font-family:'Bebas Neue',sans-serif;font-size:1.45rem;color:#FFF;letter-spacing:3px;">{code}</div>
        <div style="font-size:0.68rem;color:rgba(255,255,255,0.62);margin-bottom:10px;">{get_full_name(code)}</div>
        <div style="font-family:'Bebas Neue',sans-serif;font-size:3.2rem;line-height:1;color:{mc};">{count}</div>
        <div style="font-family:'Barlow Condensed',sans-serif;font-size:0.67rem;letter-spacing:2px;color:rgba(255,255,255,0.45);">TÍTULOS</div>
    </div>"""


# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:20px 0 10px">
        <div style="font-family:'Bebas Neue';font-size:2.2rem;color:var(--gold);letter-spacing:3px">MMJ</div>
        <div style="font-family:'Barlow Condensed';font-size:0.7rem;letter-spacing:4px;color:var(--muted)">TOURNAMENT HUB</div>
    </div><hr>""", unsafe_allow_html=True)

    page = st.selectbox("📋 Navegación", [
        "🏅 Palmarés MMJ",
        "🏟️ Papa Johns Leagues Cup",
        "🥤 Cisco Super Cup",
        "🍔 McDonald's Community Cup"
    ])

    tournament = page

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.75rem;color:var(--muted);text-align:center">MMJ Soccer League<br><span style="color:var(--gold)">Season 2025</span></div>', unsafe_allow_html=True)


# ─── HEADER ───────────────────────────────────────────────────────────────────
TINFO = {
    "🏅 Palmarés MMJ":              ("MMJ","PALMARÉS",          "HISTORIAL COMPLETO DE CAMPEONES"),
    "🏟️ Papa Johns Leagues Cup":   ("MMJ PAPA JOHNS","LEAGUES CUP",   "30 TEAMS · 5 ZONES · PHASE FINAL"),
    "🥤 Cisco Super Cup":          ("MMJ CISCO","SUPER CUP",           "STREAMLIT LEAGUE CHAMP VS EMIRATES CUP CHAMP"),
    "🍔 McDonald's Community Cup": ("MMJ McDONALD'S","COMMUNITY CUP", "4 TEAMS · 2 SEMIFINALES · GRAN FINAL"),
}
info = TINFO[tournament]
st.markdown(f"""
<div style="padding:30px 0 20px;border-bottom:1px solid var(--border);margin-bottom:30px">
    <div class="hero-sub" style="margin-bottom:4px">{info[2]}</div>
    <div class="hero-title">{info[0]}<br>{info[1]}</div>
</div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PALMARÉS MMJ
# ═══════════════════════════════════════════════════════════════════════════════
if tournament == "🏅 Palmarés MMJ":

    PALMARES = {
        "SEASON Ⅰ": [
            ("NHS",  "Campeón MMJ Streamlit League I"),
            ("ATX",  "Campeón MMJ Emirates Cup I"),
            ("ATX",  "Campeón MMJ Cisco Super Cup I"),
        ],
        "SEASON Ⅱ": [
            ("LAFC", "Campeón MMJ Streamlit League II"),
            ("NHS",  "Campeón MMJ Emirates Cup II"),
            ("LAFC", "Campeón MMJ Cisco Super Cup II"),
        ],
        "SEASON Ⅲ": [
            ("TOR",  "Campeón Canadian Zone I"),
            ("NYC",  "Campeón North Zone I"),
            ("NHS",  "Campeón South Zone I"),
            ("CLB",  "Campeón Midwest Zone I"),
            ("LAFC", "Campeón West Zone I"),
            ("LAFC", "Campeón MMJ Streamlit League III"),
            ("ATL",  "Campeón MMJ Emirates Cup III"),
            ("ATL",  "Campeón MMJ Cisco Super Cup III"),
        ],
        "SEASON Ⅳ": [
            ("MTL",  "Campeón Canadian Zone II"),
            ("PHI",  "Campeón North Zone II"),
            ("MIA",  "Campeón South Zone II"),
            ("MIN",  "Campeón Midwest Zone II"),
            ("LAFC", "Campeón West Zone II"),
            ("LAFC", "Campeón MMJ Streamlit League IV"),
            ("LAFC", "Campeón MMJ Emirates Cup IV"),
            ("NHS",  "Campeón MMJ Cisco Super Cup IV"),
        ],
        "SEASON Ⅴ": [
            ("VAN",  "Campeón Canadian Zone III"),
            ("PHI",  "Campeón North Zone III"),
            ("??",   "Campeón South Zone III"),
            ("??",   "Campeón Midwest Zone III"),
            ("??",   "Campeón West Zone III"),
            ("??",   "Campeón MMJ Streamlit League V"),
            ("??",   "Campeón MMJ Emirates Cup V"),
            ("??",   "Campeón MMJ Cisco Super Cup V"),
        ],
        "SEASON Ⅵ": [
            ("??",   "Campeón Canadian Zone IV"),
            ("??",   "Campeón North Zone IV"),
            ("??",   "Campeón South Zone IV"),
            ("??",   "Campeón Midwest Zone IV"),
            ("??",   "Campeón West Zone IV"),
            ("??",   "Campeón MMJ Papa Johns Leagues Cup I"),
            ("??",   "Campeón MMJ Emirates Cup VI"),
            ("??",   "Campeón MMJ Streamlit League VI"),
            ("??",   "Campeón MMJ Cisco Super Cup VI"),
            ("??",   "Campeón MMJ McDonald's Community Cup I"),
        ],
    }

    # Conteo de títulos
    title_count = {}
    for season_entries in PALMARES.values():
        for code, title in season_entries:
            if code != "??":
                title_count[code] = title_count.get(code, 0) + 1

    top_teams    = sorted(title_count.items(), key=lambda x: -x[1])
    medal_colors = ["#F5C518", "#C0C0C0", "#CD7F32", "#9B59B6", "#3498DB"]

    # ── Hall of Fame ──────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">🏆 HALL OF FAME</div>', unsafe_allow_html=True)
    st.markdown("<div class='info-box'>Equipos con más títulos en la historia de la MMJ Federation</div>", unsafe_allow_html=True)

    hof_html = '<div style="display:flex;flex-wrap:wrap;gap:16px;margin-bottom:36px">'
    for rank, (code, count) in enumerate(top_teams):
        hof_html += make_hof_card(rank, code, count, medal_colors)
    hof_html += '</div>'
    st.markdown(hof_html, unsafe_allow_html=True)

    st.markdown("---")

    # ── Palmarés por temporada ────────────────────────────────────────────────
    st.markdown('<div class="section-title">📋 PALMARÉS POR TEMPORADA</div>', unsafe_allow_html=True)

    for season_name, entries in PALMARES.items():
        is_current = season_name == "SEASON Ⅴ"
        is_future  = season_name == "SEASON Ⅵ"
        alpha      = "0.45" if is_future else "1"
        header_color = "var(--gold)" if is_current else ("var(--muted)" if is_future else "var(--text)")

        badge_html = ""
        if is_current:
            badge_html = '<span style="background:var(--gold);color:#000;font-family:\'Barlow Condensed\',sans-serif;font-size:0.7rem;letter-spacing:2px;padding:3px 12px;border-radius:20px;font-weight:700">EN CURSO</span>'
        elif is_future:
            badge_html = '<span style="background:var(--dark3);color:var(--muted);font-family:\'Barlow Condensed\',sans-serif;font-size:0.7rem;letter-spacing:2px;padding:3px 12px;border-radius:20px;border:1px solid var(--border)">PRÓXIMA</span>'

        st.markdown(f'<div style="font-family:\'Bebas Neue\';font-size:2.2rem;color:{header_color};letter-spacing:3px;margin-bottom:14px;">{season_name} {badge_html}</div>', unsafe_allow_html=True)

        cards_html = f'<div style="display:flex;flex-wrap:wrap;gap:12px;margin-bottom:30px;opacity:{alpha};">'
        for delay_i, (code, title) in enumerate(entries):
            cards_html += make_champ_card(code, title, delay_ms=delay_i * 75)
        cards_html += '</div>'
        st.markdown(cards_html, unsafe_allow_html=True)

    # ── Estadísticas globales ─────────────────────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-title">📊 ESTADÍSTICAS HISTÓRICAS</div>', unsafe_allow_html=True)

    total_titles  = sum(1 for s in PALMARES.values() for code, _ in s if code != "??")
    total_seasons = len(PALMARES)
    unique_champs = len(set(code for s in PALMARES.values() for code, _ in s if code != "??"))

    sc1, sc2, sc3 = st.columns(3)
    for col, val, lbl, icon in [
        (sc1, total_titles,  "Títulos entregados", "🏆"),
        (sc2, total_seasons, "Temporadas",          "📅"),
        (sc3, unique_champs, "Campeones distintos", "⚽"),
    ]:
        with col:
            col.markdown(f"""
            <div style="background:var(--card);border:1px solid var(--border);border-radius:10px;padding:20px;text-align:center">
                <div style="font-size:2rem">{icon}</div>
                <div style="font-family:'Bebas Neue';font-size:2.8rem;color:var(--gold)">{val}</div>
                <div style="font-size:0.8rem;color:var(--muted);letter-spacing:1px">{lbl.upper()}</div>
            </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAPA JOHNS LEAGUES CUP
# ═══════════════════════════════════════════════════════════════════════════════
elif tournament == "🏟️ Papa Johns Leagues Cup":
    T = "pjlc"
    tabs = st.tabs(["🌍 PHASE ZONE", "🏆 PHASE FINAL", "📊 ESTADÍSTICAS"])

    with tabs[0]:
        zone_tabs = st.tabs(list(ZONES.keys()))
        for z_idx, (zone_name, zone_data) in enumerate(ZONES.items()):
            with zone_tabs[z_idx]:
                color = ZONE_COLORS[zone_name]
                teams = zone_data["teams"]
                fmt   = zone_data["format"]

                logos_html = "".join(logo_img(t,28) for t in teams)
                st.markdown(f"""
                <div style="background:var(--card);border-left:4px solid {color};padding:14px 18px;border-radius:0 8px 8px 0;margin-bottom:20px">
                    <div style="font-family:'Bebas Neue';font-size:1.8rem;color:{color};letter-spacing:2px">{zone_name}</div>
                    <div style="font-size:0.8rem;color:var(--muted);margin-bottom:10px">{len(teams)} equipos · {"2 grupos" if fmt=="groups" else "Round Robin"}</div>
                    <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center">{logos_html}</div>
                </div>""", unsafe_allow_html=True)

                if fmt == "groups":
                    half   = len(teams) // 2
                    groups = [teams[:half], teams[half:]]
                    gcols  = st.columns(2)

                    for g_idx, grp in enumerate(groups):
                        with gcols[g_idx]:
                            lbl = "A" if g_idx == 0 else "B"
                            st.markdown(f"### GRUPO {lbl}")
                            pfx = gk(T, zone_name, f"G{g_idx}")
                            ts, tbl = compute_standings(grp, pfx)
                            render_standings(ts, tbl, highlight=1)
                            with st.expander(f"📋 Partidos Grupo {lbl}"):
                                for i, t1 in enumerate(grp):
                                    for j, t2 in enumerate(grp):
                                        if i < j:
                                            mk = gk(T, zone_name, f"G{g_idx}", t1, t2)
                                            render_match(t1, t2, mk, f"Grupo {lbl} · {zone_name}")
                                            st.markdown("---")

                    st.markdown("---")
                    st.markdown(f"### 🏅 ZONA FINAL — {zone_name}")
                    st.markdown("<div class='info-box'>1° Grupo A vs 1° Grupo B → automático según resultados</div>", unsafe_allow_html=True)

                    sa, _ = compute_standings(groups[0], gk(T, zone_name, "G0"))
                    sb, _ = compute_standings(groups[1], gk(T, zone_name, "G1"))
                    za = sa[0] if sa else groups[0][0]
                    zb = sb[0] if sb else groups[1][0]

                    zf_key = gk(T, zone_name, "ZF")
                    st.markdown(big_match_card(za, zb, f"ZONA FINAL · {zone_name}"), unsafe_allow_html=True)
                    render_match(za, zb, zf_key, f"Zona Final · {zone_name}")
                    zf_r = d_get(zf_key, {})
                    if zf_r.get("played"):
                        zc = za if zf_r.get("g1",0) >= zf_r.get("g2",0) else zb
                        zs = zb if zc == za else za
                        d_set(gk(T, zone_name, "champion"), zc)
                        d_set(gk(T, zone_name, "runner_up"), zs)
                        st.success(f"🥇 Campeón: **{zc}** | 🥈 Sub-Campeón: **{zs}**")

                else:  # roundrobin
                    pfx = gk(T, zone_name, "RR")
                    ts, tbl = compute_standings(teams, pfx)
                    render_standings(ts, tbl, highlight=2)

                    with st.expander("📋 Todos los partidos"):
                        for i, t1 in enumerate(teams):
                            for j, t2 in enumerate(teams):
                                if i < j:
                                    mk = gk(T, zone_name, "RR", t1, t2)
                                    render_match(t1, t2, mk, f"{zone_name} · Round Robin")
                                    st.markdown("---")

                    st.markdown("---")
                    st.markdown(f"### 🏅 ZONA FINAL — {zone_name}")
                    st.markdown("<div class='info-box'>1° vs 2° del Round Robin → automático según resultados</div>", unsafe_allow_html=True)

                    f1 = ts[0] if len(ts) > 0 else teams[0]
                    f2 = ts[1] if len(ts) > 1 else teams[1]

                    zf_key = gk(T, zone_name, "ZF")
                    st.markdown(big_match_card(f1, f2, f"ZONA FINAL · {zone_name}"), unsafe_allow_html=True)
                    render_match(f1, f2, zf_key, f"Zona Final · {zone_name}")
                    zf_r = d_get(zf_key, {})
                    if zf_r.get("played"):
                        zc = f1 if zf_r.get("g1",0) >= zf_r.get("g2",0) else f2
                        zs = f2 if zc == f1 else f1
                        d_set(gk(T, zone_name, "champion"), zc)
                        d_set(gk(T, zone_name, "runner_up"), zs)
                        label_txt = f"🥇 Campeón CZ: **{zc}** → Avanza a Phase Final | 🥈 Sub-Campeón: **{zs}**" if zone_name=="CANADIAN ZONE" else f"🥇 Campeón: **{zc}** | 🥈 Sub-Campeón: **{zs}**"
                        st.success(label_txt)

    with tabs[1]:
        st.markdown('<div class="section-title">🏆 PHASE FINAL</div>', unsafe_allow_html=True)

        WZ_C = d_get(gk(T,"WEST ZONE","champion"),    "TBD")
        WZ_S = d_get(gk(T,"WEST ZONE","runner_up"),   "TBD")
        MZ_C = d_get(gk(T,"MIDWEST ZONE","champion"), "TBD")
        MZ_S = d_get(gk(T,"MIDWEST ZONE","runner_up"),"TBD")
        SZ_C = d_get(gk(T,"SOUTH ZONE","champion"),   "TBD")
        SZ_S = d_get(gk(T,"SOUTH ZONE","runner_up"),  "TBD")
        NZ_C = d_get(gk(T,"NORTH ZONE","champion"),   "TBD")
        CZ_C = d_get(gk(T,"CANADIAN ZONE","champion"),"TBD")

        st.markdown("#### Clasificados por Zona")
        zone_cols = st.columns(5)
        zone_info = [
            ("WEST",     "#E67E22", WZ_C, WZ_S),
            ("MIDWEST",  "#3498DB", MZ_C, MZ_S),
            ("SOUTH",    "#2ECC71", SZ_C, SZ_S),
            ("NORTH",    "#9B59B6", NZ_C, None),
            ("CANADIAN", "#E74C3C", CZ_C, None),
        ]
        for col, (zshort, zcolor, champ, sub) in zip(zone_cols, zone_info):
            with col:
                champ_logo = logo_img(champ, 36) if champ != "TBD" else "❓"
                sub_line = f"<div style='margin-top:6px'>{logo_img(sub,24)} <span style='font-size:0.82rem;color:var(--muted)'>🥈 {sub}</span></div>" if sub else ""
                st.markdown(f"""
                <div style="background:var(--card);border-top:3px solid {zcolor};border-radius:0 0 8px 8px;padding:12px;text-align:center">
                    <div style="font-family:'Barlow Condensed';font-size:0.7rem;letter-spacing:2px;color:{zcolor};margin-bottom:8px">{zshort}</div>
                    <div>{champ_logo}</div>
                    <div style="font-weight:700;font-size:0.9rem;margin-top:4px">🥇 {champ}</div>
                    {sub_line}
                </div>""", unsafe_allow_html=True)

        st.markdown("---")

        st.markdown(f"""
        <div style="background:var(--card);border:1px solid var(--border);border-radius:10px;padding:20px;margin-bottom:20px">
            <div style="font-family:'Bebas Neue';font-size:1.3rem;letter-spacing:3px;color:var(--gold);margin-bottom:14px">BRACKET</div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px">
                <div>
                    <div style="font-family:'Barlow Condensed';font-size:0.75rem;letter-spacing:2px;color:var(--muted);margin-bottom:10px">LLAVE F1</div>
                    <div style="display:flex;align-items:center;gap:6px;margin:8px 0"><b style="color:var(--gold);min-width:24px">A1</b>{logo_img(WZ_C,20)}{WZ_C}<span style="color:var(--muted);margin:0 6px">vs</span>{logo_img(SZ_S,20)}{SZ_S}</div>
                    <div style="display:flex;align-items:center;gap:6px;margin:8px 0"><b style="color:var(--gold);min-width:24px">B1</b>{logo_img(NZ_C,20)}{NZ_C}<span style="color:var(--muted);margin:0 6px">vs</span>{logo_img(MZ_C,20)}{MZ_C}</div>
                </div>
                <div>
                    <div style="font-family:'Barlow Condensed';font-size:0.75rem;letter-spacing:2px;color:var(--muted);margin-bottom:10px">LLAVE F2</div>
                    <div style="display:flex;align-items:center;gap:6px;margin:8px 0"><b style="color:var(--gold);min-width:24px">C1</b>{logo_img(CZ_C,20)}{CZ_C}<span style="color:var(--muted);margin:0 6px">vs</span>{logo_img(WZ_S,20)}{WZ_S}</div>
                    <div style="display:flex;align-items:center;gap:6px;margin:8px 0"><b style="color:var(--gold);min-width:24px">D1</b>{logo_img(SZ_C,20)}{SZ_C}<span style="color:var(--muted);margin:0 6px">vs</span>{logo_img(MZ_S,20)}{MZ_S}</div>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

        st.markdown('<div class="section-title" style="font-size:1.4rem">CUARTOS DE FINAL</div>', unsafe_allow_html=True)
        q1, q2 = st.columns(2)

        with q1:
            st.markdown("**F1 · A1 — WZ Campeón vs SZ Sub-Cam.**")
            mk_a1 = gk(T,"PF","A1")
            st.markdown(big_match_card(WZ_C, SZ_S, "F1 · A1"), unsafe_allow_html=True)
            render_match(WZ_C, SZ_S, mk_a1, "Cuartos F1·A1")
            st.markdown("---")
            st.markdown("**F2 · C1 — CZ Campeón vs WZ Sub-Cam.**")
            mk_c1 = gk(T,"PF","C1")
            st.markdown(big_match_card(CZ_C, WZ_S, "F2 · C1"), unsafe_allow_html=True)
            render_match(CZ_C, WZ_S, mk_c1, "Cuartos F2·C1")

        with q2:
            st.markdown("**F1 · B1 — NZ Campeón vs MZ Campeón**")
            mk_b1 = gk(T,"PF","B1")
            st.markdown(big_match_card(NZ_C, MZ_C, "F1 · B1"), unsafe_allow_html=True)
            render_match(NZ_C, MZ_C, mk_b1, "Cuartos F1·B1")
            st.markdown("---")
            st.markdown("**F2 · D1 — SZ Campeón vs MZ Sub-Cam.**")
            mk_d1 = gk(T,"PF","D1")
            st.markdown(big_match_card(SZ_C, MZ_S, "F2 · D1"), unsafe_allow_html=True)
            render_match(SZ_C, MZ_S, mk_d1, "Cuartos F2·D1")

        a1_w = get_match_winner(mk_a1, WZ_C, SZ_S)
        b1_w = get_match_winner(mk_b1, NZ_C, MZ_C)
        c1_w = get_match_winner(mk_c1, CZ_C, WZ_S)
        d1_w = get_match_winner(mk_d1, SZ_C, MZ_S)

        st.markdown("---")
        st.markdown('<div class="section-title" style="font-size:1.4rem">SEMIFINALES</div>', unsafe_allow_html=True)
        sf1c, sf2c = st.columns(2)

        with sf1c:
            st.markdown("**SEMIFINAL F1 · A1 vs B1**")
            mk_sf1 = gk(T,"PF","SF1")
            st.markdown(big_match_card(a1_w, b1_w, "Semifinal F1"), unsafe_allow_html=True)
            render_match(a1_w, b1_w, mk_sf1, "Semifinal F1")

        with sf2c:
            st.markdown("**SEMIFINAL F2 · C1 vs D1**")
            mk_sf2 = gk(T,"PF","SF2")
            st.markdown(big_match_card(c1_w, d1_w, "Semifinal F2"), unsafe_allow_html=True)
            render_match(c1_w, d1_w, mk_sf2, "Semifinal F2")

        sf1_w = get_match_winner(mk_sf1, a1_w, b1_w)
        sf2_w = get_match_winner(mk_sf2, c1_w, d1_w)

        st.markdown("---")
        st.markdown('<div class="section-title" style="font-size:1.8rem">🏆 GRAN FINAL</div>', unsafe_allow_html=True)
        st.markdown(big_match_card(sf1_w, sf2_w, "GRAN FINAL · MMJ PAPA JOHNS LEAGUES CUP"), unsafe_allow_html=True)
        mk_gf = gk(T,"PF","GF")
        render_match(sf1_w, sf2_w, mk_gf, "🏆 Gran Final · Papa Johns Leagues Cup")
        gf_r = d_get(mk_gf, {})
        if gf_r.get("played"):
            champ = get_match_winner(mk_gf, sf1_w, sf2_w)
            d_set(gk(T,"champion"), champ)
            st.markdown(champion_card(champ, "MMJ PAPA JOHNS LEAGUES CUP"), unsafe_allow_html=True)

    with tabs[2]:
        st.markdown('<div class="section-title">📊 ESTADÍSTICAS DEL TORNEO</div>', unsafe_allow_html=True)
        st.markdown("### ⚽ Tabla de Goleadores")
        render_scorers_table(get_all_scorers(T))

        st.markdown("---")
        st.markdown("### 🗺️ Campeones por Zona")
        zcols = st.columns(5)
        for i, (zname, _) in enumerate(ZONES.items()):
            with zcols[i]:
                champ = d_get(gk(T,zname,"champion"), "TBD")
                sub   = d_get(gk(T,zname,"runner_up"), "TBD")
                color = ZONE_COLORS[zname]
                st.markdown(f"""
                <div style="background:var(--card);border-top:3px solid {color};border-radius:0 0 8px 8px;padding:14px;text-align:center">
                    <div style="font-family:'Barlow Condensed';font-size:0.7rem;letter-spacing:2px;color:{color};margin-bottom:8px">{zname}</div>
                    <div style="margin:8px 0">{logo_img(champ,40)}</div>
                    <div style="font-weight:700;font-size:0.9rem">🥇 {champ}</div>
                    <div style="margin-top:8px">{logo_img(sub,28)}</div>
                    <div style="font-size:0.82rem;color:var(--muted)">🥈 {sub}</div>
                </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# CISCO SUPER CUP
# ═══════════════════════════════════════════════════════════════════════════════
elif tournament == "🥤 Cisco Super Cup":
    T = "csc"

    st.markdown("<div class='info-box' style='font-size:0.95rem;margin-bottom:24px'>La MMJ Cisco Super Cup enfrenta al <strong>Campeón de la MMJ Streamlit League</strong> contra el <strong>Campeón de la MMJ Emirates Cup</strong> en un partido único.</div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### 🏆 Campeón Streamlit League")
        sl_champ = st.selectbox("Equipo", ALL_CODES,
            index=ALL_CODES.index(d_get(gk(T,"sl_champ"), ALL_CODES[0])) if d_get(gk(T,"sl_champ")) in ALL_CODES else 0,
            format_func=lambda c: f"{c} — {get_full_name(c)}", key="csc_sl")
        d_set(gk(T,"sl_champ"), sl_champ)
        st.markdown(f'<div style="text-align:center;padding:12px">{logo_img(sl_champ,72)}<br><span style="font-family:\'Bebas Neue\';font-size:1.1rem">{get_full_name(sl_champ)}</span></div>', unsafe_allow_html=True)

    with c2:
        st.markdown("#### 🏆 Campeón Emirates Cup")
        ec_champ = st.selectbox("Equipo", ALL_CODES,
            index=ALL_CODES.index(d_get(gk(T,"ec_champ"), ALL_CODES[1])) if d_get(gk(T,"ec_champ")) in ALL_CODES else 1,
            format_func=lambda c: f"{c} — {get_full_name(c)}", key="csc_ec")
        d_set(gk(T,"ec_champ"), ec_champ)
        st.markdown(f'<div style="text-align:center;padding:12px">{logo_img(ec_champ,72)}<br><span style="font-family:\'Bebas Neue\';font-size:1.1rem">{get_full_name(ec_champ)}</span></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(big_match_card(sl_champ, ec_champ, "MMJ CISCO SUPER CUP · GRAN FINAL"), unsafe_allow_html=True)
    mk_f = gk(T,"final")
    render_match(sl_champ, ec_champ, mk_f, "MMJ Cisco Super Cup · Gran Final")
    gf_r = d_get(mk_f, {})
    if gf_r.get("played"):
        champ = get_match_winner(mk_f, sl_champ, ec_champ)
        st.markdown(champion_card(champ, "MMJ CISCO SUPER CUP"), unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📊 Goleadores")
    render_scorers_table(get_all_scorers(T))


# ═══════════════════════════════════════════════════════════════════════════════
# McDONALD'S COMMUNITY CUP
# ═══════════════════════════════════════════════════════════════════════════════
elif tournament == "🍔 McDonald's Community Cup":
    T = "mcc"

    st.markdown("#### ⚙️ Configuración de Equipos")
    st.markdown("<div class='info-box'>Selecciona los equipos participantes.</div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div style="background:var(--card);border-top:3px solid var(--green);border-radius:0 0 8px 8px;padding:12px 16px;margin-bottom:12px"><div style="font-family:\'Barlow Condensed\';font-size:0.75rem;letter-spacing:2px;color:var(--green)">SEMIFINAL A</div><div style="font-size:0.82rem;color:var(--muted)">Campeón Streamlit League vs Último lugar</div></div>', unsafe_allow_html=True)
        sl_champ = st.selectbox("🏆 Campeón Streamlit League", ALL_CODES,
            index=ALL_CODES.index(d_get(gk(T,"sl_champ"), ALL_CODES[0])) if d_get(gk(T,"sl_champ")) in ALL_CODES else 0,
            format_func=lambda c: f"{c} — {get_full_name(c)}", key="mcc_sl")
        d_set(gk(T,"sl_champ"), sl_champ)
        last_place = st.selectbox("📉 Último lugar de la Liga", ALL_CODES,
            index=ALL_CODES.index(d_get(gk(T,"last_place"), ALL_CODES[-1])) if d_get(gk(T,"last_place")) in ALL_CODES else len(ALL_CODES)-1,
            format_func=lambda c: f"{c} — {get_full_name(c)}", key="mcc_lp")
        d_set(gk(T,"last_place"), last_place)

    with c2:
        st.markdown('<div style="background:var(--card);border-top:3px solid var(--orange);border-radius:0 0 8px 8px;padding:12px 16px;margin-bottom:12px"><div style="font-family:\'Barlow Condensed\';font-size:0.75rem;letter-spacing:2px;color:var(--orange)">SEMIFINAL B</div><div style="font-size:0.82rem;color:var(--muted)">Campeón Papa Johns Leagues Cup vs Campeón Emirates Cup</div></div>', unsafe_allow_html=True)
        pjlc_champ = st.selectbox("🏟️ Campeón Papa Johns Leagues Cup", ALL_CODES,
            index=ALL_CODES.index(d_get(gk(T,"pjlc_champ"), ALL_CODES[0])) if d_get(gk(T,"pjlc_champ")) in ALL_CODES else 0,
            format_func=lambda c: f"{c} — {get_full_name(c)}", key="mcc_pj")
        d_set(gk(T,"pjlc_champ"), pjlc_champ)
        ec_champ = st.selectbox("🏆 Campeón Emirates Cup", ALL_CODES,
            index=ALL_CODES.index(d_get(gk(T,"ec_champ"), ALL_CODES[1])) if d_get(gk(T,"ec_champ")) in ALL_CODES else 1,
            format_func=lambda c: f"{c} — {get_full_name(c)}", key="mcc_ec")
        d_set(gk(T,"ec_champ"), ec_champ)

    st.markdown("---")
    st.markdown('<div class="section-title">⚽ SEMIFINALES</div>', unsafe_allow_html=True)

    sf1c, sf2c = st.columns(2)
    with sf1c:
        st.markdown("### 🟢 SEMIFINAL A")
        mk_sfa = gk(T,"SFA")
        st.markdown(big_match_card(sl_champ, last_place, "Semifinal A"), unsafe_allow_html=True)
        render_match(sl_champ, last_place, mk_sfa, "Semifinal A")
        sfa_r = d_get(mk_sfa, {})
        sfa_w = get_match_winner(mk_sfa, sl_champ, last_place) if sfa_r.get("played") else "TBD"
        if sfa_r.get("played"):
            st.success(f"✅ Pasa a la Final: **{sfa_w}**")

    with sf2c:
        st.markdown("### 🟠 SEMIFINAL B")
        mk_sfb = gk(T,"SFB")
        st.markdown(big_match_card(pjlc_champ, ec_champ, "Semifinal B"), unsafe_allow_html=True)
        render_match(pjlc_champ, ec_champ, mk_sfb, "Semifinal B")
        sfb_r = d_get(mk_sfb, {})
        sfb_w = get_match_winner(mk_sfb, pjlc_champ, ec_champ) if sfb_r.get("played") else "TBD"
        if sfb_r.get("played"):
            st.success(f"✅ Pasa a la Final: **{sfb_w}**")

    st.markdown("---")
    st.markdown('<div class="section-title">🏆 GRAN FINAL</div>', unsafe_allow_html=True)
    st.markdown(big_match_card(sfa_w, sfb_w, "MMJ McDONALD'S COMMUNITY CUP · GRAN FINAL"), unsafe_allow_html=True)
    mk_gf = gk(T,"GF")
    render_match(sfa_w, sfb_w, mk_gf, "🏆 Gran Final · McDonald's Community Cup")
    gf_r = d_get(mk_gf, {})
    if gf_r.get("played"):
        champ = get_match_winner(mk_gf, sfa_w, sfb_w)
        st.markdown(champion_card(champ, "MMJ McDONALD'S COMMUNITY CUP"), unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📊 Goleadores")
    render_scorers_table(get_all_scorers(T))
