"""Темы оформления для приложения"""


class LightTheme:
    """Светлая тема"""
    PRIMARY_COLOR = "#3498db"
    SECONDARY_COLOR = "#2980b9"
    BACKGROUND = "#f8f9fa"
    CARD_BG = "#ffffff"
    TEXT = "#2c3e50"
    BORDER = "#ced4da"
    SUCCESS = "#2ecc71"
    WARNING = "#e74c3c"
    INFO = "#3498db"


class DarkTheme:
    """Темная тема"""
    PRIMARY_COLOR = "#3498db"
    SECONDARY_COLOR = "#2980b9"
    BACKGROUND = "#2c3e50"
    CARD_BG = "#34495e"
    TEXT = "#ecf0f1"
    BORDER = "#7f8c8d"
    SUCCESS = "#27ae60"
    WARNING = "#c0392b"
    INFO = "#2980b9"


# Активная тема (можно переключать)
current_theme = LightTheme()