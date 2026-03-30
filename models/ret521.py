from .device import ProtectionDevice, WindingSide, SlopeFormat


class RET521Device(ProtectionDevice):

    def __init__(self, device_type, default_params):
        super().__init__(device_type, default_params, slope_format=SlopeFormat.RATIO)
        self.I_brake1 = 1.25

    def _get_char_params(self, params):
        p = super()._get_char_params(params)
        p['k1'] = params.get('k1', self.default_params.get('k1', 0))
        p['I_brake1'] = self.I_brake1
        p['I_brake2'] = (1 - p['I_diff']) / p['k1'] + self.I_brake1
        return p

    def _calculate_retom_points(self, base, p):
        I_brake1, I_brake2 = self.I_brake1, p['I_brake2']
        I_diff = p['I_diff']
        k1 = p['k1']

        if self.winding_side == WindingSide.HV:

            retom_hv1 = I_brake1 / base['koeff_CT_HV'] * base['I_nom_hv']
            retom_lv1 = (I_brake1 - I_diff) / base['koeff_CT_LV'] * base['I_nom_lv']
            retom_hv2 = I_brake2 / base['koeff_CT_HV'] * base['I_nom_hv']
            retom_lv2 = (I_brake2 - (I_diff + k1 * (I_brake2 - I_brake1))) / base['koeff_CT_LV'] * base['I_nom_lv']

            print(f"retom_hv1 = {retom_hv1:.2f}")
            print(f"retom_lv1 = {retom_lv1:.2f}")
            print(f"retom_hv2 = {retom_hv2:.2f}")
            print(f"retom_lv2 = {retom_lv2:.2f}")

            return {
                'retom_hv1': round(retom_hv1, 2),
                'retom_lv1': round(retom_lv1, 2),
                'retom_hv2': round(retom_hv2, 2),
                'retom_lv2': round(retom_lv2, 2)
            }
        else:

            retom_hv1 = (I_brake1 - I_diff) / base['koeff_CT_HV'] * base['I_nom_hv']
            retom_lv1 = I_brake1 / base['koeff_CT_LV'] * base['I_nom_lv']
            retom_hv2 = (I_brake2 - (I_diff + k1 * (I_brake2 - I_brake1))) / base['koeff_CT_HV'] * base['I_nom_hv']
            retom_lv2 = I_brake2 / base['koeff_CT_LV'] * base['I_nom_lv']

            return {
                'retom_hv1': round(retom_hv1, 2),
                'retom_lv1': round(retom_lv1, 2),
                'retom_hv2': round(retom_hv2, 2),
                'retom_lv2': round(retom_lv2, 2)
            }

    def _calculate_arbitrary_retom(self, base, I_brake, I_diff):
        if self.winding_side == WindingSide.HV:
            return {
                'retom_hv_arb': I_brake * base['I_nom_hv'] / base['koeff_CT_HV'],
                'retom_lv_arb': (I_brake - I_diff) * base['I_nom_lv'] / base['koeff_CT_LV'],
                'retom_skvoz_arb': I_brake * base['I_nom_hv'] * base['U_hv'] / base['U_lv'] / base['koeff_CT_LV']
            }
        else:
            return {
                'retom_hv_arb': (I_brake - I_diff) * base['I_nom_hv'] / base['koeff_CT_HV'],
                'retom_lv_arb': I_brake * base['I_nom_lv'] / base['koeff_CT_LV'],
                'retom_skvoz_arb': (I_brake - I_diff) * base['I_nom_hv'] * base['U_hv'] / base['U_lv'] / base[
                    'koeff_CT_LV']
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