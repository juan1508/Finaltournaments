# MMJ Tournament Hub ⚽

App de gestión para los torneos MMJ Soccer League Season 2025.

## Torneos incluidos

### 🏟️ MMJ Papa Johns Leagues Cup
- **30 equipos** divididos en **5 zonas**
- Phase Zone: Grupos + Zona Final en West, Midwest y South Zone; Round Robin en North y Canadian Zone
- Phase Final: Cuartos de final → Semifinales → Gran Final
- Registro de goleadores y estadísticas completas

### 🥤 MMJ Cisco Super Cup
- Partido único: Campeón Streamlit League vs Campeón Emirates Cup
- Registro de goleadores

### 🍔 MMJ McDonald's Community Cup
- Semifinal A: Campeón Streamlit League vs Último lugar de la Liga
- Semifinal B: Campeón Papa Johns Leagues Cup vs Campeón Emirates Cup
- Gran Final entre los ganadores de ambas semifinales

## Instalación y ejecución

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Características
- Persistencia de datos en `tournament_data.json`
- Tablas de posiciones con puntos, goles, diferencia de gol
- Registro de goleadores con nombre, equipo y minuto
- Bracket visual de la Phase Final
- Diseño oscuro con estética deportiva profesional
