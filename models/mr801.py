from .device import ProtectionDevice, SlopeFormat


class MR801Device(ProtectionDevice):

    def __init__(self, default_params=None, device_type="MR_801"):
        if default_params is None:
            default_params = {}
        super().__init__(device_type, default_params, slope_format=SlopeFormat.DEGREES)

    def _calculate_retom_points(self, base, p):
        I_brake1, I_brake2 = p['I_brake1'], p['I_brake2']
        I_diff = p['I_diff']
        k1 = p['k1']
        I_diff_at_2 = I_diff + k1 * (I_brake2 - I_brake1)

        return {
            'retom_hv1': f"{(I_brake1 + I_diff) / 2 / base['koeff_CT_HV'] * base['I_nom_hv']:.2f}",
            'retom_lv1': f"{(I_brake1 - I_diff) / 2 / base['koeff_CT_LV'] * base['I_nom_lv']:.2f}",
            'retom_skvoz_hv1': f"{(I_brake1 + I_diff) / 2 / base['koeff_CT_HV'] * base['I_nom_hv']:.2f}",
            'retom_skvoz_lv1':f"{(I_brake1 + I_diff) / 2 / base['koeff_CT_LV'] * base['I_nom_lv']:.2f}",
            'retom_hv2': f"{(I_brake2 + I_diff_at_2) / 2 / base['koeff_CT_HV'] * base['I_nom_hv']:.2f}",
            'retom_lv2': f"{(I_brake2 - I_diff_at_2) / 2 / base['koeff_CT_LV'] * base['I_nom_lv']:.2f}",
            'retom_skvoz_hv2': f"{(I_brake2 + I_diff_at_2) / 2 / base['koeff_CT_HV'] * base['I_nom_hv']:.2f}",
            'retom_skvoz_lv2': f"{(I_brake2 + I_diff_at_2) / 2 / base['koeff_CT_LV'] * base['I_nom_lv']:.2f}",
        }

    def _calculate_arbitrary_retom(self, base, I_brake, I_diff):
        I_brake = float(I_brake)
        I_diff = float(I_diff)
        return {
            'retom_hv_arb': f"{((I_brake + I_diff) * base['I_nom_hv'] / 2 / base['koeff_CT_HV']):.2f}",
            'retom_lv_arb': f"{((I_brake - I_diff) * base['I_nom_lv'] / 2 / base['koeff_CT_LV']):.2f}",
            'retom_skvoz_arb_hv': f"{((I_brake + I_diff) * base['I_nom_hv']  / 2 / base['koeff_CT_HV']):.2f}",
            'retom_skvoz_arb_lv': f"{((I_brake + I_diff) * base['I_nom_lv']  / 2 / base['koeff_CT_LV']):.2f}"
        }


