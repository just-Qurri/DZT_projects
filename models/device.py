"""
Базовый класс для всех устройств защиты.
Определяет общий интерфейс и методы для расчета характеристик.
"""

import numpy as np
from abc import ABC, abstractmethod


class ProtectionDevice(ABC):
    """
    Абстрактный базовый класс для устройств релейной защиты.
    Определяет общий интерфейс для всех типов устройств.
    """

    def __init__(self, device_type, default_params):
        """
        Инициализация устройства защиты.

        Args:
            device_type: Тип устройства (MR_801, RET_521_HV, RET_521_LV)
            default_params: Параметры по умолчанию для данного устройства
        """
        self.device_type = device_type
        self.default_params = default_params.copy()
        self.current_params = default_params.copy()
        self.Ibrake1 = 1.25  # Для RET-521 фиксированное значение

    @abstractmethod
    def calculate_characteristic(self, I_brake):
        """
        Расчет характеристики срабатывания защиты.

        Args:
            I_brake: Массив тормозных токов

        Returns:
            Массив дифференциальных токов
        """
        pass

    @abstractmethod
    def calculate_currents(self, params):
        """
        Расчет токов для таблицы результатов.

        Args:
            params: Параметры для расчета

        Returns:
            Словарь с рассчитанными токами
        """
        pass

    def get_break_points(self, params=None):
        """
        Получение точек излома характеристики.

        Args:
            params: Параметры для расчета (если None, используются текущие)

        Returns:
            Кортеж (I_brake1, I_brake2, y1, y2)
        """
        if params is None:
            params = self.current_params

        I_diff = params['I_diff']
        k1 = params['k1']

        if self.device_type == "MR_801":
            I_brake1 = params.get('I_brake1', self.default_params['I_brake1'])
            I_brake2 = params.get('I_brake2', self.default_params['I_brake2'])
        else:
            I_brake1 = self.Ibrake1
            I_brake2 = (1 - I_diff) / k1 + I_brake1

        y1 = I_diff
        y2 = y1 + k1 * (I_brake2 - I_brake1)

        return I_brake1, I_brake2, y1, y2

    def validate_params(self, params):
        """
        Проверка корректности параметров.

        Args:
            params: Словарь параметров для проверки

        Returns:
            Кортеж (is_valid, error_message)
        """
        required = ['S_nom', 'U_hv', 'U_lv', 'CT_hv_perv', 'CT_hv_sec',
                   'CT_lv_perv', 'CT_lv_sec']

        for key in required:
            if key not in params:
                return False, f"Отсутствует параметр: {key}"

            try:
                val = float(params[key])
            except (ValueError, TypeError):
                return False, f"Параметр {key} не является числом"

            if val <= 0:
                return False, f"Параметр {key} должен быть больше 0"

        return True, ""

    def numeric_params(self, params):
        """
        Преобразование параметров в числовой формат.

        Args:
            params: Словарь параметров со строковыми значениями

        Returns:
            Словарь с числовыми значениями
        """
        numeric = {}
        for k, v in params.items():
            try:
                if isinstance(v, str):
                    numeric[k] = float(v.replace(',', '.'))
                else:
                    numeric[k] = float(v)
            except (ValueError, TypeError, AttributeError):
                numeric[k] = 0.0
        return numeric

    def update_params(self, params):
        """Обновление текущих параметров"""
        self.current_params.update(params)