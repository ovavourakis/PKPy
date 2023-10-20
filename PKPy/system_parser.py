import json


class Parser:
    """
    This class pareses system.json file and returns a list of dictionaries:
    [basic parameters, [compartment1, compartment2]]
    """

    def __init__(self, system_config):
        with open(system_config) as system_config_file:
            self.sys_config = json.load(system_config_file)

    def construct(self):

        basic_pars = self.sys_config['basic_parameters']
        sys_config_cp = self.sys_config.copy()
        del sys_config_cp['basic_parameters']
        compartments = list(sys_config_cp.values())
        compartments_sorted = sorted(compartments, key=lambda d: d['type'])  # Sorting compartments

        # Item with index 0 in the "compartments_sorted" list is the CENTRAL compartment.
        # Item with index -1  in the "compartments_sorted" list is SUBCUTANEOUS compartment (if present).

        for i in compartments_sorted:
            missing_attributes = list(
                {"name", "type", "volume", "initial_amount", "rate_in", "rate_out"} - set(i.keys()))
            if len(missing_attributes) != 0:
                for attribute in missing_attributes:
                    i.update({attribute: None})               # Adding missing parameters

        # Testing for wrong system_config files
        if ((basic_pars['subcutaneous'] == 1 and compartments_sorted[-1]['type'] != 'subcutaneous') or
                (basic_pars['subcutaneous'] != 1 and compartments_sorted[-1]['type'] == 'subcutaneous')):
            raise ValueError("If the subcutaneous flag is set to True, the corresponding compartment must also be "
                             "defined and vice versa.")
        if type(basic_pars['dose'][0]) not in [int, float] or basic_pars['dose'][0] <= 0:
            raise ValueError("Drug dosage must be positive number.")
        if basic_pars['dose'][1] not in ["bolus", "continuous"]:
            raise ValueError("Drug administration type must be 'bolus' or 'continuous'")
        if [i['type'] for i in compartments_sorted].count('central') != 1:
            raise ValueError("One and only one of the compartments must have a 'central' type")
        if [i['type'] for i in compartments_sorted].count('subcutaneous') > 1:
            raise ValueError("Only one compartment could have a 'subcutaneous' type.")
        for compartment in compartments_sorted:
            if compartment['type'] not in ['central', 'subcutaneous', 'peripheral']:
                raise ValueError(f"The {compartment['name']} compartment can be central, subcutaneous, or peripheral")
            if compartment['volume'] is None or compartment['volume'] <= 0:
                raise ValueError(f"The volume of compartment {compartment['name']} must be positive number.")

        return [basic_pars, compartments_sorted]
