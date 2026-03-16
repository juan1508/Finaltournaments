"""
app.py - FMMJ World Cup Simulator — archivo único, sin imports externos propios
"""
import streamlit as st
import sys
import os
import random
import copy
import json

# ============================================================
# DATA
# ============================================================
# ---------------------------------------------------------------------------
# LISTAS DE EQUIPOS POR CONFEDERACIÓN
# ---------------------------------------------------------------------------
UEFA_TEAMS = [
    "Switzerland", "Denmark", "Poland", "Austria", "Croatia",
    "Sweden", "Serbia", "Wales", "Scotland", "Belgium",
    "Ukraine", "Czech Republic", "Iceland", "Greece", "Turkey",
    "Norway", "Netherlands", "France", "Spain", "Portugal",
    "Italy", "England", "Germany", "Hungary"
]

CONMEBOL_TEAMS = [
    "Brazil", "Argentina", "Colombia", "Chile", "Peru",
    "Uruguay", "Venezuela", "Bolivia", "Paraguay", "Ecuador",
]

CAF_TEAMS = [
    "South Africa", "Morocco", "Tunisia", "Ghana", "Senegal",
    "Egypt", "Ivory Coast", "Cameroon", "Nigeria", "Algeria",
]

CONCACAF_TEAMS = ["Mexico", "Panama", "Costa Rica", "USA", "Canada", "Jamaica"]
AFC_TEAMS = ["Korea", "Saudi Arabia", "Japan", "Australia", "Israel", "Qatar"]
PLAYOFF_TEAMS = ["New Zealand"]

ALL_TEAMS = UEFA_TEAMS + CONMEBOL_TEAMS + CAF_TEAMS + CONCACAF_TEAMS + AFC_TEAMS + PLAYOFF_TEAMS
COPA_AMERICA_GUESTS_POOL = CONCACAF_TEAMS + AFC_TEAMS + CAF_TEAMS + PLAYOFF_TEAMS

CONFEDERATIONS = {
    "UEFA": UEFA_TEAMS,
    "CONMEBOL": CONMEBOL_TEAMS,
    "CAF": CAF_TEAMS,
    "CONCACAF": CONCACAF_TEAMS,
    "AFC": AFC_TEAMS,
    "OFC": PLAYOFF_TEAMS,
}

# ---------------------------------------------------------------------------
# FLAG_MAP
# ---------------------------------------------------------------------------
FLAG_MAP = {
    "Switzerland": "ch", "Denmark": "dk", "Poland": "pl", "Austria": "at",
    "Croatia": "hr", "Sweden": "se", "Serbia": "rs", "Wales": "gb-wls",
    "Scotland": "gb-sct", "Belgium": "be", "Ukraine": "ua",
    "Czech Republic": "cz", "Iceland": "is", "Greece": "gr", "Turkey": "tr",
    "Norway": "no", "Netherlands": "nl", "France": "fr", "Spain": "es",
    "Portugal": "pt", "Italy": "it", "England": "gb-eng", "Germany": "de",
    "Hungary": "hu", "Israel": "il",
    "Brazil": "br", "Argentina": "ar", "Colombia": "co", "Chile": "cl",
    "Peru": "pe", "Uruguay": "uy", "Venezuela": "ve", "Bolivia": "bo",
    "Paraguay": "py", "Ecuador": "ec",
    "South Africa": "za", "Morocco": "ma", "Tunisia": "tn", "Ghana": "gh",
    "Senegal": "sn", "Egypt": "eg", "Ivory Coast": "ci", "Cameroon": "cm",
    "Nigeria": "ng", "Algeria": "dz",
    "Mexico": "mx", "Panama": "pa", "Costa Rica": "cr", "USA": "us",
    "Canada": "ca", "Jamaica": "jm",
    "Korea": "kr", "Saudi Arabia": "sa", "Japan": "jp", "Australia": "au",
    "Qatar": "qa",
    "New Zealand": "nz",
}

COUNTRY_CODES = FLAG_MAP

# ---------------------------------------------------------------------------
# LOGOS DE CONFEDERACIONES
# ---------------------------------------------------------------------------
CONF_LOGOS = {
    "UEFA":     "uefa.png",
    "CONMEBOL": "conmebol.png",
    "CAF":      "caf.png",
    "CONCACAF": "concacaf.png",
    "AFC":      "afc.png",
    "FIFA":     "fmmj.png",
    "FMMJ":     "fmmj.png",
}

def get_flag_url(country_name, width=20, height=15):
    code = FLAG_MAP.get(country_name, "")
    if code:
        return f"https://flagcdn.com/{width}x{height}/{code}.png"
    return ""

# ---------------------------------------------------------------------------
# RANKING INICIAL FIFA FMMJ
# ---------------------------------------------------------------------------
INITIAL_FIFA_RANKING = {
    "France": 1840, "Spain": 1810, "England": 1780, "Germany": 1750,
    "Portugal": 1720, "Italy": 1690, "Netherlands": 1650, "Belgium": 1620,
    "Croatia": 1580, "Denmark": 1560, "Switzerland": 1530, "Norway": 1480,
    "Austria": 1450, "Sweden": 1420, "Poland": 1390, "Serbia": 1360,
    "Turkey": 1330, "Ukraine": 1310, "Czech Republic": 1280, "Greece": 1250,
    "Scotland": 1220, "Wales": 1200, "Hungary": 1180, "Iceland": 1150,
    "Israel": 1200,
    "Argentina": 1870, "Brazil": 1830, "Colombia": 1650, "Uruguay": 1620,
    "Chile": 1540, "Ecuador": 1510, "Paraguay": 1430, "Peru": 1380,
    "Bolivia": 1250, "Venezuela": 1230,
    "Senegal": 1630, "Morocco": 1600, "Tunisia": 1530, "Ghana": 1480,
    "Egypt": 1450, "Ivory Coast": 1440, "Nigeria": 1420, "Cameroon": 1390,
    "Algeria": 1350, "South Africa": 1330,
    "Mexico": 1550, "USA": 1530, "Canada": 1490, "Costa Rica": 1380,
    "Panama": 1360, "Jamaica": 1280,
    "Japan": 1560, "Korea": 1530, "Australia": 1470, "Saudi Arabia": 1420,
    "Qatar": 1370, "New Zealand": 1100,
}

# ---------------------------------------------------------------------------
# NOMBRES PARA MOSTRAR EN ESPAÑOL
# ---------------------------------------------------------------------------
TEAM_DISPLAY_NAMES = {
    "Switzerland": "Suiza", "Denmark": "Dinamarca", "Poland": "Polonia",
    "Austria": "Austria", "Croatia": "Croacia", "Sweden": "Suecia",
    "Serbia": "Serbia", "Wales": "Gales", "Scotland": "Escocia",
    "Belgium": "Bélgica", "Ukraine": "Ucrania", "Czech Republic": "Rep. Checa",
    "Iceland": "Islandia", "Greece": "Grecia", "Turkey": "Turquía",
    "Norway": "Noruega", "Netherlands": "Países Bajos", "France": "Francia",
    "Spain": "España", "Portugal": "Portugal", "Italy": "Italia",
    "England": "Inglaterra", "Germany": "Alemania", "Hungary": "Hungría",
    "Israel": "Israel",
    "Brazil": "Brasil", "Argentina": "Argentina", "Colombia": "Colombia",
    "Chile": "Chile", "Peru": "Perú", "Uruguay": "Uruguay",
    "Venezuela": "Venezuela", "Bolivia": "Bolivia", "Paraguay": "Paraguay",
    "Ecuador": "Ecuador",
    "South Africa": "Sudáfrica", "Morocco": "Marruecos", "Tunisia": "Túnez",
    "Ghana": "Ghana", "Senegal": "Senegal", "Egypt": "Egipto",
    "Ivory Coast": "Costa de Marfil", "Cameroon": "Camerún", "Nigeria": "Nigeria",
    "Algeria": "Argelia",
    "Mexico": "México", "Panama": "Panamá", "Costa Rica": "Costa Rica",
    "USA": "Estados Unidos", "Canada": "Canadá", "Jamaica": "Jamaica",
    "Korea": "Corea del Sur", "Saudi Arabia": "Arabia Saudita", "Japan": "Japón",
    "Australia": "Australia", "Israel": "Israel", "Qatar": "Catar",
    "New Zealand": "Nueva Zelanda",
}

# ---------------------------------------------------------------------------
# JUGADORES
# ---------------------------------------------------------------------------
PLAYERS = {
    "Ukraine": [
        {"name": "V. Tsygankov", "pos": "MF"}, {"name": "O. Zinchenko", "pos": "DF"},
        {"name": "R. Malinovskyi", "pos": "MF"}, {"name": "T. Stepanenko", "pos": "MF"},
        {"name": "Y. Rakitskyi", "pos": "DF"}, {"name": "M. Shaparenko", "pos": "MF"},
        {"name": "A. Lunin", "pos": "GK"}, {"name": "V. Buyalskyi", "pos": "MF"},
        {"name": "M. Matviienko", "pos": "DF"}, {"name": "M. Mudryk", "pos": "FW"},
    ],
    "Czech Republic": [
        {"name": "P. Schick", "pos": "FW"}, {"name": "T. Soucek", "pos": "MF"},
        {"name": "A. Barak", "pos": "MF"}, {"name": "V. Coufal", "pos": "DF"},
        {"name": "A. Hložek", "pos": "FW"}, {"name": "T. Holes", "pos": "MF"},
        {"name": "L. Krejčí", "pos": "DF"}, {"name": "J. Pavlenka", "pos": "GK"},
        {"name": "V. Černý", "pos": "FW"}, {"name": "M. Jurásek", "pos": "DF"},
    ],
    "Iceland": [
        {"name": "S. Ingason", "pos": "DF"}, {"name": "A. Guðmundsson", "pos": "MF"},
        {"name": "H. Magnússon", "pos": "DF"}, {"name": "J. Guðmundsson", "pos": "MF"},
        {"name": "R. Rúnarsson", "pos": "GK"}, {"name": "A. Sigurðsson", "pos": "MF"},
        {"name": "J. Þorsteinsson", "pos": "MF"}, {"name": "M. Anderson", "pos": "MF"},
        {"name": "H. Haraldsson", "pos": "MF"}, {"name": "K. Hlynsson", "pos": "MF"},
    ],
    "Greece": [
        {"name": "O. Vlachodimos", "pos": "GK"}, {"name": "K. Mavropanos", "pos": "DF"},
        {"name": "V. Pavlidis", "pos": "FW"}, {"name": "K. Tsimikas", "pos": "DF"},
        {"name": "A. Bakasetas", "pos": "MF"}, {"name": "P. Mantalos", "pos": "MF"},
        {"name": "T. Fountas", "pos": "FW"}, {"name": "T. Douvikas", "pos": "FW"},
        {"name": "G. Giakoumakis", "pos": "FW"}, {"name": "G. Koutsias", "pos": "FW"},
    ],
    "Turkey": [
        {"name": "H. Çalhanoğlu", "pos": "MF"}, {"name": "O. Kökçü", "pos": "MF"},
        {"name": "E. Ünal", "pos": "FW"}, {"name": "U. Çakır", "pos": "GK"},
        {"name": "S. Özcan", "pos": "MF"}, {"name": "C. Ünder", "pos": "MF"},
        {"name": "K.Aktürkoğlu", "pos": "FW"}, {"name": "A. Bardakçı", "pos": "DF"},
        {"name": "M. Demiral", "pos": "DF"}, {"name": "A. Güler", "pos": "MF"},
    ],
    "Brazil": [
        {"name": "Neymar Jr", "pos": "FW"}, {"name": "Vini Jr.", "pos": "FW"},
        {"name": "Casemiro", "pos": "MF"}, {"name": "Allison", "pos": "GK"},
        {"name": "Thiago Silva", "pos": "DF"}, {"name": "Marquinhos", "pos": "DF"},
        {"name": "Gabriel Jesús", "pos": "FW"}, {"name": "Gabriel Martinelli", "pos": "FW"},
        {"name": "Rodrygo", "pos": "FW"}, {"name": "Matheus Martins", "pos": "FW"},
    ],
    "Ecuador": [
        {"name": "M. Caicedo", "pos": "MF"}, {"name": "A. Obando", "pos": "MF"},
        {"name": "P. Estupiñán", "pos": "DF"}, {"name": "P. Hincapié", "pos": "DF"},
        {"name": "A. Alvarado", "pos": "GK"}, {"name": "J. Sornoza", "pos": "MF"},
        {"name": "D. Díaz", "pos": "FW"}, {"name": "C. Ramírez", "pos": "MF"},
        {"name": "M. Ramírez", "pos": "FW"}, {"name": "K. Páez", "pos": "MF"},
    ],
    "Paraguay": [
        {"name": "M. Almirón", "pos": "MF"}, {"name": "Kaku", "pos": "MF"},
        {"name": "A. Sanabria", "pos": "FW"}, {"name": "O. Alderete", "pos": "DF"},
        {"name": "G. Ávalos", "pos": "MF"}, {"name": "D. González", "pos": "MF"},
        {"name": "A. Bareiro", "pos": "FW"}, {"name": "A. Cubas", "pos": "MF"},
        {"name": "J. Espínola", "pos": "MF"}, {"name": "J. Enciso", "pos": "MF"},
    ],
    "Mexico": [
        {"name": "G. Ochoa", "pos": "GK"}, {"name": "H. Lozano", "pos": "FW"},
        {"name": "S. Giménez", "pos": "FW"}, {"name": "R. Jiménez", "pos": "FW"},
        {"name": "E. Álvarez", "pos": "MF"}, {"name": "E. Sánchez", "pos": "DF"},
        {"name": "H. Herrera", "pos": "MF"}, {"name": "L. Chávez", "pos": "MF"},
        {"name": "C. Montes", "pos": "DF"}, {"name": "J. Quiñones", "pos": "FW"},
    ],
    "Panama": [
        {"name": "A. Murillo", "pos": "DF"}, {"name": "A. Godoy", "pos": "MF"},
        {"name": "A. Carrasquilla", "pos": "MF"}, {"name": "A. Andrade", "pos": "DF"},
        {"name": "I. Díaz", "pos": "FW"}, {"name": "J. Rodríguez", "pos": "MF"},
        {"name": "C. Waterman", "pos": "FW"}, {"name": "L. Mejía", "pos": "DF"},
        {"name": "J. Fajardo", "pos": "FW"}, {"name": "E. Zorrilla", "pos": "MF"},
    ],
    "Italy": [
        {"name": "G. Donnarumma", "pos": "GK"}, {"name": "L. Pellegrini", "pos": "MF"},
        {"name": "F. Dimarco", "pos": "DF"}, {"name": "N. Barella", "pos": "MF"},
        {"name": "G. Di Lorenzo", "pos": "DF"}, {"name": "F. Chiesa", "pos": "FW"},
        {"name": "A. Bastoni", "pos": "DF"}, {"name": "C. Immobile", "pos": "FW"},
        {"name": "Jorginho", "pos": "MF"}, {"name": "S. Pafundi", "pos": "FW"},
    ],
    "Portugal": [
        {"name": "Cristiano Ronaldo", "pos": "FW"}, {"name": "Rafael Leão", "pos": "FW"},
        {"name": "Rui Patricio", "pos": "GK"}, {"name": "Rúben Dias", "pos": "DF"},
        {"name": "Bernardo Silva", "pos": "MF"}, {"name": "João Cancelo", "pos": "DF"},
        {"name": "Diogo Jota", "pos": "FW"}, {"name": "João Félix", "pos": "FW"},
        {"name": "Nuno Mendes", "pos": "DF"}, {"name": "João Neves", "pos": "MF"},
    ],
    "Spain": [
        {"name": "Morata", "pos": "FW"}, {"name": "Gavi", "pos": "MF"},
        {"name": "Pedri", "pos": "MF"}, {"name": "Carvajal", "pos": "DF"},
        {"name": "U. Simón", "pos": "GK"}, {"name": "Rodri", "pos": "MF"},
        {"name": "Thiago", "pos": "MF"}, {"name": "A. Grimaldo", "pos": "DF"},
        {"name": "Koke", "pos": "MF"}, {"name": "Stefan Bajcetic", "pos": "MF"},
    ],
    "Korea": [
        {"name": "H. Son", "pos": "FW"}, {"name": "Hyeon Woo", "pos": "GK"},
        {"name": "Kim Min jae", "pos": "DF"}, {"name": "Lee Kang In", "pos": "MF"},
        {"name": "Hwang Hee Chan", "pos": "FW"}, {"name": "Lee Jae Sung", "pos": "MF"},
        {"name": "Hong Hyeon Seok", "pos": "MF"}, {"name": "Joo Min Kyu", "pos": "FW"},
        {"name": "Um Won Sang", "pos": "GK"}, {"name": "Kim Young Gwon", "pos": "DF"},
    ],
    "Saudi Arabia": [
        {"name": "A. Al Mayoof", "pos": "GK"}, {"name": "S. Al Faraj", "pos": "MF"},
        {"name": "S. Al Dawsari", "pos": "FW"}, {"name": "A. Sharahili", "pos": "DF"},
        {"name": "S. Abdulhamid", "pos": "DF"}, {"name": "H. Tombakti", "pos": "MF"},
        {"name": "F. Al Birekan", "pos": "MF"}, {"name": "A. Al Bulayhi", "pos": "DF"},
        {"name": "Y. Al Shahrani", "pos": "DF"}, {"name": "A. Al Ayeri", "pos": "FW"},
    ],
    "South Africa": [
        {"name": "J. Barr", "pos": "DF"}, {"name": "Foster", "pos": "FW"},
        {"name": "Mothiba", "pos": "FW"}, {"name": "Hlongwane", "pos": "FW"},
        {"name": "Links", "pos": "MF"}, {"name": "Cafú Phete", "pos": "MF"},
        {"name": "Kodisang", "pos": "FW"}, {"name": "Blom", "pos": "MF"},
        {"name": "Ngezana", "pos": "DF"}, {"name": "Mailula", "pos": "FW"},
    ],
    "Tunisia": [
        {"name": "Dahmen", "pos": "GK"}, {"name": "Skhiri", "pos": "MF"},
        {"name": "Laïdouni", "pos": "MF"}, {"name": "Talbi", "pos": "FW"},
        {"name": "Khazri", "pos": "FW"}, {"name": "Bguir", "pos": "MF"},
        {"name": "Layouni", "pos": "MF"}, {"name": "Valery", "pos": "DF"},
        {"name": "Abdi", "pos": "DF"}, {"name": "Bronn", "pos": "DF"},
    ],
    "Ghana": [
        {"name": "T. Partey", "pos": "MF"}, {"name": "Iñaki williams", "pos": "FW"},
        {"name": "L. Zigi", "pos": "GK"}, {"name": "Kudus", "pos": "MF"},
        {"name": "Aidoo", "pos": "DF"}, {"name": "Lamptey", "pos": "DF"},
        {"name": "Abdul Samed", "pos": "MF"}, {"name": "Djiku", "pos": "DF"},
        {"name": "Paintsil", "pos": "FW"}, {"name": "Semenyo", "pos": "FW"},
    ],
    "New Zealand": [
        {"name": "C. Wood", "pos": "FW"}, {"name": "J. Bell", "pos": "DF"},
        {"name": "L. Cacace", "pos": "DF"}, {"name": "M. Stamenić", "pos": "MF"},
        {"name": "A. Paulsen", "pos": "GK"}, {"name": "A. Rufer", "pos": "FW"},
        {"name": "T. Bindon", "pos": "MF"}, {"name": "M. Boxall", "pos": "DF"},
        {"name": "K. Barbarouses", "pos": "FW"}, {"name": "B. Old", "pos": "MF"},
    ],
    "Switzerland": [
        {"name": "G. Kobel", "pos": "GK"}, {"name": "G. Xhaka", "pos": "MF"},
        {"name": "M. Akanji", "pos": "DF"}, {"name": "F. Schär", "pos": "DF"},
        {"name": "R. Freuler", "pos": "MF"}, {"name": "D. Zakaria", "pos": "MF"},
        {"name": "N. Elvedi", "pos": "DF"}, {"name": "R. Rodríguez", "pos": "DF"},
        {"name": "B. Embolo", "pos": "FW"}, {"name": "N. Okafor", "pos": "FW"},
    ],
    "Denmark": [
        {"name": "K. Schmeichel", "pos": "GK"}, {"name": "A. Christensen", "pos": "DF"},
        {"name": "P. Højbjerg", "pos": "MF"}, {"name": "S. Kjær", "pos": "DF"},
        {"name": "M. Hjulmand", "pos": "MF"}, {"name": "C. Eriksen", "pos": "MF"},
        {"name": "M. O'Riley", "pos": "MF"}, {"name": "J. Andersen", "pos": "DF"},
        {"name": "A. Bah", "pos": "DF"}, {"name": "R. Højlund", "pos": "FW"},
    ],
    "Poland": [
        {"name": "W. Szczęsny", "pos": "GK"}, {"name": "R. Lewandowski", "pos": "FW"},
        {"name": "P. Zieliński", "pos": "MF"}, {"name": "A. Milik", "pos": "FW"},
        {"name": "M. Cash", "pos": "DF"}, {"name": "S. Szymański", "pos": "MF"},
        {"name": "P. Frankowski", "pos": "DF"}, {"name": "J. Kiwior", "pos": "DF"},
        {"name": "N. Zalewski", "pos": "MF"}, {"name": "J. Bednarek", "pos": "DF"},
    ],
    "Austria": [
        {"name": "C. Stankovic", "pos": "GK"}, {"name": "D. Alaba", "pos": "DF"},
        {"name": "K. Laimer", "pos": "MF"}, {"name": "M. Sabitzer", "pos": "MF"},
        {"name": "X. Schlager", "pos": "MF"}, {"name": "Arnautovic", "pos": "FW"},
        {"name": "K. Danso", "pos": "DF"}, {"name": "C. Baumgartner", "pos": "MF"},
        {"name": "G. Trauner", "pos": "DF"}, {"name": "M. Gregoritsch", "pos": "FW"},
    ],
    "Croatia": [
        {"name": "D. Livaković", "pos": "GK"}, {"name": "L. Modrić", "pos": "MF"},
        {"name": "M. Brozović", "pos": "MF"}, {"name": "M. Kovačić", "pos": "MF"},
        {"name": "J. Gvardiol", "pos": "DF"}, {"name": "A. Kramarić", "pos": "FW"},
        {"name": "I. Rakitić", "pos": "MF"}, {"name": "M. Pasalic", "pos": "MF"},
        {"name": "N. Vlasic", "pos": "MF"}, {"name": "L. Majer", "pos": "MF"},
    ],
    "Uruguay": [
        {"name": "F. Muslera", "pos": "GK"}, {"name": "L. Suárez", "pos": "FW"},
        {"name": "F. Valverde", "pos": "MF"}, {"name": "R. Araujo", "pos": "DF"},
        {"name": "J. Giménez", "pos": "DF"}, {"name": "D. Núñez", "pos": "FW"},
        {"name": "R. Bentancur", "pos": "MF"}, {"name": "L. Torreira", "pos": "MF"},
        {"name": "S. Coates", "pos": "DF"}, {"name": "M. Ugarte", "pos": "MF"},
    ],
    "Argentina": [
        {"name": "E. Martínez", "pos": "GK"}, {"name": "L. Messi", "pos": "FW"},
        {"name": "L. Martínez", "pos": "FW"}, {"name": "P. Dybala", "pos": "FW"},
        {"name": "J. Álvarez", "pos": "FW"}, {"name": "M. Acuña", "pos": "DF"},
        {"name": "A. Mac Allister", "pos": "MF"}, {"name": "C. Romero", "pos": "DF"},
        {"name": "Á. Di María", "pos": "FW"}, {"name": "R. De Paul", "pos": "MF"},
    ],
    "Venezuela": [
        {"name": "R. Romo", "pos": "GK"}, {"name": "Y. Herrera", "pos": "MF"},
        {"name": "D. Machís", "pos": "FW"}, {"name": "J. Martinez", "pos": "MF"},
        {"name": "C. Cásseres Jr", "pos": "MF"}, {"name": "M. Villanueva", "pos": "MF"},
        {"name": "J. Cádiz", "pos": "DF"}, {"name": "L. Gonzalez", "pos": "DF"},
        {"name": "J. Moreno", "pos": "FW"}, {"name": "S. Rondón", "pos": "FW"},
    ],
    "Bolivia": [
        {"name": "C. Lampe", "pos": "GK"}, {"name": "S. Galindo", "pos": "DF"},
        {"name": "M. Enoumba", "pos": "DF"}, {"name": "H. Vaca", "pos": "MF"},
        {"name": "A. Jusino", "pos": "DF"}, {"name": "J. Arrascaita", "pos": "MF"},
        {"name": "A. Quiroga", "pos": "MF"}, {"name": "D. Mancilla", "pos": "FW"},
        {"name": "J. Chura", "pos": "FW"}, {"name": "J. Sagredo", "pos": "MF"},
    ],
    "Germany": [
        {"name": "M. ter Stegen", "pos": "GK"}, {"name": "K. Havertz", "pos": "MF"},
        {"name": "J. Musiala", "pos": "MF"}, {"name": "İ. Gündoğan", "pos": "MF"},
        {"name": "F. Wirtz", "pos": "MF"}, {"name": "J. Kimmich", "pos": "MF"},
        {"name": "S. Gnabry", "pos": "FW"}, {"name": "L. Sané", "pos": "FW"},
        {"name": "A. Rüdiger", "pos": "DF"}, {"name": "J. Brandt", "pos": "MF"},
    ],
    "England": [
        {"name": "N. Pope", "pos": "GK"}, {"name": "P. Foden", "pos": "MF"},
        {"name": "M. Rashford", "pos": "FW"}, {"name": "J. Bellingham", "pos": "MF"},
        {"name": "T. Alexander-Arnold", "pos": "DF"}, {"name": "B. Saka", "pos": "FW"},
        {"name": "D. Rice", "pos": "MF"}, {"name": "H. Kane", "pos": "FW"},
        {"name": "C. Palmer", "pos": "MF"}, {"name": "R. Sterling", "pos": "FW"},
    ],
    "Norway": [
        {"name": "Ø. Nyland", "pos": "GK"}, {"name": "E. Haaland", "pos": "FW"},
        {"name": "M. Ødegaard", "pos": "MF"}, {"name": "F. Aursnes", "pos": "MF"},
        {"name": "A. Sørloth", "pos": "FW"}, {"name": "J. Ryerson", "pos": "DF"},
        {"name": "K. Ajer", "pos": "DF"}, {"name": "P. Berg", "pos": "MF"},
        {"name": "A. Pellegrino", "pos": "DF"}, {"name": "J. Svensson", "pos": "DF"},
    ],
    "USA": [
        {"name": "M. Turner", "pos": "GK"}, {"name": "C. Pulisic", "pos": "MF"},
        {"name": "G. Reyna", "pos": "MF"}, {"name": "W. McKennie", "pos": "MF"},
        {"name": "S. Dest", "pos": "DF"}, {"name": "F. Balogun", "pos": "FW"},
        {"name": "A. Robinson", "pos": "DF"}, {"name": "T. Adams", "pos": "MF"},
        {"name": "C. Carter-Vickers", "pos": "DF"}, {"name": "J. Brooks", "pos": "DF"},
    ],
    "Costa Rica": [
        {"name": "K. Navas", "pos": "GK"}, {"name": "J. Vargas", "pos": "MF"},
        {"name": "O. Duarte", "pos": "DF"}, {"name": "C. Gamboa", "pos": "DF"},
        {"name": "R. Leal", "pos": "FW"}, {"name": "F. Brown Forbes", "pos": "MF"},
        {"name": "J. Cascante", "pos": "DF"}, {"name": "K. Vargas", "pos": "FW"},
        {"name": "D. Chacón", "pos": "MF"}, {"name": "A. Martínez", "pos": "MF"},
    ],
    "Qatar": [
        {"name": "M. Barsham", "pos": "GK"}, {"name": "A. Afif", "pos": "FW"},
        {"name": "A. Ali", "pos": "MF"}, {"name": "K. Boudiaf", "pos": "MF"},
        {"name": "H. Al Haydos", "pos": "MF"}, {"name": "A. Hatem", "pos": "MF"},
        {"name": "B. Khoukhi", "pos": "DF"}, {"name": "Lucas Mendes", "pos": "DF"},
        {"name": "A. Asad", "pos": "DF"}, {"name": "H. Ahmed", "pos": "MF"},
    ],
    "Australia": [
        {"name": "M. Ryan", "pos": "GK"}, {"name": "C. Goodwin", "pos": "MF"},
        {"name": "J. Irvine", "pos": "MF"}, {"name": "M. Leckie", "pos": "FW"},
        {"name": "R. McGree", "pos": "MF"}, {"name": "A. Grant", "pos": "MF"},
        {"name": "H. Souttar", "pos": "DF"}, {"name": "M. Luongo", "pos": "MF"},
        {"name": "C. Devlin", "pos": "MF"}, {"name": "J. Maclaren", "pos": "FW"},
    ],
    "Morocco": [
        {"name": "Y. Bounou", "pos": "GK"}, {"name": "A. Hakimi", "pos": "DF"},
        {"name": "Y. En-Nesyri", "pos": "FW"}, {"name": "Brahim", "pos": "MF"},
        {"name": "N. Mazraoui", "pos": "DF"}, {"name": "H. Ziyech", "pos": "MF"},
        {"name": "S. Amrabat", "pos": "MF"}, {"name": "Munir", "pos": "FW"},
        {"name": "A. Adli", "pos": "MF"}, {"name": "A. Ezzalzouli", "pos": "FW"},
    ],
    "Egypt": [
        {"name": "K. Eissa", "pos": "GK"}, {"name": "M. Salah", "pos": "FW"},
        {"name": "Marmoush", "pos": "FW"}, {"name": "A. Hegazi", "pos": "DF"},
        {"name": "Trezeguet", "pos": "FW"}, {"name": "M. Mohamed", "pos": "MF"},
        {"name": "T. Hamed", "pos": "MF"}, {"name": "M. Elneny", "pos": "MF"},
        {"name": "M. Morsy", "pos": "MF"}, {"name": "A. Hassan", "pos": "MF"},
    ],
    "Senegal": [
        {"name": "É. Mendy", "pos": "GK"}, {"name": "S. Mané", "pos": "FW"},
        {"name": "K. Koulibaly", "pos": "DF"}, {"name": "B. Dia", "pos": "FW"},
        {"name": "P. Sarr", "pos": "MF"}, {"name": "M. Niakhaté", "pos": "DF"},
        {"name": "N. Jackson", "pos": "FW"}, {"name": "Y. Sabaly", "pos": "DF"},
        {"name": "I. Gueye", "pos": "MF"}, {"name": "I. Sarr", "pos": "FW"},
    ],
    "Sweden": [
        {"name": "R. Olsen", "pos": "GK"}, {"name": "A. Isak", "pos": "FW"},
        {"name": "D. Kulusevski", "pos": "FW"}, {"name": "V. Gyökeres", "pos": "FW"},
        {"name": "E. Forsberg", "pos": "MF"}, {"name": "V. Lindelöf", "pos": "DF"},
        {"name": "M. Svanberg", "pos": "MF"}, {"name": "J. Karlsson", "pos": "MF"},
        {"name": "K. Olsson", "pos": "DF"}, {"name": "H. Larsson", "pos": "FW"},
    ],
    "Serbia": [
        {"name": "V. Milinković-Savić", "pos": "GK"},
        {"name": "S. Milinković-Savić", "pos": "MF"},
        {"name": "D. Vlahović", "pos": "FW"}, {"name": "F. Kostić", "pos": "MF"},
        {"name": "D. Tadić", "pos": "MF"}, {"name": "A. Mitrović", "pos": "FW"},
        {"name": "N. Gudelj", "pos": "MF"}, {"name": "N. Matić", "pos": "MF"},
        {"name": "N. Milenković", "pos": "DF"}, {"name": "M. Milovanović", "pos": "MF"},
    ],
    "Wales": [
        {"name": "W. Hennessey", "pos": "GK"}, {"name": "B. Johnson", "pos": "DF"},
        {"name": "B. Davies", "pos": "DF"}, {"name": "J. Rodon", "pos": "DF"},
        {"name": "E. Ampadu", "pos": "MF"}, {"name": "D. Brooks", "pos": "MF"},
        {"name": "H. Wilson", "pos": "MF"}, {"name": "C. Roberts", "pos": "MF"},
        {"name": "D. James", "pos": "FW"}, {"name": "L. Harris", "pos": "MF"},
    ],
    "Scotland": [
        {"name": "A. Gunn", "pos": "GK"}, {"name": "A. Robertson", "pos": "DF"},
        {"name": "K. Tierney", "pos": "DF"}, {"name": "J. McGinn", "pos": "MF"},
        {"name": "C. McGregor", "pos": "MF"}, {"name": "S. McTominay", "pos": "MF"},
        {"name": "R. Gauld", "pos": "MF"}, {"name": "L. Ferguson", "pos": "MF"},
        {"name": "T. Cairney", "pos": "MF"}, {"name": "B. Doak", "pos": "FW"},
    ],
    "Belgium": [
        {"name": "T. Courtois", "pos": "GK"}, {"name": "K. De Bruyne", "pos": "MF"},
        {"name": "Y. Carrasco", "pos": "MF"}, {"name": "R. Lukaku", "pos": "FW"},
        {"name": "L. Openda", "pos": "FW"}, {"name": "L. Trossard", "pos": "FW"},
        {"name": "J. Doku", "pos": "FW"}, {"name": "Y. Tielemans", "pos": "MF"},
        {"name": "A. Witsel", "pos": "MF"}, {"name": "A. Vermeeren", "pos": "MF"},
    ],
    "Colombia": [
        {"name": "Á. Montero", "pos": "GK"}, {"name": "L. Díaz", "pos": "FW"},
        {"name": "D. Muñoz", "pos": "DF"}, {"name": "L. Muriel", "pos": "FW"},
        {"name": "L. Sinisterra", "pos": "FW"}, {"name": "J. Quintero", "pos": "MF"},
        {"name": "J. Mojica", "pos": "DF"}, {"name": "D. Silva", "pos": "MF"},
        {"name": "D. Cataño", "pos": "MF"}, {"name": "Y. Asprilla", "pos": "FW"},
    ],
    "Chile": [
        {"name": "C. Bravo", "pos": "GK"}, {"name": "A. Sánchez", "pos": "FW"},
        {"name": "G. Maripán", "pos": "DF"}, {"name": "A. Vidal", "pos": "MF"},
        {"name": "P. Díaz", "pos": "DF"}, {"name": "B. Brereton Díaz", "pos": "FW"},
        {"name": "E. Bolindos", "pos": "MF"}, {"name": "R. Echeverría", "pos": "MF"},
        {"name": "C. Palacios", "pos": "MF"}, {"name": "D. Pizarro", "pos": "MF"},
    ],
    "Peru": [
        {"name": "P. Gallese", "pos": "GK"}, {"name": "R. Tapia", "pos": "MF"},
        {"name": "L. Advíncula", "pos": "DF"}, {"name": "R. Ruidíaz", "pos": "FW"},
        {"name": "A. Callens", "pos": "DF"}, {"name": "G. Lapadula", "pos": "FW"},
        {"name": "C. Cueva", "pos": "MF"}, {"name": "P. Guerrero", "pos": "FW"},
        {"name": "A. Polo", "pos": "MF"}, {"name": "A. Valera", "pos": "DF"},
    ],
    "Jamaica": [
        {"name": "A. Blake", "pos": "GK"}, {"name": "L. Bailey", "pos": "FW"},
        {"name": "E. Pinnock", "pos": "DF"}, {"name": "M. Antonio", "pos": "FW"},
        {"name": "D. Gray", "pos": "DF"}, {"name": "B. Cordova", "pos": "MF"},
        {"name": "K. Roofe", "pos": "FW"}, {"name": "S. Nicholson", "pos": "FW"},
        {"name": "A. Bell", "pos": "DF"}, {"name": "O. Hutchinson", "pos": "FW"},
    ],
    "Canada": [
        {"name": "M. Crépeau", "pos": "GK"}, {"name": "A. Davies", "pos": "DF"},
        {"name": "J. David", "pos": "FW"}, {"name": "S. Eustáquio", "pos": "MF"},
        {"name": "C. Larin", "pos": "FW"}, {"name": "A. Johnston", "pos": "MF"},
        {"name": "J. Osorio", "pos": "MF"}, {"name": "T. Buchanan", "pos": "MF"},
        {"name": "L. Millar", "pos": "MF"}, {"name": "N. Saliba", "pos": "DF"},
    ],
    "Hungary": [
        {"name": "P. Gulácsi", "pos": "GK"}, {"name": "W. Orban", "pos": "DF"},
        {"name": "D. Szoboszlai", "pos": "MF"}, {"name": "R. Sallai", "pos": "FW"},
        {"name": "M. Kerkez", "pos": "DF"}, {"name": "D. Gazdag", "pos": "MF"},
        {"name": "B. Varga", "pos": "FW"}, {"name": "Z. Kalmár", "pos": "MF"},
        {"name": "D. Sallói", "pos": "FW"}, {"name": "K. Lisztes", "pos": "MF"},
    ],
    "Netherlands": [
        {"name": "M. Flekken", "pos": "GK"}, {"name": "V. van Dijk", "pos": "DF"},
        {"name": "F. de Jong", "pos": "MF"}, {"name": "J. Frimpong", "pos": "DF"},
        {"name": "M. de Ligt", "pos": "DF"}, {"name": "D. Malen", "pos": "FW"},
        {"name": "M. Depay", "pos": "FW"}, {"name": "C. Gakpo", "pos": "FW"},
        {"name": "X. Simons", "pos": "MF"}, {"name": "J. Hato", "pos": "DF"},
    ],
    "France": [
        {"name": "M. Maignan", "pos": "GK"}, {"name": "K. Mbappé", "pos": "FW"},
        {"name": "K. Benzema", "pos": "FW"}, {"name": "A. Griezmann", "pos": "FW"},
        {"name": "J. Koundé", "pos": "DF"}, {"name": "K. Coman", "pos": "FW"},
        {"name": "N. Kanté", "pos": "MF"}, {"name": "T. Hernández", "pos": "DF"},
        {"name": "C. Nkunku", "pos": "FW"}, {"name": "W. Zaïre-Emery", "pos": "MF"},
    ],
    "Japan": [
        {"name": "K. Nakamura", "pos": "GK"}, {"name": "D. Kamada", "pos": "MF"},
        {"name": "K. Mitoma", "pos": "FW"}, {"name": "T. Kubo", "pos": "FW"},
        {"name": "W. Endo", "pos": "MF"}, {"name": "H. Morita", "pos": "MF"},
        {"name": "T. Minamino", "pos": "FW"}, {"name": "J. Ito", "pos": "FW"},
        {"name": "R. Doan", "pos": "MF"}, {"name": "K. Sano", "pos": "MF"},
    ],
    "Israel": [
        {"name": "D. Peretz", "pos": "GK"}, {"name": "M. Solomon", "pos": "MF"},
        {"name": "M. Abu Fani", "pos": "MF"}, {"name": "S. Weissman", "pos": "FW"},
        {"name": "O. Gloukh", "pos": "MF"}, {"name": "L. Abada", "pos": "FW"},
        {"name": "O. Atzili", "pos": "FW"}, {"name": "R. Safuri", "pos": "MF"},
        {"name": "T. Baribo", "pos": "FW"}, {"name": "O. Gandelman", "pos": "FW"},
    ],
    "Nigeria": [
        {"name": "M. Okoye", "pos": "GK"}, {"name": "V. Osimhen", "pos": "FW"},
        {"name": "A. Lookman", "pos": "FW"}, {"name": "V. Boniface", "pos": "FW"},
        {"name": "S. Chukwueze", "pos": "FW"}, {"name": "W. Ndidi", "pos": "MF"},
        {"name": "T. Moffi", "pos": "FW"}, {"name": "T. Awoniyi", "pos": "FW"},
        {"name": "A. Nwakaeme", "pos": "FW"}, {"name": "S. Nwankwo", "pos": "FW"},
    ],
    "Cameroon": [
        {"name": "A. Onana", "pos": "GK"}, {"name": "A. Zambo Anguissa", "pos": "MF"},
        {"name": "J. Matip", "pos": "DF"}, {"name": "B. Mbeumo", "pos": "FW"},
        {"name": "V. Aboubakar", "pos": "FW"}, {"name": "E. Choupo-Moting", "pos": "FW"},
        {"name": "G. Nkoudou", "pos": "FW"}, {"name": "H. Moukoudi", "pos": "DF"},
        {"name": "K. Toko Ekambi", "pos": "FW"}, {"name": "C. Baleba", "pos": "MF"},
    ],
    "Ivory Coast": [
        {"name": "Y. Fofana", "pos": "MF"}, {"name": "F. Kessié", "pos": "MF"},
        {"name": "S. Fofana", "pos": "DF"}, {"name": "W. Zaha", "pos": "FW"},
        {"name": "S. Haller", "pos": "FW"}, {"name": "I. Sangaré", "pos": "MF"},
        {"name": "O. Kossounou", "pos": "DF"}, {"name": "N. Pépé", "pos": "FW"},
        {"name": "C. Kouamé", "pos": "FW"}, {"name": "A. Diallo", "pos": "DF"},
    ],
    "Algeria": [
        {"name": "A. Oukidja", "pos": "GK"}, {"name": "R. Mahrez", "pos": "FW"},
        {"name": "I. Bennacer", "pos": "MF"}, {"name": "N. Bentaleb", "pos": "MF"},
        {"name": "A. Gouiri", "pos": "FW"}, {"name": "R. Bensebaini", "pos": "DF"},
        {"name": "S. Benrahma", "pos": "FW"}, {"name": "R. Ghezzal", "pos": "FW"},
        {"name": "F. Chaïbi", "pos": "MF"}, {"name": "B. Bouanani", "pos": "FW"},
    ],
}

# ============================================================
# STATE
# ============================================================
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

# ============================================================
# TOURNAMENT UTILS
# ============================================================
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
def _scorer_input(team, num_goals, existing_scorers, widget_key, state, torneo):
    """
    Muestra la lista de jugadores del equipo para marcar goleadores.
    Usa multiselect con los jugadores reales + número de goles por jugador.
    Retorna lista de strings "Nombre N" para compatibilidad con register_scorers.
    """
    players = PLAYERS.get(team, [])
    if not players:
        # Fallback: text input si no hay jugadores
        val = st.text_input(
            f"⚽ Goleadores {display_name(team)}",
            value=", ".join(existing_scorers),
            key=widget_key,
            placeholder="Jugador 1, Jugador 2"
        )
        return [s.strip() for s in val.split(",") if s.strip()]

    # Separar jugadores por posición para mejor UX
    fw = [p["name"] for p in players if p["pos"] == "FW"]
    mf = [p["name"] for p in players if p["pos"] == "MF"]
    df_gk = [p["name"] for p in players if p["pos"] in ("DF", "GK")]
    player_names = fw + mf + df_gk  # FW primero

    # Reconstruir selección existente
    existing_names = []
    existing_counts = {}
    for entry in existing_scorers:
        parts = entry.rsplit(" ", 1)
        if len(parts) == 2:
            try:
                existing_counts[parts[0]] = int(parts[1])
                existing_names.append(parts[0])
            except ValueError:
                existing_counts[entry] = 1
                existing_names.append(entry)
        else:
            existing_counts[entry] = 1
            existing_names.append(entry)

    # Filtrar nombres válidos
    valid_existing = [n for n in existing_names if n in player_names]

    if num_goals == 0:
        return []

    st.markdown(f"<div style='font-size:0.8rem;color:#a0c0ff;font-weight:600;margin-bottom:4px;'>⚽ {display_name(team)}</div>", unsafe_allow_html=True)
    
    selected = st.multiselect(
        f"Goleadores {display_name(team)}",
        options=player_names,
        default=valid_existing,
        key=f"{widget_key}_ms",
        label_visibility="collapsed",
        placeholder="Selecciona goleadores..."
    )

    result = []
    for player in selected:
        default_g = existing_counts.get(player, 1)
        goals = st.number_input(
            f"Goles de {player}",
            min_value=1,
            max_value=num_goals,
            value=min(default_g, num_goals),
            key=f"{widget_key}_{player}_g",
            label_visibility="collapsed"
        )
        result.append(f"{player} {goals}")

    return result


def register_scorers(scorers_list, team, state, torneo):
    """
    Registra goles en all_scorers global.
    scorers_list: lista de "Nombre N" o string CSV.
    """
    if not scorers_list:
        return
    if isinstance(scorers_list, str):
        entries = [s.strip() for s in scorers_list.split(",") if s.strip()]
    else:
        entries = list(scorers_list)

    if "all_scorers" not in state:
        state["all_scorers"] = {}

    for entry in entries:
        parts = entry.rsplit(" ", 1)
        if len(parts) == 2:
            name, goals_str = parts
            try:
                goals = int(goals_str)
            except ValueError:
                goals = 1
        else:
            name = entry
            goals = 1

        skey = f"{name}||{team}"
        sc = state["all_scorers"]
        if skey not in sc:
            sc[skey] = {"name": name, "team": team, "goals": 0, "torneos": {}}
        sc[skey]["goals"] += goals
        sc[skey]["torneos"][torneo] = sc[skey]["torneos"].get(torneo, 0) + goals

# ---------------------------------------------------------------------------
# RENDER TABLA DE POSICIONES
# ---------------------------------------------------------------------------
def render_standings_table(standings, advancing=2, show_thirds=False):
    """
    Renderiza tabla de posiciones usando st.dataframe nativo.
    No retorna HTML — llama directamente a st.dataframe.
    """
    import pandas as pd

    rows = []
    for row in standings:
        pos = row["pos"]
        dg = row["dg"]
        dg_str = f"+{dg}" if dg > 0 else str(dg)

        if pos <= advancing:
            estado = "✅ Clasifica"
        elif pos <= advancing + 2 and show_thirds:
            estado = "🟡 Posible 3ro"
        else:
            estado = "❌ Eliminado"

        rows.append({
            "#": pos,
            "Selección": display_name(row["team"]),
            "PJ": row["pj"],
            "PG": row["pg"],
            "PE": row["pe"],
            "PP": row["pp"],
            "GF": row["gf"],
            "GC": row["gc"],
            "DG": dg_str,
            "PTS": row["pts"],
            "Estado": estado,
        })

    df = pd.DataFrame(rows)

    def color_row(row):
        estado = row["Estado"]
        if "✅" in estado:
            bg = "background-color: #0d3a1e; color: #4eff91"
        elif "🟡" in estado:
            bg = "background-color: #2a3a00; color: #ccff44"
        else:
            bg = "background-color: #1a1a2e; color: #888899"
        return [bg] * len(row)

    styled = df.style.apply(color_row, axis=1)
    st.dataframe(
        styled,
        use_container_width=True,
        hide_index=True,
        column_config={
            "#": st.column_config.NumberColumn(width="small"),
            "PJ": st.column_config.NumberColumn(width="small"),
            "PG": st.column_config.NumberColumn(width="small"),
            "PE": st.column_config.NumberColumn(width="small"),
            "PP": st.column_config.NumberColumn(width="small"),
            "GF": st.column_config.NumberColumn(width="small"),
            "GC": st.column_config.NumberColumn(width="small"),
            "DG": st.column_config.TextColumn(width="small"),
            "PTS": st.column_config.NumberColumn(width="small"),
            "Estado": st.column_config.TextColumn(width="medium"),
        }
    )
    # Retornar string vacío para compatibilidad con llamadas que hacen st.markdown(...)
    return ""



# ---------------------------------------------------------------------------
# ARMADO MANUAL DE GRUPOS (función genérica para todos los torneos)
# ---------------------------------------------------------------------------
def _manual_group_setup(state, tour_key, teams, num_groups, teams_per_group, confirm_label="Confirmar grupos"):
    """
    Interfaz manual para armar grupos: selectbox con texto plano (sin HTML).
    """
    tour = state[tour_key]
    group_labels = [chr(65+i) for i in range(num_groups)]
    ranking = state["ranking"]
    teams_sorted = sorted(teams, key=lambda t: -ranking.get(t, 0))

    st.markdown("#### 📋 Asigna cada equipo a su grupo:")
    st.caption(f"{len(teams)} equipos → {num_groups} grupos de {teams_per_group}")

    group_opts = ["— Sin asignar —"] + [f"Grupo {g}" for g in group_labels]

    key_prefix = f"manual_{tour_key}"
    if f"{key_prefix}_assignments" not in state:
        state[f"{key_prefix}_assignments"] = {}
    assignments = state[f"{key_prefix}_assignments"]

    # Mostrar en columnas con TEXTO PLANO (sin HTML en labels)
    cols = st.columns(3)
    for idx, team in enumerate(teams_sorted):
        with cols[idx % 3]:
            current_val = assignments.get(team, "— Sin asignar —")
            current_idx = group_opts.index(current_val) if current_val in group_opts else 0
            # Label con bandera emoji o solo texto — sin HTML
            code = FLAG_MAP.get(team, "")
            label = f"{display_name(team)}"
            sel = st.selectbox(
                label,
                group_opts,
                index=current_idx,
                key=f"{key_prefix}_{team}",
            )
            assignments[team] = sel
    state[f"{key_prefix}_assignments"] = assignments

    # Preview de grupos
    preview = {g: [] for g in group_labels}
    for team, grp in assignments.items():
        if grp != "— Sin asignar —":
            g = grp.replace("Grupo ", "")
            if g in preview:
                preview[g].append(team)

    st.markdown("---")
    st.markdown("**Vista previa de grupos:**")
    ncols = min(num_groups, 8)
    pcols = st.columns(ncols)
    all_valid = True
    for i, g in enumerate(group_labels):
        with pcols[i % ncols]:
            teams_in = preview[g]
            color = "#00cc66" if len(teams_in) == teams_per_group else ("#ffd700" if len(teams_in) > 0 else "#6080aa")
            st.markdown(
                f"<div style='background:#0a1020;border:1px solid {color};border-radius:8px;padding:10px;margin-bottom:8px;'>"
                f"<div style='font-weight:700;color:{color};margin-bottom:6px;'>GRUPO {g} ({len(teams_in)}/{teams_per_group})</div>"
                + "".join([f"<div style='font-size:0.85rem;padding:2px 0;'>{get_flag_url(t,16,12) and chr(127)+chr(127) or ''}{display_name(t)}</div>" for t in teams_in])
                + "</div>",
                unsafe_allow_html=True
            )
            if len(teams_in) != teams_per_group:
                all_valid = False

    unassigned = [t for t in teams if assignments.get(t, "— Sin asignar —") == "— Sin asignar —"]
    if unassigned:
        st.warning(f"⚠️ Sin asignar ({len(unassigned)}): {', '.join([display_name(t) for t in unassigned])}")

    if all_valid:
        if st.button(f"✅ {confirm_label}", type="primary", use_container_width=True):
            tour["groups"] = preview
            tour["group_results"] = {}
            tour["group_standings"] = {}
            tour["phase"] = "grupos"
            tour["setup_done"] = True
            if f"{key_prefix}_assignments" in state:
                del state[f"{key_prefix}_assignments"]
            st.rerun()
            return True
    else:
        st.info(f"Asigna exactamente {teams_per_group} equipos a cada grupo para continuar.")
    return False

# ============================================================
# EUROCOPA UEFA
# ============================================================
TOURNAMENT_KEY_EURO = 'euro'
TORNEO_NAME_EURO = 'Eurocopa FMMJ'
# ---------------------------------------------------------------------------
# SORTEO DE GRUPOS EUROCOPA (con restricción de confederación = todos UEFA)
# ---------------------------------------------------------------------------
def setup_euro_groups(state):
    """
    24 equipos UEFA → 6 grupos de 4.
    Se forman 4 bombos de 6 (por ranking). De cada bombo se extrae
    1 equipo por grupo (6 grupos), igual que en la Eurocopa real.
    """
    ranking = state["ranking"]
    teams_sorted = sorted(UEFA_TEAMS, key=lambda t: -ranking.get(t, 0))
    # 4 bombos de 6 equipos (4 bombos × 6 = 24)
    pots = [teams_sorted[i*6:(i+1)*6] for i in range(4)]
    groups = {chr(65+i): [] for i in range(6)}
    group_keys = list(groups.keys())  # ['A','B','C','D','E','F']
    # De cada bombo, repartir 1 equipo a cada grupo
    for pot in pots:
        shuffled = pot[:]
        random.shuffle(shuffled)
        for i, team in enumerate(shuffled):
            groups[group_keys[i]].append(team)
    state["euro"]["groups"] = groups
    state["euro"]["group_results"] = {}
    state["euro"]["group_standings"] = {}
    state["euro"]["phase"] = "grupos"
    state["euro"]["setup_done"] = True

# ---------------------------------------------------------------------------
# PÁGINA PRINCIPAL
# ---------------------------------------------------------------------------
def show_eurocopa():
    state = get_state()
    euro = state["euro"]
    host = state.get("host", "Nigeria")

    st.markdown("""
    <style>
    .euro-header {
        background: linear-gradient(135deg, #003580 0%, #0066cc 50%, #003580 100%);
        border-radius: 16px; padding: 24px 32px; margin-bottom: 24px;
        display: flex; align-items: center; gap: 20px;
        box-shadow: 0 8px 32px rgba(0,53,128,0.4);
    }
    .euro-title {font-size: 2rem; font-weight: 800; color: #ffd700; margin: 0;}
    .euro-subtitle {font-size: 0.9rem; color: #aaccff; margin: 4px 0 0 0;}
    .group-card {
        background: #0d1b3e; border: 1px solid #1a3a6e;
        border-radius: 12px; padding: 16px; margin-bottom: 16px;
    }
    .group-title {
        font-size: 1.1rem; font-weight: 700; color: #ffd700;
        border-bottom: 2px solid #ffd700; padding-bottom: 8px; margin-bottom: 12px;
    }
    .match-input-row {
        background: #111a35; border-radius: 8px; padding: 10px 14px;
        margin-bottom: 8px; border: 1px solid #1e3055;
    }
    .match-label {font-size: 0.85rem; color: #8899cc; margin-bottom: 6px;}
    .qualified-badge {
        display: inline-block; padding: 4px 10px; border-radius: 20px;
        font-size: 0.75rem; font-weight: 600; margin: 2px;
    }
    .direct { background: #0d4f2e; color: #4eff91; }
    .playoff { background: #2a3d0d; color: #aaff44; }
    .eliminated { background: #3d0d0d; color: #ff6666; }
    .phase-badge {
        display: inline-block; background: #003580; color: #ffd700;
        padding: 4px 14px; border-radius: 20px; font-size: 0.8rem;
        font-weight: 700; margin-bottom: 16px;
    }
    .knockout-match {
        background: #0a1628; border: 1px solid #1a3a6e;
        border-radius: 10px; padding: 14px; margin-bottom: 10px;
    }
    .match-teams {font-size: 1rem; color: #fff; font-weight: 600; margin-bottom: 8px;}
    .winner-tag {color: #ffd700; font-weight: 700;}
    </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown(f"""
    <div class='euro-header'>
        <div>
            <div class='euro-title'>🏆 {"Eurocopa FMMJ"}</div>
            <div class='euro-subtitle'>24 selecciones UEFA · 6 grupos · 13 cupos al FMMJ World Cup</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Pestañas
    tabs = st.tabs(["🎲 Sorteo", "📊 Fase de Grupos", "⚽ Llaves", "🔄 Playoff UEFA", "🌍 Clasificados"])

    # ── TAB 1: ARMADO DE GRUPOS ────────────────────────────────────────────
    with tabs[0]:
        st.markdown("### 📋 Armado de Grupos — Eurocopa FMMJ")
        if not euro["setup_done"]:
            _manual_group_setup(state, "euro", UEFA_TEAMS, num_groups=6, teams_per_group=4,
                                confirm_label="Confirmar grupos Eurocopa")
        else:
            st.success("✅ Grupos confirmados")
            if st.button("✏️ Editar grupos", type="secondary"):
                euro["setup_done"] = False
                st.rerun()
            _show_groups_draw(euro)

    # ── TAB 2: FASE DE GRUPOS ──────────────────────────────────────────────
    with tabs[1]:
        if not euro["setup_done"]:
            st.warning("Primero realiza el sorteo en la pestaña **Sorteo**.")
        else:
            _show_group_stage(state, euro)

    # ── TAB 3: LLAVES (Knockout desde Octavos) ────────────────────────────
    with tabs[2]:
        if not euro["setup_done"]:
            st.warning("Primero completa el sorteo.")
        elif euro["phase"] not in ["llaves", "completado"]:
            st.warning("Completa la fase de grupos primero.")
        else:
            _show_knockout(state, euro)

    # ── TAB 4: PLAYOFF UEFA ───────────────────────────────────────────────
    with tabs[3]:
        _show_uefa_playoff(state, euro)

    # ── TAB 5: CLASIFICADOS ───────────────────────────────────────────────
    with tabs[4]:
        _show_qualified(state, euro)


# ---------------------------------------------------------------------------
# SORTEO VISUAL
# ---------------------------------------------------------------------------
def _show_groups_draw(euro):
    groups = euro["groups"]
    cols = st.columns(3)
    for idx, (g, teams) in enumerate(groups.items()):
        with cols[idx % 3]:
            st.markdown(f"<div class='group-card'><div class='group-title'>GRUPO {g}</div>", unsafe_allow_html=True)
            for t in teams:
                st.markdown(f"{flag_img(t,20,15)}&nbsp;**{display_name(t)}**", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# FASE DE GRUPOS
# ---------------------------------------------------------------------------
def _show_group_stage(state, euro):
    groups = euro["groups"]
    results = euro.get("group_results", {})

    st.markdown("### 📊 Fase de Grupos — Eurocopa FMMJ")
    st.caption("Ingresa los resultados de cada partido. Clasifican los **2 primeros** de cada grupo + los **4 mejores terceros** al cuadro de llaves.")

    all_groups_complete = True

    for g, teams in groups.items():
        fixtures = []
        for i in range(len(teams)):
            for j in range(i+1, len(teams)):
                fixtures.append((teams[i], teams[j]))

        with st.expander(f"📋 GRUPO {g}", expanded=True):
            # Ingresar resultados
            st.markdown("**Resultados de partidos:**")
            for home, away in fixtures:
                key = match_key(home, away)
                res = results.get(key, {})
                played = res.get("played", False)

                col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 3, 1])
                with col1:
                    st.markdown(f"{flag_img(home,20,15)}&nbsp;**{display_name(home)}**", unsafe_allow_html=True)
                with col2:
                    hg = st.number_input("", min_value=0, max_value=20,
                                        value=res.get("home_goals", 0),
                                        key=f"euro_hg_{g}_{home}_{away}",
                                        label_visibility="collapsed")
                with col3:
                    ag = st.number_input("", min_value=0, max_value=20,
                                        value=res.get("away_goals", 0),
                                        key=f"euro_ag_{g}_{home}_{away}",
                                        label_visibility="collapsed")
                with col4:
                    st.markdown(f"{flag_img(away,20,15)}&nbsp;**{display_name(away)}**", unsafe_allow_html=True)
                with col5:
                    save = st.button("💾", key=f"euro_save_{g}_{home}_{away}", help="Guardar resultado")

                # Goleadores con jugadores reales
                col_sc1, col_sc2 = st.columns(2)
                with col_sc1:
                    hs = _scorer_input(home, hg, res.get("home_scorers", []),
                                       f"euro_sc_{g}_{home}_{away}_h", state, "Eurocopa FMMJ")
                with col_sc2:
                    as_ = _scorer_input(away, ag, res.get("away_scorers", []),
                                        f"euro_sc_{g}_{home}_{away}_a", state, "Eurocopa FMMJ")

                if save:
                    # Registrar limpiando duplicados primero
                    old_sc = state.get("all_scorers", {})
                    for skey in list(old_sc.keys()):
                        if old_sc[skey]["team"] in (home, away) and "Eurocopa FMMJ" in old_sc[skey].get("torneos", {}):
                            pass  # se sobreescribe en register
                    euro["group_results"][key] = {
                        "home_goals": hg, "away_goals": ag,
                        "home_scorers": hs,
                        "away_scorers": as_,
                        "played": True
                    }
                    register_scorers(hs, home, state, "Eurocopa FMMJ")
                    register_scorers(as_, away, state, "Eurocopa FMMJ")
                    st.rerun()

                if not results.get(key, {}).get("played"):
                    all_groups_complete = False
                st.markdown("---")

            # Tabla
            st.markdown("**Tabla de posiciones:**")
            standings = calculate_standings(teams, {k: v for k, v in results.items()
                                                     if any(t in k for t in teams)})
            euro["group_standings"][g] = standings
            render_standings_table(standings, advancing=2, show_thirds=True)
            st.caption("🟢 Clasificado directo | 🟡 Posible mejor tercero")

    # Botón para avanzar a llaves
    if all_groups_complete or st.checkbox("🔓 Forzar avance a llaves (aunque falten resultados)"):
        if euro["phase"] == "grupos":
            if st.button("⚽ Generar Llaves — Fase de Eliminación", type="primary", use_container_width=True):
                _build_knockout_bracket(state, euro)
                euro["phase"] = "llaves"
                st.rerun()


# ---------------------------------------------------------------------------
# CONSTRUCCIÓN DEL CUADRO ELIMINATORIO
# ---------------------------------------------------------------------------
def _build_knockout_bracket(state, euro):
    """
    Top 2 de cada grupo (12) + 4 mejores terceros = 16 equipos
    Formato UEFA Euro: Octavos definidos por tabla de mejores terceros
    """
    standings = euro.get("group_standings", {})
    groups_order = sorted(standings.keys())

    firsts = []
    seconds = []
    thirds = []

    for g in groups_order:
        s = standings[g]
        if len(s) >= 1:
            firsts.append(s[0]["team"])
        if len(s) >= 2:
            seconds.append(s[1]["team"])
        if len(s) >= 3:
            thirds.append(s[2])

    # Mejores 4 terceros (por puntos, dg, gf)
    best4_thirds = sorted(thirds, key=lambda x: (-x["pts"], -x["dg"], -x["gf"]))[:4]
    best4_thirds_teams = [x["team"] for x in best4_thirds]
    best4_thirds_groups = [g for g in groups_order
                           if any(standings[g][2]["team"] == t for t in best4_thirds_teams
                                  if len(standings.get(g, [])) > 2)]

    # Emparejamiento octavos de final (simplificado por posición)
    # 1A vs Mejor3(BCDEF), 1C vs 3(DEF), etc. (usamos orden estándar UEFA)
    round_of_16 = []
    # Emparejamiento estándar UEFA Euro 2024:
    # 1A vs 2C, 1B vs 3(ADEF), 1C vs 3(DEF), 1D vs 2B
    # 1E vs 3(ABC), 1F vs 3(ABCD), 2D vs 2E, 2A vs 2F
    # Simplificado: top2 + best4thirds aleatoriamente
    qualified_16 = firsts + seconds
    random.shuffle(best4_thirds_teams)
    qualified_16 = qualified_16[:12] + best4_thirds_teams

    random.shuffle(qualified_16)
    for i in range(0, 16, 2):
        round_of_16.append((qualified_16[i], qualified_16[i+1]))

    euro["knockout_bracket"] = {
        "octavos": [{"home": m[0], "away": m[1], "winner": None} for m in round_of_16],
        "cuartos": [],
        "semis": [],
        "tercer_puesto": [],
        "final": [],
    }
    euro["knockout_results"] = {}


# ---------------------------------------------------------------------------
# LLAVES ELIMINATORIAS
# ---------------------------------------------------------------------------
def _show_knockout(state, euro):
    st.markdown("### ⚽ Fase de Eliminación — Eurocopa FMMJ")
    bracket = euro.get("knockout_bracket", {})
    results = euro.get("knockout_results", {})

    phases = [
        ("octavos", "🔵 Octavos de Final", "cuartos"),
        ("cuartos", "🟡 Cuartos de Final", "semis"),
        ("semis", "🟠 Semifinales", "final"),
        ("final", "🏆 Final", None),
    ]

    for phase_key, phase_name, next_phase in phases:
        matches = bracket.get(phase_key, [])
        if not matches:
            continue

        st.markdown(f"#### {phase_name}")
        all_done = True

        for idx, match in enumerate(matches):
            home = match["home"]
            away = match["away"]
            if not home or not away:
                st.markdown(f"*Pendiente de clasificación*")
                all_done = False
                continue

            key = f"euro_{phase_key}_{idx}"
            res = results.get(key, {})

            with st.container():
                st.markdown(f"<div class='knockout-match'>", unsafe_allow_html=True)
                col1, col2, col3, col4, col5, col6 = st.columns([3,1,1,3,2,1])
                with col1:
                    st.markdown(f"{flag_img(home,22,16)}&nbsp;**{display_name(home)}**", unsafe_allow_html=True)
                with col2:
                    hg = st.number_input("", min_value=0, max_value=20,
                                        value=res.get("home_goals", 0),
                                        key=f"{key}_hg", label_visibility="collapsed")
                with col3:
                    ag = st.number_input("", min_value=0, max_value=20,
                                        value=res.get("away_goals", 0),
                                        key=f"{key}_ag", label_visibility="collapsed")
                with col4:
                    st.markdown(f"{flag_img(away,22,16)}&nbsp;**{display_name(away)}**", unsafe_allow_html=True)
                with col5:
                    if hg == ag:
                        pen_opt = [None, home, away]
                        pen_disp = ["— Penales —", display_name(home), display_name(away)]
                        pen_idx = pen_opt.index(res.get("penalty_winner")) if res.get("penalty_winner") in pen_opt else 0
                        pen_sel = st.selectbox("Penales", pen_disp, index=pen_idx, key=f"{key}_pen")
                        pen_winner = pen_opt[pen_disp.index(pen_sel)]
                    else:
                        pen_winner = None
                        st.markdown("")
                with col6:
                    save = st.button("💾", key=f"{key}_save", help="Guardar")

                # Goleadores
                col_s1, col_s2 = st.columns(2)
                with col_s1:
                    hs = _scorer_input(home, hg, res.get("home_scorers", []), f"{key}_hs", state, "Eurocopa FMMJ")
                with col_s2:
                    as_ = _scorer_input(away, ag, res.get("away_scorers", []), f"{key}_as", state, "Eurocopa FMMJ")

                if save:
                    winner = home if hg > ag else (away if ag > hg else pen_winner)
                    results[key] = {
                        "home_goals": hg, "away_goals": ag,
                        "penalty_winner": pen_winner, "winner": winner,
                        "home_scorers": hs, "away_scorers": as_,
                    }
                    euro["knockout_bracket"][phase_key][idx]["winner"] = winner
                    register_scorers(hs, home, state, "Eurocopa FMMJ")
                    register_scorers(as_, away, state, "Eurocopa FMMJ")
                    st.rerun()

                if res.get("winner"):
                    st.markdown(f"<span class='winner-tag'>✅ Ganador: {flag_img(res['winner'],18,13)}{display_name(res['winner'])}</span>",
                               unsafe_allow_html=True)
                else:
                    all_done = False

                st.markdown("</div>", unsafe_allow_html=True)

        # Avanzar a siguiente fase
        if all_done and next_phase is not None and not bracket.get(next_phase):
            winners = [results.get(f"euro_{phase_key}_{i}", {}).get("winner")
                      for i in range(len(matches))]
            winners = [w for w in winners if w]
            if next_phase == "semis" and phase_key == "cuartos":
                losers = [m.get("winner") for m in bracket.get("cuartos", []) if m.get("winner")]
                # semis toma winners de cuartos
            next_matches = [(winners[i], winners[i+1]) for i in range(0, len(winners)-1, 2)]
            bracket[next_phase] = [{"home": m[0], "away": m[1], "winner": None} for m in next_matches]
            if next_phase == "semis":
                # También preparar el partido por el tercer puesto
                bracket["tercer_puesto"] = []
            euro["knockout_results"] = results
            st.rerun()

        if all_done and phase_key == "semis" and not bracket.get("tercer_puesto"):
            losers = []
            for i, match in enumerate(matches):
                key = f"euro_semis_{i}"
                res = results.get(key, {})
                winner = res.get("winner")
                loser = match["home"] if winner == match["away"] else match["away"]
                if loser:
                    losers.append(loser)
            if len(losers) == 2:
                bracket["tercer_puesto"] = [{"home": losers[0], "away": losers[1], "winner": None}]
                st.rerun()

        # Final y 3er puesto -> clasificados
        if all_done and phase_key == "final":
            _determine_euro_qualified(state, euro, results, bracket)


def _determine_euro_qualified(state, euro, results, bracket):
    if euro.get("qualified"):
        return  # ya calculado

    # Orden knockout: campeón=1, finalista=2, semifinalistas=3-4, cuartos=5-8...
    champion = None
    final_res = results.get("euro_final_0", {})
    if final_res.get("winner"):
        champion = final_res["winner"]

    finalist = None
    for m in bracket.get("final", []):
        if m.get("winner"):
            finalist = m["home"] if m["winner"] == m["away"] else m["away"]

    semifinalists = []
    for i, m in enumerate(bracket.get("semis", [])):
        res_s = results.get(f"euro_semis_{i}", {})
        loser = m["home"] if res_s.get("winner") == m["away"] else m["away"]
        if loser:
            semifinalists.append(loser)

    quarter_losers = []
    for i, m in enumerate(bracket.get("cuartos", [])):
        res_q = results.get(f"euro_cuartos_{i}", {})
        loser = m["home"] if res_q.get("winner") == m["away"] else m["away"]
        if loser:
            quarter_losers.append(loser)

    # Top 5 van al mundial directo
    direct = [champion, finalist] + semifinalists + quarter_losers[:1]
    direct = [t for t in direct if t][:5]

    # Puestos 6-21: van al playoff UEFA (16 equipos, 4 grupos, top2 van al mundial = 8 clasificados)
    all_knockout = [champion, finalist] + semifinalists + quarter_losers
    all_round16 = [m["home"] for m in bracket.get("octavos", [])] + \
                  [m["away"] for m in bracket.get("octavos", [])]

    group_teams_flat = [t for teams in euro["groups"].values() for t in teams]
    # Eliminados en fase de grupos (puestos 3 y 4 sin ser mejores terceros)
    best_thirds = []
    fourth_placed = []
    for g, standings in euro.get("group_standings", {}).items():
        if len(standings) >= 3:
            best_thirds.append(standings[2]["team"])
        if len(standings) >= 4:
            fourth_placed.append(standings[3]["team"])

    playoff_candidates = [t for t in all_round16
                         if t and t not in direct and t not in all_knockout[:6]]
    # Completar con grupos
    for t in fourth_placed + best_thirds:
        if t and t not in direct and t not in playoff_candidates:
            playoff_candidates.append(t)

    playoff_candidates = list(dict.fromkeys(playoff_candidates))[:16]

    euro["qualified_direct"] = direct
    euro["playoff_candidates"] = playoff_candidates
    euro["phase"] = "playoff_uefa"


# ---------------------------------------------------------------------------
# PLAYOFF UEFA (puestos 6-21 → 8 clasificados)
# ---------------------------------------------------------------------------
def _show_uefa_playoff(state, euro):
    st.markdown("### 🔄 Playoff UEFA — 8 cupos al Mundial")
    st.caption("16 equipos eliminados en llaves + mejores grupos compiten en 4 grupos de 4. Los 2 primeros de cada grupo clasifican.")

    if euro["phase"] not in ["playoff_uefa", "completado"]:
        st.info("Esta fase se habilita una vez concluya la Eurocopa.")
        return

    if not euro.get("playoff_bracket"):
        candidates = euro.get("playoff_candidates", [])
        if len(candidates) < 16:
            st.warning(f"Solo hay {len(candidates)} candidatos al playoff. Se necesitan 16.")
            return
        # Sorteo 4 grupos de 4
        random.shuffle(candidates)
        playoff_groups = {f"P{i+1}": candidates[i*4:(i+1)*4] for i in range(4)}
        euro["playoff_bracket"] = {
            "groups": playoff_groups,
            "results": {},
            "standings": {},
        }

    pb = euro["playoff_bracket"]
    playoff_results = pb.get("results", {})
    all_complete = True

    for g, teams in pb["groups"].items():
        with st.expander(f"Grupo Playoff {g}", expanded=True):
            fixtures = [(teams[i], teams[j]) for i in range(len(teams)) for j in range(i+1, len(teams))]
            for home, away in fixtures:
                key = match_key(home, away)
                res = playoff_results.get(key, {})
                col1, col2, col3, col4, col5 = st.columns([3,1,1,3,1])
                with col1:
                    st.markdown(f"{flag_img(home)}&nbsp;**{display_name(home)}**", unsafe_allow_html=True)
                with col2:
                    hg = st.number_input("", 0, 20, res.get("home_goals", 0), key=f"epo_hg_{g}_{home}_{away}", label_visibility="collapsed")
                with col3:
                    ag = st.number_input("", 0, 20, res.get("away_goals", 0), key=f"epo_ag_{g}_{home}_{away}", label_visibility="collapsed")
                with col4:
                    st.markdown(f"{flag_img(away)}&nbsp;**{display_name(away)}**", unsafe_allow_html=True)
                with col5:
                    if st.button("💾", key=f"epo_save_{g}_{home}_{away}"):
                        playoff_results[key] = {"home_goals": hg, "away_goals": ag, "played": True}
                        pb["results"] = playoff_results
                        st.rerun()
                if not playoff_results.get(key, {}).get("played"):
                    all_complete = False

            standings = calculate_standings(teams, {k: v for k, v in playoff_results.items()
                                                     if any(t in k for t in teams)})
            pb["standings"][g] = standings
            render_standings_table(standings, advancing=2)

    if all_complete:
        qualified_playoff = []
        for g, standings in pb["standings"].items():
            for row in standings[:2]:
                qualified_playoff.append(row["team"])

        all_qualified = euro.get("qualified_direct", []) + qualified_playoff
        euro["qualified"] = all_qualified
        euro["phase"] = "completado"

        st.success(f"✅ Playoff completado. {len(qualified_playoff)} equipos adicionales clasificados al Mundial.")


# ---------------------------------------------------------------------------
# CLASIFICADOS
# ---------------------------------------------------------------------------
def _show_qualified(state, euro):
    st.markdown("### 🌍 Clasificados UEFA al Mundial FMMJ")

    direct = euro.get("qualified_direct", [])
    playoff_q = [t for t in euro.get("qualified", []) if t not in direct]

    if direct:
        st.markdown("#### ✅ Clasificados Directos (Top 5 Eurocopa)")
        for i, t in enumerate(direct, 1):
            st.markdown(f"{i}. {flag_img(t,22,16)}&nbsp;**{display_name(t)}**", unsafe_allow_html=True)

    if playoff_q:
        st.markdown("#### 🔄 Clasificados vía Playoff UEFA")
        for i, t in enumerate(playoff_q, 1):
            st.markdown(f"{i}. {flag_img(t,22,16)}&nbsp;**{display_name(t)}**", unsafe_allow_html=True)

    total = euro.get("qualified", [])
    if total:
        st.info(f"**Total UEFA clasificados: {len(total)}/13**")
        # Actualizar en estado global
        state["world_cup_qualified"] = list(set(state["world_cup_qualified"] + total))
    else:
        st.info("Los clasificados aparecerán aquí una vez concluyan ambas fases.")

# ============================================================
# COPA AMERICA CONMEBOL
# ============================================================
TOURNAMENT_KEY_CA = 'copa_america'
TORNEO_NAME_CA = 'Copa América FMMJ'
GUEST_POOL_CA = CONCACAF_TEAMS + AFC_TEAMS + CAF_TEAMS + PLAYOFF_TEAMS
def show_copa_america():
    state = get_state()
    ca = state["copa_america"]

    st.markdown("""
    <style>
    .ca-header {
        background: linear-gradient(135deg, #006b3c 0%, #009b4e 50%, #004d2a 100%);
        border-radius:16px;padding:24px 32px;margin-bottom:24px;
        box-shadow:0 8px 32px rgba(0,107,60,0.4);
    }
    .ca-title {font-size:2rem;font-weight:800;color:#ffd700;margin:0;}
    .ca-subtitle {font-size:.9rem;color:#a0ffcc;margin:4px 0 0;}
    .group-card {background:#0a1f12;border:1px solid #1a4a2a;border-radius:12px;padding:16px;margin-bottom:16px;}
    .group-title {font-size:1.1rem;font-weight:700;color:#ffd700;border-bottom:2px solid #ffd700;padding-bottom:8px;margin-bottom:12px;}
    .knockout-match {background:#071510;border:1px solid #1a4a2a;border-radius:10px;padding:14px;margin-bottom:10px;}
    .winner-tag {color:#ffd700;font-weight:700;}
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class='ca-header'>
        <div>
            <div class='ca-title'>🏆 {"Copa América FMMJ"}</div>
            <div class='ca-subtitle'>10 CONMEBOL + 6 invitadas · 4 grupos · 4 cupos al FMMJ World Cup</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tabs = st.tabs(["🌎 Invitadas", "🎲 Sorteo", "📊 Fase de Grupos", "⚽ Llaves", "🔄 Playoff", "🌍 Clasificados"])

    # ── INVITADAS ──────────────────────────────────────────────────────────
    with tabs[0]:
        st.markdown("### 🌎 Selección de Equipos Invitados")
        st.caption("Elige 6 invitadas de CONCACAF, AFC, CAF u OFC (no UEFA)")

        if ca.get("guests"):
            st.success(f"✅ Invitadas elegidas: {', '.join([display_name(g) for g in ca['guests']])}")
            if st.button("Cambiar invitadas"):
                ca["guests"] = []
                ca["setup_done"] = False
                st.rerun()
        else:
            selected = []
            st.markdown("**Equipos disponibles:**")
            cols = st.columns(3)
            for idx, team in enumerate(GUEST_POOL_CA):
                with cols[idx % 3]:
                    if st.checkbox(f"{flag_img(team,16,12)}{display_name(team)}", key=f"ca_guest_{team}"):
                        selected.append(team)

            st.markdown(f"**Seleccionados: {len(selected)}/6**")
            if len(selected) == 6:
                if st.button("✅ Confirmar invitadas", type="primary"):
                    ca["guests"] = selected
                    st.rerun()
            elif len(selected) > 6:
                st.error("Máximo 6 invitadas. Deselecciona algunas.")

    # ── SORTEO ─────────────────────────────────────────────────────────────
    with tabs[1]:
        st.markdown("### 🎲 Sorteo de Grupos")
        if not ca.get("guests"):
            st.warning("Primero selecciona las 6 invitadas.")
        elif not ca.get("setup_done"):
            all_teams_ca2 = CONMEBOL_TEAMS + ca["guests"]
            _manual_group_setup(state, "copa_america", all_teams_ca2, num_groups=4, teams_per_group=4,
                                confirm_label="Confirmar grupos Copa América")
        else:
            st.success("✅ Grupos confirmados")
            if st.button("✏️ Editar grupos"):
                ca["setup_done"] = False
                st.rerun()
            _show_groups_draw(ca)

    # ── FASE DE GRUPOS ─────────────────────────────────────────────────────
    with tabs[2]:
        if not ca.get("setup_done"):
            st.warning("Primero realiza el sorteo.")
        else:
            _show_group_stage(state, ca)

    # ── LLAVES ─────────────────────────────────────────────────────────────
    with tabs[3]:
        if ca.get("phase") not in ["llaves", "completado"]:
            st.warning("Completa la fase de grupos primero.")
        else:
            _show_knockout(state, ca)

    # ── PLAYOFF ────────────────────────────────────────────────────────────
    with tabs[4]:
        _show_playoff(state, ca)

    # ── CLASIFICADOS ───────────────────────────────────────────────────────
    with tabs[5]:
        _show_qualified(state, ca)


def _setup_ca_groups(state, ca):
    all_teams = CONMEBOL_TEAMS + ca["guests"]
    ranking = state["ranking"]
    teams_sorted = sorted(all_teams, key=lambda t: -ranking.get(t, 0))
    # 4 bombos de 4
    pots = [teams_sorted[i*4:(i+1)*4] for i in range(4)]
    groups = {"A": [], "B": [], "C": [], "D": []}
    group_keys = list(groups.keys())
    for pot in pots:
        shuffled = pot[:]
        random.shuffle(shuffled)
        for i, team in enumerate(shuffled):
            groups[group_keys[i]].append(team)
    ca["groups"] = groups
    ca["group_results"] = {}
    ca["group_standings"] = {}
    ca["phase"] = "grupos"
    ca["setup_done"] = True


def _show_groups_draw(ca):
    groups = ca["groups"]
    cols = st.columns(2)
    for idx, (g, teams) in enumerate(groups.items()):
        with cols[idx % 2]:
            st.markdown(f"<div class='group-card'><div class='group-title'>GRUPO {g}</div>", unsafe_allow_html=True)
            for t in teams:
                st.markdown(f"{flag_img(t,20,15)}&nbsp;**{display_name(t)}**", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)


def _show_group_stage(state, ca):
    groups = ca["groups"]
    results = ca.get("group_results", {})

    st.markdown("### 📊 Fase de Grupos — Copa América FMMJ")
    st.caption("Clasifican **2 primeros** de cada grupo a cuartos de final.")
    all_complete = True

    for g, teams in groups.items():
        fixtures = [(teams[i], teams[j]) for i in range(len(teams)) for j in range(i+1, len(teams))]
        with st.expander(f"📋 GRUPO {g}", expanded=True):
            for home, away in fixtures:
                key = match_key(home, away)
                res = results.get(key, {})
                col1, col2, col3, col4, col5 = st.columns([3,1,1,3,1])
                with col1:
                    st.markdown(f"{flag_img(home)}&nbsp;**{display_name(home)}**", unsafe_allow_html=True)
                with col2:
                    hg = st.number_input("", 0, 20, res.get("home_goals", 0), key=f"ca_hg_{g}_{home}_{away}", label_visibility="collapsed")
                with col3:
                    ag = st.number_input("", 0, 20, res.get("away_goals", 0), key=f"ca_ag_{g}_{home}_{away}", label_visibility="collapsed")
                with col4:
                    st.markdown(f"{flag_img(away)}&nbsp;**{display_name(away)}**", unsafe_allow_html=True)
                with col5:
                    save = st.button("💾", key=f"ca_save_{g}_{home}_{away}")
                col_s1, col_s2 = st.columns(2)
                with col_s1:
                    hs = _scorer_input(home, hg, res.get("home_scorers", []), f"ca_hs_{g}_{home}_{away}", state, "Copa América FMMJ")
                with col_s2:
                    as_ = _scorer_input(away, ag, res.get("away_scorers", []), f"ca_as_{g}_{home}_{away}", state, "Copa América FMMJ")
                if save:
                    ca["group_results"][key] = {
                        "home_goals": hg, "away_goals": ag, "played": True,
                        "home_scorers": [s.strip() for s in hs.split(",") if s.strip()],
                        "away_scorers": [s.strip() for s in as_.split(",") if s.strip()],
                    }
                    register_scorers(hs, home, state, "Copa América FMMJ")
                    register_scorers(as_, away, state, "Copa América FMMJ")
                    st.rerun()
                if not results.get(key, {}).get("played"):
                    all_complete = False
                st.markdown("---")

            standings = calculate_standings(teams, {k: v for k, v in results.items() if any(t in k for t in teams)})
            ca["group_standings"][g] = standings
            render_standings_table(standings, advancing=2)

    if all_complete or st.checkbox("🔓 Forzar avance a llaves"):
        if ca["phase"] == "grupos":
            if st.button("⚽ Generar Cuartos de Final", type="primary", use_container_width=True):
                _build_knockout(state, ca)
                ca["phase"] = "llaves"
                st.rerun()


def _build_knockout(state, ca):
    standings = ca.get("group_standings", {})
    # Top 2 de cada grupo = 8 equipos → Cuartos
    firsts = []
    seconds = []
    for g in sorted(standings.keys()):
        s = standings[g]
        if s: firsts.append(s[0]["team"])
        if len(s) > 1: seconds.append(s[1]["team"])

    # 1A vs 2B, 1B vs 2A, 1C vs 2D, 1D vs 2C
    qf = [
        (firsts[0], seconds[1]),
        (firsts[1], seconds[0]),
        (firsts[2], seconds[3]),
        (firsts[3], seconds[2]),
    ]
    ca["knockout_bracket"] = {
        "cuartos": [{"home": m[0], "away": m[1], "winner": None} for m in qf],
        "semis": [],
        "tercer_puesto": [],
        "final": [],
    }
    ca["knockout_results"] = {}
    # Para playoff: registrar 3ros y 4tos de grupo
    thirds = []
    fourths = []
    for g in sorted(standings.keys()):
        s = standings[g]
        if len(s) > 2: thirds.append(s[2]["team"])
        if len(s) > 3: fourths.append(s[3]["team"])
    ca["group_thirds"] = thirds
    ca["group_fourths"] = fourths


def _show_knockout(state, ca):
    st.markdown("### ⚽ Fase de Eliminación — Copa América FMMJ")
    bracket = ca.get("knockout_bracket", {})
    results = ca.get("knockout_results", {})
    if not results:
        ca["knockout_results"] = {}
        results = ca["knockout_results"]

    phases = [
        ("cuartos", "🟡 Cuartos de Final", "semis"),
        ("semis", "🟠 Semifinales", "final"),
        ("final", "🏆 Final", None),
    ]

    for phase_key, phase_name, next_phase in phases:
        matches = bracket.get(phase_key, [])
        if not matches:
            continue
        st.markdown(f"#### {phase_name}")
        all_done = True

        for idx, match in enumerate(matches):
            home, away = match["home"], match["away"]
            if not home or not away:
                all_done = False
                continue
            key = f"ca_{phase_key}_{idx}"
            res = results.get(key, {})

            with st.container():
                col1,col2,col3,col4,col5,col6 = st.columns([3,1,1,3,2,1])
                with col1:
                    st.markdown(f"{flag_img(home)}&nbsp;**{display_name(home)}**", unsafe_allow_html=True)
                with col2:
                    hg = st.number_input("", 0, 20, res.get("home_goals", 0), key=f"{key}_hg", label_visibility="collapsed")
                with col3:
                    ag = st.number_input("", 0, 20, res.get("away_goals", 0), key=f"{key}_ag", label_visibility="collapsed")
                with col4:
                    st.markdown(f"{flag_img(away)}&nbsp;**{display_name(away)}**", unsafe_allow_html=True)
                with col5:
                    if hg == ag:
                        pen_opt = [None, home, away]
                        pen_disp = ["— Penales —", display_name(home), display_name(away)]
                        pen_idx = pen_opt.index(res.get("penalty_winner")) if res.get("penalty_winner") in pen_opt else 0
                        pen_sel = st.selectbox("Penales", pen_disp, index=pen_idx, key=f"{key}_pen")
                        pen_winner = pen_opt[pen_disp.index(pen_sel)]
                    else:
                        pen_winner = None
                        st.empty()
                with col6:
                    save = st.button("💾", key=f"{key}_save")

                col_s1, col_s2 = st.columns(2)
                with col_s1:
                    hs = _scorer_input(home, hg, res.get("home_scorers", []), f"{key}_hs", state, torneo_name)
                with col_s2:
                    as_ = _scorer_input(away, ag, res.get("away_scorers", []), f"{key}_as", state, torneo_name)

                if save:
                    winner = home if hg > ag else (away if ag > hg else pen_winner)
                    results[key] = {"home_goals": hg, "away_goals": ag, "winner": winner,
                                    "penalty_winner": pen_winner,
                                    "home_scorers": [s.strip() for s in hs.split(",") if s.strip()],
                                    "away_scorers": [s.strip() for s in as_.split(",") if s.strip()]}
                    ca["knockout_bracket"][phase_key][idx]["winner"] = winner
                    register_scorers(hs, home, state, "Copa América FMMJ")
                    register_scorers(as_, away, state, "Copa América FMMJ")
                    st.rerun()

                if res.get("winner"):
                    st.markdown(f"<span class='winner-tag'>✅ Ganador: {flag_img(res['winner'],18,13)}{display_name(res['winner'])}</span>", unsafe_allow_html=True)
                else:
                    all_done = False
                st.markdown("---")

        if all_done and next_phase and not bracket.get(next_phase):
            winners = [results.get(f"ca_{phase_key}_{i}", {}).get("winner") for i in range(len(matches))]
            winners = [w for w in winners if w]
            if phase_key == "semis" and not bracket.get("tercer_puesto"):
                losers = []
                for i, m in enumerate(matches):
                    r = results.get(f"ca_semis_{i}", {})
                    loser = m["home"] if r.get("winner") == m["away"] else m["away"]
                    if loser: losers.append(loser)
                if len(losers) == 2:
                    bracket["tercer_puesto"] = [{"home": losers[0], "away": losers[1], "winner": None}]
            next_m = [(winners[i], winners[i+1]) for i in range(0, len(winners)-1, 2)]
            bracket[next_phase] = [{"home": m[0], "away": m[1], "winner": None} for m in next_m]
            ca["knockout_results"] = results
            st.rerun()

        if all_done and phase_key == "final":
            _determine_ca_qualified(state, ca, results, bracket)

    # Tercer puesto
    if bracket.get("tercer_puesto"):
        st.markdown("#### 🥉 Tercer Puesto")
        for idx, match in enumerate(bracket["tercer_puesto"]):
            home, away = match["home"], match["away"]
            key = f"ca_tercer_{idx}"
            res = results.get(key, {})
            col1,col2,col3,col4,col5,col6 = st.columns([3,1,1,3,2,1])
            with col1: st.markdown(f"{flag_img(home)}&nbsp;**{display_name(home)}**", unsafe_allow_html=True)
            with col2:
                hg = st.number_input("", 0, 20, res.get("home_goals", 0), key=f"{key}_hg", label_visibility="collapsed")
            with col3:
                ag = st.number_input("", 0, 20, res.get("away_goals", 0), key=f"{key}_ag", label_visibility="collapsed")
            with col4: st.markdown(f"{flag_img(away)}&nbsp;**{display_name(away)}**", unsafe_allow_html=True)
            with col5:
                if hg == ag:
                    pen_sel = st.selectbox("Penales", ["— —", display_name(home), display_name(away)], key=f"{key}_pen")
                    pen_winner = home if pen_sel == display_name(home) else (away if pen_sel == display_name(away) else None)
                else:
                    pen_winner = None; st.empty()
            with col6:
                if st.button("💾", key=f"{key}_save"):
                    winner = home if hg > ag else (away if ag > hg else pen_winner)
                    results[key] = {"home_goals": hg, "away_goals": ag, "winner": winner}
                    bracket["tercer_puesto"][idx]["winner"] = winner
                    ca["knockout_results"] = results
                    st.rerun()
            if res.get("winner"):
                st.markdown(f"**🥉 3er Lugar: {display_name(res['winner'])}**")


def _determine_ca_qualified(state, ca, results, bracket):
    if ca.get("qualified"): return
    champion = results.get("ca_final_0", {}).get("winner")
    finalist = None
    for m in bracket.get("final", []):
        if m.get("winner"):
            finalist = m["home"] if m["winner"] == m["away"] else m["away"]
    third = results.get("ca_tercer_0", {}).get("winner")
    semis_losers = []
    for i, m in enumerate(bracket.get("semis", [])):
        r = results.get(f"ca_semis_{i}", {})
        loser = m["home"] if r.get("winner") == m["away"] else m["away"]
        if loser: semis_losers.append(loser)
    qf_losers = []
    for i, m in enumerate(bracket.get("cuartos", [])):
        r = results.get(f"ca_cuartos_{i}", {})
        loser = m["home"] if r.get("winner") == m["away"] else m["away"]
        if loser: qf_losers.append(loser)

    ca["champion"] = champion
    ca["qualified_direct"] = [champion] if champion else []
    # 2do-7mo van al playoff
    playoff_candidates = []
    for t in [finalist, third] + semis_losers + qf_losers:
        if t and t not in playoff_candidates: playoff_candidates.append(t)
    ca["playoff_candidates"] = playoff_candidates[:6]
    ca["phase"] = "playoff"


def _show_playoff(state, ca):
    st.markdown("### 🔄 Playoff CONMEBOL — 3 cupos + 1 repechaje")
    st.caption("Puestos 2do al 7mo de Copa América juegan todos contra todos. Top 3 → Mundial. 4to → Repechaje internacional.")
    if ca.get("phase") not in ["playoff", "completado"]:
        st.info("Esta fase se habilita al concluir la Copa América.")
        return

    candidates = ca.get("playoff_candidates", [])
    if not candidates:
        st.warning("No hay candidatos para el playoff.")
        return

    pb = ca.get("playoff_bracket", {})
    if not pb:
        pb = {"results": {}, "standings": {}}
        ca["playoff_bracket"] = pb

    results = pb.get("results", {})
    fixtures = [(candidates[i], candidates[j]) for i in range(len(candidates)) for j in range(i+1, len(candidates))]
    all_done = True

    st.markdown("**Partidos (todos contra todos):**")
    for home, away in fixtures:
        key = match_key(home, away)
        res = results.get(key, {})
        col1,col2,col3,col4,col5 = st.columns([3,1,1,3,1])
        with col1: st.markdown(f"{flag_img(home)}&nbsp;**{display_name(home)}**", unsafe_allow_html=True)
        with col2:
            hg = st.number_input("", 0, 20, res.get("home_goals", 0), key=f"cap_{home}_{away}_hg", label_visibility="collapsed")
        with col3:
            ag = st.number_input("", 0, 20, res.get("away_goals", 0), key=f"cap_{home}_{away}_ag", label_visibility="collapsed")
        with col4: st.markdown(f"{flag_img(away)}&nbsp;**{display_name(away)}**", unsafe_allow_html=True)
        with col5:
            if st.button("💾", key=f"cap_{home}_{away}_save"):
                results[key] = {"home_goals": hg, "away_goals": ag, "played": True}
                pb["results"] = results
                st.rerun()
        if not results.get(key, {}).get("played"):
            all_done = False

    standings = calculate_standings(candidates, results)
    pb["standings"] = standings
    st.markdown("**Tabla Playoff CONMEBOL:**")
    render_standings_table(standings, advancing=3)
    st.caption("🟢 Top 3 → Mundial | 4to → Repechaje Internacional")

    if all_done:
        if st.button("✅ Confirmar Clasificados CONMEBOL", type="primary"):
            top3 = [s["team"] for s in standings[:3]]
            fourth = standings[3]["team"] if len(standings) > 3 else None
            ca["qualified"] = ca.get("qualified_direct", []) + top3
            if fourth:
                state["playoff_teams"]["conmebol_slot"] = fourth
                st.info(f"🔄 {display_name(fourth)} va al Repechaje Internacional.")
            ca["phase"] = "completado"
            state["world_cup_qualified"] = list(set(state["world_cup_qualified"] + ca["qualified"]))
            st.rerun()


def _show_qualified(state, ca):
    st.markdown("### 🌍 Clasificados CONMEBOL al Mundial FMMJ")
    direct = ca.get("qualified_direct", [])
    playoff_q = [t for t in ca.get("qualified", []) if t not in direct]
    repechaje = state["playoff_teams"].get("conmebol_slot")

    if direct:
        st.markdown("#### ✅ Campeón Copa América (Directo)")
        for t in direct:
            st.markdown(f"{flag_img(t,22,16)}&nbsp;**{display_name(t)}**", unsafe_allow_html=True)
    if playoff_q:
        st.markdown("#### 🔄 Clasificados vía Playoff CONMEBOL")
        for i, t in enumerate(playoff_q, 1):
            st.markdown(f"{i}. {flag_img(t,22,16)}&nbsp;**{display_name(t)}**", unsafe_allow_html=True)
    if repechaje:
        st.markdown(f"#### 🔁 Repechaje Internacional: **{display_name(repechaje)}**")

    total = ca.get("qualified", [])
    if total:
        st.info(f"**Total CONMEBOL clasificados: {len(total)}/4**")

# ============================================================
# CONFEDERACIONES: CAF, CONCACAF, AFC
# ============================================================
# ---------------------------------------------------------------------------
# FUNCIÓN GENÉRICA PARA TORNEOS DE 6 EQUIPOS (2 GRUPOS DE 3)
# ---------------------------------------------------------------------------

def _generic_6team_tournament(state, tournament_key, torneo_name, teams,
                               direct_spots, playoff_spots, repechaje_slot_key):
    """
    6 equipos, 2 grupos de 3.
    Campeón → directo.
    2do-5to → playoff todos contra todos.
    """
    tour = state[tournament_key]

    if not tour.get("setup_done"):
        st.markdown("### 📋 Armado de Grupos")
        _manual_group_setup(state, tournament_key, teams, num_groups=2, teams_per_group=3,
                            confirm_label="Confirmar grupos")
        return

    tabs = st.tabs(["📊 Fase de Grupos", "⚽ Llaves", "🔄 Playoff", "🌍 Clasificados"])

    with tabs[0]:
        _show_6team_groups(state, tour, torneo_name)
    with tabs[1]:
        _show_6team_knockout(state, tour, torneo_name)
    with tabs[2]:
        _show_6team_playoff(state, tour, torneo_name, direct_spots, playoff_spots, repechaje_slot_key)
    with tabs[3]:
        _show_6team_qualified(state, tour, torneo_name, repechaje_slot_key)


def _setup_6team_groups(state, tour, teams):
    ranking = state["ranking"]
    teams_sorted = sorted(teams, key=lambda t: -ranking.get(t, 0))
    random.shuffle(teams_sorted)
    groups = {"A": teams_sorted[:3], "B": teams_sorted[3:6]}
    tour["groups"] = groups
    tour["group_results"] = {}
    tour["group_standings"] = {}
    tour["phase"] = "grupos"
    tour["setup_done"] = True


def _show_6team_groups(state, tour, torneo_name):
    st.markdown("### 📊 Fase de Grupos")
    groups = tour["groups"]
    results = tour.get("group_results", {})
    all_complete = True

    for g, teams in groups.items():
        fixtures = [(teams[i], teams[j]) for i in range(len(teams)) for j in range(i+1, len(teams))]
        with st.expander(f"📋 GRUPO {g}", expanded=True):
            for home, away in fixtures:
                key = match_key(home, away)
                res = results.get(key, {})
                col1,col2,col3,col4,col5 = st.columns([3,1,1,3,1])
                with col1: st.markdown(f"{flag_img(home)}&nbsp;**{display_name(home)}**", unsafe_allow_html=True)
                with col2:
                    hg = st.number_input("", 0, 20, res.get("home_goals", 0), key=f"{torneo_name[:3]}_hg_{g}_{home}_{away}", label_visibility="collapsed")
                with col3:
                    ag = st.number_input("", 0, 20, res.get("away_goals", 0), key=f"{torneo_name[:3]}_ag_{g}_{home}_{away}", label_visibility="collapsed")
                with col4: st.markdown(f"{flag_img(away)}&nbsp;**{display_name(away)}**", unsafe_allow_html=True)
                with col5:
                    save = st.button("💾", key=f"{torneo_name[:3]}_save_{g}_{home}_{away}")
                col_s1, col_s2 = st.columns(2)
                with col_s1:
                    hs = _scorer_input(home, hg, res.get("home_scorers", []), f"{torneo_name[:3]}_hs_{g}_{home}_{away}", state, torneo_name)
                with col_s2:
                    as_ = _scorer_input(away, ag, res.get("away_scorers", []), f"{torneo_name[:3]}_as_{g}_{home}_{away}", state, torneo_name)
                if save:
                    tour["group_results"][key] = {
                        "home_goals": hg, "away_goals": ag, "played": True,
                        "home_scorers": [s.strip() for s in hs.split(",") if s.strip()],
                        "away_scorers": [s.strip() for s in as_.split(",") if s.strip()],
                    }
                    register_scorers(hs, home, state, torneo_name)
                    register_scorers(as_, away, state, torneo_name)
                    st.rerun()
                if not results.get(key, {}).get("played"):
                    all_complete = False
                st.markdown("---")

            standings = calculate_standings(teams, {k: v for k, v in results.items() if any(t in k for t in teams)})
            tour["group_standings"][g] = standings
            render_standings_table(standings, advancing=1)
            st.caption("🟢 1ro → Semifinales")

    if all_complete or st.checkbox(f"🔓 Forzar avance a semis ({torneo_name[:5]})", key=f"force_{torneo_name[:5]}"):
        if tour["phase"] == "grupos":
            if st.button("⚽ Generar Semifinales", type="primary", use_container_width=True, key=f"gen_sf_{torneo_name[:5]}"):
                _build_6team_knockout(state, tour)
                tour["phase"] = "llaves"
                st.rerun()


def _build_6team_knockout(state, tour):
    standings = tour.get("group_standings", {})
    groups = sorted(standings.keys())
    first_A = standings[groups[0]][0]["team"] if standings.get(groups[0]) else None
    second_A = standings[groups[0]][1]["team"] if len(standings.get(groups[0], [])) > 1 else None
    first_B = standings[groups[1]][0]["team"] if standings.get(groups[1]) else None
    second_B = standings[groups[1]][1]["team"] if len(standings.get(groups[1], [])) > 1 else None
    third_A = standings[groups[0]][2]["team"] if len(standings.get(groups[0], [])) > 2 else None
    third_B = standings[groups[1]][2]["team"] if len(standings.get(groups[1], [])) > 2 else None

    # Semifinales: 1A vs 2B, 1B vs 2A
    tour["knockout_bracket"] = {
        "semis": [
            {"home": first_A, "away": second_B, "winner": None},
            {"home": first_B, "away": second_A, "winner": None},
        ],
        "tercer_puesto": [],
        "final": [],
    }
    tour["knockout_results"] = {}
    # Playoff: los eliminados en semis + 3ros de grupo
    tour["playoff_pool"] = [second_A, second_B, third_A, third_B]
    tour["playoff_pool"] = [t for t in tour["playoff_pool"] if t]


def _show_6team_knockout(state, tour, torneo_name):
    st.markdown("### ⚽ Fase de Eliminación")
    bracket = tour.get("knockout_bracket", {})
    if not bracket:
        st.info("Completa la fase de grupos primero.")
        return
    results = tour.get("knockout_results", {})
    if results is None:
        tour["knockout_results"] = {}
        results = tour["knockout_results"]

    phases = [("semis", "🟠 Semifinales", "final"), ("final", "🏆 Final", None)]

    for phase_key, phase_name, next_phase in phases:
        matches = bracket.get(phase_key, [])
        if not matches: continue
        st.markdown(f"#### {phase_name}")
        all_done = True

        for idx, match in enumerate(matches):
            home, away = match["home"], match["away"]
            if not home or not away: continue
            key = f"{torneo_name[:3]}_{phase_key}_{idx}"
            res = results.get(key, {})

            col1,col2,col3,col4,col5,col6 = st.columns([3,1,1,3,2,1])
            with col1: st.markdown(f"{flag_img(home)}&nbsp;**{display_name(home)}**", unsafe_allow_html=True)
            with col2:
                hg = st.number_input("", 0, 20, res.get("home_goals", 0), key=f"{key}_hg", label_visibility="collapsed")
            with col3:
                ag = st.number_input("", 0, 20, res.get("away_goals", 0), key=f"{key}_ag", label_visibility="collapsed")
            with col4: st.markdown(f"{flag_img(away)}&nbsp;**{display_name(away)}**", unsafe_allow_html=True)
            with col5:
                if hg == ag:
                    pen_sel = st.selectbox("Penales", ["—", display_name(home), display_name(away)], key=f"{key}_pen")
                    pen_winner = home if pen_sel == display_name(home) else (away if pen_sel == display_name(away) else None)
                else:
                    pen_winner = None; st.empty()
            with col6:
                save = st.button("💾", key=f"{key}_save")

            col_s1, col_s2 = st.columns(2)
            with col_s1:
                hs = _scorer_input(home, hg, res.get("home_scorers", []), f"{key}_hs", state, torneo_name)
            with col_s2:
                as_ = _scorer_input(away, ag, res.get("away_scorers", []), f"{key}_as", state, torneo_name)

            if save:
                winner = home if hg > ag else (away if ag > hg else pen_winner)
                results[key] = {"home_goals": hg, "away_goals": ag, "winner": winner, "penalty_winner": pen_winner,
                                "home_scorers": [s.strip() for s in hs.split(",") if s.strip()],
                                "away_scorers": [s.strip() for s in as_.split(",") if s.strip()]}
                tour["knockout_bracket"][phase_key][idx]["winner"] = winner
                register_scorers(hs, home, state, torneo_name)
                register_scorers(as_, away, state, torneo_name)
                st.rerun()

            if res.get("winner"):
                st.markdown(f"**✅ Ganador: {flag_img(res['winner'],18,13)}{display_name(res['winner'])}**", unsafe_allow_html=True)
            else:
                all_done = False
            st.markdown("---")

        if all_done and next_phase and not bracket.get(next_phase):
            winners = [results.get(f"{torneo_name[:3]}_{phase_key}_{i}", {}).get("winner") for i in range(len(matches))]
            winners = [w for w in winners if w]
            if phase_key == "semis":
                losers = []
                for i, m in enumerate(matches):
                    r = results.get(f"{torneo_name[:3]}_semis_{i}", {})
                    loser = m["home"] if r.get("winner") == m["away"] else m["away"]
                    if loser: losers.append(loser)
                bracket["tercer_puesto"] = [{"home": losers[0], "away": losers[1], "winner": None}] if len(losers) == 2 else []
                # Agregar losers al playoff pool
                existing = tour.get("playoff_pool", [])
                for l in losers:
                    if l and l not in existing:
                        existing.append(l)
                tour["playoff_pool"] = existing
            bracket[next_phase] = [{"home": winners[i], "away": winners[i+1], "winner": None} for i in range(0, len(winners)-1, 2)]
            tour["knockout_results"] = results
            st.rerun()

        if all_done and phase_key == "final":
            champion = results.get(f"{torneo_name[:3]}_final_0", {}).get("winner")
            if champion:
                tour["champion"] = champion
                tour["qualified_direct"] = [champion]
                tour["phase"] = "playoff"

    # Tercer puesto
    if bracket.get("tercer_puesto"):
        st.markdown("#### 🥉 Tercer Puesto")
        for idx, m in enumerate(bracket["tercer_puesto"]):
            home, away = m["home"], m["away"]
            key = f"{torneo_name[:3]}_tercer_{idx}"
            res = results.get(key, {})
            col1,col2,col3,col4,col5,col6 = st.columns([3,1,1,3,2,1])
            with col1: st.markdown(f"{flag_img(home)}&nbsp;**{display_name(home)}**", unsafe_allow_html=True)
            with col2:
                hg = st.number_input("", 0, 20, res.get("home_goals", 0), key=f"{key}_hg", label_visibility="collapsed")
            with col3:
                ag = st.number_input("", 0, 20, res.get("away_goals", 0), key=f"{key}_ag", label_visibility="collapsed")
            with col4: st.markdown(f"{flag_img(away)}&nbsp;**{display_name(away)}**", unsafe_allow_html=True)
            with col5:
                if hg == ag:
                    p = st.selectbox("Penales", ["—", display_name(home), display_name(away)], key=f"{key}_pen")
                    pw = home if p == display_name(home) else (away if p == display_name(away) else None)
                else:
                    pw = None; st.empty()
            with col6:
                if st.button("💾", key=f"{key}_save"):
                    winner = home if hg > ag else (away if ag > hg else pw)
                    results[key] = {"home_goals": hg, "away_goals": ag, "winner": winner}
                    bracket["tercer_puesto"][idx]["winner"] = winner
                    tour["knockout_results"] = results
                    st.rerun()
            if res.get("winner"):
                st.markdown(f"**🥉 3er Lugar: {display_name(res['winner'])}**")


def _show_6team_playoff(state, tour, torneo_name, direct_spots, playoff_spots, repechaje_slot_key):
    st.markdown("### 🔄 Playoff")
    if tour.get("phase") not in ["playoff", "completado"]:
        st.info("Esta fase se habilita al concluir las llaves.")
        return

    candidates = tour.get("playoff_pool", [])
    if not candidates:
        st.warning("No hay candidatos.")
        return

    pb = tour.get("playoff_bracket", {})
    if not pb:
        pb = {"results": {}, "standings": {}}
        tour["playoff_bracket"] = pb

    results = pb.get("results", {})
    fixtures = [(candidates[i], candidates[j]) for i in range(len(candidates)) for j in range(i+1, len(candidates))]
    all_done = True

    for home, away in fixtures:
        key = match_key(home, away)
        res = results.get(key, {})
        col1,col2,col3,col4,col5 = st.columns([3,1,1,3,1])
        with col1: st.markdown(f"{flag_img(home)}&nbsp;**{display_name(home)}**", unsafe_allow_html=True)
        with col2:
            hg = st.number_input("", 0, 20, res.get("home_goals", 0), key=f"pb_{torneo_name[:3]}_{home}_{away}_hg", label_visibility="collapsed")
        with col3:
            ag = st.number_input("", 0, 20, res.get("away_goals", 0), key=f"pb_{torneo_name[:3]}_{home}_{away}_ag", label_visibility="collapsed")
        with col4: st.markdown(f"{flag_img(away)}&nbsp;**{display_name(away)}**", unsafe_allow_html=True)
        with col5:
            if st.button("💾", key=f"pb_{torneo_name[:3]}_{home}_{away}_save"):
                results[key] = {"home_goals": hg, "away_goals": ag, "played": True}
                pb["results"] = results
                st.rerun()
        if not results.get(key, {}).get("played"):
            all_done = False

    standings = calculate_standings(candidates, results)
    pb["standings"] = standings
    render_standings_table(standings, advancing=playoff_spots)

    if all_done:
        repechaje_idx = playoff_spots
        st.markdown(f"🟢 Top {playoff_spots} → Mundial | Pos {playoff_spots+1} → Repechaje")
        if st.button(f"✅ Confirmar Clasificados {torneo_name[:10]}", type="primary", key=f"confirm_{torneo_name[:5]}"):
            top_n = [s["team"] for s in standings[:playoff_spots]]
            repechaje = standings[repechaje_idx]["team"] if len(standings) > repechaje_idx else None
            tour["qualified"] = tour.get("qualified_direct", []) + top_n
            if repechaje and repechaje_slot_key:
                state["playoff_teams"][repechaje_slot_key] = repechaje
            tour["phase"] = "completado"
            state["world_cup_qualified"] = list(set(state["world_cup_qualified"] + tour["qualified"]))
            st.rerun()


def _show_6team_qualified(state, tour, torneo_name, repechaje_slot_key):
    st.markdown(f"### 🌍 Clasificados al Mundial — {torneo_name}")
    direct = tour.get("qualified_direct", [])
    playoff_q = [t for t in tour.get("qualified", []) if t not in direct]
    repechaje = state["playoff_teams"].get(repechaje_slot_key) if repechaje_slot_key else None

    if direct:
        st.markdown("#### ✅ Campeón (Directo)")
        for t in direct:
            st.markdown(f"{flag_img(t,22,16)}&nbsp;**{display_name(t)}**", unsafe_allow_html=True)
    if playoff_q:
        st.markdown("#### 🔄 Playoff")
        for i, t in enumerate(playoff_q, 1):
            st.markdown(f"{i}. {flag_img(t,22,16)}&nbsp;**{display_name(t)}**", unsafe_allow_html=True)
    if repechaje:
        st.markdown(f"#### 🔁 Repechaje: **{display_name(repechaje)}**")

    total = tour.get("qualified", [])
    if total:
        st.info(f"**Clasificados: {len(total)}**")


# ---------------------------------------------------------------------------
# COPA ÁFRICA (CAF) - 10 equipos, 2 grupos de 5
# ---------------------------------------------------------------------------
def show_copa_africa():
    state = get_state()
    tour = state["copa_africa"]
    host = state.get("host", "Nigeria")

    st.markdown("""
    <style>
    .caf-header {background:linear-gradient(135deg,#b8860b 0%,#daa520 50%,#8b6914 100%);
    border-radius:16px;padding:24px 32px;margin-bottom:24px;box-shadow:0 8px 32px rgba(184,134,11,.4);}
    .caf-title {font-size:2rem;font-weight:800;color:#fff;margin:0;}
    .caf-subtitle {font-size:.9rem;color:#fff3a0;margin:4px 0 0;}
    </style>
    """, unsafe_allow_html=True)
    col_logo, col_title = st.columns([1, 6])
    with col_logo:
        st.image("caf.png", width=80)
    with col_title:
        st.markdown(f"""
        <div class='caf-header' style='margin-bottom:0;'>
            <div class='caf-title'>Copa África FMMJ</div>
            <div class='caf-subtitle'>{len(CAF_TEAMS)} selecciones CAF · 2 grupos de 5 · 5 cupos al Mundial</div>
        </div>""", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # El anfitrión participa normalmente pero si clasifica cede su cupo al siguiente
    if host in CAF_TEAMS:
        st.info(
            f"🏠 **{display_name(host)}** es el anfitrión del Mundial y participa en la Copa África normalmente. "
            f"Si clasifica entre los 5 primeros, su cupo pasa al siguiente en la tabla."
        )

    _show_10team_caf_tournament(state, tour, CAF_TEAMS)


def _show_10team_caf_tournament(state, tour, teams):
    """Copa África: 10 equipos, 2 grupos de 5"""
    
    if not tour.get("setup_done"):
        st.markdown("### 📋 Armado de Grupos — Copa África FMMJ")
        teams_per_g = 5 if len(teams) == 10 else (len(teams)+1)//2
        _manual_group_setup(state, "copa_africa", teams, num_groups=2,
                            teams_per_group=teams_per_g,
                            confirm_label="Confirmar grupos Copa África")
        return

    tabs = st.tabs(["📊 Grupos", "⚽ Llaves", "🔄 Playoff CAF", "🌍 Clasificados"])
    with tabs[0]: _show_caf_groups(state, tour, TORNEO_NAME)
    with tabs[1]: _show_caf_knockout(state, tour, TORNEO_NAME)
    with tabs[2]: _show_caf_playoff(state, tour, TORNEO_NAME)
    with tabs[3]: _show_caf_qualified(state, tour)


def _setup_caf_groups(state, tour, teams):
    """
    CAF puede tener 10 equipos (2 grupos de 5) o 9 equipos si el anfitrión
    es de CAF (grupos de 5 y 4). El cuadro de llaves se arma con top 2 de
    cada grupo en ambos casos.
    """
    ranking = state["ranking"]
    teams_sorted = sorted(teams, key=lambda t: -ranking.get(t, 0))
    random.shuffle(teams_sorted)
    n = len(teams_sorted)
    mid = (n + 1) // 2   # 5 si n=9 o 10; grupo A siempre igual o mayor
    groups = {"A": teams_sorted[:mid], "B": teams_sorted[mid:n]}
    tour["groups"] = groups
    tour["group_results"] = {}
    tour["group_standings"] = {}
    tour["phase"] = "grupos"
    tour["setup_done"] = True


def _show_caf_groups(state, tour, torneo_name):
    st.markdown("### 📊 Fase de Grupos — Copa África")
    groups = tour["groups"]
    results = tour.get("group_results", {})
    all_complete = True

    for g, teams in groups.items():
        fixtures = [(teams[i], teams[j]) for i in range(len(teams)) for j in range(i+1, len(teams))]
        with st.expander(f"📋 GRUPO {g}", expanded=True):
            for home, away in fixtures:
                key = match_key(home, away)
                res = results.get(key, {})
                col1,col2,col3,col4,col5 = st.columns([3,1,1,3,1])
                with col1: st.markdown(f"{flag_img(home)}&nbsp;**{display_name(home)}**", unsafe_allow_html=True)
                with col2:
                    hg = st.number_input("", 0, 20, res.get("home_goals", 0), key=f"caf_hg_{g}_{home}_{away}", label_visibility="collapsed")
                with col3:
                    ag = st.number_input("", 0, 20, res.get("away_goals", 0), key=f"caf_ag_{g}_{home}_{away}", label_visibility="collapsed")
                with col4: st.markdown(f"{flag_img(away)}&nbsp;**{display_name(away)}**", unsafe_allow_html=True)
                with col5:
                    save = st.button("💾", key=f"caf_save_{g}_{home}_{away}")
                col_s1, col_s2 = st.columns(2)
                with col_s1:
                    hs = _scorer_input(home, hg, res.get("home_scorers", []), f"caf_hs_{g}_{home}_{away}", state, "Copa África FMMJ")
                with col_s2:
                    as_ = _scorer_input(away, ag, res.get("away_scorers", []), f"caf_as_{g}_{home}_{away}", state, "Copa África FMMJ")
                if save:
                    tour["group_results"][key] = {
                        "home_goals": hg, "away_goals": ag, "played": True,
                        "home_scorers": [s.strip() for s in hs.split(",") if s.strip()],
                        "away_scorers": [s.strip() for s in as_.split(",") if s.strip()],
                    }
                    register_scorers(hs, home, state, torneo_name)
                    register_scorers(as_, away, state, torneo_name)
                    st.rerun()
                if not results.get(key, {}).get("played"):
                    all_complete = False
                st.markdown("---")

            standings = calculate_standings(teams, {k: v for k, v in results.items() if any(t in k for t in teams)})
            tour["group_standings"][g] = standings
            render_standings_table(standings, advancing=2)
            st.caption("🟢 Top 2 → Cuartos de Final")

    if all_complete or st.checkbox("🔓 Forzar avance Copa África"):
        if tour["phase"] == "grupos":
            if st.button("⚽ Generar Cuartos de Final CAF", type="primary", use_container_width=True):
                _build_caf_knockout(state, tour)
                tour["phase"] = "llaves"
                st.rerun()


def _build_caf_knockout(state, tour):
    standings = tour.get("group_standings", {})
    groups = sorted(standings.keys())
    top4 = []
    thirds = []
    rest = []
    for g in groups:
        s = standings[g]
        if len(s) >= 1: top4.append(s[0]["team"])
        if len(s) >= 2: top4.append(s[1]["team"])
        if len(s) >= 3: thirds.append(s[2]["team"])
        for t in s[3:]:
            rest.append(t["team"])

    # Cuartos: 1A vs 2B, 1B vs 2A
    qf = [(top4[0], top4[3]), (top4[1], top4[2])]
    tour["knockout_bracket"] = {
        "cuartos": [{"home": m[0], "away": m[1], "winner": None} for m in qf],
        "semis": [],
        "tercer_puesto": [],
        "final": [],
    }
    tour["knockout_results"] = {}
    tour["playoff_pool"] = thirds + rest


def _show_caf_knockout(state, tour, torneo_name):
    st.markdown("### ⚽ Fase de Eliminación — Copa África")
    bracket = tour.get("knockout_bracket", {})
    if not bracket:
        st.info("Completa grupos primero.")
        return
    results = tour.get("knockout_results", {})
    if results is None:
        tour["knockout_results"] = {}
        results = tour["knockout_results"]

    phases = [("cuartos", "🟡 Cuartos de Final", "semis"), ("semis", "🟠 Semifinales", "final"), ("final", "🏆 Final", None)]

    for phase_key, phase_name, next_phase in phases:
        matches = bracket.get(phase_key, [])
        if not matches: continue
        st.markdown(f"#### {phase_name}")
        all_done = True

        for idx, match in enumerate(matches):
            home, away = match["home"], match["away"]
            if not home or not away: all_done = False; continue
            key = f"caf_{phase_key}_{idx}"
            res = results.get(key, {})

            col1,col2,col3,col4,col5,col6 = st.columns([3,1,1,3,2,1])
            with col1: st.markdown(f"{flag_img(home)}&nbsp;**{display_name(home)}**", unsafe_allow_html=True)
            with col2:
                hg = st.number_input("", 0, 20, res.get("home_goals", 0), key=f"{key}_hg", label_visibility="collapsed")
            with col3:
                ag = st.number_input("", 0, 20, res.get("away_goals", 0), key=f"{key}_ag", label_visibility="collapsed")
            with col4: st.markdown(f"{flag_img(away)}&nbsp;**{display_name(away)}**", unsafe_allow_html=True)
            with col5:
                if hg == ag:
                    ps = st.selectbox("Penales", ["—", display_name(home), display_name(away)], key=f"{key}_pen")
                    pw = home if ps == display_name(home) else (away if ps == display_name(away) else None)
                else:
                    pw = None; st.empty()
            with col6:
                save = st.button("💾", key=f"{key}_save")

            col_s1, col_s2 = st.columns(2)
            with col_s1:
                hs = _scorer_input(home, hg, res.get("home_scorers", []), f"{key}_hs", state, torneo_name)
            with col_s2:
                as_ = _scorer_input(away, ag, res.get("away_scorers", []), f"{key}_as", state, torneo_name)

            if save:
                winner = home if hg > ag else (away if ag > hg else pw)
                results[key] = {"home_goals": hg, "away_goals": ag, "winner": winner, "penalty_winner": pw,
                                "home_scorers": [s.strip() for s in hs.split(",") if s.strip()],
                                "away_scorers": [s.strip() for s in as_.split(",") if s.strip()]}
                tour["knockout_bracket"][phase_key][idx]["winner"] = winner
                register_scorers(hs, home, state, torneo_name)
                register_scorers(as_, away, state, torneo_name)
                st.rerun()

            if res.get("winner"):
                st.markdown(f"**✅ {display_name(res['winner'])}**")
            else:
                all_done = False
            st.markdown("---")

        if all_done and next_phase and not bracket.get(next_phase):
            winners = [results.get(f"caf_{phase_key}_{i}", {}).get("winner") for i in range(len(matches))]
            winners = [w for w in winners if w]
            if phase_key == "semis":
                losers = []
                for i, m in enumerate(matches):
                    r = results.get(f"caf_semis_{i}", {})
                    loser = m["home"] if r.get("winner") == m["away"] else m["away"]
                    if loser: losers.append(loser)
                bracket["tercer_puesto"] = [{"home": losers[0], "away": losers[1], "winner": None}] if len(losers) == 2 else []
                pool = tour.get("playoff_pool", [])
                for l in losers:
                    if l not in pool: pool.append(l)
                tour["playoff_pool"] = pool
            if phase_key == "cuartos":
                losers_qf = []
                for i, m in enumerate(matches):
                    r = results.get(f"caf_cuartos_{i}", {})
                    loser = m["home"] if r.get("winner") == m["away"] else m["away"]
                    if loser: losers_qf.append(loser)
                pool = tour.get("playoff_pool", [])
                for l in losers_qf:
                    if l not in pool: pool.append(l)
                tour["playoff_pool"] = pool
            nxt = [(winners[i], winners[i+1]) for i in range(0, len(winners)-1, 2)]
            bracket[next_phase] = [{"home": m[0], "away": m[1], "winner": None} for m in nxt]
            tour["knockout_results"] = results
            st.rerun()

        if all_done and phase_key == "final":
            res_final = results.get("caf_final_0", {})
            finalist_winner = res_final.get("winner")
            finalist_loser = None
            for m in bracket.get("final", []):
                if m.get("winner"):
                    finalist_loser = m["home"] if m["winner"] == m["away"] else m["away"]
            if finalist_winner:
                tour["champion"] = finalist_winner
                tour["finalist"] = finalist_loser
                tour["qualified_direct"] = [finalist_winner, finalist_loser] if finalist_loser else [finalist_winner]
                tour["phase"] = "playoff"

    # Tercer puesto
    if bracket.get("tercer_puesto"):
        st.markdown("#### 🥉 Tercer Puesto")
        for idx, m in enumerate(bracket["tercer_puesto"]):
            home, away = m["home"], m["away"]
            key = f"caf_tercer_{idx}"
            res = results.get(key, {})
            col1,col2,col3,col4,col5,col6 = st.columns([3,1,1,3,2,1])
            with col1: st.markdown(f"{flag_img(home)}&nbsp;**{display_name(home)}**", unsafe_allow_html=True)
            with col2:
                hg = st.number_input("", 0, 20, res.get("home_goals", 0), key=f"{key}_hg", label_visibility="collapsed")
            with col3:
                ag = st.number_input("", 0, 20, res.get("away_goals", 0), key=f"{key}_ag", label_visibility="collapsed")
            with col4: st.markdown(f"{flag_img(away)}&nbsp;**{display_name(away)}**", unsafe_allow_html=True)
            with col5:
                if hg == ag:
                    p = st.selectbox("Penales", ["—", display_name(home), display_name(away)], key=f"{key}_pen")
                    pw = home if p == display_name(home) else (away if p == display_name(away) else None)
                else:
                    pw = None; st.empty()
            with col6:
                if st.button("💾", key=f"{key}_save"):
                    winner = home if hg > ag else (away if ag > hg else pw)
                    results[key] = {"home_goals": hg, "away_goals": ag, "winner": winner}
                    bracket["tercer_puesto"][idx]["winner"] = winner
                    tour["knockout_results"] = results
                    st.rerun()
            if res.get("winner"):
                st.markdown(f"**🥉 3er Lugar: {display_name(res['winner'])}**")


def _show_caf_playoff(state, tour, torneo_name):
    st.markdown("### 🔄 Playoff CAF — 3 cupos adicionales")
    st.caption("3ro-7mo Copa África: todos contra todos. Top 3 → Mundial.")
    if tour.get("phase") not in ["playoff", "completado"]:
        st.info("Se habilita al terminar las llaves.")
        return

    candidates = tour.get("playoff_pool", [])
    if not candidates:
        st.warning("No hay candidatos.")
        return

    pb = tour.get("playoff_bracket", {})
    if not pb:
        pb = {"results": {}, "standings": {}}
        tour["playoff_bracket"] = pb

    results = pb.get("results", {})
    fixtures = [(candidates[i], candidates[j]) for i in range(len(candidates)) for j in range(i+1, len(candidates))]
    all_done = True

    for home, away in fixtures:
        key = match_key(home, away)
        res = results.get(key, {})
        col1,col2,col3,col4,col5 = st.columns([3,1,1,3,1])
        with col1: st.markdown(f"{flag_img(home)}&nbsp;**{display_name(home)}**", unsafe_allow_html=True)
        with col2:
            hg = st.number_input("", 0, 20, res.get("home_goals", 0), key=f"cafp_{home}_{away}_hg", label_visibility="collapsed")
        with col3:
            ag = st.number_input("", 0, 20, res.get("away_goals", 0), key=f"cafp_{home}_{away}_ag", label_visibility="collapsed")
        with col4: st.markdown(f"{flag_img(away)}&nbsp;**{display_name(away)}**", unsafe_allow_html=True)
        with col5:
            if st.button("💾", key=f"cafp_{home}_{away}_save"):
                results[key] = {"home_goals": hg, "away_goals": ag, "played": True}
                pb["results"] = results
                st.rerun()
        if not results.get(key, {}).get("played"):
            all_done = False

    standings = calculate_standings(candidates, results)
    pb["standings"] = standings
    render_standings_table(standings, advancing=3)

    if all_done:
        if st.button("✅ Confirmar Clasificados CAF", type="primary"):
            top3 = [s["team"] for s in standings[:3]]
            tour["qualified"] = tour.get("qualified_direct", []) + top3
            tour["phase"] = "completado"
            state["world_cup_qualified"] = list(set(state["world_cup_qualified"] + tour["qualified"]))
            st.rerun()


def _show_caf_qualified(state, tour):
    st.markdown("### 🌍 Clasificados CAF al Mundial FMMJ")
    host = state.get("host", "Nigeria")
    if host in CAF_TEAMS:
        st.markdown(f"🏠 **{display_name(host)}** — Anfitrión (clasificado directo)")

    direct = tour.get("qualified_direct", [])
    playoff_q = [t for t in tour.get("qualified", []) if t not in direct]

    if direct:
        st.markdown("#### ✅ Campeón y Subcampeón (Directos)")
        for t in direct:
            st.markdown(f"{flag_img(t,22,16)}&nbsp;**{display_name(t)}**", unsafe_allow_html=True)
    if playoff_q:
        st.markdown("#### 🔄 Playoff CAF")
        for i, t in enumerate(playoff_q, 1):
            st.markdown(f"{i}. {flag_img(t,22,16)}&nbsp;**{display_name(t)}**", unsafe_allow_html=True)

    total = tour.get("qualified", [])
    host_count = 1 if host in CAF_TEAMS else 0
    st.info(f"**Total CAF al Mundial: {len(total) + host_count}/5** (incluyendo anfitrión)" if host in CAF_TEAMS
            else f"**Total CAF: {len(total)}/5**")


# ---------------------------------------------------------------------------
# COPA ORO — CONCACAF
# ---------------------------------------------------------------------------
def show_copa_oro():
    state = get_state()
    tour = state["copa_oro"]

    st.markdown("""
    <style>
    .concacaf-header {background:linear-gradient(135deg,#8b0000 0%,#cc2200 50%,#6b0000 100%);
    border-radius:16px;padding:24px 32px;margin-bottom:24px;box-shadow:0 8px 32px rgba(139,0,0,.4);}
    .concacaf-title {font-size:2rem;font-weight:800;color:#ffd700;margin:0;}
    .concacaf-subtitle {font-size:.9rem;color:#ffaaaa;margin:4px 0 0;}
    </style>""", unsafe_allow_html=True)
    col_logo, col_title = st.columns([1, 6])
    with col_logo:
        st.image("concacaf.png", width=80)
    with col_title:
        st.markdown("""
        <div class='concacaf-header' style='margin-bottom:0;'>
            <div class='concacaf-title'>Copa Oro FMMJ</div>
            <div class='concacaf-subtitle'>6 selecciones CONCACAF · 2 grupos de 3 · 3 cupos al Mundial</div>
        </div>""", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    st.caption("Campeón → directo. 2do-5to → playoff todos contra todos. Top 2 playoff → Mundial. 3ro → Repechaje.")
    _generic_6team_tournament(state, "copa_oro", "Copa Oro FMMJ", CONCACAF_TEAMS,
                              direct_spots=1, playoff_spots=2, repechaje_slot_key="concacaf_slot")


# ---------------------------------------------------------------------------
# COPA ASIA — AFC
# ---------------------------------------------------------------------------
def show_copa_asia():
    state = get_state()
    tour = state["copa_asia"]

    st.markdown("""
    <style>
    .afc-header {background:linear-gradient(135deg,#4a0080 0%,#7700cc 50%,#330060 100%);
    border-radius:16px;padding:24px 32px;margin-bottom:24px;box-shadow:0 8px 32px rgba(74,0,128,.4);}
    .afc-title {font-size:2rem;font-weight:800;color:#ffd700;margin:0;}
    .afc-subtitle {font-size:.9rem;color:#ddaaff;margin:4px 0 0;}
    </style>""", unsafe_allow_html=True)
    col_logo, col_title = st.columns([1, 6])
    with col_logo:
        st.image("afc.png", width=80)
    with col_title:
        st.markdown("""
        <div class='afc-header' style='margin-bottom:0;'>
            <div class='afc-title'>Copa Asia FMMJ</div>
            <div class='afc-subtitle'>6 selecciones AFC · 2 grupos de 3 · 4 cupos al Mundial</div>
        </div>""", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    st.caption("Campeón → directo. 2do-5to → playoff todos contra todos. Top 3 playoff → Mundial. 4to → Repechaje.")
    _generic_6team_tournament(state, "copa_asia", "Copa Asia FMMJ", AFC_TEAMS,
                              direct_spots=1, playoff_spots=3, repechaje_slot_key="afc_slot")

# ============================================================
# REPECHAJE + RANKING + MUNDIAL
# ============================================================
# ---------------------------------------------------------------------------
# REPECHAJE INTERNACIONAL
# ---------------------------------------------------------------------------
def show_repechaje():
    state = get_state()
    playoff = state["playoff_teams"]

    st.markdown("""
    <style>
    .rep-header {background:linear-gradient(135deg,#1a1a1a 0%,#333 50%,#1a1a1a 100%);
    border:2px solid #ffd700;border-radius:16px;padding:24px 32px;margin-bottom:24px;}
    .rep-title {font-size:1.8rem;font-weight:800;color:#ffd700;}
    .rep-subtitle {color:#aaa;font-size:.9rem;}
    .playoff-card {background:#111;border:1px solid #333;border-radius:12px;padding:16px;margin-bottom:12px;}
    .playoff-title {font-size:1rem;font-weight:700;color:#ffd700;margin-bottom:10px;}
    .winner-announce {background:#0d4f2e;border-radius:8px;padding:10px;color:#4eff91;font-weight:700;font-size:1rem;}
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""<div class='rep-header'>
        <div class='rep-title'>🔁 Repechaje Internacional FMMJ</div>
        <div class='rep-subtitle'>2 llaves de ida y vuelta · 2 cupos al Mundial</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("""
    **Sistema de Repechaje:**
    - 🌎 **Llave 1:** CONMEBOL vs OFC (Nueva Zelanda)
    - 🌏 **Llave 2:** CONCACAF vs AFC
    - Partidos de ida y vuelta. El global define al clasificado.
    """)

    conmebol_team = playoff.get("conmebol_slot")
    ofc_team = playoff.get("ofc_slot", "New Zealand")
    concacaf_team = playoff.get("concacaf_slot")
    afc_team = playoff.get("afc_slot")

    tabs = st.tabs(["🌎 Llave 1: CONMEBOL vs OFC", "🌏 Llave 2: CONCACAF vs AFC", "✅ Resultados"])

    # ── LLAVE 1 ────────────────────────────────────────────────────────────
    with tabs[0]:
        st.markdown("### 🌎 Llave 1: CONMEBOL vs OFC")
        if not conmebol_team:
            st.warning("⏳ Esperando clasificado CONMEBOL del Playoff Copa América (4to lugar).")
            st.info(f"OFC: **{display_name(ofc_team)}** ✅")
        else:
            st.info(f"**{display_name(conmebol_team)}** (CONMEBOL) vs **{display_name(ofc_team)}** (OFC/Nueva Zelanda)")
            _show_playoff_tie(state, "llave1", conmebol_team, ofc_team, "mundial_slot_1")

    # ── LLAVE 2 ────────────────────────────────────────────────────────────
    with tabs[1]:
        st.markdown("### 🌏 Llave 2: CONCACAF vs AFC")
        if not concacaf_team:
            st.warning("⏳ Esperando clasificado CONCACAF del Playoff Copa Oro (3er lugar).")
        elif not afc_team:
            st.warning("⏳ Esperando clasificado AFC del Playoff Copa Asia (4to lugar).")
        else:
            st.info(f"**{display_name(concacaf_team)}** (CONCACAF) vs **{display_name(afc_team)}** (AFC)")
            _show_playoff_tie(state, "llave2", concacaf_team, afc_team, "mundial_slot_2")

    # ── RESULTADOS ─────────────────────────────────────────────────────────
    with tabs[2]:
        st.markdown("### ✅ Clasificados vía Repechaje")
        slot1 = state["playoff_results"].get("mundial_slot_1")
        slot2 = state["playoff_results"].get("mundial_slot_2")

        if slot1:
            st.markdown(f"<div class='winner-announce'>🎉 Clasificado Llave 1: {flag_img(slot1,24,18)}&nbsp;{display_name(slot1)}</div>", unsafe_allow_html=True)
        else:
            st.markdown("⏳ Llave 1 pendiente")

        if slot2:
            st.markdown(f"<div class='winner-announce'>🎉 Clasificado Llave 2: {flag_img(slot2,24,18)}&nbsp;{display_name(slot2)}</div>", unsafe_allow_html=True)
        else:
            st.markdown("⏳ Llave 2 pendiente")

        if slot1 and slot2:
            st.balloons()
            st.success("✅ ¡Todos los clasificados al Mundial FMMJ están definidos!")
            # Añadir a clasificados
            for t in [slot1, slot2]:
                if t and t not in state["world_cup_qualified"]:
                    state["world_cup_qualified"].append(t)


def _show_playoff_tie(state, tie_key, home_team, away_team, slot_key):
    """Partidos de ida y vuelta"""
    pr = state.get("playoff_results", {})
    if not pr:
        state["playoff_results"] = {}
        pr = state["playoff_results"]

    for leg, leg_name in [("ida", "⚽ Partido de Ida"), ("vuelta", "⚽ Partido de Vuelta")]:
        st.markdown(f"#### {leg_name}")
        if leg == "ida":
            h, a = home_team, away_team
        else:
            h, a = away_team, home_team

        key = f"{tie_key}_{leg}"
        res = pr.get(key, {})

        col1,col2,col3,col4,col5 = st.columns([3,1,1,3,1])
        with col1: st.markdown(f"{flag_img(h)}&nbsp;**{display_name(h)}**", unsafe_allow_html=True)
        with col2:
            hg = st.number_input("", 0, 20, res.get("home_goals", 0), key=f"rep_{key}_hg", label_visibility="collapsed")
        with col3:
            ag = st.number_input("", 0, 20, res.get("away_goals", 0), key=f"rep_{key}_ag", label_visibility="collapsed")
        with col4: st.markdown(f"{flag_img(a)}&nbsp;**{display_name(a)}**", unsafe_allow_html=True)
        with col5:
            save = st.button("💾", key=f"rep_{key}_save")

        col_s1, col_s2 = st.columns(2)
        with col_s1:
            hs_v = st.text_input(f"⚽ {display_name(h)}", value=", ".join(res.get("home_scorers", [])), key=f"rep_{key}_hs")
        with col_s2:
            as_v = st.text_input(f"⚽ {display_name(a)}", value=", ".join(res.get("away_scorers", [])), key=f"rep_{key}_as")

        if save:
            pr[key] = {
                "home": h, "away": a,
                "home_goals": hg, "away_goals": ag, "played": True,
                "home_scorers": [s.strip() for s in hs_v.split(",") if s.strip()],
                "away_scorers": [s.strip() for s in as_v.split(",") if s.strip()],
            }
            state["playoff_results"] = pr
            st.rerun()

        if res.get("played"):
            st.markdown(f"*Resultado: {display_name(h)} {res['home_goals']} - {res['away_goals']} {display_name(a)}*")

    # Calcular global
    ida = pr.get(f"{tie_key}_ida", {})
    vuelta = pr.get(f"{tie_key}_vuelta", {})

    if ida.get("played") and vuelta.get("played"):
        # home_team goles totales
        home_total = ida.get("home_goals", 0) + vuelta.get("away_goals", 0)
        away_total = ida.get("away_goals", 0) + vuelta.get("home_goals", 0)

        st.markdown(f"""
        ---
        **Global:** {flag_img(home_team)}{display_name(home_team)} **{home_total}** - **{away_total}** {display_name(away_team)}{flag_img(away_team)}
        """, unsafe_allow_html=True)

        if home_total != away_total:
            winner = home_team if home_total > away_total else away_team
            st.success(f"🎉 **Clasificado: {display_name(winner)}**")
            pr[slot_key] = winner
            state["playoff_results"] = pr
        else:
            # Penales
            st.warning("⚠️ Empate en el global → Penales en la vuelta")
            pen_opts = ["— Elegir —", display_name(home_team), display_name(away_team)]
            pen_sel = st.selectbox("Ganador en penales:", pen_opts, key=f"rep_{tie_key}_pen_global")
            if pen_sel != "— Elegir —":
                winner = home_team if pen_sel == display_name(home_team) else away_team
                if st.button(f"✅ Confirmar: {display_name(winner)}", key=f"rep_{tie_key}_pen_confirm"):
                    pr[slot_key] = winner
                    state["playoff_results"] = pr
                    st.rerun()


# ---------------------------------------------------------------------------
# RANKING FMMJ
# ---------------------------------------------------------------------------
def show_ranking():
    state = get_state()

    st.markdown("""
    <style>
    .ranking-header {background:linear-gradient(135deg,#0a0a1a 0%,#1a1a3e 100%);
    border:2px solid #c8a000;border-radius:16px;padding:20px 28px;margin-bottom:24px;}
    .ranking-title {font-size:1.8rem;font-weight:800;color:#c8a000;}
    .ranking-row {display:flex;align-items:center;padding:8px 12px;border-radius:8px;margin-bottom:4px;}
    .ranking-pos {width:40px;font-weight:700;color:#888;}
    .ranking-team {flex:1;font-weight:600;}
    .ranking-pts {color:#ffd700;font-weight:700;font-size:0.9rem;}
    .conf-badge {display:inline-block;padding:2px 8px;border-radius:10px;font-size:0.7rem;font-weight:700;margin-left:8px;}
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""<div class='ranking-header'>
        <div class='ranking-title'>🏅 Ranking FMMJ</div>
        <div style='color:#888;font-size:.85rem;'>Ranking actualizado con puntos de los torneos clasificatorios</div>
    </div>""", unsafe_allow_html=True)

    ranking = state["ranking"]
    sorted_ranking = sorted(ranking.items(), key=lambda x: -x[1])

    # Filtros
    col1, col2 = st.columns([1, 3])
    with col1:
        conf_filter = st.selectbox("Confederación", ["Todas", "UEFA", "CONMEBOL", "CAF", "CONCACAF", "AFC", "OFC"])
    with col2:
        search = st.text_input("🔍 Buscar selección", placeholder="Escribe el nombre...")

    # Construir tabla de datos filtrada
    rows = []
    for pos, (team, pts) in enumerate(sorted_ranking, 1):
        conf = get_team_confederation(team)
        if conf_filter != "Todas" and conf != conf_filter:
            continue
        if search and search.lower() not in display_name(team).lower() and search.lower() not in team.lower():
            continue
        rows.append({
            "#": pos,
            "Selección": display_name(team),
            "Confederación": conf,
            "Puntos": pts,
        })

    if rows:
        import pandas as pd
        df = pd.DataFrame(rows)
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "#": st.column_config.NumberColumn(width="small"),
                "Selección": st.column_config.TextColumn(width="medium"),
                "Confederación": st.column_config.TextColumn(width="small"),
                "Puntos": st.column_config.NumberColumn(width="small"),
            }
        )
    else:
        st.info("No hay resultados para el filtro seleccionado.")


# ---------------------------------------------------------------------------
# SORTEO MUNDIAL
# ---------------------------------------------------------------------------
def show_world_cup_draw():
    state = get_state()
    wc = state["world_cup"]
    qualified = state["world_cup_qualified"]
    host = state.get("host", "Nigeria")

    st.markdown("""
    <style>
    .wc-header {
        background:linear-gradient(135deg,#c8a000 0%,#ffd700 40%,#c8a000 100%);
        border-radius:16px;padding:24px 32px;margin-bottom:24px;
        box-shadow:0 8px 32px rgba(200,160,0,.4);
    }
    .wc-title {font-size:2rem;font-weight:800;color:#0a0a1a;margin:0;}
    .wc-subtitle {font-size:.9rem;color:#333;margin:4px 0 0;}
    .pot-card {border-radius:12px;padding:16px;margin-bottom:16px;}
    .pot1 {background:#1a1500;border:2px solid #ffd700;}
    .pot2 {background:#001a0d;border:2px solid #00cc66;}
    .pot3 {background:#00001a;border:2px solid #3388ff;}
    .pot4 {background:#1a000d;border:2px solid #ff6699;}
    .pot-title {font-weight:800;font-size:1rem;margin-bottom:10px;}
    .group-wc {background:#0a1020;border:1px solid #1a3060;border-radius:10px;padding:14px;}
    .group-wc-title {color:#ffd700;font-weight:700;font-size:1.1rem;border-bottom:1px solid #ffd700;margin-bottom:8px;padding-bottom:4px;}
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""<div class='wc-header'>
        <div><div class='wc-title'>🌍 FMMJ World Cup</div>
        <div class='wc-subtitle'>32 selecciones · 8 grupos de 4 · Anfitrión: {display_name(host)}</div></div>
    </div>""", unsafe_allow_html=True)

    # Asegurar que el anfitrión esté en clasificados
    if host and host not in qualified:
        qualified.insert(0, host)
        state["world_cup_qualified"] = qualified

    tabs = st.tabs(["🏅 Clasificados", "🎲 Bombos", "🎯 Sorteo Grupos", "📊 Fase de Grupos", "⚽ Llaves Mundial"])

    with tabs[0]:
        _show_qualified_32(state, qualified)
    with tabs[1]:
        _show_pots(state, wc, qualified)
    with tabs[2]:
        _show_draw(state, wc)
    with tabs[3]:
        _show_wc_groups(state, wc)
    with tabs[4]:
        _show_wc_knockout(state, wc)


def _show_qualified_32(state, qualified):
    st.markdown("### 🏅 Las 32 Selecciones del FMMJ World Cup")
    host = state.get("host")

    conf_groups = {}
    for t in qualified:
        conf = get_team_confederation(t)
        if conf not in conf_groups:
            conf_groups[conf] = []
        conf_groups[conf].append(t)

    conf_order = ["UEFA", "CONMEBOL", "CAF", "CONCACAF", "AFC", "OFC"]
    cupos = {"UEFA": 13, "CONMEBOL": 4, "CAF": 5, "CONCACAF": 3, "AFC": 4, "OFC": 1}

    for conf in conf_order:
        teams_conf = conf_groups.get(conf, [])
        total = cupos.get(conf, 0)
        with st.expander(f"{conf} — {len(teams_conf)}/{total}", expanded=True):
            for t in teams_conf:
                host_tag = "🏠 **ANFITRIÓN**" if t == host else ""
                st.markdown(f"{flag_img(t,22,16)}&nbsp;**{display_name(t)}** {host_tag}", unsafe_allow_html=True)

    st.info(f"**Total clasificados: {len(qualified)}/32**")
    if len(qualified) < 32:
        st.warning(f"Faltan {32 - len(qualified)} equipos por clasificar.")


def _show_pots(state, wc, qualified):
    st.markdown("### 🏅 Bombos para el Sorteo")
    st.caption("Los equipos se distribuyen en 4 bombos de 8 según ranking FMMJ. El anfitrión es cabeza de serie en Bombo 1.")

    if len(qualified) < 32:
        st.warning(f"Aún no están los 32 clasificados. Hay {len(qualified)} equipos.")
    
    host = state.get("host")
    ranking = state["ranking"]
    teams_sorted = sorted(qualified, key=lambda t: -ranking.get(t, 0))

    # Anfitrión siempre en bombo 1
    if host in teams_sorted:
        teams_sorted.remove(host)
        teams_sorted.insert(0, host)

    pot_size = 8
    pots = {i+1: teams_sorted[i*pot_size:(i+1)*pot_size] for i in range(4)}
    wc["pots"] = pots

    pot_styles = ["pot1", "pot2", "pot3", "pot4"]
    pot_colors = ["🟡", "🟢", "🔵", "🔴"]
    cols = st.columns(2)
    for pot_num, teams in pots.items():
        with cols[(pot_num-1) % 2]:
            st.markdown(f"<div class='{pot_styles[pot_num-1]}'><div class='pot-title'>{pot_colors[pot_num-1]} BOMBO {pot_num}</div>", unsafe_allow_html=True)
            for t in teams:
                h_tag = "🏠" if t == host else ""
                st.markdown(f"{flag_img(t,18,13)}&nbsp;{display_name(t)} {h_tag}", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)


def _show_draw(state, wc):
    st.markdown("### 🎯 Sorteo del Mundial FMMJ")
    st.caption("Regla: máx. 2 equipos UEFA por grupo. No puede haber 2 equipos de misma confederación excepto UEFA.")

    pots = wc.get("pots", {})
    if not pots or not pots.get(1):
        st.warning("Primero genera los bombos en la pestaña anterior.")
        return

    if wc.get("groups") and wc["phase"] != "sorteo":
        st.success("✅ Sorteo ya realizado.")
        _display_wc_groups_draw(wc)
        if st.button("🔄 Repetir Sorteo", type="secondary"):
            wc["groups"] = {}
            wc["phase"] = "sorteo"
            st.rerun()
        return

    if not wc.get("groups"):
        st.info("Asigna cada selección clasificada a uno de los 8 grupos (4 equipos por grupo).")
        _manual_group_setup(state, "world_cup", qualified, num_groups=8, teams_per_group=4,
                            confirm_label="Confirmar grupos del Mundial")
    else:
        st.success("✅ Grupos confirmados")
        if st.button("✏️ Editar grupos", type="secondary"):
            wc["groups"] = {}
            wc["phase"] = "sorteo"
            st.rerun()
        _display_wc_groups_draw(wc)


def _do_world_cup_draw(pots, state):
    """Sorteo con restricción de confederaciones"""
    groups = {chr(65+i): [] for i in range(8)}
    host = state.get("host")

    # Pot 1: un equipo por grupo (anfitrión al Grupo A)
    pot1 = list(pots[1])
    if host in pot1:
        pot1.remove(host)
        groups["A"].append(host)
        random.shuffle(pot1)
        for i, t in enumerate(pot1):
            key = chr(65 + i + 1)
            groups[key].append(t)
    else:
        random.shuffle(pot1)
        for i, t in enumerate(pot1):
            groups[chr(65+i)].append(t)

    # Pots 2-4: respetar restricciones de confederación
    for pot_num in [2, 3, 4]:
        pot = list(pots.get(pot_num, []))
        random.shuffle(pot)
        for team in pot:
            conf = get_team_confederation(team)
            placed = False
            group_order = list(groups.keys())
            random.shuffle(group_order)
            for g in group_order:
                current = groups[g]
                if len(current) >= 4:
                    continue
                conf_count = sum(1 for t in current if get_team_confederation(t) == conf)
                if conf == "UEFA" and conf_count >= 2:
                    continue
                elif conf != "UEFA" and conf_count >= 1:
                    continue
                groups[g].append(team)
                placed = True
                break
            if not placed:
                # Forzar colocación ignorando restricción de confederación
                for g in groups:
                    if len(groups[g]) < 4:
                        groups[g].append(team)
                        break
    return groups


def _display_wc_groups_draw(wc):
    groups = wc.get("groups", {})
    cols = st.columns(4)
    for idx, (g, teams) in enumerate(groups.items()):
        with cols[idx % 4]:
            st.markdown(f"<div class='group-wc'><div class='group-wc-title'>GRUPO {g}</div>", unsafe_allow_html=True)
            for t in teams:
                st.markdown(f"{flag_img(t,20,15)}&nbsp;**{display_name(t)}**", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)


def _show_wc_groups(state, wc):
    if not wc.get("groups"):
        st.warning("Realiza el sorteo primero.")
        return

    groups = wc["groups"]
    results = wc.get("group_results", {})
    st.markdown("### 📊 Fase de Grupos — FMMJ World Cup")
    all_complete = True

    for g, teams in groups.items():
        fixtures = [(teams[i], teams[j]) for i in range(len(teams)) for j in range(i+1, len(teams))]
        with st.expander(f"📋 GRUPO {g}", expanded=False):
            for home, away in fixtures:
                key = match_key(home, away)
                res = results.get(key, {})
                col1,col2,col3,col4,col5 = st.columns([3,1,1,3,1])
                with col1: st.markdown(f"{flag_img(home)}&nbsp;**{display_name(home)}**", unsafe_allow_html=True)
                with col2:
                    hg = st.number_input("", 0, 20, res.get("home_goals", 0), key=f"wc_hg_{g}_{home}_{away}", label_visibility="collapsed")
                with col3:
                    ag = st.number_input("", 0, 20, res.get("away_goals", 0), key=f"wc_ag_{g}_{home}_{away}", label_visibility="collapsed")
                with col4: st.markdown(f"{flag_img(away)}&nbsp;**{display_name(away)}**", unsafe_allow_html=True)
                with col5:
                    save = st.button("💾", key=f"wc_save_{g}_{home}_{away}")
                col_s1, col_s2 = st.columns(2)
                with col_s1:
                    hs = _scorer_input(home, hg, res.get("home_scorers", []), f"wc_hs_{g}_{home}_{away}", state, "FMMJ World Cup")
                with col_s2:
                    as_ = _scorer_input(away, ag, res.get("away_scorers", []), f"wc_as_{g}_{home}_{away}", state, "FMMJ World Cup")
                if save:
                    wc["group_results"][key] = {
                        "home_goals": hg, "away_goals": ag, "played": True,
                        "home_scorers": [s.strip() for s in hs.split(",") if s.strip()],
                        "away_scorers": [s.strip() for s in as_.split(",") if s.strip()],
                    }
                    register_scorers(hs, home, state, "FMMJ World Cup")
                    register_scorers(as_, away, state, "FMMJ World Cup")
                    st.rerun()
                if not results.get(key, {}).get("played"):
                    all_complete = False
                st.markdown("---")

            standings = calculate_standings(teams, {k: v for k, v in results.items() if any(t in k for t in teams)})
            wc["group_standings"][g] = standings
            render_standings_table(standings, advancing=2)

    if all_complete or st.checkbox("🔓 Forzar avance a octavos"):
        if wc["phase"] == "grupos":
            if st.button("⚽ Generar Octavos de Final", type="primary", use_container_width=True):
                _build_wc_knockout(state, wc)
                wc["phase"] = "octavos"
                st.rerun()


def _build_wc_knockout(state, wc):
    standings = wc.get("group_standings", {})
    groups = sorted(standings.keys())
    # Octavos: 1A vs 2B, 1B vs 2A, etc.
    pairs = [
        (groups[0], groups[1]),
        (groups[2], groups[3]),
        (groups[4], groups[5]),
        (groups[6], groups[7]),
    ]
    octavos = []
    for ga, gb in pairs:
        first_a = standings[ga][0]["team"] if standings.get(ga) else None
        second_b = standings[gb][1]["team"] if len(standings.get(gb, [])) > 1 else None
        first_b = standings[gb][0]["team"] if standings.get(gb) else None
        second_a = standings[ga][1]["team"] if len(standings.get(ga, [])) > 1 else None
        octavos.append({"home": first_a, "away": second_b, "winner": None})
        octavos.append({"home": first_b, "away": second_a, "winner": None})

    wc["knockout_bracket"] = {
        "octavos": octavos,
        "cuartos": [],
        "semis": [],
        "tercer_puesto": [],
        "final": [],
    }
    wc["knockout_results"] = {}


def _show_wc_knockout(state, wc):
    st.markdown("### ⚽ Fase de Eliminación — FMMJ World Cup")
    bracket = wc.get("knockout_bracket", {})
    if not bracket:
        st.info("Completa la fase de grupos primero.")
        return
    results = wc.get("knockout_results", {})
    if results is None:
        wc["knockout_results"] = {}
        results = wc["knockout_results"]

    phases = [
        ("octavos", "🔵 Octavos de Final", "cuartos"),
        ("cuartos", "🟡 Cuartos de Final", "semis"),
        ("semis", "🟠 Semifinales", "final"),
        ("final", "🏆 GRAN FINAL", None),
    ]

    for phase_key, phase_name, next_phase in phases:
        matches = bracket.get(phase_key, [])
        if not matches: continue
        st.markdown(f"#### {phase_name}")
        all_done = True

        for idx, match in enumerate(matches):
            home, away = match.get("home"), match.get("away")
            if not home or not away:
                st.markdown("*Pendiente*"); all_done = False; continue

            key = f"wc_{phase_key}_{idx}"
            res = results.get(key, {})

            col1,col2,col3,col4,col5,col6 = st.columns([3,1,1,3,2,1])
            with col1: st.markdown(f"{flag_img(home)}&nbsp;**{display_name(home)}**", unsafe_allow_html=True)
            with col2:
                hg = st.number_input("", 0, 20, res.get("home_goals", 0), key=f"{key}_hg", label_visibility="collapsed")
            with col3:
                ag = st.number_input("", 0, 20, res.get("away_goals", 0), key=f"{key}_ag", label_visibility="collapsed")
            with col4: st.markdown(f"{flag_img(away)}&nbsp;**{display_name(away)}**", unsafe_allow_html=True)
            with col5:
                if hg == ag:
                    ps = st.selectbox("Penales", ["—", display_name(home), display_name(away)], key=f"{key}_pen")
                    pw = home if ps == display_name(home) else (away if ps == display_name(away) else None)
                else:
                    pw = None; st.empty()
            with col6:
                save = st.button("💾", key=f"{key}_save")

            col_s1, col_s2 = st.columns(2)
            with col_s1:
                hs = _scorer_input(home, hg, res.get("home_scorers", []), f"{key}_hs", state, torneo_name)
            with col_s2:
                as_ = _scorer_input(away, ag, res.get("away_scorers", []), f"{key}_as", state, torneo_name)

            if save:
                winner = home if hg > ag else (away if ag > hg else pw)
                results[key] = {"home_goals": hg, "away_goals": ag, "winner": winner, "penalty_winner": pw,
                                "home_scorers": [s.strip() for s in hs.split(",") if s.strip()],
                                "away_scorers": [s.strip() for s in as_.split(",") if s.strip()]}
                wc["knockout_bracket"][phase_key][idx]["winner"] = winner
                register_scorers(hs, home, state, "FMMJ World Cup")
                register_scorers(as_, away, state, "FMMJ World Cup")
                st.rerun()

            if res.get("winner"):
                st.markdown(f"**✅ {display_name(res['winner'])}** avanza")
            else:
                all_done = False
            st.markdown("---")

        if all_done and next_phase and not bracket.get(next_phase):
            winners = [results.get(f"wc_{phase_key}_{i}", {}).get("winner") for i in range(len(matches))]
            winners = [w for w in winners if w]
            if phase_key == "semis":
                losers = []
                for i, m in enumerate(matches):
                    r = results.get(f"wc_semis_{i}", {})
                    loser = m["home"] if r.get("winner") == m["away"] else m["away"]
                    if loser: losers.append(loser)
                bracket["tercer_puesto"] = [{"home": losers[0], "away": losers[1], "winner": None}] if len(losers) == 2 else []
            nxt = [(winners[i], winners[i+1]) for i in range(0, len(winners)-1, 2)]
            bracket[next_phase] = [{"home": m[0], "away": m[1], "winner": None} for m in nxt]
            wc["knockout_results"] = results
            st.rerun()

        if all_done and phase_key == "final":
            champion = results.get("wc_final_0", {}).get("winner")
            if champion:
                wc["champion"] = champion
                wc["phase"] = "completado"
                st.balloons()
                st.markdown(f"""
                <div style='background:linear-gradient(135deg,#ffd700,#c8a000);border-radius:16px;
                padding:24px;text-align:center;margin-top:20px;'>
                <div style='font-size:2.5rem;'>🏆</div>
                <div style='font-size:1.8rem;font-weight:900;color:#0a0a1a;'>{display_name(champion)}</div>
                <div style='font-size:1rem;color:#333;'>¡CAMPEÓN DEL FMMJ WORLD CUP!</div>
                </div>
                """, unsafe_allow_html=True)

    # 3er puesto
    if bracket.get("tercer_puesto"):
        st.markdown("#### 🥉 Tercer Puesto")
        for idx, m in enumerate(bracket["tercer_puesto"]):
            home, away = m["home"], m["away"]
            key = f"wc_tercer_{idx}"
            res = results.get(key, {})
            col1,col2,col3,col4,col5,col6 = st.columns([3,1,1,3,2,1])
            with col1: st.markdown(f"{flag_img(home)}&nbsp;**{display_name(home)}**", unsafe_allow_html=True)
            with col2:
                hg = st.number_input("", 0, 20, res.get("home_goals", 0), key=f"{key}_hg", label_visibility="collapsed")
            with col3:
                ag = st.number_input("", 0, 20, res.get("away_goals", 0), key=f"{key}_ag", label_visibility="collapsed")
            with col4: st.markdown(f"{flag_img(away)}&nbsp;**{display_name(away)}**", unsafe_allow_html=True)
            with col5:
                if hg == ag:
                    p = st.selectbox("Penales", ["—", display_name(home), display_name(away)], key=f"{key}_pen")
                    pw = home if p == display_name(home) else (away if p == display_name(away) else None)
                else:
                    pw = None; st.empty()
            with col6:
                if st.button("💾", key=f"{key}_save"):
                    winner = home if hg > ag else (away if ag > hg else pw)
                    results[key] = {"home_goals": hg, "away_goals": ag, "winner": winner}
                    bracket["tercer_puesto"][idx]["winner"] = winner
                    wc["knockout_results"] = results
                    st.rerun()
            if res.get("winner"):
                st.markdown(f"**🥉 3er Puesto: {display_name(res['winner'])}**")


# ============================================================
# TABLA DE GOLEADORES
# ============================================================
def show_goleadores():
    state = get_state()
    st.markdown("""
    <style>
    .gol-header {background:linear-gradient(135deg,#1a0030 0%,#3a0060 50%,#1a0030 100%);
    border:2px solid #ffd700;border-radius:16px;padding:20px 28px;margin-bottom:24px;}
    </style>
    """, unsafe_allow_html=True)
    st.markdown("""<div class='gol-header'>
        <div style='font-size:1.8rem;font-weight:800;color:#ffd700;'>⚽ Tabla de Goleadores FMMJ</div>
        <div style='color:#aaa;font-size:.85rem;'>Goles acumulados en todos los torneos clasificatorios y el Mundial</div>
    </div>""", unsafe_allow_html=True)

    all_scorers = state.get("all_scorers", {})
    if not all_scorers:
        st.info("Aún no hay goles registrados. Comienza a ingresar resultados en los torneos.")
        return

    # Construir lista de goleadores
    rows = []
    for skey, data in all_scorers.items():
        name = data.get("name", skey.split("||")[0])
        team = data.get("team", "")
        goals = data.get("goals", 0)
        torneos = data.get("torneos", {})
        if goals > 0:
            rows.append({
                "name": name,
                "team": team,
                "goals": goals,
                "torneos": torneos,
            })

    rows.sort(key=lambda x: -x["goals"])

    # ── FILTROS ──────────────────────────────────────────────────────────────
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        torneos_list = sorted(set(t for r in rows for t in r["torneos"].keys()))
        torneo_filter = st.selectbox("🏆 Torneo", ["Todos"] + torneos_list)
    with col_f2:
        conf_filter_g = st.selectbox("🌍 Confederación", ["Todas", "UEFA", "CONMEBOL", "CAF", "CONCACAF", "AFC", "OFC"])
    with col_f3:
        top_n = st.selectbox("Mostrar", [10, 20, 50, "Todos"], index=0)

    # Filtrar
    filtered = []
    for r in rows:
        if torneo_filter != "Todos" and torneo_filter not in r["torneos"]:
            continue
        conf = get_team_confederation(r["team"])
        if conf_filter_g != "Todas" and conf != conf_filter_g:
            continue
        goles = r["torneos"].get(torneo_filter, 0) if torneo_filter != "Todos" else r["goals"]
        if goles > 0:
            filtered.append({**r, "goles_filtro": goles})

    filtered.sort(key=lambda x: -x["goles_filtro"])
    if top_n != "Todos":
        filtered = filtered[:int(top_n)]

    if not filtered:
        st.info("No hay goleadores con ese filtro.")
        return

    # ── PODIO TOP 3 ──────────────────────────────────────────────────────────
    if len(filtered) >= 3:
        st.markdown("### 🥇 Podio")
        podio_cols = st.columns(3)
        medals = ["🥇", "🥈", "🥉"]
        colors = ["#ffd700", "#c0c0c0", "#cd7f32"]
        for i, (col, medal, color) in enumerate(zip(podio_cols, medals, colors)):
            if i < len(filtered):
                r = filtered[i]
                with col:
                    st.markdown(f"""
                    <div style='background:#0a1020;border:2px solid {color};border-radius:12px;
                    padding:16px;text-align:center;'>
                        <div style='font-size:2rem;'>{medal}</div>
                        <div style='font-size:1rem;font-weight:700;color:#fff;margin:4px 0;'>{r["name"]}</div>
                        <div style='font-size:0.8rem;color:#aaa;'>{flag_img(r["team"],18,13)}&nbsp;{display_name(r["team"])}</div>
                        <div style='font-size:2rem;font-weight:900;color:{color};margin-top:8px;'>{r["goles_filtro"]}</div>
                        <div style='font-size:0.7rem;color:#888;'>goles</div>
                    </div>
                    """, unsafe_allow_html=True)

    # ── TABLA COMPLETA ────────────────────────────────────────────────────────
    st.markdown("### 📊 Tabla Completa")
    import pandas as pd
    table_rows = []
    for pos, r in enumerate(filtered, 1):
        torneos_str = ", ".join([f"{t}: {g}" for t, g in sorted(r["torneos"].items(), key=lambda x: -x[1])])
        table_rows.append({
            "#": pos,
            "Jugador": r["name"],
            "Selección": display_name(r["team"]),
            "Goles": r["goles_filtro"],
            "Torneos": torneos_str,
        })
    df = pd.DataFrame(table_rows)
    st.dataframe(df, use_container_width=True, hide_index=True,
                 column_config={
                     "#": st.column_config.NumberColumn(width="small"),
                     "Goles": st.column_config.NumberColumn(width="small"),
                 })

    # ── GOLEADORES POR EQUIPO ─────────────────────────────────────────────────
    st.markdown("### 🏳️ Por Selección")
    teams_in_table = sorted(set(r["team"] for r in filtered))
    sel_team = st.selectbox("Ver equipo:", ["— Selecciona —"] + [display_name(t) for t in teams_in_table])
    if sel_team != "— Selecciona —":
        team_key = next((t for t in teams_in_table if display_name(t) == sel_team), None)
        if team_key:
            team_rows = [r for r in filtered if r["team"] == team_key]
            for r in team_rows:
                torneos_str = " · ".join([f"{t}: {g}⚽" for t, g in r["torneos"].items()])
                st.markdown(
                    f"<div style='padding:6px 12px;background:#0a1020;border-radius:6px;margin-bottom:4px;'>"
                    f"<span style='font-weight:700;color:#fff;'>{r['name']}</span>"
                    f"&nbsp;<span style='color:#ffd700;font-weight:900;'>{r['goles_filtro']} ⚽</span>"
                    f"&nbsp;<span style='color:#888;font-size:0.8rem;'>{torneos_str}</span></div>",
                    unsafe_allow_html=True
                )

# ============================================================
# APP PRINCIPAL — LAYOUT Y ROUTING
# ============================================================

st.set_page_config(
    page_title="FMMJ World Cup Simulator",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Oswald:wght@400;600;700&family=Source+Sans+3:wght@400;600&display=swap');
.stApp { background: #060b18; color: #e0e8ff; font-family: 'Source Sans 3', sans-serif; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #080d1e 0%, #0a1228 100%) !important; border-right: 1px solid #1a2a5a; }
[data-testid="stSidebar"] * { color: #c0cce0 !important; }
[data-testid="stSidebar"] .stRadio label { padding: 8px 12px !important; border-radius: 8px !important; cursor: pointer !important; display: block; }
[data-testid="stSidebar"] .stRadio label:hover { background: #1a2a5a !important; }
.stSelectbox > div > div, .stTextInput > div > input, .stNumberInput > div > input { background: #111a35 !important; border-color: #1e3055 !important; color: #e0e8ff !important; }
.stTabs [data-baseweb="tab-list"] { background: #0a1020 !important; border-radius: 10px !important; padding: 4px !important; }
.stTabs [data-baseweb="tab"] { background: transparent !important; color: #7090c0 !important; border-radius: 8px !important; font-weight: 600 !important; }
.stTabs [aria-selected="true"] { background: #1a3a80 !important; color: #ffd700 !important; }
.stButton > button[kind="primary"] { background: linear-gradient(135deg, #1a4aff, #0033cc) !important; color: white !important; border: none !important; font-weight: 700 !important; font-family: 'Oswald', sans-serif !important; border-radius: 8px !important; }
.stButton > button { background: #111a35 !important; color: #c0d0f0 !important; border: 1px solid #1e3055 !important; border-radius: 8px !important; }
[data-testid="stExpander"] { background: #0a1020 !important; border: 1px solid #1a2a5a !important; border-radius: 10px !important; }
[data-testid="stExpander"] summary { color: #c8d8f0 !important; font-weight: 600 !important; }
h1, h2, h3 { font-family: 'Oswald', sans-serif !important; }
h1 { color: #ffd700 !important; } h2 { color: #c8d8ff !important; } h3 { color: #a0c0ff !important; }
hr { border-color: #1a2a5a !important; }
::-webkit-scrollbar { width: 6px; } ::-webkit-scrollbar-track { background: #0a1020; } ::-webkit-scrollbar-thumb { background: #1a3a6a; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

init_state()
state = get_state()


def _show_home(state):
    host = state.get("host", "Nigeria")
    edition = state.get("edition", 1)
    qualified = state.get("world_cup_qualified", [])
    conf_q = {}
    for t in qualified:
        conf = get_team_confederation(t)
        conf_q[conf] = conf_q.get(conf, 0) + 1

    st.markdown(f"""
    <div style='background:linear-gradient(135deg,#060b18 0%,#0d1a3a 50%,#060b18 100%);
    border:2px solid #c8a000;border-radius:20px;padding:40px;margin-bottom:32px;text-align:center;'>
        <div style='margin-bottom:12px;'>
            <img src='fmmj.png' style='height:80px;' onerror="this.style.display='none'">
        </div>
        <div style='font-size:3.5rem;font-family:Oswald,sans-serif;font-weight:700;
                    color:#ffd700;letter-spacing:4px;text-shadow:0 0 30px rgba(255,215,0,.6);'>
            🌍 FMMJ WORLD CUP
        </div>
        <div style='font-size:1.1rem;color:#6080aa;letter-spacing:2px;margin-top:8px;'>
            EDICIÓN {edition} · SIMULADOR OFICIAL
        </div>
        <div style='margin-top:20px;font-size:1rem;color:#a0c0e0;'>
            Anfitrión: {flag_img(host,24,18)}&nbsp;<strong>{display_name(host)}</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)

    cupos_info = [
        ("🏆 UEFA", 13, "UEFA", "#003580"),
        ("🌎 CONMEBOL", 4, "CONMEBOL", "#006b3c"),
        ("🌍 CAF", 5, "CAF", "#b8860b"),
        ("⭐ CONCACAF", 3, "CONCACAF", "#8b0000"),
        ("🌏 AFC", 4, "AFC", "#4a0080"),
    ]
    cols = st.columns(5)
    for col, (label, total, conf, color) in zip(cols, cupos_info):
        current = conf_q.get(conf, 0)
        with col:
            st.markdown(f"""
            <div style='background:#0a1020;border:1px solid {color};border-radius:12px;
            padding:16px;text-align:center;'>
                <div style='font-size:0.9rem;font-weight:700;color:#c8d8ff;'>{label}</div>
                <div style='font-size:2rem;font-weight:900;color:{"#00cc66" if current >= total else "#ffd700"};'>{current}/{total}</div>
                <div style='font-size:0.7rem;color:#6080aa;'>cupos</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("### 🗺️ Guía de uso")
        st.markdown("""
1. **🏅 Ranking FMMJ** — Consulta el ranking actualizado
2. **🏆 Eurocopa** → 6 grupos + llaves + playoff UEFA (13 cupos)
3. **🌎 Copa América** → Elige invitadas, sortea, juega (4 cupos)
4. **🌍 Copa África** → 10 equipos CAF (5 cupos)
5. **⭐ Copa Oro** → CONCACAF (3 cupos)
6. **🌏 Copa Asia** → AFC (4 cupos)
7. **🔁 Repechaje** → 2 llaves ida y vuelta (2 cupos)
8. **🌍 Sorteo y Mundial** → 32 equipos, 8 grupos, llaves 🏆
        """)
    with col_b:
        if qualified:
            st.markdown("### ✅ Clasificados al Mundial")
            for t in qualified[:16]:
                st.markdown(f"{flag_img(t,20,15)}&nbsp;**{display_name(t)}**", unsafe_allow_html=True)
            if len(qualified) > 16:
                st.caption(f"... y {len(qualified)-16} más")
        else:
            st.info("Ningún equipo clasificado aún. Comienza por la Eurocopa.")
    if len(qualified) == 32:
        st.balloons()
        st.success("🎉 ¡Los 32 equipos están clasificados! Ve al **Sorteo y Mundial**.")


def _show_config(state):
    st.markdown("### ⚙️ Configuración del Simulador FMMJ")
    st.markdown("#### 🏠 Anfitrión del Mundial")
    current_host = state.get("host", "Nigeria")
    host_options = sorted(ALL_TEAMS, key=lambda t: display_name(t))
    host_display = [display_name(t) for t in host_options]
    current_idx = host_options.index(current_host) if current_host in host_options else 0
    selected_display = st.selectbox("Selecciona el anfitrión:", host_display, index=current_idx)
    new_host = host_options[host_display.index(selected_display)]
    if new_host != current_host:
        if st.button(f"✅ Confirmar: {display_name(new_host)} como anfitrión", type="primary"):
            state["host"] = new_host
            if new_host not in state["world_cup_qualified"]:
                state["world_cup_qualified"].insert(0, new_host)
            st.success(f"✅ Anfitrión: {display_name(new_host)}")
            st.rerun()
    st.markdown("---")
    st.markdown("#### 🔄 Nueva Edición")
    st.warning("⚠️ Borra todos los resultados pero conserva el ranking.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Nueva Edición", type="primary"):
            reset_for_new_edition()
            st.success("✅ Nueva edición iniciada.")
            st.rerun()
    with col2:
        if st.button("🗑️ Reset Completo"):
            st.session_state.fmmj_state = get_initial_state()
            st.success("✅ Reset completo.")
            st.rerun()
    st.markdown("---")
    st.json({
        "edicion": state.get("edition"),
        "anfitrion": display_name(state.get("host", "")),
        "clasificados": len(state.get("world_cup_qualified", [])),
        "eurocopa": state.get("euro", {}).get("phase", "—"),
        "copa_america": state.get("copa_america", {}).get("phase", "—"),
        "copa_africa": state.get("copa_africa", {}).get("phase", "—"),
        "copa_oro": state.get("copa_oro", {}).get("phase", "—"),
        "copa_asia": state.get("copa_asia", {}).get("phase", "—"),
    })


# SIDEBAR
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:16px 0 8px;'>
        <img src='fmmj.png' style='height:50px;margin-bottom:4px;' onerror="this.style.display='none'">
        <div style='font-size:2.2rem;font-family:Oswald,sans-serif;font-weight:700;
                    color:#ffd700;letter-spacing:2px;text-shadow:0 0 20px rgba(255,215,0,0.5);'>
            FMMJ
        </div>
        <div style='font-size:0.7rem;color:#6080aa;letter-spacing:3px;text-transform:uppercase;'>
            World Cup Simulator
        </div>
    </div>
    <hr style='border-color:#1a2a5a;margin:8px 0 16px;'/>
    """, unsafe_allow_html=True)

    host = state.get("host", "Nigeria")
    edition = state.get("edition", 1)
    qualified_count = len(state.get("world_cup_qualified", []))

    st.markdown(f"""
    <div style='background:#0a1530;border:1px solid #1a3a6a;border-radius:10px;padding:12px;margin-bottom:16px;'>
        <div style='font-size:0.75rem;color:#6080aa;text-transform:uppercase;'>Edición</div>
        <div style='font-size:1.1rem;font-weight:700;color:#ffd700;'>FMMJ {edition}ª Copa</div>
        <div style='margin-top:8px;font-size:0.75rem;color:#6080aa;'>Anfitrión</div>
        <div style='font-size:0.95rem;font-weight:600;color:#e0e8ff;'>{flag_img(host,20,15)}&nbsp;{display_name(host)}</div>
        <div style='margin-top:8px;font-size:0.75rem;color:#6080aa;'>Clasificados</div>
        <div style='font-size:0.95rem;font-weight:700;color:{"#00cc66" if qualified_count >= 32 else "#ffd700"};'>{qualified_count}/32</div>
    </div>
    """, unsafe_allow_html=True)

    menu_options = {
        "🏠 Inicio": "inicio",
        "🏅 Ranking FMMJ": "ranking",
        "⚽ Goleadores": "goleadores",
        "🏆 Eurocopa (UEFA)": "eurocopa",
        "🌎 Copa América (CONMEBOL)": "copa_america",
        "🌍 Copa África (CAF)": "copa_africa",
        "⭐ Copa Oro (CONCACAF)": "copa_oro",
        "🌏 Copa Asia (AFC)": "copa_asia",
        "🔁 Repechaje Internacional": "repechaje",
        "🌍 Sorteo y Mundial": "mundial",
        "⚙️ Configuración": "config",
    }
    selected = st.radio("", list(menu_options.keys()), label_visibility="collapsed")
    page_key = menu_options[selected]

    st.markdown("<hr style='border-color:#1a2a5a;margin:16px 0;'/>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:0.75rem;color:#6080aa;text-transform:uppercase;margin-bottom:8px;'>Progreso</div>", unsafe_allow_html=True)
    for name, ph_key in [("Eurocopa","euro"),("Copa América","copa_america"),
                          ("Copa África","copa_africa"),("Copa Oro","copa_oro"),("Copa Asia","copa_asia")]:
        phase = state.get(ph_key, {}).get("phase", "—")
        icon = "✅" if phase == "completado" else ("🔄" if phase not in ["—","configuracion"] else "⏳")
        color = "#00cc66" if icon == "✅" else ("#ffd700" if icon == "🔄" else "#6080aa")
        st.markdown(f"<div style='font-size:0.8rem;color:{color};padding:2px 0;'>{icon} {name}: <span style='color:#888;'>{phase}</span></div>", unsafe_allow_html=True)

# ROUTING
if page_key == "inicio":
    _show_home(state)
elif page_key == "ranking":
    show_ranking()
elif page_key == "goleadores":
    show_goleadores()
elif page_key == "eurocopa":
    show_eurocopa()
elif page_key == "copa_america":
    show_copa_america()
elif page_key == "copa_africa":
    show_copa_africa()
elif page_key == "copa_oro":
    show_copa_oro()
elif page_key == "copa_asia":
    show_copa_asia()
elif page_key == "repechaje":
    show_repechaje()
elif page_key == "mundial":
    show_world_cup_draw()
elif page_key == "config":
    _show_config(state)
