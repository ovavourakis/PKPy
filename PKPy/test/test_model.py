import pytest
import sys
import os
from PKPy.model import Model, Compartment

current_dir = os.path.dirname(__file__)

file = os.path.join(current_dir, "test_model_subc.json")

def test_compartment_constructor():
    data = {
        'name': 'Unusual',
        'type': 'subcutaneous',
        'volume': 100,
        'initial_amount': 50,
        'rate_out': 0.5
    }
    compartment = Compartment(data)
    assert compartment.name == 'Unusual'
    assert compartment.type == 'subcutaneous'
    assert compartment.volume == 100
    assert compartment.initial_amount == 50
    assert compartment.rate_in is None
    assert compartment.rate_out == 0.5

def test_dose():
    model = Model(file) 

    model.dose_type = 'continuous'
    assert model.dose(0) == model.dose_constant
    assert model.dose(1) == model.dose_constant

    model.dose_type = 'bolus'
    assert model.dose(0) == model.dose_constant
    assert model.dose(1) == 0

def test_solve():
    model = Model(file) 

    result = model.solve()
    assert isinstance(result, dict)

    for compartment in model.compartment_list:
        assert compartment.name in result
        assert len(result[compartment.name]) == self.time_span


def test_ode_system_values():
    model = Model(file) 

    if model.is_subcutaneous == True:
        initial_values = [15.0, 3.0, 9.0]
        t = 5.0

        deriv = model.ode_system(t, initial_values)

        expected_derivatives = [
            2.0 * 9.0 - ((15.0 / 600.0) * 1.0) - 1.0 * ((15.0 / 600.0 - 3.0 / 300)),  # central compartment
            1.0 * (15.0 / 600.0 - 3.0 / 300),  # liver peripheral compartment
            20 - 2 * 9.0  #subcutaneous compartment 
        ]
        print(expected_derivatives)
        print(deriv)
        assert all(isinstance(val, float) for val in deriv)
        assert len(deriv) == len(expected_derivatives)
        for val, expected_val in zip(deriv, expected_derivatives):
            assert val == expected_val

    else:
        initial_values = [15.0, 3.0]
        t = 5.0

        deriv = model.ode_system(t, initial_values)

        expected_derivatives = [
            20 - (15.0 / 600) - 1.0 * (15.0 / 600.0 - 3.0 / 300), #Central compartment
            1.0 * (15.0 / 600.0 - 3.0 / 300.0)  # liver peripheral compartment
        ]

        assert all(isinstance(val, float) for val in deriv)
        assert len(deriv) == len(expected_derivatives)
        for val, expected_val in zip(deriv, expected_derivatives):
            assert val == expected_val
            
if __name__ == '__main__':
    pytest.main()

