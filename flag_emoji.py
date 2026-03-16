"""
flag_emoji.py — Emojis de bandera Unicode para todos los equipos
Funcionan en labels de widgets Streamlit sin necesidad de HTML
"""

FLAG_EMOJI = {
    # UEFA
    "Switzerland":    "🇨🇭",
    "Denmark":        "🇩🇰",
    "Poland":         "🇵🇱",
    "Austria":        "🇦🇹",
    "Croatia":        "🇭🇷",
    "Sweden":         "🇸🇪",
    "Serbia":         "🇷🇸",
    "Wales":          "🏴󠁧󠁢󠁷󠁬󠁳󠁿",
    "Scotland":       "🏴󠁧󠁢󠁳󠁣󠁴󠁿",
    "Belgium":        "🇧🇪",
    "Ukraine":        "🇺🇦",
    "Czech Republic": "🇨🇿",
    "Iceland":        "🇮🇸",
    "Greece":         "🇬🇷",
    "Turkey":         "🇹🇷",
    "Norway":         "🇳🇴",
    "Netherlands":    "🇳🇱",
    "France":         "🇫🇷",
    "Spain":          "🇪🇸",
    "Portugal":       "🇵🇹",
    "Italy":          "🇮🇹",
    "England":        "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
    "Germany":        "🇩🇪",
    "Hungary":        "🇭🇺",
    "Israel":         "🇮🇱",
    # CONMEBOL
    "Brazil":         "🇧🇷",
    "Argentina":      "🇦🇷",
    "Colombia":       "🇨🇴",
    "Chile":          "🇨🇱",
    "Peru":           "🇵🇪",
    "Uruguay":        "🇺🇾",
    "Venezuela":      "🇻🇪",
    "Bolivia":        "🇧🇴",
    "Paraguay":       "🇵🇾",
    "Ecuador":        "🇪🇨",
    # CAF
    "South Africa":   "🇿🇦",
    "Morocco":        "🇲🇦",
    "Tunisia":        "🇹🇳",
    "Ghana":          "🇬🇭",
    "Senegal":        "🇸🇳",
    "Egypt":          "🇪🇬",
    "Ivory Coast":    "🇨🇮",
    "Cameroon":       "🇨🇲",
    "Nigeria":        "🇳🇬",
    "Algeria":        "🇩🇿",
    # CONCACAF
    "Mexico":         "🇲🇽",
    "Panama":         "🇵🇦",
    "Costa Rica":     "🇨🇷",
    "USA":            "🇺🇸",
    "Canada":         "🇨🇦",
    "Jamaica":        "🇯🇲",
    # AFC
    "Korea":          "🇰🇷",
    "Saudi Arabia":   "🇸🇦",
    "Japan":          "🇯🇵",
    "Australia":      "🇦🇺",
    "Qatar":          "🇶🇦",
    # OFC
    "New Zealand":    "🇳🇿",
}


def flag_emoji(team):
    """Devuelve emoji de bandera — funciona en cualquier widget Streamlit."""
    return FLAG_EMOJI.get(team, "🏳️")


def team_label_emoji(team, display_names):
    """Label completo con emoji para widgets: '🇫🇷 Francia'"""
    name = display_names.get(team, team)
    emoji = flag_emoji(team)
    return f"{emoji} {name}"
