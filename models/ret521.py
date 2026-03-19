"""
Модель для устройства RET-521.
Реализует специфичную логику расчета для данного устройства.
"""

import numpy as np
from .device import ProtectionDevice


class RET521Device(ProtectionDevice):
    """
    Класс для работы с устройством RET-521.
    Реализует методы расчета характеристик для данного типа защиты.
    Поддерживает два режима: опора ВН и опора НН.
    """

    def __init__(self, device_type, default_params):
        """
        Инициализация устройства RET-521.

        Args:
            device_type: Тип устройства (RET_521_HV или RET_521_LV)
            default_params: Параметры по умолчанию
        """
        super().__init__(device_type, default_params)
        self.Ibrake1 = 1.25  # Фиксированное значение для RET-521

    def calculate_characteristic(self, I_brake):
        """
        Расчет характеристики срабатывания для RET-521.

        Args:
            I_brake: Массив тормозных токов

        Returns:
            Массив дифференциальных токов
        """
        params = self.current_params
        I_diff = params['I_diff']
        k1 = params['k1']
        k2 = params['k2']
        I_brake2 = (1 - I_diff) / k1 + self.Ibrake1

        conditions = [
            I_brake <= self.Ibrake1,
            (I_brake > self.Ibrake1) & (I_brake <= I_brake2),
            I_brake > I_brake2
        ]

        choices = [
            I_diff,
            I_diff + k1 * (I_brake - self.Ibrake1),
            I_diff + k1 * (I_brake2 - self.Ibrake1) + k2 * (I_brake - I_brake2)
        ]

        return np.select(conditions, choices)

    def calculate_currents(self, params):
        """
        Расчет токов для RET-521.

        Args:
            params: Параметры для расчета

        Returns:
            Словарь с рассчитанными токами
        """
        S_nom = params['S_nom'] * 1e6
        sqrt3 = np.sqrt(3)

        U_hv = float(params['U_hv'])
        U_lv = float(params['U_lv'])

        I_nom_hv = S_nom / (sqrt3 * U_hv * 1e3)
        I_nom_lv = S_nom / (sqrt3 * U_lv * 1e3)

        koeff_CT_HV = params['CT_hv_perv'] / params['CT_hv_sec']
        koeff_CT_LV = params['CT_lv_perv'] / params['CT_lv_sec']

        I_sec_hv = I_nom_hv / koeff_CT_HV
        I_sec_lv = I_nom_lv / koeff_CT_LV

        Id_hv = params['I_diff'] * I_nom_hv / koeff_CT_HV
        Id_lv = params['I_diff'] * I_nom_lv / koeff_CT_LV

        I_brake2 = (1 - params['I_diff']) / params['k1'] + self.Ibrake1

        if self.device_type == "RET_521_HV":
            retom_hv1 = self.Ibrake1 / koeff_CT_HV * I_nom_hv
            retom_lv1 = (self.Ibrake1 - params['I_diff']) / koeff_CT_LV * I_nom_lv
            retom_hv2 = I_brake2 / koeff_CT_HV * I_nom_hv
            retom_lv2 = (I_brake2 - (
                        params['I_diff'] + params['k1'] * (I_brake2 - self.Ibrake1))) / koeff_CT_LV * I_nom_lv
        else:  # RET_521_LV
            retom_hv1 = (self.Ibrake1 - params['I_diff']) / koeff_CT_HV * I_nom_hv
            retom_lv1 = self.Ibrake1 / koeff_CT_LV * I_nom_lv
            retom_hv2 = (I_brake2 - (
                        params['I_diff'] + params['k1'] * (I_brake2 - self.Ibrake1))) / koeff_CT_HV * I_nom_hv
            retom_lv2 = I_brake2 / koeff_CT_LV * I_nom_lv

        return {
            'I_nom_hv': round(I_nom_hv, 2),
            'I_nom_lv': round(I_nom_lv, 2),
            'I_sec_hv': round(I_sec_hv, 2),
            'I_sec_lv': round(I_sec_lv, 2),
            'koeff_CT_HV': round(koeff_CT_HV, 2),
            'koeff_CT_LV': round(koeff_CT_LV, 2),
            'retom_hv1': round(retom_hv1, 2),
            'retom_lv1': round(retom_lv1, 2),
            'retom_hv2': round(retom_hv2, 2),
            'retom_lv2': round(retom_lv2, 2),
            'Id_hv': round(Id_hv, 2),
            'Id_lv': round(Id_lv, 2)
        }

    def calculate_arbitrary_point(self, I_brake, I_diff, params):
        """
        Расчет токов для произвольной точки.

        Args:
            I_brake: Тормозной ток в произвольной точке
            I_diff: Дифференциальный ток в произвольной точке
            params: Параметры для расчета

        Returns:
            Словарь с рассчитанными токами для произвольной точки
        """
        S_nom = params['S_nom'] * 1e6
        sqrt3 = np.sqrt(3)

        I_nom_hv = S_nom / (sqrt3 * params['U_hv'] * 1e3)
        I_nom_lv = S_nom / (sqrt3 * params['U_lv'] * 1e3)

        koeff_CT_HV = params['CT_hv_perv'] / params['CT_hv_sec']
        koeff_CT_LV = params['CT_lv_perv'] / params['CT_lv_sec']

        if self.device_type == "RET_521_HV":
            return {
                'retom_hv_arb': I_brake * I_nom_hv / koeff_CT_HV,
                'retom_lv_arb': (I_brake - I_diff) * I_nom_lv / koeff_CT_LV,
                'retom_skvoz_arb': I_brake * I_nom_hv * params['U_hv'] / params['U_lv'] / koeff_CT_LV
            }
        else:  # RET_521_LV
            return {
                'retom_hv_arb': (I_brake - I_diff) * I_nom_hv / koeff_CT_HV,
                'retom_lv_arb': I_brake * I_nom_lv / koeff_CT_LV,
                'retom_skvoz_arb': (I_brake - I_diff) * I_nom_hv * params['U_hv'] / params['U_lv'] / koeff_CT_LV
            }