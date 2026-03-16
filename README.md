# 🌍 FMMJ World Cup Simulator

Simulador completo del Mundial FMMJ con torneos clasificatorios por confederación.

## 🏆 Torneos incluidos

| Torneo | Confederación | Equipos | Cupos al Mundial |
|--------|--------------|---------|-----------------|
| Eurocopa | UEFA | 24 | 13 |
| Copa América | CONMEBOL + 6 invitadas | 16 | 4 |
| Copa África | CAF | 10 | 5 |
| Copa Oro | CONCACAF | 6 | 3 |
| Copa Asia | AFC | 6 | 4 |
| Repechaje | Inter-confederaciones | 4 | 2 |
| **FMMJ World Cup** | **Mundial** | **32** | **🏆** |

## 🚀 Cómo ejecutar

```bash
pip install -r requirements.txt
streamlit run app.py
```

## ☁️ Deploy en Streamlit Cloud

1. Fork/sube este repositorio a GitHub
2. Ve a [share.streamlit.io](https://share.streamlit.io)
3. Conecta tu repo y selecciona `app.py`
4. ¡Listo! La app se despliega automáticamente

## 📁 Estructura del proyecto

```
fmmj_worldcup/
├── app.py              # Aplicación principal
├── data.py             # Base de datos (equipos, ranking, jugadores)
├── state.py            # Gestión del estado global
├── requirements.txt    # Dependencias
├── .streamlit/
│   └── config.toml     # Tema oscuro
├── pages/
│   ├── eurocopa.py     # Eurocopa UEFA
│   ├── copa_america.py # Copa América CONMEBOL
│   ├── confederaciones.py # CAF, CONCACAF, AFC
│   └── repechaje.py    # Repechaje + Ranking + Mundial
└── utils/
    └── tournament.py   # Lógica compartida
```

## 🎮 Cómo usar

1. **Selecciona el anfitrión** en Configuración (Nigeria por defecto)
2. **Simula la Eurocopa**: sorteo → grupos → llaves → playoff UEFA
3. **Simula la Copa América**: elige 6 invitadas → grupos → llaves → playoff
4. **Simula Copa África, Copa Oro, Copa Asia**
5. **Juega el Repechaje Internacional** (ida y vuelta)
6. **Realiza el Sorteo del Mundial** con los 32 clasificados
7. **Juega el Mundial**: grupos → octavos → cuartos → semis → ¡FINAL! 🏆

## 📊 Sistema de clasificación

- **Nigeria** 🇳🇬 clasifica directamente como **Anfitrión**
- Si Nigeria gana la Copa África, su cupo lo toma el siguiente clasificado
- El Ranking FMMJ se actualiza con puntos de cada torneo
- Los bombos del Mundial se forman según el ranking final

