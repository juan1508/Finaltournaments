"""
app.py — FMMJ Nations · Competencias de Selecciones
Banderas reales via flagcdn.com · Logos de confederaciones · Diseño Sports App
"""
import streamlit as st
import pandas as pd
import base64
import json
import os
from itertools import combinations
from data import (
    UEFA_TEAMS, CONMEBOL_TEAMS, CAF_TEAMS, CONCACAF_TEAMS, AFC_TEAMS,
    PLAYOFF_TEAMS, PLAYERS, FLAG_MAP, INITIAL_FIFA_RANKING,
    ALL_TEAMS, COPA_AMERICA_GUESTS_POOL, COUNTRY_CODES, CONF_LOGOS,
    get_flag_url
)
from state import (
    init_state, flag, flag_img, flag_url, compute_standings,
    generate_group_matches, get_match_result, update_scorer,
    update_ranking_from_standings, save_state, reset_season
)

# ══════════════════════════════════════════════
# CARGA DE LOGOS — rutas directas en el repo
# ══════════════════════════════════════════════
LOGO_FILES = {
    "FIFA":     "fmmj.png",
    "UEFA":     "uefa.png",
    "CONMEBOL": "conmebol.png",
    "CAF":      "caf.png",
    "CONCACAF": "concacaf.png",
    "AFC":      "afc.png",
}

@st.cache_data
def load_logo_b64(path: str) -> str:
    if not path:
        return ""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        path,
        os.path.join(script_dir, path),
        os.path.join(os.getcwd(), path),
    ]
    found = next((p for p in candidates if os.path.exists(p)), None)
    if not found:
        return ""
    with open(found, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    ext = found.rsplit(".", 1)[-1].lower()
    mime = "image/png" if ext == "png" else f"image/{ext}"
    return f"data:{mime};base64,{data}"

LOGOS_B64 = {k: load_logo_b64(v) for k, v in LOGO_FILES.items()}

st.set_page_config(
    page_title="FMMJ Nations",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════
# ESTILOS GLOBALES
# ══════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Barlow:wght@400;600;700&family=Barlow+Condensed:wght@400;600;700&display=swap');

:root {
  --g:      #00E5A0;
  --g2:     #00B87A;
  --acc:    #FF5722;
  --gold:   #FFD700;
  --dark:   #07111E;
  --card:   #0D1B2A;
  --card2:  #132335;
  --border: rgba(0,229,160,.13);
  --txt:    #DDE4EF;
  --muted:  #5A7090;
}

html, body, [class*="css"] {
  font-family: 'Barlow', sans-serif;
  background: var(--dark) !important;
  color: var(--txt) !important;
}
.stApp { background: var(--dark) !important; }

[data-testid="stSidebar"] {
  background: linear-gradient(180deg,#050E1A 0%,#0A1828 100%) !important;
  border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] * { color: var(--txt) !important; }
[data-testid="stSidebar"] .stButton > button {
  background: transparent !important;
  color: var(--txt) !important;
  border: 1px solid rgba(0,229,160,.1) !important;
  text-align: left !important;
  font-size: 13px !important;
  letter-spacing: 1px !important;
  padding: 7px 14px !important;
  border-radius: 6px !important;
  font-family: 'Barlow Condensed', sans-serif !important;
  font-weight: 600 !important;
  transition: all .18s !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
  background: rgba(0,229,160,.08) !important;
  border-color: var(--g) !important;
  color: var(--g) !important;
}

.stButton > button {
  background: linear-gradient(135deg, var(--g), var(--g2)) !important;
  color: #050E1A !important;
  font-family: 'Bebas Neue', cursive !important;
  font-size: 15px !important;
  letter-spacing: 2px !important;
  border: none !important;
  border-radius: 6px !important;
  padding: 8px 22px !important;
  transition: all .2s !important;
  width: 100% !important;
}
.stButton > button:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 6px 20px rgba(0,229,160,.3) !important;
}

h1,h2,h3,h4 {
  font-family: 'Bebas Neue', cursive !important;
  letter-spacing: 3px !important;
  color: var(--txt) !important;
}

.card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 16px;
  margin: 5px 0;
}
.card-g    { border-left: 4px solid var(--g)   !important; }
.card-acc  { border-left: 4px solid var(--acc) !important; }
.card-gold { border-left: 4px solid var(--gold)!important; }
.card-blue { border-left: 4px solid #4A90D9   !important; }

.match-row {
  background: var(--card2);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 10px 14px;
  margin: 4px 0;
  display: flex;
  align-items: center;
  gap: 10px;
}
.match-row img { border-radius: 2px; }
.team-name { font-weight: 600; font-size: 14px; }
.score-box {
  background: rgba(0,0,0,.4);
  padding: 3px 14px;
  border-radius: 6px;
  font-family: 'Bebas Neue', cursive;
  font-size: 22px;
  letter-spacing: 2px;
  white-space: nowrap;
}

.hero {
  font-family: 'Bebas Neue', cursive;
  font-size: 68px;
  letter-spacing: 10px;
  background: linear-gradient(135deg,#00E5A0,#FFD700);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-align: center;
  line-height: 1;
}
.sub {
  font-family: 'Barlow Condensed';
  font-size: 13px;
  letter-spacing: 6px;
  color: var(--muted);
  text-align: center;
  text-transform: uppercase;
  margin-bottom: 28px;
}

.conf-hdr {
  padding: 14px 20px;
  border-radius: 10px;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 14px;
}
.conf-hdr-title {
  font-family: 'Bebas Neue', cursive;
  font-size: 30px;
  letter-spacing: 4px;
  line-height: 1;
}
.conf-hdr-sub {
  color: var(--muted);
  font-size: 12px;
  letter-spacing: 2px;
  margin-top: 3px;
}

.champ-banner {
  background: linear-gradient(135deg,#1a1200,#2a1f00);
  border: 1px solid var(--gold);
  border-radius: 14px;
  padding: 32px;
  text-align: center;
  margin: 16px 0;
}

thead tr th {
  background: rgba(0,229,160,.07) !important;
  color: var(--g) !important;
  font-family: 'Bebas Neue', cursive !important;
  letter-spacing: 1.5px !important;
}

.stTabs [data-baseweb="tab"] {
  font-family: 'Bebas Neue', cursive !important;
  letter-spacing: 2px !important;
  font-size: 15px !important;
}

.stSelectbox > label,
.stMultiSelect > label,
.stNumberInput > label {
  font-family: 'Barlow Condensed' !important;
  font-size: 12px !important;
  letter-spacing: 2px !important;
  color: var(--muted) !important;
  text-transform: uppercase !important;
}

.sb-section {
  font-family: 'Bebas Neue', cursive;
  font-size: 11px;
  letter-spacing: 3px;
  color: var(--muted);
  padding: 8px 8px 2px;
  margin-top: 6px;
  border-top: 1px solid var(--border);
  text-transform: uppercase;
}

.sb-conf-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 8px;
}
.sb-conf-logo {
  width: 22px;
  height: 22px;
  object-fit: contain;
  filter: brightness(0) invert(1);
  opacity: 0.7;
}

.player-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(130px,1fr));
  gap: 10px;
  margin-top: 12px;
}
.player-card {
  background: var(--card2);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 12px 10px 10px;
  text-align: center;
  position: relative;
  overflow: hidden;
  transition: border-color .2s, transform .2s;
}
.player-card::before {
  content:''; position:absolute; top:0; left:0; right:0; height:3px; border-radius:10px 10px 0 0;
}
.pos-GK-card::before { background:#F0A500; }
.pos-DF-card::before { background:#2196F3; }
.pos-MF-card::before { background:#4CAF50; }
.pos-FW-card::before { background:#F44336; }
.player-card:hover { border-color:var(--g); transform:translateY(-3px); }
.pos-badge { display:inline-block; padding:2px 9px; border-radius:10px; font-size:10px; font-weight:700; letter-spacing:1px; margin-bottom:7px; }
.pos-GK { background:rgba(240,165,0,.18); color:#F0A500; border:1px solid #F0A500; }
.pos-DF { background:rgba(33,150,243,.18);color:#2196F3; border:1px solid #2196F3; }
.pos-MF { background:rgba(76,175,80,.18); color:#4CAF50; border:1px solid #4CAF50; }
.pos-FW { background:rgba(244,67,54,.18); color:#F44336; border:1px solid #F44336; }
.pname { font-family:'Barlow Condensed'; font-weight:700; font-size:13px; min-height:30px; display:flex; align-items:center; justify-content:center; }

hr { border-color: var(--border) !important; }
[data-testid="metric-container"] {
  background: var(--card); border:1px solid var(--border); border-radius:10px; padding:14px;
}

.conf-logo-badge {
  width: 48px;
  height: 48px;
  object-fit: contain;
  filter: drop-shadow(0 2px 8px rgba(0,0,0,.5));
}

/* Etiqueta banderas en expanders */
.group-teams-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
  padding: 8px 0;
  border-bottom: 1px solid var(--border);
}
.group-team-chip {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 13px;
  font-weight: 600;
  color: var(--txt);
}
</style>
""", unsafe_allow_html=True)

init_state()

# ══════════════════════════════════════════════
# HELPERS DE BANDERAS
# ══════════════════════════════════════════════

def fl(team, size=20):
    code = FLAG_MAP.get(team, "")
    if not code:
        return ""
    h = int(size * 0.75)
    return f'<img src="https://flagcdn.com/{size}x{h}/{code}.png" style="vertical-align:middle;border-radius:2px;margin-right:5px;">'

def fl_big(team, width=40):
    code = FLAG_MAP.get(team, "")
    if not code:
        return ""
    h = int(width * 0.75)
    return f'<img src="https://flagcdn.com/{width}x{h}/{code}.png" style="vertical-align:middle;border-radius:3px;">'

def group_teams_header(teams):
    """Renderiza las banderas + nombres de equipos de un grupo DENTRO del expander."""
    chips = ""
    for t in teams:
        code = FLAG_MAP.get(t, "")
        img = f'<img src="https://flagcdn.com/20x15/{code}.png" style="vertical-align:middle;border-radius:2px;">' if code else ""
        chips += f'<div class="group-team-chip">{img} {t}</div>'
    st.markdown(f'<div class="group-teams-row">{chips}</div>', unsafe_allow_html=True)

POS_COLOR = {"GK":"#F0A500","DF":"#2196F3","MF":"#4CAF50","FW":"#F44336"}

# ══════════════════════════════════════════════
# FUNCIONES AUXILIARES
# ══════════════════════════════════════════════


def locked_banner(tournament_name, lock_key):
    """Muestra banner de grupos bloqueados con opción de desbloquear."""
    teams_summary = ""
    st.markdown(f"""
    <div style='background:linear-gradient(135deg,rgba(0,229,160,.08),rgba(0,229,160,.03));
    border:1px solid rgba(0,229,160,.3);border-left:4px solid var(--g);
    border-radius:10px;padding:16px 20px;margin:8px 0;display:flex;align-items:center;gap:12px;'>
      <div style='font-size:24px;'>🔒</div>
      <div>
        <div style='font-family:Bebas Neue;font-size:18px;letter-spacing:3px;color:var(--g);'>
          GRUPOS BLOQUEADOS</div>
        <div style='font-size:12px;color:var(--muted);margin-top:2px;'>
          {tournament_name} · Los grupos están guardados y protegidos contra cambios accidentales</div>
      </div>
    </div>""", unsafe_allow_html=True)
    if st.button(f"🔓 Desbloquear grupos {tournament_name}", key=f"unlock_{lock_key}"):
        st.session_state[lock_key] = False
        save_state()
        st.rerun()


def drag_drop_groups(teams, group_labels, group_size, existing_groups, key_prefix, accent_color="#00E5A0"):
    """
    Drag & drop visual. 
    Comunicación JS → Streamlit via st.query_params:
    El JS escribe window.parent.location.search con el estado serializado,
    lo que dispara un rerun de Streamlit que lee los params y los guarda.
    """
    import streamlit.components.v1 as _comp

    ss_key = f"_dnd_{key_prefix}"

    # Leer si ya hay un resultado en query_params (viene del JS)
    qp = st.query_params.to_dict()
    if f"dnd_{key_prefix}" in qp:
        raw_qp = qp[f"dnd_{key_prefix}"]
        try:
            parsed_qp = json.loads(raw_qp)
            if all(len(parsed_qp.get(gl, [])) == group_size for gl in group_labels):
                st.session_state[ss_key] = parsed_qp
                # Limpiar el query param para no acumular en la URL
                del st.query_params[f"dnd_{key_prefix}"]
        except Exception:
            pass

    # Estado actual: preferir session_state sobre existing_groups
    current = st.session_state.get(ss_key, None)
    if current and all(gl in current for gl in group_labels):
        assigned = {gl: [t for t in current.get(gl, []) if t in teams] for gl in group_labels}
    else:
        assigned = {gl: [t for t in existing_groups.get(gl, []) if t in teams] for gl in group_labels}

    all_asgn  = [t for v in assigned.values() for t in v]
    pool      = [t for t in teams if t not in all_asgn]

    teams_json   = json.dumps(teams)
    groups_json  = json.dumps(assigned)
    labels_json  = json.dumps(group_labels)
    flagmap_json = json.dumps({t: FLAG_MAP.get(t, "") for t in teams})
    pool_json    = json.dumps(pool)
    n_groups     = len(group_labels)
    widget_h     = max(480, n_groups * 100 + 200)

    # URL base actual sin query params de dnd
    base_url = "?"

    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Segoe UI',sans-serif;background:transparent;color:#DDE4EF;padding:6px;user-select:none}}
.wrap{{display:grid;grid-template-columns:185px 1fr;gap:10px}}
.panel{{background:#0D1B2A;border:1px solid rgba(0,229,160,.2);border-radius:10px;padding:8px;min-height:160px}}
.ptitle{{font-size:9px;letter-spacing:3px;color:#5A7090;margin-bottom:6px;text-transform:uppercase}}
.gg{{display:grid;grid-template-columns:repeat(auto-fill,minmax(142px,1fr));gap:7px}}
.gbox{{background:#0D1B2A;border:1px solid rgba(0,229,160,.18);border-radius:10px;padding:7px;min-height:72px;transition:border-color .12s,background .12s}}
.gbox.over{{border-color:{accent_color};background:rgba(0,229,160,.07)}}
.glabel{{font-size:9px;letter-spacing:3px;color:{accent_color};font-weight:700;margin-bottom:5px;display:flex;justify-content:space-between;align-items:center}}
.badge{{background:rgba(0,229,160,.15);color:{accent_color};border-radius:6px;padding:1px 6px;font-size:9px;font-weight:700}}
.badge.full{{background:rgba(0,229,160,.3)}}
.chip{{display:flex;align-items:center;gap:4px;background:#132335;border:1px solid rgba(255,255,255,.08);border-radius:5px;padding:3px 7px;margin:2px 0;cursor:grab;font-size:11px;font-weight:600;transition:opacity .1s,border-color .1s}}
.chip:hover{{border-color:{accent_color}}}
.chip.dragging{{opacity:.3;cursor:grabbing}}
.chip img{{border-radius:2px;flex-shrink:0}}
.btns{{display:flex;gap:7px;margin-top:8px}}
.btn{{font-family:'Segoe UI',sans-serif;font-size:10px;letter-spacing:1.5px;font-weight:700;border:none;border-radius:6px;padding:6px 13px;cursor:pointer;text-transform:uppercase}}
.bshuffle{{background:rgba(255,255,255,.07);color:#DDE4EF;border:1px solid rgba(255,255,255,.12)}}
.bclear{{background:rgba(244,67,54,.1);color:#F44336;border:1px solid rgba(244,67,54,.2)}}
.bsend{{background:linear-gradient(135deg,{accent_color},#00B87A);color:#050E1A;flex:1}}
.bsend:disabled{{opacity:.4;cursor:not-allowed}}
.status{{font-size:11px;margin-top:7px;min-height:16px}}
.ok{{color:{accent_color}}}.err{{color:#F44336}}
</style></head><body>
<div class="wrap">
  <div>
    <div class="ptitle">📦 sin asignar</div>
    <div class="panel" id="pool" ondragover="ov(event)" ondragleave="ol(event)" ondrop="drop(event,'__pool__')"></div>
  </div>
  <div>
    <div class="ptitle">grupos — arrastra los equipos</div>
    <div class="gg" id="gg"></div>
  </div>
</div>
<div class="btns">
  <button class="btn bshuffle" onclick="shuffle()">🎲 Sorteo</button>
  <button class="btn bclear"   onclick="clearAll()">✕ Limpiar</button>
  <button class="btn bsend" id="bsend" onclick="send()" disabled>✅ Confirmar y guardar</button>
</div>
<div class="status" id="st"></div>

<script>
const TEAMS={teams_json},LABELS={labels_json},FM={flagmap_json},SZ={group_size};
let S={groups_json},drag=null;

const fi=t=>{{const c=FM[t]||'';return c?`<img src="https://flagcdn.com/20x15/${{c}}.png" style="border-radius:2px;">`:''}};
const chip=t=>`<div class="chip" draggable="true" data-t="${{t}}" ondragstart="ds(event)" ondragend="de(event)">${{fi(t)}} ${{t}}</div>`;

function render(){{
  const asgn=Object.values(S).flat();
  const p=TEAMS.filter(t=>!asgn.includes(t));
  document.getElementById('pool').innerHTML=p.map(chip).join('')||'<span style="color:#5A7090;font-size:10px">Todos asignados ✓</span>';
  document.getElementById('gg').innerHTML=LABELS.map(gl=>{{
    const ts=S[gl]||[],full=ts.length>=SZ;
    return`<div class="gbox" id="gb_${{gl}}" ondragover="ov(event)" ondragleave="ol(event)" ondrop="drop(event,'${{gl}}')">
      <div class="glabel">GRUPO ${{gl}}<span class="badge${{full?' full':''}}">${{ts.length}}/${{SZ}}</span></div>
      ${{ts.map(chip).join('')}}
    </div>`;
  }}).join('');
  validate();
}}

function validate(){{
  const flat=Object.values(S).flat();
  const allFull=LABELS.every(gl=>(S[gl]||[]).length===SZ);
  const ok=allFull&&flat.length===new Set(flat).size;
  document.getElementById('bsend').disabled=!ok;
  const el=document.getElementById('st');
  if(ok){{
    el.innerHTML='<span class="ok">✅ Grupos completos</span>';
  }}else{{
    const miss=LABELS.reduce((a,gl)=>a+Math.max(0,SZ-(S[gl]||[]).length),0);
    el.innerHTML=`<span class="err">⚠️ Faltan ${{miss}} equipo(s) por asignar</span>`;
  }}
}}

function ds(e){{drag=e.currentTarget.dataset.t;e.currentTarget.classList.add('dragging');e.dataTransfer.effectAllowed='move';}}
function de(e){{e.currentTarget.classList.remove('dragging');}}
function ov(e){{e.preventDefault();e.currentTarget.classList.add('over');}}
function ol(e){{e.currentTarget.classList.remove('over');}}
function drop(e,gl){{
  e.preventDefault();e.currentTarget.classList.remove('over');
  if(!drag)return;
  for(const g of LABELS)S[g]=(S[g]||[]).filter(t=>t!==drag);
  if(gl!=='__pool__'){{
    if(!S[gl])S[gl]=[];
    if(S[gl].length<SZ&&!S[gl].includes(drag))S[gl].push(drag);
  }}
  drag=null;render();
}}

function shuffle(){{
  const sh=[...TEAMS].sort(()=>Math.random()-.5);
  S={{}};LABELS.forEach((gl,i)=>{{S[gl]=sh.slice(i*SZ,(i+1)*SZ);}});render();
}}

function clearAll(){{S={{}};LABELS.forEach(gl=>S[gl]=[]);render();}}

function send(){{
  const flat=Object.values(S).flat();
  const allFull=LABELS.every(gl=>(S[gl]||[]).length===SZ);
  if(!allFull||flat.length!==new Set(flat).size)return;
  // Escribir en query param del padre para que Streamlit lo lea en el próximo rerun
  const encoded=encodeURIComponent(JSON.stringify(S));
  window.parent.location.href=window.parent.location.pathname+'?dnd_{key_prefix}='+encoded;
}}

render();
</script></body></html>"""

    _comp.html(html, height=widget_h, scrolling=False)

    # Devolver el estado guardado en session_state si existe y es válido
    saved = st.session_state.get(ss_key)
    if isinstance(saved, dict) and all(len(saved.get(gl, [])) == group_size for gl in group_labels):
        return saved
    return None


def standings_df(standings, highlight=0, repechaje_pos=None):
    rows = []
    for s in standings:
        pos  = s["pos"]
        team = s["team"]
        code = FLAG_MAP.get(team, "")
        if code:
            flag_html = (
                f'<img src="https://flagcdn.com/20x15/{code}.png" ' +
                'style="vertical-align:middle;border-radius:2px;margin-right:6px;">'
            )
        else:
            flag_html = ""
        if pos <= highlight:
            estado = "✅ Clasifica"
        elif repechaje_pos and pos == repechaje_pos:
            estado = "🔄 Repechaje"
        else:
            estado = "❌"
        rows.append({
            "Pos":    str(pos),
            "Equipo": flag_html + team,
            "Pts":    str(s["pts"]),
            "PJ":     str(s["played"]),
            "G":      str(s["w"]),
            "E":      str(s["d"]),
            "P":      str(s["l"]),
            "GF":     str(s["gf"]),
            "GC":     str(s["ga"]),
            "GD":     str(s["gd"]),
            "Estado": estado,
        })
    return rows


def html_table(rows_list, col_widths=None, max_height=None):
    if not rows_list:
        st.info("Sin datos.")
        return

    cols = list(rows_list[0].keys())

    th = ""
    for c in cols:
        th += (
            '<th style="padding:6px 10px;text-align:left;' +
            'border-bottom:2px solid var(--g);' +
            'font-family:Barlow Condensed,sans-serif;font-size:13px;' +
            'letter-spacing:1px;color:var(--g);white-space:nowrap;">' +
            str(c) + '</th>'
        )

    tbody = ""
    for i, row in enumerate(rows_list):
        bg = "rgba(255,255,255,0.03)" if i % 2 == 0 else "transparent"
        tds = ""
        for c in cols:
            val = row.get(c, "")
            v = val if isinstance(val, str) else str(val) if val is not None else ""
            tds += (
                '<td style="padding:5px 10px;' +
                'border-bottom:1px solid rgba(255,255,255,0.06);' +
                'font-size:13px;white-space:nowrap;vertical-align:middle;">' +
                v + '</td>'
            )
        tbody += f'<tr style="background:{bg};">' + tds + '</tr>'

    # max_height limita la tabla para que no sobresalga de la col de partidos
    overflow_style = f"max-height:{max_height};overflow-y:auto;" if max_height else ""
    html = (
        f'<div style="overflow-x:auto;border-radius:8px;{overflow_style}'
        'border:1px solid rgba(255,255,255,0.08);">' +
        '<table style="width:100%;border-collapse:collapse;">' +
        '<thead><tr>' + th + '</tr></thead>' +
        '<tbody>' + tbody + '</tbody>' +
        '</table></div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def render_standings(standings, title="", highlight=0, repechaje_pos=None, max_height=None):
    if title:
        st.markdown(f"#### {title}")
    if not standings:
        st.info("Sin datos aún.")
        return
    rows = standings_df(standings, highlight, repechaje_pos)
    html_table(rows, max_height=max_height)


def build_rounds(teams):
    """
    Algoritmo round-robin que genera las jornadas para N equipos.
    Si N es impar agrega un 'BYE' ficticio y lo filtra al final.
    Devuelve lista de jornadas; cada jornada es lista de tuplas (t1, t2).
    """
    t = list(teams)
    if len(t) % 2 == 1:
        t.append("__BYE__")
    n = len(t)
    rounds = []
    for r in range(n - 1):
        pairs = []
        for i in range(n // 2):
            a = t[i]
            b = t[n - 1 - i]
            if a != "__BYE__" and b != "__BYE__":
                pairs.append((a, b))
        rounds.append(pairs)
        # rotación: fija el primero, rota el resto
        t = [t[0]] + [t[-1]] + t[1:-1]
    return rounds


def render_group_section(teams, matches_dict, prefix, matches_state_key,
                          players_dict, scorer_prefix, standings,
                          highlight=2, repechaje_pos=None):
    """
    Layout de grupo: tabla de posiciones arriba, partidos por fecha abajo.
    """
    # ── TABLA DE POSICIONES
    st.markdown(
        "<div style='font-family:Bebas Neue;font-size:13px;letter-spacing:3px;"
        "color:var(--g);margin:8px 0 6px;'>\U0001f4ca POSICIONES</div>",
        unsafe_allow_html=True
    )
    render_standings(standings, highlight=highlight, repechaje_pos=repechaje_pos)
    st.markdown("<div style='margin-top:14px;'></div>", unsafe_allow_html=True)

    # ── PARTIDOS POR FECHA
    st.markdown(
        "<div style='font-family:Bebas Neue;font-size:13px;letter-spacing:3px;"
        "color:var(--g);margin:0 0 6px;'>\u26bd PARTIDOS</div>",
        unsafe_allow_html=True
    )
    rounds = build_rounds(teams)
    for ri, pairs in enumerate(rounds):
        played_in_round = sum(
            1 for t1, t2 in pairs
            if matches_dict.get((t1,t2)) is not None or matches_dict.get((t2,t1)) is not None
        )
        total_in_round = len(pairs)
        badge = (
            f"<span style=\'background:rgba(0,229,160,.15);color:var(--g);"
            f"border-radius:10px;padding:1px 8px;font-size:11px;margin-left:6px;\'>"
            f"{played_in_round}/{total_in_round}</span>"
        )
        st.markdown(
            f"<div style=\'font-family:Bebas Neue;font-size:13px;letter-spacing:2px;"
            f"color:var(--muted);margin:8px 0 4px;border-left:3px solid var(--g);"
            f"padding-left:8px;\'>FECHA {ri + 1} {badge}</div>",
            unsafe_allow_html=True
        )
        for t1, t2 in pairs:
            key = (t1, t2) if (t1, t2) in matches_dict else (t2, t1)
            res = matches_dict.get(key)
            render_match_result(t1, t2, res)
            if res is None:
                r = match_input_form(prefix, t1, t2,
                    players_dict.get(t1, []), players_dict.get(t2, []),
                    f"{prefix}_r{ri}")
                if r:
                    hg, ag, sh, sa = r
                    st.session_state[matches_state_key][key] = {
                        "hg": hg, "ag": ag, "scorers_h": sh, "scorers_a": sa
                    }
                    for s in sh: update_scorer(s, t1, 1, scorer_prefix)
                    for s in sa: update_scorer(s, t2, 1, scorer_prefix)
                    save_state()
                    st.rerun()


def render_matches_by_round(teams, matches_dict, prefix, matches_state_key,
                             players_dict, scorer_prefix):
    """Partidos por fecha sin tabla — para playoffs sin grupos."""
    rounds = build_rounds(teams)
    for ri, pairs in enumerate(rounds):
        st.markdown(
            f"<div style=\'font-family:Bebas Neue;font-size:14px;letter-spacing:3px;"
            f"color:var(--g);margin:10px 0 4px;border-left:3px solid var(--g);"
            f"padding-left:8px;\'>FECHA {ri + 1}</div>",
            unsafe_allow_html=True
        )
        for t1, t2 in pairs:
            key = (t1, t2) if (t1, t2) in matches_dict else (t2, t1)
            res = matches_dict.get(key)
            render_match_result(t1, t2, res)
            if res is None:
                r = match_input_form(prefix, t1, t2,
                    players_dict.get(t1, []), players_dict.get(t2, []),
                    f"{prefix}_r{ri}")
                if r:
                    hg, ag, sh, sa = r
                    st.session_state[matches_state_key][key] = {
                        "hg": hg, "ag": ag, "scorers_h": sh, "scorers_a": sa
                    }
                    for s in sh: update_scorer(s, t1, 1, scorer_prefix)
                    for s in sa: update_scorer(s, t2, 1, scorer_prefix)
                    save_state()
                    st.rerun()


def render_match_result(t1, t2, res):
    img1 = fl(t1, 24)
    img2 = fl(t2, 24)
    if res is None:
        st.markdown(
            f"<div class='match-row'>"
            f"{img1} <span class='team-name'>{t1}</span>"
            f"<span style='margin:0 auto;color:var(--muted);font-family:Bebas Neue;font-size:18px;'>VS</span>"
            f"<span class='team-name'>{t2}</span> {img2}"
            f"<span style='color:var(--muted);font-size:11px;margin-left:8px;'>⏳ Pendiente</span>"
            f"</div>", unsafe_allow_html=True)
    else:
        hg = res.get("hg", 0); ag = res.get("ag", 0)
        hc = "#00E5A0" if hg > ag else "#F44336" if hg < ag else "#aaa"
        ac = "#00E5A0" if ag > hg else "#F44336" if ag < hg else "#aaa"
        sh = " ".join(f'<span style="font-size:10px;color:#aaa">⚽{s}</span>' for s in res.get("scorers_h", []))
        sa = " ".join(f'<span style="font-size:10px;color:#aaa">⚽{s}</span>' for s in res.get("scorers_a", []))
        st.markdown(
            f"<div class='match-row'>"
            f"{img1} <span class='team-name' style='color:{hc}'>{t1}</span>"
            f"<span class='score-box' style='margin:0 12px;'>{hg} – {ag}</span>"
            f"<span class='team-name' style='color:{ac}'>{t2}</span> {img2}"
            f"<span style='margin-left:auto;display:flex;gap:4px;flex-wrap:wrap;'>{sh} {sa}</span>"
            f"</div>", unsafe_allow_html=True)


def match_input_form(prefix, t1, t2, players_t1, players_t2, key_suffix=""):
    key_base = f"{prefix}_{t1}_{t2}_{key_suffix}"
    with st.expander(f"✏️ {t1} vs {t2}", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            hg = st.number_input(f"Goles {t1}", 0, 20, 0, key=f"{key_base}_hg")
        with col2:
            ag = st.number_input(f"Goles {t2}", 0, 20, 0, key=f"{key_base}_ag")
        scorers_h, scorers_a = [], []
        if hg > 0 and players_t1:
            st.markdown(f"<small style='color:var(--muted)'>⚽ Goleadores {t1}</small>", unsafe_allow_html=True)
            pn = [p["name"] for p in players_t1]
            for g in range(int(hg)):
                s = st.selectbox(f"Gol {g+1}", ["(sin registrar)"]+pn, key=f"{key_base}_sh_{g}")
                if s != "(sin registrar)": scorers_h.append(s)
        if ag > 0 and players_t2:
            st.markdown(f"<small style='color:var(--muted)'>⚽ Goleadores {t2}</small>", unsafe_allow_html=True)
            pn2 = [p["name"] for p in players_t2]
            for g in range(int(ag)):
                s = st.selectbox(f"Gol {g+1}", ["(sin registrar)"]+pn2, key=f"{key_base}_sa_{g}")
                if s != "(sin registrar)": scorers_a.append(s)
        if st.button("💾 Guardar resultado", key=f"{key_base}_save"):
            return int(hg), int(ag), scorers_h, scorers_a
    return None


def knockout_input(prefix, t1, t2, players_t1, players_t2, allow_draw=False):
    key_base = f"ko_{prefix}_{t1}_{t2}"
    with st.expander(f"⚔️ {t1}  vs  {t2}", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            hg = st.number_input(f"Goles {t1}", 0, 20, 0, key=f"{key_base}_hg")
        with col2:
            ag = st.number_input(f"Goles {t2}", 0, 20, 0, key=f"{key_base}_ag")
        winner = None; penalty_winner = None
        if hg == ag and not allow_draw:
            st.markdown("<small style='color:#F0A500'>⚠️ Empate → definir por penaltis</small>", unsafe_allow_html=True)
            penalty_winner = st.selectbox("Ganador en penaltis", [t1, t2], key=f"{key_base}_pen")
            winner = penalty_winner
        elif hg > ag:
            winner = t1
        elif ag > hg:
            winner = t2
        scorers_h, scorers_a = [], []
        if hg > 0 and players_t1:
            pn = [p["name"] for p in players_t1]
            for g in range(int(hg)):
                s = st.selectbox(f"⚽ Gol {g+1} ({t1})", ["(sin registrar)"]+pn, key=f"{key_base}_sh{g}")
                if s != "(sin registrar)": scorers_h.append(s)
        if ag > 0 and players_t2:
            pn2 = [p["name"] for p in players_t2]
            for g in range(int(ag)):
                s = st.selectbox(f"⚽ Gol {g+1} ({t2})", ["(sin registrar)"]+pn2, key=f"{key_base}_sa{g}")
                if s != "(sin registrar)": scorers_a.append(s)
        if st.button("💾 Guardar", key=f"{key_base}_save"):
            if winner is None and hg == ag and not allow_draw:
                st.error("Elige ganador en penaltis")
                return None
            if winner is None:
                winner = t1 if hg >= ag else t2
            return {"hg":int(hg),"ag":int(ag),"winner":winner,
                    "penalty_winner":penalty_winner,
                    "scorers_h":scorers_h,"scorers_a":scorers_a}
    return None


def champ_banner(team, title="CAMPEÓN"):
    img = fl_big(team, 80)
    st.markdown(f"""
    <div class='champ-banner'>
      {img}
      <div style='font-family:Bebas Neue;font-size:16px;letter-spacing:6px;color:var(--gold);margin-top:14px;'>🏆 {title}</div>
      <div style='font-family:Bebas Neue;font-size:38px;letter-spacing:4px;margin-top:4px;'>{team}</div>
    </div>""", unsafe_allow_html=True)


def conf_header(color, emoji, name, info="", conf_key=None):
    logo_html = ""
    if conf_key and LOGOS_B64.get(conf_key):
        logo_html = f'<img src="{LOGOS_B64[conf_key]}" class="conf-logo-badge" onerror="this.style.display=\'none\'">'
    else:
        logo_html = f'<div style="font-size:36px;line-height:1;">{emoji}</div>'

    st.markdown(f"""
    <div class='conf-hdr' style='background:linear-gradient(135deg,{color}18,{color}05);border:1px solid {color}40;border-left:4px solid {color};'>
      {logo_html}
      <div>
        <div class='conf-hdr-title' style='color:{color};'>{name}</div>
        <div class='conf-hdr-sub'>{info}</div>
      </div>
    </div>""", unsafe_allow_html=True)


def team_chip(team, color="var(--g)"):
    code = FLAG_MAP.get(team, "")
    if code:
        img = f'<img src="https://flagcdn.com/20x15/{code}.png" style="vertical-align:middle;border-radius:2px;margin-right:5px;">'
    else:
        img = ""
    return (f'<span style="display:inline-flex;align-items:center;background:rgba(0,0,0,.3);'
            f'border:1px solid {color}40;border-radius:20px;padding:3px 10px;font-size:12px;margin:2px;">'
            f'{img}{team}</span>')


# ══════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════
with st.sidebar:
    fifa_logo = LOGOS_B64.get("FIFA", "")
    if fifa_logo:
        logo_tag = f'<img src="{fifa_logo}" style="width:54px;height:54px;object-fit:contain;margin-bottom:6px;">'
    else:
        logo_tag = '<div style="font-size:36px;">⚽</div>'

    st.markdown(f"""
    <div style='text-align:center;padding:18px 0 12px;'>
      {logo_tag}
      <div style='font-family:Bebas Neue;font-size:30px;letter-spacing:6px;color:#00E5A0;'>FMMJ</div>
      <div style='font-size:9px;letter-spacing:4px;color:#5A7090;'>NATIONS · COMPETENCIAS</div>
    </div>""", unsafe_allow_html=True)

    st.divider()

    if st.button("🏠  Inicio", key="nav_home", use_container_width=True):
        save_state()
        st.session_state.active_page = "🏠 Inicio"; st.rerun()
    if st.button("📊  Ranking FIFA", key="nav_rank", use_container_width=True):
        save_state()
        st.session_state.active_page = "📊 Ranking FIFA"; st.rerun()
    if st.button("⚽  Goleadores", key="nav_score", use_container_width=True):
        save_state()
        st.session_state.active_page = "⚽ Goleadores"; st.rerun()
    if st.button("👥  Plantillas", key="nav_squad", use_container_width=True):
        save_state()
        st.session_state.active_page = "👥 Plantillas"; st.rerun()

    # ─── UEFA ───
    uefa_logo = LOGOS_B64.get("UEFA", "")
    logo_tag_uefa = f'<img src="{uefa_logo}" class="sb-conf-logo" onerror="this.style.display=\'none\'">' if uefa_logo else "🌍"
    st.markdown(
        f"<div class='sb-section' style='color:#4A90D9;'>"
        f"<div class='sb-conf-row'>{logo_tag_uefa} <span>UEFA</span></div></div>",
        unsafe_allow_html=True)
    if st.button("🏆  Eurocopa", key="nav_euro", use_container_width=True):
        save_state()
        st.session_state.active_page = "🏆 Eurocopa"; st.rerun()
    if st.button("🔢  Playoffs UEFA", key="nav_europ", use_container_width=True):
        save_state()
        st.session_state.active_page = "🔢 Playoffs UEFA"; st.rerun()

    # ─── CONMEBOL ───
    conmebol_logo = LOGOS_B64.get("CONMEBOL", "")
    logo_tag_conmebol = f'<img src="{conmebol_logo}" class="sb-conf-logo" onerror="this.style.display=\'none\'">' if conmebol_logo else "🌎"
    st.markdown(
        f"<div class='sb-section' style='color:#27AE60;'>"
        f"<div class='sb-conf-row'>{logo_tag_conmebol} <span>CONMEBOL</span></div></div>",
        unsafe_allow_html=True)
    if st.button("🏆  Copa América", key="nav_ca", use_container_width=True):
        save_state()
        st.session_state.active_page = "🏆 Copa América"; st.rerun()
    if st.button("🔢  Playoffs CONMEBOL", key="nav_cmp", use_container_width=True):
        save_state()
        st.session_state.active_page = "🔢 Playoffs CONMEBOL"; st.rerun()

    # ─── CAF ───
    caf_logo = LOGOS_B64.get("CAF", "")
    logo_tag_caf = f'<img src="{caf_logo}" class="sb-conf-logo" onerror="this.style.display=\'none\'">' if caf_logo else "🌍"
    st.markdown(
        f"<div class='sb-section' style='color:#F39C12;'>"
        f"<div class='sb-conf-row'>{logo_tag_caf} <span>CAF</span></div></div>",
        unsafe_allow_html=True)
    if st.button("🏆  Copa África", key="nav_af", use_container_width=True):
        save_state()
        st.session_state.active_page = "🏆 Copa África"; st.rerun()
    if st.button("🔢  Playoffs CAF", key="nav_cafp", use_container_width=True):
        save_state()
        st.session_state.active_page = "🔢 Playoffs CAF"; st.rerun()

    # ─── CONCACAF ───
    concacaf_logo = LOGOS_B64.get("CONCACAF", "")
    logo_tag_concacaf = f'<img src="{concacaf_logo}" class="sb-conf-logo" onerror="this.style.display=\'none\'">' if concacaf_logo else "🌎"
    st.markdown(
        f"<div class='sb-section' style='color:#E74C3C;'>"
        f"<div class='sb-conf-row'>{logo_tag_concacaf} <span>CONCACAF</span></div></div>",
        unsafe_allow_html=True)
    if st.button("🏆  Copa Oro", key="nav_co", use_container_width=True):
        save_state()
        st.session_state.active_page = "🏆 Copa Oro"; st.rerun()
    if st.button("🔢  Playoffs CONCACAF", key="nav_ccp", use_container_width=True):
        save_state()
        st.session_state.active_page = "🔢 Playoffs CONCACAF"; st.rerun()

    # ─── AFC ───
    afc_logo = LOGOS_B64.get("AFC", "")
    logo_tag_afc = f'<img src="{afc_logo}" class="sb-conf-logo" onerror="this.style.display=\'none\'">' if afc_logo else "🌏"
    st.markdown(
        f"<div class='sb-section' style='color:#9B59B6;'>"
        f"<div class='sb-conf-row'>{logo_tag_afc} <span>AFC</span></div></div>",
        unsafe_allow_html=True)
    if st.button("🏆  Copa Asia", key="nav_as", use_container_width=True):
        save_state()
        st.session_state.active_page = "🏆 Copa Asia"; st.rerun()
    if st.button("🔢  Playoffs AFC", key="nav_afcp", use_container_width=True):
        save_state()
        st.session_state.active_page = "🔢 Playoffs AFC"; st.rerun()

    # ─── MUNDIAL ───
    st.markdown("<div class='sb-section' style='color:#FFD700;'>🌐 MUNDIAL</div>", unsafe_allow_html=True)
    if st.button("🔄  Repechaje Internacional", key="nav_rep", use_container_width=True):
        save_state()
        st.session_state.active_page = "🔄 Repechaje"; st.rerun()
    if st.button("🏆  Copa del Mundo", key="nav_wc", use_container_width=True):
        save_state()
        st.session_state.active_page = "🏆 Mundial"; st.rerun()

    st.divider()
    nq = len(st.session_state.wc_qualified)
    st.markdown(f"""
    <div style='text-align:center;'>
      <div style='font-size:11px;color:var(--muted);letter-spacing:2px;'>CLASIFICADOS MUNDIAL</div>
      <div style='font-family:Bebas Neue;font-size:28px;color:var(--g);'>{nq}<span style='font-size:16px;color:var(--muted);'>/32</span></div>
      <div style='font-size:11px;color:var(--muted);'>Temporada {st.session_state.season}</div>
    </div>""", unsafe_allow_html=True)

page = st.session_state.active_page

# ══════════════════════════════════════════════
# INICIO
# ══════════════════════════════════════════════
if page == "🏠 Inicio":
    st.markdown("<div class='hero'>FMMJ NATIONS</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='sub'>Competencias de Selecciones · Temporada {st.session_state.season}</div>", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Clasificados", f"{len(st.session_state.wc_qualified)}/32")
    champ_wc = st.session_state.wc_champion or "—"
    c2.metric("🏆 Campeón del Mundo", champ_wc)
    rnk1 = max(st.session_state.fifa_ranking, key=st.session_state.fifa_ranking.get)
    c3.metric("Ranking #1", rnk1)
    c4.metric("Temporada", st.session_state.season)

    st.divider()
    st.markdown("### 📋 Estado de Torneos")

    CUPS = [
        ("🌍 Eurocopa",    "euro_champion", "#4A90D9",  "UEFA"),
        ("🌎 Copa América","ca_champion",   "#27AE60",  "CONMEBOL"),
        ("🌍 Copa África", "af_champion",   "#F39C12",  "CAF"),
        ("🌎 Copa Oro",    "co_champion",   "#E74C3C",  "CONCACAF"),
        ("🌏 Copa Asia",   "as_champion",   "#9B59B6",  "AFC"),
    ]
    cols = st.columns(5)
    for col, (name, key, color, conf_key) in zip(cols, CUPS):
        cv = st.session_state.get(key)
        img = fl_big(cv, 32) if cv else ""
        logo = LOGOS_B64.get(conf_key, "")
        logo_tag = f'<img src="{logo}" style="width:28px;height:28px;object-fit:contain;filter:brightness(0) invert(1);opacity:.4;margin-bottom:4px;" onerror="this.style.display=\'none\'">' if logo else ""
        with col:
            st.markdown(f"""
            <div class='card' style='border-top:3px solid {color};text-align:center;padding:16px 10px;'>
              {logo_tag}
              <div style='font-size:11px;color:{color};letter-spacing:2px;margin-bottom:6px;'>{name}</div>
              {'<div>'+img+'</div><div style="font-weight:700;font-size:13px;color:#FFD700;">🏆 '+cv+'</div>' if cv
               else "<div style='color:var(--muted);font-size:12px;margin-top:8px;'>⏳ En curso</div>"}
            </div>""", unsafe_allow_html=True)

    if st.session_state.wc_qualified:
        st.divider()
        st.markdown("### ✅ Clasificados al Mundial")
        teams = st.session_state.wc_qualified
        html = "<div style='display:flex;flex-wrap:wrap;gap:8px;margin-top:8px;'>"
        for t in teams:
            code = FLAG_MAP.get(t, "")
            img_tag = f'<img src="https://flagcdn.com/24x18/{code}.png" style="vertical-align:middle;border-radius:2px;margin-right:5px;">' if code else ""
            html += f'<div class="card" style="padding:8px 12px;display:inline-flex;align-items:center;gap:4px;">{img_tag}<span style="font-size:13px;font-weight:600;">{t}</span></div>'
        html += "</div>"
        st.markdown(html, unsafe_allow_html=True)

    if st.session_state.wc_champion:
        st.divider()
        champ_banner(st.session_state.wc_champion, "CAMPEÓN DEL MUNDO")
        st.markdown("""
        <div style='background:rgba(255,87,34,.08);border:1px solid rgba(255,87,34,.3);
        border-left:4px solid #FF5722;border-radius:10px;padding:14px 18px;margin:12px 0;'>
          <div style='font-family:Bebas Neue;font-size:16px;letter-spacing:3px;color:#FF5722;'>
            ⚠️ NUEVA TEMPORADA</div>
          <div style='font-size:12px;color:var(--muted);margin-top:4px;'>
            Se borrarán todos los grupos, partidos y resultados de todos los torneos.<br>
            Se conservarán el Ranking FIFA, el historial de temporadas y los goleadores.</div>
        </div>""", unsafe_allow_html=True)
        if st.button("🔄 Confirmar Nueva Temporada", type="primary"):
            st.session_state.season_history.append({
                "season": st.session_state.season,
                "champion": st.session_state.wc_champion,
                "ranking": dict(st.session_state.fifa_ranking),
            })
            st.session_state.season += 1
            reset_season()
            st.rerun()

# ══════════════════════════════════════════════
# EUROCOPA
# ══════════════════════════════════════════════
elif page == "🏆 Eurocopa":
    conf_header("#4A90D9", "🌍", "EUROCOPA UEFA",
                "24 equipos · 6 grupos de 4 · Pasan 2 por grupo + 4 mejores 3ros → R16",
                conf_key="UEFA")

    tab_setup, tab_groups, tab_ko, tab_result = st.tabs(["⚙️ Configurar","📊 Grupos","⚔️ Eliminatorias","🏆 Resultado"])

    with tab_setup:
        st.markdown("#### Selecciona 24 equipos y asígnalos a grupos arrastrando")
        _def = [t for t in (st.session_state.euro_teams or UEFA_TEAMS[:24]) if t in UEFA_TEAMS]
        selected = st.multiselect("1️⃣ Elige los 24 equipos UEFA", UEFA_TEAMS, default=_def, max_selections=24)
        if len(selected) == 24:
            st.session_state.euro_teams = selected
            st.markdown("---")
            st.markdown("**2️⃣ Arrastra los equipos a cada grupo:**")
            dnd_result = drag_drop_groups(
                selected, ["A","B","C","D","E","F"], 4,
                st.session_state.euro_groups, "euro", "#4A90D9"
            )
            st.markdown("---")
            if st.button("💾 Guardar grupos"):
                groups_to_save = dnd_result or st.session_state.euro_groups
                all_a = sum(groups_to_save.values(), [])
                if len(all_a) != len(set(all_a)) or len(all_a) != 24:
                    st.error("Asigna exactamente 4 equipos a cada uno de los 6 grupos sin repetir.")
                elif any(len(v) != 4 for v in groups_to_save.values()):
                    st.error("Cada grupo debe tener exactamente 4 equipos.")
                else:
                    st.session_state.euro_groups = groups_to_save
                    all_m = {}
                    for gl, teams in groups_to_save.items():
                        all_m.update(generate_group_matches(teams))
                    st.session_state.euro_matches = all_m
                    st.success("✅ Grupos guardados.")
                    save_state()
                    st.rerun()
        else:
            st.info(f"Selecciona exactamente 24 equipos. Tienes {len(selected)}.")

    with tab_groups:
        if not st.session_state.euro_groups:
            st.info("Configura los grupos primero.")
        else:
            for gl in ["A","B","C","D","E","F"]:
                teams = st.session_state.euro_groups.get(gl, [])
                if not teams: continue
                with st.expander(f"Grupo {gl}", expanded=True):
                    group_teams_header(teams)
                    gm = {k:v for k,v in st.session_state.euro_matches.items()
                          if k[0] in teams and k[1] in teams and v is not None}
                    standings = compute_standings(teams, gm)
                    st.session_state.euro_standings[gl] = standings
                    render_group_section(
                        teams, st.session_state.euro_matches,
                        "euro", "euro_matches", PLAYERS, "euro_",
                        standings, highlight=2
                    )

            st.divider()
            st.markdown("#### 📋 Clasificados al R16")
            all_standings = st.session_state.euro_standings
            if len(all_standings) == 6:
                qualifiers_r16 = []
                third_places = []
                for gl in ["A","B","C","D","E","F"]:
                    s = all_standings.get(gl, [])
                    if len(s) >= 2:
                        qualifiers_r16.append((f"{gl}1", s[0]["team"]))
                        qualifiers_r16.append((f"{gl}2", s[1]["team"]))
                    if len(s) >= 3:
                        third_places.append((gl, s[2]))
                third_sorted = sorted(third_places, key=lambda x:(x[1]["pts"],x[1]["gd"],x[1]["gf"]), reverse=True)
                best_thirds = [(f"{gl}3*", s["team"]) for gl, s in third_sorted[:4]]
                all_r16 = qualifiers_r16 + best_thirds
                html = "<div style='display:flex;flex-wrap:wrap;gap:6px;'>"
                for lbl, t in all_r16:
                    code = FLAG_MAP.get(t, "")
                    img_tag = f'<img src="https://flagcdn.com/20x15/{code}.png" style="vertical-align:middle;border-radius:2px;margin:4px 0;">' if code else ""
                    html += (f'<div class="card" style="padding:8px 12px;text-align:center;min-width:120px;">'
                             f'<div style="font-size:10px;color:var(--muted);">{lbl}</div>'
                             f'<div style="margin:4px 0;">{img_tag}</div>'
                             f'<div style="font-size:12px;font-weight:600;">{t}</div></div>')
                html += "</div>"
                st.markdown(html, unsafe_allow_html=True)
                if st.button("➡️ Generar R16") and len(all_r16) == 16:
                    by_slot = {lbl: t for lbl, t in all_r16}
                    r16_pairs = [
                        (by_slot.get("A1","?"), by_slot.get("C2","?")),
                        (by_slot.get("D1","?"), by_slot.get("F2","?")),
                        (by_slot.get("B1","?"), by_slot.get("E2","?")),
                        (by_slot.get("A2","?"), by_slot.get("B2","?")),
                        (by_slot.get("C1","?"), by_slot.get("D2","?")),
                        (by_slot.get("E1","?"), by_slot.get("F1","?")),
                        (best_thirds[0][1] if best_thirds else "?", best_thirds[1][1] if len(best_thirds)>1 else "?"),
                        (best_thirds[2][1] if len(best_thirds)>2 else "?", best_thirds[3][1] if len(best_thirds)>3 else "?"),
                    ]
                    st.session_state.euro_r16 = r16_pairs
                    st.session_state.euro_r16_results = {}
                    st.success("✅ R16 generado. Ve a Eliminatorias.")
                    save_state()
                    st.rerun()

    with tab_ko:
        if not st.session_state.euro_r16:
            st.info("Completa los grupos y genera el R16 primero.")
        else:
            st.markdown("### ⚔️ Octavos de Final (R16)")
            r16_winners = []
            for i,(t1,t2) in enumerate(st.session_state.euro_r16):
                res = st.session_state.euro_r16_results.get(i)
                if res:
                    render_match_result(t1,t2,res); r16_winners.append(res["winner"])
                else:
                    r = knockout_input(f"euro_r16_{i}",t1,t2,PLAYERS.get(t1,[]),PLAYERS.get(t2,[]))
                    if r:
                        st.session_state.euro_r16_results[i] = r
                        for s in r.get("scorers_h",[]): update_scorer(s,t1,1,"euro_")
                        for s in r.get("scorers_a",[]): update_scorer(s,t2,1,"euro_")
                        save_state()
                        st.rerun()
                    r16_winners.append(None)
            if all(r16_winners) and len(r16_winners) == 8:
                if not st.session_state.euro_qf:
                    st.session_state.euro_qf = [(r16_winners[i], r16_winners[i+1]) for i in range(0,8,2)]
                st.markdown("### ⚔️ Cuartos de Final")
                qf_winners = []
                for i,(t1,t2) in enumerate(st.session_state.euro_qf):
                    if t1 is None or t2 is None: continue
                    res = st.session_state.euro_qf_results.get(i)
                    if res:
                        render_match_result(t1,t2,res); qf_winners.append(res["winner"])
                    else:
                        r = knockout_input(f"euro_qf_{i}",t1,t2,PLAYERS.get(t1,[]),PLAYERS.get(t2,[]))
                        if r:
                            st.session_state.euro_qf_results[i] = r
                            for s in r.get("scorers_h",[]): update_scorer(s,t1,1,"euro_")
                            for s in r.get("scorers_a",[]): update_scorer(s,t2,1,"euro_")
                            save_state()
                            st.rerun()
                        qf_winners.append(None)
                if all(qf_winners) and len(qf_winners) == 4:
                    if not st.session_state.euro_sf:
                        st.session_state.euro_sf = [(qf_winners[0],qf_winners[1]),(qf_winners[2],qf_winners[3])]
                    st.markdown("### ⚔️ Semifinales")
                    sf_winners = []; sf_losers = []
                    for i,(t1,t2) in enumerate(st.session_state.euro_sf):
                        if t1 is None or t2 is None: continue
                        res = st.session_state.euro_sf_results.get(i)
                        if res:
                            render_match_result(t1,t2,res)
                            sf_winners.append(res["winner"])
                            sf_losers.append(t2 if res["winner"]==t1 else t1)
                        else:
                            r = knockout_input(f"euro_sf_{i}",t1,t2,PLAYERS.get(t1,[]),PLAYERS.get(t2,[]))
                            if r:
                                st.session_state.euro_sf_results[i] = r
                                for s in r.get("scorers_h",[]): update_scorer(s,t1,1,"euro_")
                                for s in r.get("scorers_a",[]): update_scorer(s,t2,1,"euro_")
                                save_state()
                                st.rerun()
                            sf_winners.append(None)
                    if all(sf_winners) and len(sf_winners) == 2:
                        if st.session_state.euro_final is None:
                            st.session_state.euro_final = (sf_winners[0], sf_winners[1])
                        st.markdown("### 🏆 FINAL")
                        t1,t2 = st.session_state.euro_final
                        res = st.session_state.euro_final_result
                        if res:
                            render_match_result(t1,t2,res)
                            champ_banner(res["winner"],"CAMPEÓN DE EUROPA")
                        else:
                            r = knockout_input("euro_final",t1,t2,PLAYERS.get(t1,[]),PLAYERS.get(t2,[]))
                            if r:
                                st.session_state.euro_final_result = r
                                champion = r["winner"]; runner = t2 if champion==t1 else t1
                                st.session_state.euro_champion = champion
                                for s in r.get("scorers_h",[]): update_scorer(s,t1,1,"euro_")
                                for s in r.get("scorers_a",[]): update_scorer(s,t2,1,"euro_")
                                fs = [{"pos":1,"team":champion},{"pos":2,"team":runner}]
                                pos = 3
                                for lsr in (sf_losers or []):
                                    if lsr: fs.append({"pos":pos,"team":lsr}); pos+=1
                                for i_,res_ in st.session_state.euro_qf_results.items():
                                    lsr = (st.session_state.euro_qf[i_][0] if res_["winner"]==st.session_state.euro_qf[i_][1]
                                           else st.session_state.euro_qf[i_][1]) if i_ < len(st.session_state.euro_qf) else None
                                    if lsr and lsr not in [e["team"] for e in fs]:
                                        fs.append({"pos":pos,"team":lsr}); pos+=1
                                for i_,res_ in st.session_state.euro_r16_results.items():
                                    t1_,t2_ = st.session_state.euro_r16[i_]
                                    lsr = t2_ if res_["winner"]==t1_ else t1_
                                    if lsr and lsr not in [e["team"] for e in fs]:
                                        fs.append({"pos":pos,"team":lsr}); pos+=1
                                placed = {e["team"] for e in fs}
                                for gl,s in st.session_state.euro_standings.items():
                                    for entry in s:
                                        if entry["team"] not in placed:
                                            fs.append({"pos":pos,"team":entry["team"]}); pos+=1; placed.add(entry["team"])
                                st.session_state.euro_final_standings = fs
                                update_ranking_from_standings(fs, 80, 4)
                                if champion not in st.session_state.wc_qualified:
                                    st.session_state.wc_qualified.append(champion)
                                save_state()
                                st.rerun()

    with tab_result:
        if st.session_state.euro_champion:
            champ_banner(st.session_state.euro_champion, "CAMPEÓN DE EUROPA")
            st.markdown("#### 📊 Clasificación Final")
            render_standings(st.session_state.euro_final_standings[:10], highlight=5)
            st.info(f"El campeón **{st.session_state.euro_champion}** clasifica directamente al Mundial.")
        else:
            st.info("La Eurocopa aún no tiene resultado final.")

# ══════════════════════════════════════════════
# UEFA PLAYOFFS
# ══════════════════════════════════════════════
elif page == "🔢 Playoffs UEFA":
    conf_header("#4A90D9","🔢","UEFA · PLAYOFFS MUNDIALISTAS",
                "Puestos 6-21 Eurocopa → 4 grupos de 4 · Top 2 c/u → Mundial", conf_key="UEFA")
    if not st.session_state.euro_final_standings:
        st.warning("Primero completa la Eurocopa.")
    else:
        fs = st.session_state.euro_final_standings
        pool = [e["team"] for e in fs[5:21]]
        tab1, tab2 = st.tabs(["⚙️ Grupos","📊 Resultados"])
        with tab1:
            st.markdown("**Equipos disponibles (puestos 6-21 Eurocopa):**")
            html = "<div style='display:flex;flex-wrap:wrap;gap:6px;'>" + "".join(team_chip(t,"#4A90D9") for t in pool) + "</div>"
            st.markdown(html, unsafe_allow_html=True)
            st.markdown("---")
            st.markdown("**Arma los 4 grupos (4 equipos c/u):**")
            cols = st.columns(4)
            new_groups = {}
            for i,gl in enumerate(["A","B","C","D"]):
                with cols[i]:
                    st.markdown(f"**Grupo {gl}**")
                    default_g = st.session_state.euro_playoff_groups.get(gl, pool[i*4:(i+1)*4])
                    chosen = st.multiselect(f"Grupo {gl}", pool, default=default_g, max_selections=4, key=f"ep_grp_{gl}")
                    if chosen:
                        st.markdown(" ".join(f'{fl(t,18)}<span style="font-size:10px;color:var(--muted);">{t}</span>' for t in chosen), unsafe_allow_html=True)
                    new_groups[gl] = chosen
            if st.button("💾 Guardar grupos playoff"):
                all_a = sum(new_groups.values(),[])
                if len(all_a)!=len(set(all_a)): st.error("Duplicados.")
                elif any(len(v)!=4 for v in new_groups.values()): st.error("4 equipos por grupo.")
                else:
                    st.session_state.euro_playoff_groups = new_groups
                    all_m = {}
                    for gl,teams in new_groups.items(): all_m.update(generate_group_matches(teams))
                    st.session_state.euro_playoff_matches = all_m
                    st.success("✅ Grupos guardados."); save_state(); st.rerun()
        with tab2:
            if not st.session_state.euro_playoff_groups:
                st.info("Arma los grupos primero.")
            else:
                for gl in ["A","B","C","D"]:
                    teams = st.session_state.euro_playoff_groups.get(gl,[])
                    if not teams: continue
                    # ✅ FIX: título texto, banderas dentro
                    with st.expander(f"Grupo {gl}", expanded=True):
                        group_teams_header(teams)
                        col_m, col_t = st.columns([3,2])
                        gm = {k:v for k,v in st.session_state.euro_playoff_matches.items() if k[0] in teams and k[1] in teams and v is not None}
                        s = compute_standings(teams,gm)
                        st.session_state.euro_playoff_standings[gl] = s
                        render_group_section(
                            teams, st.session_state.euro_playoff_matches,
                            "ep", "euro_playoff_matches", PLAYERS, "euro_",
                            s, highlight=2
                        )
                st.divider()
                qualified = []
                for gl in ["A","B","C","D"]:
                    s = st.session_state.euro_playoff_standings.get(gl,[])
                    qualified.extend([e["team"] for e in s[:2]])
                st.markdown(f"#### ✅ Clasificados al Mundial via Playoffs UEFA ({len(qualified)})")
                html = "<div style='display:flex;flex-wrap:wrap;gap:6px;'>" + "".join(team_chip(t,"#4A90D9") for t in qualified) + "</div>"
                st.markdown(html, unsafe_allow_html=True)
                if st.button("💾 Confirmar clasificados UEFA al Mundial"):
                    euro_direct = [e["team"] for e in st.session_state.euro_final_standings[:5]]
                    all_uefa = list(set(euro_direct+qualified))
                    for t in all_uefa:
                        if t not in st.session_state.wc_qualified:
                            st.session_state.wc_qualified.append(t)
                    st.session_state.euro_playoff_qualified = all_uefa
                    st.success(f"✅ {len(all_uefa)} equipos UEFA confirmados al Mundial.")

# ══════════════════════════════════════════════
# COPA AMERICA
# ══════════════════════════════════════════════
elif page == "🏆 Copa América":
    conf_header("#27AE60","🌎","COPA AMÉRICA CONMEBOL",
                "10 equipos CONMEBOL + 6 invitados · 4 grupos de 4 · 2 pasan por grupo",
                conf_key="CONMEBOL")
    tab_setup, tab_groups, tab_ko, tab_result = st.tabs(["⚙️ Config","📊 Grupos","⚔️ Bracket","🏆 Resultado"])
    with tab_setup:
        st.markdown("#### Equipos invitados (6, no UEFA)")
        guests = st.multiselect("Selecciona 6 invitados", COPA_AMERICA_GUESTS_POOL,
                            default=st.session_state.ca_teams[10:] if len(st.session_state.ca_teams)==16 else [],
                            max_selections=6)
        all_ca = CONMEBOL_TEAMS + guests
        st.markdown(f"**Total: {len(all_ca)}/16 equipos**")
        if len(all_ca) == 16:
            st.markdown("---")
            st.markdown("**2️⃣ Arrastra los equipos a cada grupo:**")
            dnd_result = drag_drop_groups(
                all_ca, ["A","B","C","D"], 4,
                st.session_state.ca_groups, "ca", "#27AE60"
            )
            st.markdown("---")
            if st.button("💾 Guardar grupos"):
                groups_to_save = dnd_result or st.session_state.ca_groups
                all_a = sum(groups_to_save.values(),[])
                if len(all_a)!=len(set(all_a)) or len(all_a)!=16: st.error("Asigna 4 equipos a cada grupo sin repetir.")
                elif any(len(v)!=4 for v in groups_to_save.values()): st.error("4 equipos por grupo.")
                else:
                    st.session_state.ca_teams = all_ca
                    st.session_state.ca_groups = groups_to_save
                    all_m = {}
                    for gl,teams in groups_to_save.items(): all_m.update(generate_group_matches(teams))
                    st.session_state.ca_matches = all_m
                    st.success("✅ Grupos guardados."); save_state(); st.rerun()
    with tab_groups:
        if not st.session_state.ca_groups:
            st.info("Configura los grupos primero.")
        else:
            for gl in ["A","B","C","D"]:
                teams = st.session_state.ca_groups.get(gl,[])
                if not teams: continue
                # ✅ FIX
                with st.expander(f"Grupo {gl}", expanded=True):
                    group_teams_header(teams)
                    gm = {k:v for k,v in st.session_state.ca_matches.items() if k[0] in teams and k[1] in teams and v is not None}
                    s = compute_standings(teams,gm)
                    st.session_state.ca_standings[gl] = s
                    render_group_section(
                        teams, st.session_state.ca_matches,
                        "ca", "ca_matches", PLAYERS, "ca_",
                        s, highlight=2
                    )
            st.divider()
            by_slot = {}
            for gl in ["A","B","C","D"]:
                s = st.session_state.ca_standings.get(gl,[])
                if len(s)>=2:
                    by_slot[f"{gl}1"] = s[0]["team"]
                    by_slot[f"{gl}2"] = s[1]["team"]
            if len(by_slot)==8:
                ca_r16 = [
                    (by_slot.get("A1","?"), by_slot.get("D2","?")),
                    (by_slot.get("C1","?"), by_slot.get("B2","?")),
                    (by_slot.get("B1","?"), by_slot.get("C2","?")),
                    (by_slot.get("D1","?"), by_slot.get("A2","?")),
                ]
                st.markdown("#### Bracket Cuartos Copa América")
                for t1,t2 in ca_r16:
                    render_match_result(t1,t2,None)
                if st.button("➡️ Generar Bracket QF/SF/Final"):
                    st.session_state.ca_r16 = ca_r16
                    st.session_state.ca_r16_results = {}
                    st.success("✅ Bracket generado."); save_state(); st.rerun()
    with tab_ko:
        if not st.session_state.ca_r16:
            st.info("Completa grupos y genera bracket primero.")
        else:
            st.markdown("### ⚔️ Cuartos de Final")
            r16_winners = []
            for i,(t1,t2) in enumerate(st.session_state.ca_r16):
                res = st.session_state.ca_r16_results.get(i)
                if res:
                    render_match_result(t1,t2,res); r16_winners.append(res["winner"])
                else:
                    r = knockout_input(f"ca_r16_{i}",t1,t2,PLAYERS.get(t1,[]),PLAYERS.get(t2,[]))
                    if r:
                        st.session_state.ca_r16_results[i] = r
                        for s in r.get("scorers_h",[]): update_scorer(s,t1,1,"ca_")
                        for s in r.get("scorers_a",[]): update_scorer(s,t2,1,"ca_")
                        save_state()
                        st.rerun()
                    r16_winners.append(None)
            if all(r16_winners) and len(r16_winners)==4:
                if not st.session_state.ca_sf:
                    st.session_state.ca_sf = [(r16_winners[0],r16_winners[1]),(r16_winners[2],r16_winners[3])]
                st.markdown("### ⚔️ Semifinales")
                sf_winners = []
                for i,(t1,t2) in enumerate(st.session_state.ca_sf):
                    res = st.session_state.ca_sf_results.get(i)
                    if res:
                        render_match_result(t1,t2,res); sf_winners.append(res["winner"])
                    else:
                        r = knockout_input(f"ca_sf_{i}",t1,t2,PLAYERS.get(t1,[]),PLAYERS.get(t2,[]))
                        if r:
                            st.session_state.ca_sf_results[i] = r
                            for s in r.get("scorers_h",[]): update_scorer(s,t1,1,"ca_")
                            for s in r.get("scorers_a",[]): update_scorer(s,t2,1,"ca_")
                            save_state()
                            st.rerun()
                        sf_winners.append(None)
                if all(sf_winners) and len(sf_winners)==2:
                    if st.session_state.ca_final is None:
                        st.session_state.ca_final = (sf_winners[0],sf_winners[1])
                    st.markdown("### 🏆 FINAL")
                    t1,t2 = st.session_state.ca_final
                    res = st.session_state.ca_final_result
                    if res:
                        render_match_result(t1,t2,res); champ_banner(res["winner"],"CAMPEÓN DE AMÉRICA")
                    else:
                        r = knockout_input("ca_final",t1,t2,PLAYERS.get(t1,[]),PLAYERS.get(t2,[]))
                        if r:
                            st.session_state.ca_final_result = r
                            champ = r["winner"]; runner = t2 if champ==t1 else t1
                            st.session_state.ca_champion = champ
                            for s in r.get("scorers_h",[]): update_scorer(s,t1,1,"ca_")
                            for s in r.get("scorers_a",[]): update_scorer(s,t2,1,"ca_")
                            fs = [{"pos":1,"team":champ},{"pos":2,"team":runner}]
                            pos = 3
                            for i_,(ta,tb) in enumerate(st.session_state.ca_sf):
                                res_ = st.session_state.ca_sf_results.get(i_)
                                if res_:
                                    lsr = tb if res_["winner"]==ta else ta
                                    fs.append({"pos":pos,"team":lsr}); pos+=1
                            placed = {e["team"] for e in fs}
                            for gl,s_ in st.session_state.ca_standings.items():
                                for entry in s_:
                                    if entry["team"] not in placed:
                                        fs.append({"pos":pos,"team":entry["team"]}); pos+=1; placed.add(entry["team"])
                            st.session_state.ca_final_standings = fs
                            update_ranking_from_standings(fs,80,5)
                            if champ not in st.session_state.wc_qualified:
                                st.session_state.wc_qualified.append(champ)
                            save_state()
                            st.rerun()
    with tab_result:
        if st.session_state.ca_champion:
            champ_banner(st.session_state.ca_champion,"CAMPEÓN DE AMÉRICA")
            render_standings(st.session_state.ca_final_standings[:10], highlight=1)
        else:
            st.info("Copa América sin resultado aún.")

# ══════════════════════════════════════════════
# CONMEBOL PLAYOFFS
# ══════════════════════════════════════════════
elif page == "🔢 Playoffs CONMEBOL":
    conf_header("#27AE60","🔢","CONMEBOL · PLAYOFFS MUNDIALISTAS",
                "Puestos 2-7 → todos vs todos · Top 3 → Mundial · 4to → Repechaje",
                conf_key="CONMEBOL")
    if not st.session_state.ca_final_standings:
        st.warning("Completa la Copa América primero.")
    else:
        fs = st.session_state.ca_final_standings
        conmebol_in_ca = [e for e in fs if e["team"] in CONMEBOL_TEAMS]
        pool = [e["team"] for e in conmebol_in_ca[1:7]]
        html = "<div style='display:flex;flex-wrap:wrap;gap:6px;margin-bottom:16px;'>" + "".join(team_chip(t,"#27AE60") for t in pool) + "</div>"
        st.markdown(html, unsafe_allow_html=True)
        if not st.session_state.conmebol_playoff_teams:
            if st.button("▶️ Iniciar eliminatoria CONMEBOL"):
                st.session_state.conmebol_playoff_teams = pool
                st.session_state.conmebol_playoff_matches = generate_group_matches(pool)
                save_state()
                st.rerun()
        else:
            teams = st.session_state.conmebol_playoff_teams
            for t1,t2 in combinations(teams,2):
                key = (t1,t2) if (t1,t2) in st.session_state.conmebol_playoff_matches else (t2,t1)
                res = st.session_state.conmebol_playoff_matches.get(key)
                render_match_result(t1,t2,res)
                if res is None:
                    r = match_input_form("cmp",t1,t2,PLAYERS.get(t1,[]),PLAYERS.get(t2,[]))
                    if r:
                        hg,ag,sh,sa = r
                        st.session_state.conmebol_playoff_matches[key] = {"hg":hg,"ag":ag,"scorers_h":sh,"scorers_a":sa}
                        save_state()
                        st.rerun()
            st.divider()
            played = {k:v for k,v in st.session_state.conmebol_playoff_matches.items() if v is not None}
            standings = compute_standings(teams, played)
            st.session_state.conmebol_playoff_standings = standings
            render_standings(standings, highlight=3, repechaje_pos=4)
            qualified = [s["team"] for s in standings[:3]]
            repechaje = standings[3]["team"] if len(standings)>3 else None
            st.markdown("**✅ Clasificados:** " + " · ".join(f"{fl(t)}{t}" for t in qualified), unsafe_allow_html=True)
            if repechaje: st.markdown(f"**🔄 Repechaje:** {fl(repechaje)}{repechaje}", unsafe_allow_html=True)
            if st.button("💾 Confirmar clasificados CONMEBOL"):
                for t in qualified:
                    if t not in st.session_state.wc_qualified: st.session_state.wc_qualified.append(t)
                st.session_state.conmebol_playoff_qualified = qualified
                st.session_state.conmebol_playoff_repechaje = repechaje
                st.success("✅ Confirmados.")

# ══════════════════════════════════════════════
# COPA AFRICA
# ══════════════════════════════════════════════
elif page == "🏆 Copa África":
    conf_header("#F39C12","🌍","COPA ÁFRICA CAF",
                "10 equipos · 2 grupos de 5 · 2 primeros → Semis", conf_key="CAF")
    tab_setup,tab_groups,tab_ko,tab_result = st.tabs(["⚙️ Config","📊 Grupos","⚔️ Eliminatorias","🏆 Resultado"])
    with tab_setup:
        _af_def = [t for t in (st.session_state.af_teams or CAF_TEAMS) if t in CAF_TEAMS]
        selected = st.multiselect("1️⃣ Elige 10 equipos CAF", CAF_TEAMS, default=_af_def, max_selections=10)
        if len(selected)==10:
            st.markdown("**2️⃣ Arrastra los equipos a cada grupo (5 por grupo):**")
            dnd_result = drag_drop_groups(selected, ["A","B"], 5, st.session_state.af_groups, "af", "#F39C12")
            st.markdown("---")
            if st.button("💾 Guardar grupos"):
                g2s = dnd_result or st.session_state.af_groups
                gA = g2s.get("A",[]); gB = g2s.get("B",[])
                if len(gA)!=5 or len(gB)!=5: st.error("5 equipos por grupo.")
                elif len(set(gA+gB))!=10: st.error("Duplicados.")
                else:
                    st.session_state.af_teams = selected
                    st.session_state.af_groups = g2s
                    st.session_state.af_matches = {**generate_group_matches(gA),**generate_group_matches(gB)}
                    st.success("✅ Grupos guardados."); save_state(); st.rerun()
    with tab_groups:
        if not st.session_state.af_groups: st.info("Configura primero.")
        else:
            for gl in ["A","B"]:
                teams = st.session_state.af_groups.get(gl,[])
                # ✅ FIX
                with st.expander(f"Grupo {gl}", expanded=True):
                    group_teams_header(teams)
                    gm = {k:v for k,v in st.session_state.af_matches.items() if k[0] in teams and k[1] in teams and v is not None}
                    s = compute_standings(teams,gm)
                    st.session_state.af_standings[gl] = s
                    render_group_section(
                        teams, st.session_state.af_matches,
                        "af", "af_matches", PLAYERS, "af_",
                        s, highlight=2
                    )
            sA = st.session_state.af_standings.get("A",[])
            sB = st.session_state.af_standings.get("B",[])
            if len(sA)>=2 and len(sB)>=2:
                sf1 = (sA[0]["team"],sB[1]["team"]); sf2 = (sB[0]["team"],sA[1]["team"])
                render_match_result(sf1[0],sf1[1],None); render_match_result(sf2[0],sf2[1],None)
                if st.button("➡️ Generar Semis"):
                    st.session_state.af_sf = [sf1,sf2]; st.session_state.af_sf_results = {}
                    st.success("✅ Semis generadas."); save_state(); st.rerun()
    with tab_ko:
        if not st.session_state.af_sf: st.info("Completa grupos primero.")
        else:
            st.markdown("### ⚔️ Semifinales")
            sf_winners = []
            for i,(t1,t2) in enumerate(st.session_state.af_sf):
                res = st.session_state.af_sf_results.get(i)
                if res: render_match_result(t1,t2,res); sf_winners.append(res["winner"])
                else:
                    r = knockout_input(f"af_sf_{i}",t1,t2,PLAYERS.get(t1,[]),PLAYERS.get(t2,[]))
                    if r:
                        st.session_state.af_sf_results[i] = r
                        for s in r.get("scorers_h",[]): update_scorer(s,t1,1,"af_")
                        for s in r.get("scorers_a",[]): update_scorer(s,t2,1,"af_")
                        save_state()
                        st.rerun()
                    sf_winners.append(None)
            if all(sf_winners) and len(sf_winners)==2:
                if st.session_state.af_final is None:
                    st.session_state.af_final = (sf_winners[0],sf_winners[1])
                st.markdown("### 🏆 FINAL")
                t1,t2 = st.session_state.af_final
                res = st.session_state.af_final_result
                if res: render_match_result(t1,t2,res); champ_banner(res["winner"],"CAMPEÓN DE ÁFRICA")
                else:
                    r = knockout_input("af_final",t1,t2,PLAYERS.get(t1,[]),PLAYERS.get(t2,[]))
                    if r:
                        st.session_state.af_final_result = r
                        champ = r["winner"]; runner = t2 if champ==t1 else t1
                        st.session_state.af_champion = champ
                        for s in r.get("scorers_h",[]): update_scorer(s,t1,1,"af_")
                        for s in r.get("scorers_a",[]): update_scorer(s,t2,1,"af_")
                        fs = [{"pos":1,"team":champ},{"pos":2,"team":runner}]
                        pos=3; placed={champ,runner}
                        for gl,s_ in st.session_state.af_standings.items():
                            for e in s_:
                                if e["team"] not in placed:
                                    fs.append({"pos":pos,"team":e["team"]}); pos+=1; placed.add(e["team"])
                        st.session_state.af_final_standings = fs
                        update_ranking_from_standings(fs,70,5)
                        for t in [champ,runner]:
                            if t not in st.session_state.wc_qualified: st.session_state.wc_qualified.append(t)
                        save_state()
                        st.rerun()
    with tab_result:
        if st.session_state.af_champion:
            champ_banner(st.session_state.af_champion,"CAMPEÓN DE ÁFRICA")
            render_standings(st.session_state.af_final_standings[:6], highlight=2)
        else: st.info("Sin resultado aún.")

# ══════════════════════════════════════════════
# CAF PLAYOFFS
# ══════════════════════════════════════════════
elif page == "🔢 Playoffs CAF":
    conf_header("#F39C12","🔢","CAF · PLAYOFFS MUNDIALISTAS",
                "Puestos 3-7 → todos vs todos · Top 3 → Mundial", conf_key="CAF")
    if not st.session_state.af_final_standings:
        st.warning("Completa la Copa África primero.")
    else:
        pool = [e["team"] for e in st.session_state.af_final_standings[2:7]]
        html = "<div style='display:flex;flex-wrap:wrap;gap:6px;margin-bottom:16px;'>" + "".join(team_chip(t,"#F39C12") for t in pool) + "</div>"
        st.markdown(html, unsafe_allow_html=True)
        if not st.session_state.caf_playoff_teams:
            if st.button("▶️ Iniciar playoff CAF"):
                st.session_state.caf_playoff_teams = pool
                st.session_state.caf_playoff_matches = generate_group_matches(pool)
                save_state()
                st.rerun()
        else:
            teams = st.session_state.caf_playoff_teams
            for t1,t2 in combinations(teams,2):
                key = (t1,t2) if (t1,t2) in st.session_state.caf_playoff_matches else (t2,t1)
                res = st.session_state.caf_playoff_matches.get(key)
                render_match_result(t1,t2,res)
                if res is None:
                    r = match_input_form("cafp",t1,t2,PLAYERS.get(t1,[]),PLAYERS.get(t2,[]))
                    if r:
                        hg,ag,sh,sa = r
                        st.session_state.caf_playoff_matches[key] = {"hg":hg,"ag":ag,"scorers_h":sh,"scorers_a":sa}
                        save_state()
                        st.rerun()
            st.divider()
            played = {k:v for k,v in st.session_state.caf_playoff_matches.items() if v is not None}
            standings = compute_standings(teams,played)
            st.session_state.caf_playoff_standings = standings
            render_standings(standings, highlight=3)
            qualified = [s["team"] for s in standings[:3]]
            if st.button("💾 Confirmar clasificados CAF"):
                for t in qualified:
                    if t not in st.session_state.wc_qualified: st.session_state.wc_qualified.append(t)
                st.session_state.caf_playoff_qualified = qualified
                st.success("✅ Confirmados.")

# ══════════════════════════════════════════════
# COPA ORO
# ══════════════════════════════════════════════
elif page == "🏆 Copa Oro":
    conf_header("#E74C3C","🌎","COPA ORO CONCACAF",
                "6 equipos · 2 grupos de 3 · A1vB2 y B1vA2 → Final", conf_key="CONCACAF")
    tab_setup,tab_groups,tab_ko,tab_result = st.tabs(["⚙️ Config","📊 Grupos","⚔️ Eliminatorias","🏆 Resultado"])
    with tab_setup:
        _co_def = [t for t in (st.session_state.co_teams or CONCACAF_TEAMS) if t in CONCACAF_TEAMS]
        selected = st.multiselect("1️⃣ Elige 6 equipos CONCACAF", CONCACAF_TEAMS, default=_co_def, max_selections=6)
        if len(selected)==6:
            st.markdown("**2️⃣ Arrastra los equipos a cada grupo (3 por grupo):**")
            dnd_result = drag_drop_groups(selected, ["A","B"], 3, st.session_state.co_groups, "co", "#E74C3C")
            st.markdown("---")
            if st.button("💾 Guardar grupos"):
                g2s = dnd_result or st.session_state.co_groups
                gA = g2s.get("A",[]); gB = g2s.get("B",[])
                if len(gA)!=3 or len(gB)!=3 or len(set(gA+gB))!=6: st.error("3 por grupo sin duplicados.")
                else:
                    st.session_state.co_teams = selected
                    st.session_state.co_groups = g2s
                    st.session_state.co_matches = {**generate_group_matches(gA),**generate_group_matches(gB)}
                    st.success("✅ Grupos guardados."); save_state(); st.rerun()
    with tab_groups:
        if not st.session_state.co_groups: st.info("Configura primero.")
        else:
            for gl in ["A","B"]:
                teams = st.session_state.co_groups.get(gl,[])
                # ✅ FIX
                with st.expander(f"Grupo {gl}", expanded=True):
                    group_teams_header(teams)
                    gm = {k:v for k,v in st.session_state.co_matches.items() if k[0] in teams and k[1] in teams and v is not None}
                    s = compute_standings(teams,gm)
                    st.session_state.co_standings[gl] = s
                    render_group_section(
                        teams, st.session_state.co_matches,
                        "co", "co_matches", PLAYERS, "co_",
                        s, highlight=2
                    )
            sA = st.session_state.co_standings.get("A",[])
            sB = st.session_state.co_standings.get("B",[])
            if len(sA)>=2 and len(sB)>=2:
                sf1 = (sA[0]["team"],sB[1]["team"]); sf2 = (sB[0]["team"],sA[1]["team"])
                render_match_result(sf1[0],sf1[1],None); render_match_result(sf2[0],sf2[1],None)
                if st.button("➡️ Generar Semis Copa Oro"):
                    save_state()
                    st.session_state.co_sf = [sf1,sf2]; st.session_state.co_sf_results = {}; st.rerun()
    with tab_ko:
        if not st.session_state.co_sf: st.info("Completa grupos primero.")
        else:
            st.markdown("### ⚔️ Semifinales")
            sf_winners = []
            for i,(t1,t2) in enumerate(st.session_state.co_sf):
                res = st.session_state.co_sf_results.get(i)
                if res: render_match_result(t1,t2,res); sf_winners.append(res["winner"])
                else:
                    r = knockout_input(f"co_sf_{i}",t1,t2,PLAYERS.get(t1,[]),PLAYERS.get(t2,[]))
                    if r:
                        st.session_state.co_sf_results[i] = r
                        for s in r.get("scorers_h",[]): update_scorer(s,t1,1,"co_")
                        for s in r.get("scorers_a",[]): update_scorer(s,t2,1,"co_")
                        save_state()
                        st.rerun()
                    sf_winners.append(None)
            if all(sf_winners) and len(sf_winners)==2:
                if st.session_state.co_final is None:
                    st.session_state.co_final = (sf_winners[0],sf_winners[1])
                st.markdown("### 🏆 FINAL")
                t1,t2 = st.session_state.co_final
                res = st.session_state.co_final_result
                if res: render_match_result(t1,t2,res); champ_banner(res["winner"],"CAMPEÓN COPA ORO")
                else:
                    r = knockout_input("co_final",t1,t2,PLAYERS.get(t1,[]),PLAYERS.get(t2,[]))
                    if r:
                        st.session_state.co_final_result = r; champ = r["winner"]
                        st.session_state.co_champion = champ
                        for s in r.get("scorers_h",[]): update_scorer(s,t1,1,"co_")
                        for s in r.get("scorers_a",[]): update_scorer(s,t2,1,"co_")
                        runner = t2 if champ==t1 else t1
                        fs = [{"pos":1,"team":champ},{"pos":2,"team":runner}]
                        pos=3; placed={champ,runner}
                        for i_,(ta,tb) in enumerate(st.session_state.co_sf):
                            res_ = st.session_state.co_sf_results.get(i_)
                            if res_:
                                lsr = tb if res_["winner"]==ta else ta
                                if lsr not in placed: fs.append({"pos":pos,"team":lsr}); pos+=1; placed.add(lsr)
                        for gl,s_ in st.session_state.co_standings.items():
                            for e in s_:
                                if e["team"] not in placed: fs.append({"pos":pos,"team":e["team"]}); pos+=1; placed.add(e["team"])
                        st.session_state.co_final_standings = fs
                        update_ranking_from_standings(fs,60,6)
                        if champ not in st.session_state.wc_qualified: st.session_state.wc_qualified.append(champ)
                        save_state()
                        st.rerun()
    with tab_result:
        if st.session_state.co_champion:
            champ_banner(st.session_state.co_champion,"CAMPEÓN COPA ORO")
            render_standings(st.session_state.co_final_standings, highlight=1)
        else: st.info("Sin resultado aún.")

# ══════════════════════════════════════════════
# CONCACAF PLAYOFFS
# ══════════════════════════════════════════════
elif page == "🔢 Playoffs CONCACAF":
    conf_header("#E74C3C","🔢","CONCACAF · PLAYOFFS",
                "Puestos 2-5 → todos vs todos · Top 2 → Mundial · 3ro → Repechaje",
                conf_key="CONCACAF")
    if not st.session_state.co_final_standings:
        st.warning("Completa la Copa Oro primero.")
    else:
        pool = [e["team"] for e in st.session_state.co_final_standings[1:5]]
        html = "<div style='display:flex;flex-wrap:wrap;gap:6px;margin-bottom:16px;'>" + "".join(team_chip(t,"#E74C3C") for t in pool) + "</div>"
        st.markdown(html, unsafe_allow_html=True)
        if not st.session_state.concacaf_playoff_teams:
            if st.button("▶️ Iniciar playoff CONCACAF"):
                st.session_state.concacaf_playoff_teams = pool
                st.session_state.concacaf_playoff_matches = generate_group_matches(pool)
                save_state()
                st.rerun()
        else:
            teams = st.session_state.concacaf_playoff_teams
            for t1,t2 in combinations(teams,2):
                key = (t1,t2) if (t1,t2) in st.session_state.concacaf_playoff_matches else (t2,t1)
                res = st.session_state.concacaf_playoff_matches.get(key)
                render_match_result(t1,t2,res)
                if res is None:
                    r = match_input_form("ccp",t1,t2,PLAYERS.get(t1,[]),PLAYERS.get(t2,[]))
                    if r:
                        hg,ag,sh,sa = r
                        st.session_state.concacaf_playoff_matches[key] = {"hg":hg,"ag":ag,"scorers_h":sh,"scorers_a":sa}
                        save_state()
                        st.rerun()
            st.divider()
            played = {k:v for k,v in st.session_state.concacaf_playoff_matches.items() if v is not None}
            standings = compute_standings(teams,played)
            st.session_state.concacaf_playoff_standings = standings
            render_standings(standings, highlight=2, repechaje_pos=3)
            qualified = [s["team"] for s in standings[:2]]
            repechaje = standings[2]["team"] if len(standings)>2 else None
            if repechaje: st.markdown(f"**🔄 Repechaje:** {fl(repechaje)}{repechaje}", unsafe_allow_html=True)
            if st.button("💾 Confirmar CONCACAF"):
                for t in qualified:
                    if t not in st.session_state.wc_qualified: st.session_state.wc_qualified.append(t)
                st.session_state.concacaf_playoff_qualified = qualified
                st.session_state.concacaf_playoff_repechaje = repechaje
                st.success("✅ Confirmados.")

# ══════════════════════════════════════════════
# COPA ASIA
# ══════════════════════════════════════════════
elif page == "🏆 Copa Asia":
    conf_header("#9B59B6","🌏","COPA ASIA AFC",
                "6 equipos · 2 grupos de 3 · A1vB2 y B1vA2 → Final", conf_key="AFC")
    tab_setup,tab_groups,tab_ko,tab_result = st.tabs(["⚙️ Config","📊 Grupos","⚔️ Eliminatorias","🏆 Resultado"])
    with tab_setup:
        _as_def = [t for t in (st.session_state.as_teams or AFC_TEAMS) if t in AFC_TEAMS]
        selected = st.multiselect("1️⃣ Elige 6 equipos AFC", AFC_TEAMS, default=_as_def, max_selections=6)
        if len(selected)==6:
            st.markdown("**2️⃣ Arrastra los equipos a cada grupo (3 por grupo):**")
            dnd_result = drag_drop_groups(selected, ["A","B"], 3, st.session_state.as_groups, "as", "#9B59B6")
            st.markdown("---")
            if st.button("💾 Guardar grupos"):
                g2s = dnd_result or st.session_state.as_groups
                gA = g2s.get("A",[]); gB = g2s.get("B",[])
                if len(gA)!=3 or len(gB)!=3 or len(set(gA+gB))!=6: st.error("3 por grupo sin duplicados.")
                else:
                    st.session_state.as_teams = selected
                    st.session_state.as_groups = g2s
                    st.session_state.as_matches = {**generate_group_matches(gA),**generate_group_matches(gB)}
                    st.success("✅ Grupos guardados."); save_state(); st.rerun()
    with tab_groups:
        if not st.session_state.as_groups: st.info("Configura primero.")
        else:
            for gl in ["A","B"]:
                teams = st.session_state.as_groups.get(gl,[])
                # ✅ FIX
                with st.expander(f"Grupo {gl}", expanded=True):
                    group_teams_header(teams)
                    gm = {k:v for k,v in st.session_state.as_matches.items() if k[0] in teams and k[1] in teams and v is not None}
                    s = compute_standings(teams,gm)
                    st.session_state.as_standings[gl] = s
                    render_group_section(
                        teams, st.session_state.as_matches,
                        "as", "as_matches", PLAYERS, "as_",
                        s, highlight=2
                    )
            sA = st.session_state.as_standings.get("A",[])
            sB = st.session_state.as_standings.get("B",[])
            if len(sA)>=2 and len(sB)>=2:
                sf1 = (sA[0]["team"],sB[1]["team"]); sf2 = (sB[0]["team"],sA[1]["team"])
                render_match_result(sf1[0],sf1[1],None); render_match_result(sf2[0],sf2[1],None)
                if st.button("➡️ Generar Semis Copa Asia"):
                    save_state()
                    st.session_state.as_sf = [sf1,sf2]; st.session_state.as_sf_results = {}; st.rerun()
    with tab_ko:
        if not st.session_state.as_sf: st.info("Completa grupos primero.")
        else:
            st.markdown("### ⚔️ Semifinales")
            sf_winners = []
            for i,(t1,t2) in enumerate(st.session_state.as_sf):
                res = st.session_state.as_sf_results.get(i)
                if res: render_match_result(t1,t2,res); sf_winners.append(res["winner"])
                else:
                    r = knockout_input(f"as_sf_{i}",t1,t2,PLAYERS.get(t1,[]),PLAYERS.get(t2,[]))
                    if r:
                        st.session_state.as_sf_results[i] = r
                        for s in r.get("scorers_h",[]): update_scorer(s,t1,1,"as_")
                        for s in r.get("scorers_a",[]): update_scorer(s,t2,1,"as_")
                        save_state()
                        st.rerun()
                    sf_winners.append(None)
            if all(sf_winners) and len(sf_winners)==2:
                if st.session_state.as_final is None:
                    st.session_state.as_final = (sf_winners[0],sf_winners[1])
                st.markdown("### 🏆 FINAL")
                t1,t2 = st.session_state.as_final
                res = st.session_state.as_final_result
                if res: render_match_result(t1,t2,res); champ_banner(res["winner"],"CAMPEÓN DE ASIA")
                else:
                    r = knockout_input("as_final",t1,t2,PLAYERS.get(t1,[]),PLAYERS.get(t2,[]))
                    if r:
                        st.session_state.as_final_result = r; champ = r["winner"]
                        st.session_state.as_champion = champ
                        for s in r.get("scorers_h",[]): update_scorer(s,t1,1,"as_")
                        for s in r.get("scorers_a",[]): update_scorer(s,t2,1,"as_")
                        runner = t2 if champ==t1 else t1
                        fs = [{"pos":1,"team":champ},{"pos":2,"team":runner}]
                        pos=3; placed={champ,runner}
                        for i_,(ta,tb) in enumerate(st.session_state.as_sf):
                            res_ = st.session_state.as_sf_results.get(i_)
                            if res_:
                                lsr = tb if res_["winner"]==ta else ta
                                if lsr not in placed: fs.append({"pos":pos,"team":lsr}); pos+=1; placed.add(lsr)
                        for gl,s_ in st.session_state.as_standings.items():
                            for e in s_:
                                if e["team"] not in placed: fs.append({"pos":pos,"team":e["team"]}); pos+=1; placed.add(e["team"])
                        st.session_state.as_final_standings = fs
                        update_ranking_from_standings(fs,60,6)
                        if champ not in st.session_state.wc_qualified: st.session_state.wc_qualified.append(champ)
                        save_state()
                        st.rerun()
    with tab_result:
        if st.session_state.as_champion:
            champ_banner(st.session_state.as_champion,"CAMPEÓN DE ASIA")
            render_standings(st.session_state.as_final_standings, highlight=1)
        else: st.info("Sin resultado aún.")

# ══════════════════════════════════════════════
# AFC PLAYOFFS
# ══════════════════════════════════════════════
elif page == "🔢 Playoffs AFC":
    conf_header("#9B59B6","🔢","AFC · PLAYOFFS",
                "Puestos 2-5 → todos vs todos · Top 3 → Mundial · 4to → Repechaje",
                conf_key="AFC")
    if not st.session_state.as_final_standings:
        st.warning("Completa la Copa Asia primero.")
    else:
        pool = [e["team"] for e in st.session_state.as_final_standings[1:5]]
        html = "<div style='display:flex;flex-wrap:wrap;gap:6px;margin-bottom:16px;'>" + "".join(team_chip(t,"#9B59B6") for t in pool) + "</div>"
        st.markdown(html, unsafe_allow_html=True)
        if not st.session_state.afc_playoff_teams:
            if st.button("▶️ Iniciar playoff AFC"):
                st.session_state.afc_playoff_teams = pool
                st.session_state.afc_playoff_matches = generate_group_matches(pool)
                save_state()
                st.rerun()
        else:
            teams = st.session_state.afc_playoff_teams
            for t1,t2 in combinations(teams,2):
                key = (t1,t2) if (t1,t2) in st.session_state.afc_playoff_matches else (t2,t1)
                res = st.session_state.afc_playoff_matches.get(key)
                render_match_result(t1,t2,res)
                if res is None:
                    r = match_input_form("afcp",t1,t2,PLAYERS.get(t1,[]),PLAYERS.get(t2,[]))
                    if r:
                        hg,ag,sh,sa = r
                        st.session_state.afc_playoff_matches[key] = {"hg":hg,"ag":ag,"scorers_h":sh,"scorers_a":sa}
                        save_state()
                        st.rerun()
            st.divider()
            played = {k:v for k,v in st.session_state.afc_playoff_matches.items() if v is not None}
            standings = compute_standings(teams,played)
            st.session_state.afc_playoff_standings = standings
            render_standings(standings, highlight=3, repechaje_pos=4)
            qualified = [s["team"] for s in standings[:3]]
            repechaje = standings[3]["team"] if len(standings)>3 else None
            if repechaje: st.markdown(f"**🔄 Repechaje:** {fl(repechaje)}{repechaje}", unsafe_allow_html=True)
            if st.button("💾 Confirmar AFC"):
                for t in qualified:
                    if t not in st.session_state.wc_qualified: st.session_state.wc_qualified.append(t)
                st.session_state.afc_playoff_qualified = qualified
                st.session_state.afc_playoff_repechaje = repechaje
                st.success("✅ Confirmados.")

# ══════════════════════════════════════════════
# REPECHAJE INTERNACIONAL
# ══════════════════════════════════════════════
elif page == "🔄 Repechaje":
    conf_header("#FF5722","🔄","REPECHAJE INTERNACIONAL",
                "CONCACAF 3ro vs AFC 4to · CONMEBOL 4to vs Nueva Zelanda")
    cc3 = st.session_state.concacaf_playoff_repechaje
    afc4 = st.session_state.afc_playoff_repechaje
    cm4  = st.session_state.conmebol_playoff_repechaje
    c1,c2,c3 = st.columns(3)
    for col,label,val,color in [
        (c1,"CONCACAF 3ro",cc3,"#E74C3C"),
        (c2,"AFC 4to",afc4,"#9B59B6"),
        (c3,"CONMEBOL 4to",cm4,"#27AE60")
    ]:
        code = FLAG_MAP.get(val, "") if val else ""
        img_tag = f'<img src="https://flagcdn.com/32x24/{code}.png" style="vertical-align:middle;border-radius:2px;margin-bottom:6px;">' if code else ""
        with col:
            st.markdown(f"""
            <div class='card card-acc' style='text-align:center;padding:14px;border-left-color:{color};'>
              <div style='font-size:10px;color:{color};letter-spacing:2px;'>{label}</div>
              {('<div style="margin:6px 0;">'+img_tag+'</div><div style="font-weight:700;font-size:13px;">'+val+'</div>') if val else '<div style="color:var(--muted);font-size:12px;margin-top:8px;">⏳ Pendiente</div>'}
            </div>""", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("#### ✏️ Configuración Manual")
    all_pool = list(dict.fromkeys(ALL_TEAMS + ["New Zealand"]))
    c1,c2,c3 = st.columns(3)
    with c1: m1t1 = st.selectbox("CONCACAF 3ro", all_pool, index=all_pool.index(cc3) if cc3 in all_pool else 0)
    with c2: m1t2 = st.selectbox("AFC 4to", all_pool, index=all_pool.index(afc4) if afc4 in all_pool else 0)
    with c3: m2t1 = st.selectbox("CONMEBOL 4to", all_pool, index=all_pool.index(cm4) if cm4 in all_pool else 0)
    st.markdown("---")
    st.markdown("### ⚽ Partido 1: CONCACAF 3ro vs AFC 4to")
    res1 = st.session_state.int_playoff_match1
    if res1:
        render_match_result(m1t1,m1t2,res1)
        code = FLAG_MAP.get(res1['winner'], "")
        img_tag = f'<img src="https://flagcdn.com/20x15/{code}.png" style="vertical-align:middle;border-radius:2px;margin-right:5px;">' if code else ""
        st.markdown(f"**Clasificado:** {img_tag} **{res1['winner']}**", unsafe_allow_html=True)
    else:
        r = knockout_input("int1",m1t1,m1t2,PLAYERS.get(m1t1,[]),PLAYERS.get(m1t2,[]))
        save_state()
        if r: st.session_state.int_playoff_match1 = r; st.rerun()
    st.markdown("### ⚽ Partido 2: CONMEBOL 4to vs Nueva Zelanda 🇳🇿")
    res2 = st.session_state.int_playoff_match2
    if res2:
        render_match_result(m2t1,"New Zealand",res2)
        code = FLAG_MAP.get(res2['winner'], "")
        img_tag = f'<img src="https://flagcdn.com/20x15/{code}.png" style="vertical-align:middle;border-radius:2px;margin-right:5px;">' if code else ""
        st.markdown(f"**Clasificado:** {img_tag} **{res2['winner']}**", unsafe_allow_html=True)
    else:
        r = knockout_input("int2",m2t1,"New Zealand",PLAYERS.get(m2t1,[]),PLAYERS.get("New Zealand",[]))
        save_state()
        if r: st.session_state.int_playoff_match2 = r; st.rerun()
    if res1 and res2:
        st.divider()
        qualified = [res1["winner"],res2["winner"]]
        html = "<div style='display:flex;gap:8px;flex-wrap:wrap;'>" + "".join(team_chip(t,"#FF5722") for t in qualified) + "</div>"
        st.markdown("#### ✅ Clasificados al Mundial via Repechaje")
        st.markdown(html, unsafe_allow_html=True)
        if st.button("💾 Confirmar repechaje"):
            for t in qualified:
                if t not in st.session_state.wc_qualified: st.session_state.wc_qualified.append(t)
            st.session_state.int_playoff_qualified = qualified
            st.success("✅ Clasificados confirmados.")

# ══════════════════════════════════════════════
# MUNDIAL
# ══════════════════════════════════════════════
elif page == "🏆 Mundial":
    conf_header("#FFD700","🌐","COPA DEL MUNDO","32 equipos · 8 grupos · Modelo FIFA oficial",
                conf_key="FIFA")
    tab_config,tab_groups,tab_ko,tab_result = st.tabs(["⚙️ Config","📊 Grupos","⚔️ Eliminatorias","🏆 Resultado"])
    with tab_config:
        st.markdown(f"**Clasificados: {len(st.session_state.wc_qualified)}/32**")
        if st.session_state.wc_qualified:
            html = "<div style=\'display:flex;flex-wrap:wrap;gap:6px;\'>" + "".join(team_chip(t,"#FFD700") for t in st.session_state.wc_qualified) + "</div>"
            st.markdown(html, unsafe_allow_html=True)
        st.markdown("---")
        host = st.selectbox("🏟️ País Anfitrión", ALL_TEAMS + ["New Zealand"],
                            index=ALL_TEAMS.index(st.session_state.wc_host) if st.session_state.wc_host in ALL_TEAMS else 0)
        st.markdown("---")
        st.markdown("#### Arma los 8 grupos (4 equipos c/u)")
        pool32 = list(dict.fromkeys(st.session_state.wc_qualified + [host]))[:32]
        if len(pool32)<32:
            for t in ALL_TEAMS+["New Zealand"]:
                if t not in pool32 and len(pool32)<32: pool32.append(t)
        st.markdown("**2️⃣ Arrastra los equipos a cada grupo (4 por grupo):**")
        dnd_result = drag_drop_groups(
            pool32, ["A","B","C","D","E","F","G","H"], 4,
            st.session_state.wc_groups, "wc", "#FFD700"
        )
        st.markdown("---")
        if st.button("💾 Guardar grupos del Mundial"):
            g2s = dnd_result or st.session_state.wc_groups
            all_a = sum(g2s.values(),[])
            if len(all_a)!=len(set(all_a)): st.error("Duplicados.")
            elif any(len(v)!=4 for v in g2s.values()): st.error("4 por grupo.")
            else:
                st.session_state.wc_host = host
                st.session_state.wc_groups = g2s
                all_m = {}
                for gl,teams in g2s.items(): all_m.update(generate_group_matches(teams))
                st.session_state.wc_matches = all_m
                save_state()
                st.success("✅ Grupos del Mundial guardados."); st.rerun()
    with tab_groups:
        if not st.session_state.wc_groups: st.info("Configura los grupos primero.")
        else:
            for gl in ["A","B","C","D","E","F","G","H"]:
                teams = st.session_state.wc_groups.get(gl,[])
                if not teams: continue
                # ✅ FIX
                with st.expander(f"Grupo {gl}", expanded=False):
                    group_teams_header(teams)
                    gm = {k:v for k,v in st.session_state.wc_matches.items() if k[0] in teams and k[1] in teams and v is not None}
                    s = compute_standings(teams,gm)
                    st.session_state.wc_standings[gl] = s
                    render_group_section(
                        teams, st.session_state.wc_matches,
                        "wc", "wc_matches", PLAYERS, "wc_",
                        s, highlight=2
                    )
            st.divider()
            by_slot = {}
            for gl in ["A","B","C","D","E","F","G","H"]:
                s = st.session_state.wc_standings.get(gl,[])
                if len(s)>=2:
                    by_slot[f"{gl}1"] = s[0]["team"]; by_slot[f"{gl}2"] = s[1]["team"]
            if len(by_slot)==16:
                wc_r16 = [
                    (by_slot.get("A1","?"),by_slot.get("B2","?")),
                    (by_slot.get("C1","?"),by_slot.get("D2","?")),
                    (by_slot.get("E1","?"),by_slot.get("F2","?")),
                    (by_slot.get("G1","?"),by_slot.get("H2","?")),
                    (by_slot.get("B1","?"),by_slot.get("A2","?")),
                    (by_slot.get("D1","?"),by_slot.get("C2","?")),
                    (by_slot.get("F1","?"),by_slot.get("E2","?")),
                    (by_slot.get("H1","?"),by_slot.get("G2","?")),
                ]
                st.markdown("#### Bracket R16 (Modelo FIFA)")
                cols = st.columns(4)
                for i,(t1,t2) in enumerate(wc_r16):
                    code1 = FLAG_MAP.get(t1,""); code2 = FLAG_MAP.get(t2,"")
                    img1 = f'<img src="https://flagcdn.com/20x15/{code1}.png" style="vertical-align:middle;border-radius:2px;margin-right:4px;">' if code1 else ""
                    img2 = f'<img src="https://flagcdn.com/20x15/{code2}.png" style="vertical-align:middle;border-radius:2px;margin-right:4px;">' if code2 else ""
                    with cols[i%4]:
                        st.markdown(
                            f"<div class='card' style='text-align:center;padding:10px;font-size:12px;'>"
                            f"{img1} {t1}<br><span style='color:var(--muted);'>vs</span><br>"
                            f"{img2} {t2}</div>", unsafe_allow_html=True)
                if st.button("➡️ Generar R16 del Mundial"):
                    st.session_state.wc_r16 = wc_r16; st.session_state.wc_r16_results = {}
                    st.success("✅ R16 generado."); save_state(); st.rerun()
    with tab_ko:
        if not st.session_state.wc_r16: st.info("Completa los grupos y genera el R16 primero.")
        else:
            st.markdown("### ⚔️ Octavos de Final")
            r16w = []
            for i,(t1,t2) in enumerate(st.session_state.wc_r16):
                res = st.session_state.wc_r16_results.get(i)
                if res: render_match_result(t1,t2,res); r16w.append(res["winner"])
                else:
                    r = knockout_input(f"wc_r16_{i}",t1,t2,PLAYERS.get(t1,[]),PLAYERS.get(t2,[]))
                    if r:
                        st.session_state.wc_r16_results[i] = r
                        for s in r.get("scorers_h",[]): update_scorer(s,t1,1,"wc_")
                        for s in r.get("scorers_a",[]): update_scorer(s,t2,1,"wc_")
                        save_state()
                        st.rerun()
                    r16w.append(None)
            if all(r16w) and len(r16w)==8:
                if not st.session_state.wc_qf:
                    st.session_state.wc_qf = [
                        (r16w[0],r16w[4]),(r16w[2],r16w[6]),
                        (r16w[1],r16w[5]),(r16w[3],r16w[7]),
                    ]
                st.markdown("### ⚔️ Cuartos de Final")
                qfw = []
                for i,(t1,t2) in enumerate(st.session_state.wc_qf):
                    res = st.session_state.wc_qf_results.get(i)
                    if res: render_match_result(t1,t2,res); qfw.append(res["winner"])
                    else:
                        r = knockout_input(f"wc_qf_{i}",t1,t2,PLAYERS.get(t1,[]),PLAYERS.get(t2,[]))
                        if r:
                            st.session_state.wc_qf_results[i] = r
                            for s in r.get("scorers_h",[]): update_scorer(s,t1,1,"wc_")
                            for s in r.get("scorers_a",[]): update_scorer(s,t2,1,"wc_")
                            save_state()
                            st.rerun()
                        qfw.append(None)
                if all(qfw) and len(qfw)==4:
                    if not st.session_state.wc_sf:
                        st.session_state.wc_sf = [(qfw[0],qfw[1]),(qfw[2],qfw[3])]
                    st.markdown("### ⚔️ Semifinales")
                    sfw = []; sfl = []
                    for i,(t1,t2) in enumerate(st.session_state.wc_sf):
                        res = st.session_state.wc_sf_results.get(i)
                        if res:
                            render_match_result(t1,t2,res)
                            sfw.append(res["winner"]); sfl.append(t2 if res["winner"]==t1 else t1)
                        else:
                            r = knockout_input(f"wc_sf_{i}",t1,t2,PLAYERS.get(t1,[]),PLAYERS.get(t2,[]))
                            if r:
                                st.session_state.wc_sf_results[i] = r
                                for s in r.get("scorers_h",[]): update_scorer(s,t1,1,"wc_")
                                for s in r.get("scorers_a",[]): update_scorer(s,t2,1,"wc_")
                                save_state()
                                st.rerun()
                            sfw.append(None)
                    if all(sfw) and len(sfw)==2:
                        if len(sfl)==2:
                            st.markdown("### 🥉 Tercer Puesto")
                            t3a,t3b = sfl[0],sfl[1]
                            res3 = st.session_state.wc_third_result
                            if res3:
                                render_match_result(t3a,t3b,res3)
                                code = FLAG_MAP.get(res3['winner'],"")
                                img_tag = f'<img src="https://flagcdn.com/20x15/{code}.png" style="vertical-align:middle;border-radius:2px;margin-right:5px;">' if code else ""
                                st.markdown(f"🥉 **{img_tag} {res3['winner']}**", unsafe_allow_html=True)
                            else:
                                r = knockout_input("wc_3rd",t3a,t3b,PLAYERS.get(t3a,[]),PLAYERS.get(t3b,[]))
                                if r:
                                    st.session_state.wc_third = (t3a,t3b)
                                    save_state()
                                    st.session_state.wc_third_result = r; st.rerun()
                        st.markdown("### 🏆 FINAL MUNDIAL")
                        if st.session_state.wc_final is None:
                            st.session_state.wc_final = (sfw[0],sfw[1])
                        t1,t2 = st.session_state.wc_final
                        resf = st.session_state.wc_final_result
                        if resf:
                            render_match_result(t1,t2,resf)
                            champ_banner(resf["winner"],"🌍 CAMPEÓN DEL MUNDO")
                        else:
                            r = knockout_input("wc_final",t1,t2,PLAYERS.get(t1,[]),PLAYERS.get(t2,[]))
                            if r:
                                st.session_state.wc_final_result = r; champ = r["winner"]
                                st.session_state.wc_champion = champ
                                for s in r.get("scorers_h",[]): update_scorer(s,t1,1,"wc_")
                                for s in r.get("scorers_a",[]): update_scorer(s,t2,1,"wc_")
                                runner = t2 if champ==t1 else t1
                                update_ranking_from_standings([{"pos":1,"team":champ},{"pos":2,"team":runner}],200,10)
                                save_state()
                                st.rerun()
    with tab_result:
        if st.session_state.wc_champion:
            champ_banner(st.session_state.wc_champion,"🌍 CAMPEÓN DEL MUNDO")
            if st.session_state.wc_final_result:
                t1,t2 = st.session_state.wc_final; r = st.session_state.wc_final_result
                render_match_result(t1,t2,r)
        else:
            st.info("El Mundial aún no tiene campeón.")

# ══════════════════════════════════════════════
# RANKING FIFA
# ══════════════════════════════════════════════
elif page == "📊 Ranking FIFA":
    conf_header("#00E5A0","📊","RANKING FIFA","Se actualiza con cada torneo · Persiste entre temporadas",
                conf_key="FIFA")
    ranking = st.session_state.fifa_ranking
    sorted_r = sorted(ranking.items(), key=lambda x:x[1], reverse=True)

    c1,c2,c3 = st.columns(3)
    for col,(team,pts),medal in zip([c1,c2,c3],sorted_r[:3],["🥇","🥈","🥉"]):
        code = FLAG_MAP.get(team, "")
        img_tag = f'<img src="https://flagcdn.com/40x30/{code}.png" style="border-radius:3px;margin:8px 0;">' if code else ""
        with col:
            st.markdown(f"""
            <div class='card card-gold' style='text-align:center;padding:20px;'>
              <div style='font-size:28px;'>{medal}</div>
              <div style='margin:8px 0;'>{img_tag}</div>
              <div style='font-family:Bebas Neue;font-size:20px;letter-spacing:2px;'>{team}</div>
              <div style='color:var(--g);font-size:22px;font-weight:700;'>{pts}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    conf_teams = {"UEFA":UEFA_TEAMS,"CONMEBOL":CONMEBOL_TEAMS,"CAF":CAF_TEAMS,"CONCACAF":CONCACAF_TEAMS,"AFC":AFC_TEAMS}
    filt = st.selectbox("Filtrar por confederación", ["Todas","UEFA","CONMEBOL","CAF","CONCACAF","AFC"])
    rows = []
    for pos,(t,pts) in enumerate(sorted_r,1):
        if filt!="Todas" and t not in conf_teams.get(filt,[]): continue
        conf = "—"
        for c_,tl in conf_teams.items():
            if t in tl: conf=c_; break
        code = FLAG_MAP.get(t, "")
        flag_html = (
            f'<img src="https://flagcdn.com/20x15/{code}.png" '
            f'style="vertical-align:middle;border-radius:2px;margin-right:6px;">' if code else ""
        )
        rows.append({
            "Pos":    str(pos),
            "Equipo": flag_html + t,
            "Conf":   conf,
            "Puntos": str(pts),
        })
    html_table(rows)

    if st.button("🔄 Resetear ranking inicial"):
        save_state()
        st.session_state.fifa_ranking = dict(INITIAL_FIFA_RANKING); st.success("✅ Reseteado."); st.rerun()

# ══════════════════════════════════════════════
# GOLEADORES
# ══════════════════════════════════════════════
elif page == "⚽ Goleadores":
    conf_header("#FF5722","⚽","TABLA DE GOLEADORES","Registrados durante todos los torneos")
    scorers = st.session_state.top_scorers
    if not scorers:
        st.info("No hay goles registrados aún.")
    else:
        TOUR_PREFIX = {
            "euro_":"🌍 Eurocopa","ca_":"🌎 Copa América",
            "af_":"🌍 Copa África","co_":"🌎 Copa Oro",
            "as_":"🌏 Copa Asia","wc_":"🏆 Mundial",
        }
        filt_tour = st.selectbox("Torneo",["Todos"]+list(TOUR_PREFIX.values()))
        rows = []
        for key,goals in sorted(scorers.items(), key=lambda x:x[1], reverse=True):
            parts = key.split("|")
            if len(parts)!=2: continue
            raw_key,team = parts[0],parts[1]
            tour="—"; player=raw_key
            for pref,name in TOUR_PREFIX.items():
                if raw_key.startswith(pref): tour=name; player=raw_key[len(pref):]; break
            if filt_tour!="Todos" and tour!=filt_tour: continue
            code = FLAG_MAP.get(team, "")
            flag_html = f'<img src="https://flagcdn.com/20x15/{code}.png" style="vertical-align:middle;border-radius:2px;margin-right:6px;">' if code else ""
            rows.append({"⚽":goals,"Jugador":player,"Selección":f"{flag_html}{team}","Torneo":tour})
        if rows:
            rows_final = []
            for i, r in enumerate(rows):
                rows_final.append({
                    "Pos":      str(i + 1),
                    "⚽":       str(r["⚽"]),
                    "Jugador":  r["Jugador"],
                    "Selección": r["Selección"],
                    "Torneo":   r["Torneo"],
                })
            html_table(rows_final)

# ══════════════════════════════════════════════
# PLANTILLAS
# ══════════════════════════════════════════════
elif page == "👥 Plantillas":
    conf_header("#00E5A0","👥","PLANTILLAS","Jugadores por selección")
    conf_opts = {
        "🌍 UEFA":      UEFA_TEAMS,
        "🌎 CONMEBOL":  CONMEBOL_TEAMS,
        "🌍 CAF":       CAF_TEAMS,
        "🌎 CONCACAF":  CONCACAF_TEAMS,
        "🌏 AFC":       AFC_TEAMS,
        "🔄 Repechaje": ["New Zealand"],
    }
    c1,c2 = st.columns([1,2])
    with c1: conf_sel = st.selectbox("Confederación", list(conf_opts.keys()))
    with c2: team_sel = st.selectbox("Selección", conf_opts[conf_sel])
    players = PLAYERS.get(team_sel, [])
    total = len(players)
    pos_counts = {}
    for p in players: pos_counts[p["pos"]] = pos_counts.get(p["pos"],0)+1
    ranking_pts = st.session_state.fifa_ranking.get(team_sel,"—")
    code = FLAG_MAP.get(team_sel, "")
    big_flag = f'<img src="https://flagcdn.com/80x60/{code}.png" style="border-radius:4px;">' if code else ""
    POS_ICON = {"GK":"🧤","DF":"🛡️","MF":"⚡","FW":"🔥"}
    ps_html = ""
    for pos_key in ["GK","DF","MF","FW"]:
        c_ = POS_COLOR.get(pos_key,"#aaa")
        ps_html += (f'<div style="text-align:center;">'
                    f'<div style="color:{c_};font-family:Bebas Neue;font-size:24px;">{pos_counts.get(pos_key,0)}</div>'
                    f'<div style="font-size:10px;color:var(--muted);letter-spacing:2px;">{pos_key}</div></div>')
    st.markdown(f"""
    <div style='background:var(--card);border:1px solid var(--border);border-radius:14px;padding:22px 26px;margin-bottom:20px;display:flex;align-items:center;gap:20px;'>
      <div>{big_flag}</div>
      <div style='flex:1;'>
        <div style='font-family:Bebas Neue;font-size:32px;letter-spacing:4px;'>{team_sel}</div>
        <div style='color:var(--muted);font-size:12px;letter-spacing:2px;margin-top:2px;'>FIFA RANKING — {ranking_pts} PTS</div>
        <div style='display:flex;gap:20px;margin-top:12px;'>
          <div style='text-align:center;'>
            <div style='color:var(--g);font-family:Bebas Neue;font-size:24px;'>{total}</div>
            <div style='font-size:10px;color:var(--muted);letter-spacing:2px;'>JUGADORES</div>
          </div>
          {ps_html}
        </div>
      </div>
    </div>""", unsafe_allow_html=True)
    if not players:
        st.info("Sin datos de jugadores para esta selección.")
    else:
        pos_filt = st.radio("Filtrar", ["Todos","GK","DF","MF","FW"], horizontal=True)
        filtered = [p for p in players if pos_filt=="Todos" or p["pos"]==pos_filt]
        POS_LABEL = {"GK":"PORTEROS","DF":"DEFENSAS","MF":"CENTROCAMPISTAS","FW":"DELANTEROS"}
        if pos_filt=="Todos":
            for grp_pos in ["GK","DF","MF","FW"]:
                grp = [p for p in players if p["pos"]==grp_pos]
                if not grp: continue
                gc = POS_COLOR.get(grp_pos,"#aaa")
                icon = POS_ICON.get(grp_pos,"")
                st.markdown(f"<div style='font-family:Bebas Neue;font-size:16px;letter-spacing:4px;color:{gc};margin:16px 0 8px;border-bottom:1px solid var(--border);padding-bottom:4px;'>{icon} {POS_LABEL.get(grp_pos,grp_pos)} <span style='font-size:12px;opacity:.5;'>({len(grp)})</span></div>", unsafe_allow_html=True)
                html = "<div class='player-grid'>"
                for p in grp:
                    html += (f"<div class='player-card pos-{p['pos']}-card'>"
                             f"<div class='pos-badge pos-{p['pos']}'>{p['pos']}</div>"
                             f"<div class='pname'>{p['name']}</div></div>")
                html += "</div>"
                st.markdown(html, unsafe_allow_html=True)
        else:
            html = "<div class='player-grid'>"
            for p in filtered:
                html += (f"<div class='player-card pos-{p['pos']}-card'>"
                         f"<div class='pos-badge pos-{p['pos']}'>{p['pos']}</div>"
                         f"<div class='pname'>{p['name']}</div></div>")
            html += "</div>"
            st.markdown(html, unsafe_allow_html=True)
