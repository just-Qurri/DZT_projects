import numpy as np
from .device import ProtectionDevice, SlopeFormat


class MR801Device(ProtectionDevice):

    def __init__(self, default_params):
        super().__init__("MR_801", default_params, slope_format=SlopeFormat.DEGREES)

    def _calculate_retom_points(self, base, p):
        I_brake1, I_brake2 = p['I_brake1'], p['I_brake2']
        I_diff = p['I_diff']
        k1 = p['k1']
        I_diff_at_2 = I_diff + k1 * (I_brake2 - I_brake1)

        return {
            'retom_hv1': round((I_brake1 + I_diff) / 2 / base['koeff_CT_HV'] * base['I_nom_hv'], 2),
            'retom_lv1': round((I_brake1 - I_diff) / 2 / base['koeff_CT_LV'] * base['I_nom_lv'], 2),
            'retom_skvoz_hv1' : round((I_brake1 + I_diff) / 2 / base['koeff_CT_HV'] * base['I_nom_hv'], 2),
            'retom_skvoz_lv1': round((I_brake1 + I_diff) / 2 / base['koeff_CT_LV'] * base['I_nom_lv'], 2),
            'retom_hv2': round((I_brake2 + I_diff_at_2) / 2 / base['koeff_CT_HV'] * base['I_nom_hv'], 2),
            'retom_lv2': round((I_brake2 - I_diff_at_2) / 2 / base['koeff_CT_LV'] * base['I_nom_lv'], 2),
            'retom_skvoz_hv2': round((I_brake2 + I_diff_at_2) / 2 / base['koeff_CT_HV'] * base['I_nom_hv'], 2),
            'retom_skvoz_lv2': round((I_brake2 + I_diff_at_2) / 2 / base['koeff_CT_LV'] * base['I_nom_lv'], 2),
        }

    def _calculate_arbitrary_retom(self, base, I_brake, I_diff):
        return {
            'retom_hv_arb': (I_brake + I_diff) * base['I_nom_hv'] / 2 / base['koeff_CT_HV'],
            'retom_lv_arb': (I_brake - I_diff) * base['I_nom_lv'] / 2 / base['koeff_CT_LV'],
            'retom_skvoz_arb': (I_brake + I_diff) * base['I_nom_hv'] * base['U_hv'] / base['U_lv'] / 2 / base[
                'koeff_CT_LV']
        }

    def _get_blocking_for_point(self, base, I_brake, is_hv_side, params):
        I_diff = params['I_diff']
        I_brake_eff = (I_brake + I_diff) / 2
        return {
            'I2': f"{params['I2/I1'] / 100 * I_brake_eff:.2f}",
            'I5': f"{params['I5/I1'] / 100 * I_brake_eff:.2f}"
        }