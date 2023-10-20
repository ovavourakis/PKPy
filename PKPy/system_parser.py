import json
import numpy as np


class Parser:
    """
    This class parses and stores the system configuration from a user-provided config file in JSON (compartment definitions).

    :param system_config: The path to the system configuration file (compartment definitions).
    :type system_config: str

    :Usage Example:

    >>> parser = Parser('system.json')
    >>> parser.construct()
    [{'subcutaneous': 1, 'dose': [100, 'bolus']}, [{'name': 'Central', 'type': 'central', 'volume': 2, 'initial_amount': 0, 'rate_in': 0, 'rate_out': 0}, {'name': 'Peripheral', 'type': 'peripheral', 'volume': 1, 'initial_amount': 0, 'rate_in': 0, 'rate_out': 0}, {'name': 'Subcutaneous', 'type': 'subcutaneous', 'volume': 0.5, 'initial_amount': 0, 'rate_in': 0, 'rate_out': 0}]]
    """

    def __init__(self, system_config):
        """
        Initializes a Parser object with the given system configuration file (model compartment definitions).

        :param system_config: The path to the system configuration file.
        :type system_config: str

        :rtype: None 
        """
        with open(system_config) as system_config_file:
            self.sys_config = json.load(system_config_file)

    def construct(self):
        """
        For an initialised Parser object, constructs and returns the system configuration.

        :return: A list, containing the model's basic parameters (as a dictionary) and individual compartment parameters (as a list of dictionaries).
        :rtype: list

        :raises ValueError: If the subcutaneous flag is set to True, the corresponding compartment must also be defined and vice versa.
        :raises ValueError: If drug dosage is not a positive number.
        :raises ValueError: If drug administration type is not 'bolus' or 'continuous'.
        :raises ValueError: If there is not exactly one compartment with a 'central' type.
        :raises ValueError: If there is more than one compartment with a 'subcutaneous' type.
        :raises ValueError: If a compartment has a type other than 'central', 'subcutaneous', or 'peripheral'.
        :raises ValueError: If the volume of a compartment is not a positive number.
        """
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
                    i.update({attribute: None})  # Adding missing parameters

        # Testing for wrong system_config files
        if ((basic_pars['subcutaneous'] == 1 and compartments_sorted[-1]['type'] != 'subcutaneous') or
                (basic_pars['subcutaneous'] != 1 and compartments_sorted[-1]['type'] == 'subcutaneous')):
            raise ValueError("If the subcutaneous flag is set to True, the corresponding compartment must also be "
                             "defined and vice versa.")
        if not isinstance(basic_pars['time_span'], int) or basic_pars['time_span'] <= 0:
            raise ValueError("Time span must be positive integer.")
        try:
            dosage_func = lambda x: eval(basic_pars['dose'])
            dosage_func(10)
        except:
            if not isinstance(basic_pars['dose'], list) or basic_pars['dose'][1] not in ["bolus", "continuous"]:
                raise ValueError("Drug administration type must be 'bolus' or 'continuous' or a function expression "
                                 "containing 'x', like 'np.cos(x +3)'")
        if not isinstance(basic_pars['dose'],str):
            if type(basic_pars['dose'][0]) not in [int, float] or basic_pars['dose'][0] <= 0:
                raise ValueError("Drug dosage must be positive number.")

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
