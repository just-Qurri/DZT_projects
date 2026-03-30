"""
Базовый класс для всех устройств защиты.
Определяет общий интерфейс и содержит общую логику.
"""

from abc import ABC, abstractmethod
from enum import Enum
import numpy as np


class WindingSide(Enum):
    HV = "HV"
    LV = "LV"


class SlopeFormat(Enum):
    """Формат ввода коэффициента наклона"""
    DEGREES = "degrees"      # Градусы (MR801)
    RATIO = "ratio"          # Готовое значение tan (RET521)
    PERCENT = "percent"      # Проценты (RET670)


class ProtectionDevice(ABC):
    """Абстрактный базовый класс для устройств релейной защиты."""

    def __init__(self, device_type, default_params, slope_format=SlopeFormat.RATIO):
        """
        Инициализация устройства защиты.

        Args:
            device_type: Тип устройства
            default_params: Параметры по умолчанию
            slope_format: Формат ввода коэффициентов наклона
        """
        self.device_type = device_type
        self.default_params = default_params.copy()
        self.current_params = default_params.copy()
        self.slope_format = slope_format
        self.winding_side = self._get_winding_side(device_type)


    def _get_winding_side(self, device_type):
        if device_type and "_HV" in device_type:
            return WindingSide.HV
        elif device_type and "_LV" in device_type:
            return WindingSide.LV
        return None

    # ============ ОБЩИЕ УТИЛИТЫ ============

    def _normalize_slope(self, value):
        """
        Приводит коэффициент наклона к стандартному формату (tan).
        Зависит от формата ввода, заданного для конкретного устройства.
        """
        if value is None:
            return 0

        if self.slope_format == SlopeFormat.DEGREES:
            return np.tan(np.radians(value))

        elif self.slope_format == SlopeFormat.PERCENT:
            return value / 100

        else:
            return value

    def _get_base_params(self, params):
        """Базовые параметры трансформатора (один раз для всех расчетов)"""
        S_nom = params['S_nom'] * 1e6
        sqrt3 = np.sqrt(3)
        U_hv = float(params['U_hv'])
        U_lv = float(params['U_lv'])

        I_nom_hv = S_nom / (sqrt3 * U_hv * 1e3)
        I_nom_lv = S_nom / (sqrt3 * U_lv * 1e3)

        koeff_CT_HV = params['CT_hv_perv'] / params['CT_hv_sec']
        koeff_CT_LV = params['CT_lv_perv'] / params['CT_lv_sec']

        return {
            'U_hv': U_hv,
            'U_lv': U_lv,
            'I_nom_hv': I_nom_hv,
            'I_nom_lv': I_nom_lv,
            'koeff_CT_HV': koeff_CT_HV,
            'koeff_CT_LV': koeff_CT_LV,
            'I_sec_hv': I_nom_hv / koeff_CT_HV,
            'I_sec_lv': I_nom_lv / koeff_CT_LV
        }

    def _get_char_params(self, params):
        """
        Параметры характеристики с подстановкой default.
        Коэффициенты нормализуются в зависимости от формата устройства.
        """
        return {
            'I_diff': params['I_diff'],
            'I_brake1': params.get('I_brake1', self.default_params.get('I_brake1', 0)),
            'I_brake2': params.get('I_brake2', self.default_params.get('I_brake2', 0)),
            'k1': self._normalize_slope(params.get('k1', self.default_params.get('k1', 0))),
            'k2': self._normalize_slope(params.get('k2', self.default_params.get('k2', 0)))
        }

    # ============ УНИВЕРСАЛЬНЫЙ РАСЧЕТ ============

    def calculate_characteristic_full(self, I_brake):
        """Расчет характеристики (общий для всех)"""
        p = self._get_char_params(self.current_params)

        conditions = [
            I_brake <= p['I_brake1'],
            (I_brake > p['I_brake1']) & (I_brake <= p['I_brake2']),
            I_brake > p['I_brake2']
        ]

        choices = [
            p['I_diff'],
            p['I_diff'] + p['k1'] * (I_brake - p['I_brake1']),
            p['I_diff'] + p['k1'] * (p['I_brake2'] - p['I_brake1']) + p['k2'] * (I_brake - p['I_brake2'])
        ]

        return np.select(conditions, choices)

    def get_break_points(self, params=None):
        """Точки излома (общий для всех)"""
        p = self._get_char_params(params or self.current_params)
        y2 = p['I_diff'] + p['k1'] * (p['I_brake2'] - p['I_brake1'])
        return p['I_brake1'], p['I_brake2'], p['I_diff'], y2, p['k1'], p['k2']

    # ============ ТОКИ РЕТОМА (универсальный метод) ============

    def calculate_currents_full(self, params):
        print(f"\n{'=' * 50}")
        print(f"calculate_currents_full для {self.device_type}")
        print(f"self.winding_side = {self.winding_side}")

        base = self._get_base_params(params)
        p = self._get_char_params(params)

        print(f"p['I_brake1'] = {p['I_brake1']}")
        print(f"p['I_brake2'] = {p['I_brake2']}")
        print(f"p['I_diff'] = {p['I_diff']}")
        print(f"p['k1'] = {p['k1']}")

        # Дифференциальные токи
        Id_hv = p['I_diff'] * base['I_nom_hv'] / base['koeff_CT_HV']
        Id_lv = p['I_diff'] * base['I_nom_lv'] / base['koeff_CT_LV']

        # Токи ретома для точек излома
        retom = self._calculate_retom_points(base, p)

        return {
            'I_nom_hv': round(base['I_nom_hv'], 2),
            'I_nom_lv': round(base['I_nom_lv'], 2),
            'I_sec_hv': round(base['I_sec_hv'], 2),
            'I_sec_lv': round(base['I_sec_lv'], 2),
            'koeff_CT_HV': round(base['koeff_CT_HV'], 2),
            'koeff_CT_LV': round(base['koeff_CT_LV'], 2),
            'Id_hv': round(Id_hv, 2),
            'Id_lv': round(Id_lv, 2),
            **retom
        }
    def calculate_arbitrary_point_full(self, I_brake, I_diff, params):
        """Произвольная точка (общий для всех)"""
        base = self._get_base_params(params)
        return self._calculate_arbitrary_retom(base, I_brake, I_diff)

    def calculate_blocking_currents(self, currents, params, arbitrary_point=None):
        """Блокировки (общий для всех)"""
        is_hv = self.winding_side == WindingSide.HV
        side = "ВН" if is_hv else "НН"
        current_key = 'Id_hv' if is_hv else 'Id_lv'

        data = [
            (f"Блокировка I2/I1 (в плечо {side})",
             f"{params['I2/I1'] / 100 * currents[current_key]:.2f}", params['I2/I1']),
            (f"Блокировка I5/I1 (в плечо {side})",
             f"{params['I5/I1'] / 100 * currents[current_key]:.2f}", params['I5/I1']),
        ]

        if arbitrary_point:
            base = self._get_base_params(params)
            block = self._get_blocking_for_point(base, arbitrary_point['I_brake'], is_hv, params)
            data.extend([
                ("Блокировка I2/I1 (произвольная точка)", block['I2'], params['I2/I1']),
                ("Блокировка I5/I1 (произвольная точка)", block['I5'], params['I5/I1'])
            ])

        return data

    # ============ АБСТРАКТНЫЕ МЕТОДЫ ============

    @abstractmethod
    def _calculate_retom_points(self, base, char_params):
        """Расчет токов ретома для точек излома"""
        pass

    @abstractmethod
    def _calculate_arbitrary_retom(self, base, I_brake, I_diff):
        """Расчет токов ретома для произвольной точки"""
        pass

    @abstractmethod
    def _get_blocking_for_point(self, base, I_brake, is_hv_side, params):
        """Расчет блокировок для произвольной точки"""
        pass

    # ============ ВСПОМОГАТЕЛЬНЫЕ ============

    def validate_params(self, params):
        required = ['S_nom', 'U_hv', 'U_lv', 'CT_hv_perv', 'CT_hv_sec', 'CT_lv_perv', 'CT_lv_sec']
        for key in required:
            if key not in params:
                return False, f"Отсутствует параметр: {key}"
            try:
                if float(params[key]) <= 0:
                    return False, f"Параметр {key} должен быть > 0"
            except (ValueError, TypeError):
                return False, f"Параметр {key} не является числом"
        return True, ""

    def numeric_params(self, params):
        numeric = {}
        for k, v in params.items():
            try:
                numeric[k] = float(v.replace(',', '.')) if isinstance(v, str) else float(v)
            except (ValueError, TypeError, AttributeError):
                numeric[k] = 0.0
        return numeric

    def update_params(self, params):
        self.current_params.update(params)