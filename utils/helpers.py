"""
Вспомогательные функции и утилиты.
"""

import numpy as np


def format_number(value, decimals=2):
    """
    Форматирование числа с заданным количеством знаков после запятой.

    Args:
        value: Число для форматирования
        decimals: Количество знаков после запятой

    Returns:
        Отформатированная строка
    """
    try:
        return f"{float(value):.{decimals}f}"
    except (ValueError, TypeError):
        return str(value)


def calculate_angle_from_slope(slope):
    """
    Расчет угла наклона в градусах из тангенса.

    Args:
        slope: Тангенс угла наклона

    Returns:
        Угол в градусах
    """
    return np.degrees(np.arctan(slope))