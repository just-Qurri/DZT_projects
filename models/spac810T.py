from .device import ProtectionDevice, WindingSide, SlopeFormat


class SPAC810TDevice(ProtectionDevice):

    def __init__(self, default_params=None, device_type="SPAC810T"):
        if default_params is None:
            default_params = {}
        super().__init__(device_type, default_params, slope_format=SlopeFormat.PERCENT)

    def _get_char_params(self, params):
        """
        Переопределяем метод для SPAC810T, чтобы использовать фиксированное торможение для 3-го отрезка
        """
        # Получаем базовые параметры характеристики
        char_params = super()._get_char_params(params)
        k2 = 0.45
        char_params['k2'] = k2
        return char_params

    def _calculate_retom_points(self, base, p):
        I_brake1, I_brake2 = p['I_brake1'], p['I_brake2']
        I_diff = p['I_diff']
        k1 = p['k1']

        if self.winding_side == WindingSide.HV:
            return {
                'retom_hv1': round((2*I_brake1+I_diff)/2 / base['koeff_CT_HV'] * base['I_nom_hv'], 2),
                'retom_lv1': round((2*I_brake1-I_diff)/2 / base['koeff_CT_LV'] * base['I_nom_lv'], 2),
                'retom_skvoz_hv1' : round((2*I_brake1+I_diff)/2 / base['koeff_CT_HV'] * base['I_nom_hv'], 2),
                'retom_skvoz_lv1' : round((2*I_brake1+I_diff)/2 / base['koeff_CT_LV'] * base['I_nom_lv'], 2),
                'retom_hv2': round((2*I_brake2+(I_diff + k1 * (I_brake2 - I_brake1)))/2 / base['koeff_CT_HV'] * base['I_nom_hv'], 2),
                'retom_lv2': round((2*I_brake2-(I_diff + k1 * (I_brake2 - I_brake1)))/2 / base['koeff_CT_LV'] * base['I_nom_lv'], 2),
                'retom_skvoz_hv2': round((2*I_brake2+(I_diff + k1 * (I_brake2 - I_brake1)))/2 / base['koeff_CT_HV'] * base['I_nom_hv'], 2),
                'retom_skvoz_lv2': round((2*I_brake2+(I_diff + k1 * (I_brake2 - I_brake1))) /2/ base['koeff_CT_LV'] * base['I_nom_lv'], 2),
            }
        else:
            return {
                'retom_hv1': round((2*I_brake1-I_diff)/2 / base['koeff_CT_HV'] * base['I_nom_hv'], 2),
                'retom_lv1': round((2*I_brake1+I_diff)/2 / base['koeff_CT_LV'] * base['I_nom_lv'], 2),
                'retom_skvoz_hv1' : round((2*I_brake1+I_diff)/2 / base['koeff_CT_HV'] * base['I_nom_hv'], 2),
                'retom_skvoz_lv1' : round((2*I_brake1+I_diff)/2 / base['koeff_CT_LV'] * base['I_nom_lv'], 2),
                'retom_hv2': round((2*I_brake2-(I_diff + k1 * (I_brake2 - I_brake1)))/2 / base['koeff_CT_HV'] * base['I_nom_hv'], 2),
                'retom_lv2': round((2*I_brake2+(I_diff + k1 * (I_brake2 - I_brake1)))/2 / base['koeff_CT_LV'] * base['I_nom_lv'], 2),
                'retom_skvoz_hv2': round((2*I_brake2+(I_diff + k1 * (I_brake2 - I_brake1)))/2 / base['koeff_CT_HV'] * base['I_nom_hv'], 2),
                'retom_skvoz_lv2': round((2*I_brake2+(I_diff + k1 * (I_brake2 - I_brake1))) /2/ base['koeff_CT_LV'] * base['I_nom_lv'], 2),
            }

    def _calculate_arbitrary_retom(self, base, I_brake, I_diff):
        if self.winding_side == WindingSide.HV:
            return {
                'retom_hv_arb': (2*I_brake + I_diff)/2 * base['I_nom_hv'] / base['koeff_CT_HV'],
                'retom_lv_arb': (2*I_brake - I_diff)/2 * base['I_nom_lv'] / base['koeff_CT_LV'],
                'retom_skvoz_arb_hv': (2*I_brake + I_diff)/2 * base['I_nom_hv'] / base['koeff_CT_HV'],
                'retom_skvoz_arb_lv':(2*I_brake + I_diff)/2 * base['I_nom_lv'] / base['koeff_CT_LV'],
            }
        else:
            return {
                'retom_hv_arb': (2*I_brake - I_diff)/2 * base['I_nom_hv'] / base['koeff_CT_HV'],
                'retom_lv_arb': (2*I_brake + I_diff)/2 * base['I_nom_lv'] / base['koeff_CT_LV'],
                'retom_skvoz_arb_hv': (2*I_brake + I_diff)/2 * base['I_nom_hv'] / base['koeff_CT_HV'],
                'retom_skvoz_arb_lv': (2*I_brake + I_diff)/2 * base['I_nom_lv'] / base['koeff_CT_LV'],
            }

    def _get_blocking_for_point(self, base, I_brake, is_hv_side, params):
        if is_hv_side:
            return {
                'I2': f"{params['I2/I1'] / 100 * I_brake * base['I_nom_hv'] / base['koeff_CT_HV']:.2f}",
                'I5': f"{params['I5/I1'] / 100 * I_brake * base['I_nom_hv'] / base['koeff_CT_HV']:.2f}"
            }
        else:
            return {
                'I2': f"{params['I2/I1'] / 100 * I_brake * base['I_nom_lv'] / base['koeff_CT_LV']:.2f}",
                'I5': f"{params['I5/I1'] / 100 * I_brake * base['I_nom_lv'] / base['koeff_CT_LV']:.2f}"
            }