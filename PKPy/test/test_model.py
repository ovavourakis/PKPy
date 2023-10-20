import pytest
from PKPy.model import Model, Compartment

@pytest.fixture
def model():
    """
    Fixture that returns a Model object initialized with the file path to a JSON file with a predefined model configuration.
    """
    return Model("PKPy/test/test_model.json")

def test_compartment_constructor():
    """
    Test function that tests the constructor of the Compartment class.
    """
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

def test_dose(model):
    """
    Test function that tests the dose method of the Model class.
    """
    model.dose_type = 'continuous'
    assert model.dose(0) == model.dose_constant
    assert model.dose(1) == model.dose_constant

    model.dose_type = 'bolus'
    assert model.dose(0) == model.dose_constant
    assert model.dose(1) == 0

def test_ode_system(model):
    """
    Test function that tests the ode_system method of the Model class.
    """
    y = [15, 3, 6, 9]
    t = 5

    model.is_subcutaneous = True
    deriv = model.ode_system(t, y)
    assert len(deriv) == 4
    assert all(isinstance(val, float) for val in deriv)

    model.is_subcutaneous = False
    deriv = model.ode_system(t, y)
    assert len(deriv) == 3
    assert all(isinstance(val, float) for val in deriv)

def test_solve(model):
    """
    Test function that tests the solve method of the Model class.
    """
    result = model.solve()
    assert isinstance(result, dict)

    for compartment in model.compartment_list:
        assert compartment.name in result
        assert len(result[compartment.name]) == 1000

if __name__ == '__main__':
    pytest.main()

