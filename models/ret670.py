from .device import ProtectionDevice, WindingSide, SlopeFormat


class RET670Device(ProtectionDevice):

    def __init__(self, device_type, default_params):
        super().__init__(device_type, default_params, slope_format=SlopeFormat.PERCENT)

    def _calculate_retom_points(self, base, p):
        I_brake1, I_brake2 = p['I_brake1'], p['I_brake2']
        I_diff = p['I_diff']
        k1 = p['k1']

        if self.winding_side == WindingSide.HV:
            return {
                'retom_hv1': round(I_brake1 / base['koeff_CT_HV'] * base['I_nom_hv'], 2),
                'retom_lv1': round((I_brake1 - I_diff) / base['koeff_CT_LV'] * base['I_nom_lv'], 2),
                'retom_skvoz_hv1' : round(I_brake1 / base['koeff_CT_HV'] * base['I_nom_hv'], 2),
                'retom_skvoz_lv1' : round(I_brake1 / base['koeff_CT_LV'] * base['I_nom_lv'], 2),
                'retom_hv2': round(I_brake2 / base['koeff_CT_HV'] * base['I_nom_hv'], 2),
                'retom_lv2': round((I_brake2 - (I_diff + k1 * (I_brake2 - I_brake1))) / base['koeff_CT_LV'] * base['I_nom_lv'], 2),
                'retom_skvoz_hv2': round(I_brake2 / base['koeff_CT_HV'] * base['I_nom_hv'], 2),
                'retom_skvoz_lv2': round(I_brake2 / base['koeff_CT_LV'] * base['I_nom_lv'], 2),
            }
        else:
            return {
                'retom_hv1': round((I_brake1 - I_diff) / base['koeff_CT_HV'] * base['I_nom_hv'], 2),
                'retom_lv1': round(I_brake1 / base['koeff_CT_LV'] * base['I_nom_lv'], 2),
                'retom_skvoz_hv1': round(I_brake1 / base['koeff_CT_HV'] * base['I_nom_hv'], 2),
                'retom_skvoz_lv1': round(I_brake1 / base['koeff_CT_LV'] * base['I_nom_lv'], 2),
                'retom_hv2': round((I_brake2 - (I_diff + k1 * (I_brake2 - I_brake1))) / base['koeff_CT_HV'] * base['I_nom_hv'], 2),
                'retom_lv2': round(I_brake2 / base['koeff_CT_LV'] * base['I_nom_lv'], 2),
                'retom_skvoz_hv2': round(I_brake2 / base['koeff_CT_HV'] * base['I_nom_hv'], 2),
                'retom_skvoz_lv2': round(I_brake2 / base['koeff_CT_LV'] * base['I_nom_lv'], 2),
            }

    def _calculate_arbitrary_retom(self, base, I_brake, I_diff):
        if self.winding_side == WindingSide.HV:
            return {
                'retom_hv_arb': f"{I_brake * base['I_nom_hv'] / base['koeff_CT_HV']:.2f}",
                'retom_lv_arb': f"{(I_brake - I_diff) * base['I_nom_lv'] / base['koeff_CT_LV']:.2f}",
                'retom_skvoz_arb_hv': f"{I_brake * base['I_nom_hv']  / base['koeff_CT_HV']:.2f}",
                'retom_skvoz_arb_lv': f"{I_brake * base['I_nom_lv']  / base['koeff_CT_LV']:.2f}"
            }
        else:
            return {
                'retom_hv_arb': f"{(I_brake - I_diff) * base['I_nom_hv'] / base['koeff_CT_HV']:.2f}",
                'retom_lv_arb': f"{I_brake * base['I_nom_lv'] / base['koeff_CT_LV']:.2f}",
                'retom_skvoz_arb_hv': f"{I_brake * base['I_nom_hv']  / base['koeff_CT_HV']:.2f}",
                'retom_skvoz_arb_lv': f"{I_brake * base['I_nom_lv']  / base['koeff_CT_LV']:.2f}"
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