from .device import ProtectionDevice, WindingSide, SlopeFormat


class RET521Device(ProtectionDevice):

    def __init__(self, device_type, default_params):
        super().__init__(device_type, default_params, slope_format=SlopeFormat.RATIO)
        self.I_brake1 = 1.25

    def _get_char_params(self, params):
        """
        Переопределяем метод для RET-521, чтобы использовать фиксированное I_brake1 = 1.25
        """
        # Получаем базовые параметры характеристики
        char_params = super()._get_char_params(params)
        I_diff = char_params['I_diff']
        I_brake1 = self.I_brake1
        k1 = char_params['k1']
        char_params['I_brake1'] = self.I_brake1
        char_params['I_brake2'] = (1 - I_diff) / k1 + I_brake1
        return char_params

    def _calculate_retom_points(self, base, p):
        I_brake1= self.I_brake1
        I_diff = p['I_diff']
        k1 = p['k1']
        I_brake2=(1-I_diff)/k1+I_brake1

        if self.winding_side == WindingSide.HV:

            retom_hv1 = I_brake1 / base['koeff_CT_HV'] * base['I_nom_hv']
            retom_lv1 = (I_brake1 - I_diff) / base['koeff_CT_LV'] * base['I_nom_lv']
            retom_skvoz_hv1 = I_brake1  / base['koeff_CT_HV'] * base['I_nom_hv']
            retom_skvoz_lv1 = I_brake1  / base['koeff_CT_LV'] * base['I_nom_lv']
            retom_hv2 = I_brake2 / base['koeff_CT_HV'] * base['I_nom_hv']
            retom_lv2 = (I_brake2 - (I_diff + k1 * (I_brake2 - I_brake1))) / base['koeff_CT_LV'] * base['I_nom_lv']
            retom_skvoz_hv2=I_brake2  / base['koeff_CT_HV'] * base['I_nom_hv']
            retom_skvoz_lv2=I_brake2  / base['koeff_CT_LV'] * base['I_nom_lv']

            return {
                'retom_hv1': round(retom_hv1, 2),
                'retom_lv1': round(retom_lv1, 2),
                'retom_skvoz_hv1':round(retom_skvoz_hv1,2),
                'retom_skvoz_lv1':round(retom_skvoz_lv1,2),
                'retom_hv2': round(retom_hv2, 2),
                'retom_lv2': round(retom_lv2, 2),
                'retom_skvoz_hv2': round(retom_skvoz_hv2, 2),
                'retom_skvoz_lv2': round(retom_skvoz_lv2, 2),

            }
        else:

            retom_hv1 = (I_brake1 - I_diff) / base['koeff_CT_HV'] * base['I_nom_hv']
            retom_lv1 = I_brake1 / base['koeff_CT_LV'] * base['I_nom_lv']
            retom_skvoz_hv1 = I_brake1  / base['koeff_CT_HV'] * base['I_nom_hv']
            retom_skvoz_lv1 = I_brake1  / base['koeff_CT_LV'] * base['I_nom_lv']
            retom_hv2 = (I_brake2 - (I_diff + k1 * (I_brake2 - I_brake1))) / base['koeff_CT_HV'] * base['I_nom_hv']
            retom_lv2 = I_brake2 / base['koeff_CT_LV'] * base['I_nom_lv']
            retom_skvoz_hv2=I_brake2  / base['koeff_CT_HV'] * base['I_nom_hv']
            retom_skvoz_lv2=I_brake2  / base['koeff_CT_LV'] * base['I_nom_lv']


            return {
                'retom_hv1': round(retom_hv1, 2),
                'retom_lv1': round(retom_lv1, 2),
                'retom_skvoz_hv1': round(retom_skvoz_hv1, 2),
                'retom_skvoz_lv1': round(retom_skvoz_lv1, 2),
                'retom_hv2': round(retom_hv2, 2),
                'retom_lv2': round(retom_lv2, 2),
                'retom_skvoz_hv2': round(retom_skvoz_hv2, 2),
                'retom_skvoz_lv2': round(retom_skvoz_lv2, 2),
            }

    def _calculate_arbitrary_retom(self, base, I_brake, I_diff):
        if self.winding_side == WindingSide.HV:
            return {
                'retom_hv_arb': f"{I_brake * base['I_nom_hv'] / base['koeff_CT_HV']:.2f}",
                'retom_lv_arb': f"{(I_brake - I_diff) * base['I_nom_lv'] / base['koeff_CT_LV']:.2f}",
                'retom_skvoz_arb': f"{I_brake * base['I_nom_hv'] * base['U_hv'] / base['U_lv'] / base['koeff_CT_LV']:.2f}"
            }
        else:
            return {
                'retom_hv_arb': f"{(I_brake - I_diff) * base['I_nom_hv'] / base['koeff_CT_HV']:.2f}",
                'retom_lv_arb': f"{I_brake * base['I_nom_lv'] / base['koeff_CT_LV']:.2f}",
                'retom_skvoz_arb': f"{(I_brake - I_diff) * base['I_nom_hv'] * base['U_hv'] / base['U_lv'] / base['koeff_CT_LV']:.2f}"
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