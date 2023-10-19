import json
class Parser:
    """
    parses system.json
    returns a list of dictionaries [basic parameters, [compartment1, compartment2]] (each element is a dictionary)

    item with index 0 in second list is the CENTRAL compartment, index -1 is subcutaneous (if present), then other compartments

    within the basic parameters, the dose should be a list of two equal-length lists, one with time values, the other with dose values (doses first, then times)
    """

    def __init__(self, system_config):
        with open(system_config) as system_config_file:
            self.sys_config = json.load(system_config_file)

    def construct(self):

        basic_pars = self.sys_config['basic_parameters']
        sys_config_cp = self.sys_config.copy()
        del sys_config_cp['basic_parameters']
        compartments = list(sys_config_cp.values())
        compartments_sorted = sorted(compartments, key=lambda d: d['type'])

        if ((basic_pars['subcutaneous'] == 1 and compartments_sorted[-1]['type'] != 'subcutaneous') or
                (basic_pars['subcutaneous'] != 1 and compartments_sorted[-1]['type'] == 'subcutaneous')):
            raise ValueError("If the subcutaneous flag is True, the corresponding compartment must be defined and vice versa.")

        for compartment in compartments_sorted:
            if compartment['type'] not in ['central', 'subcutaneous', 'peripheral']:
                raise ValueError(f"The {compartment['name']} compartment can be central, subcutaneous, or peripheral")

        return [basic_pars, compartments_sorted]