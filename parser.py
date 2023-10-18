class Parser():
    """
    parses system.json
    returns a list of dictionaries [basic parameters, [compartment1, compartment2]] (each element is a dictionary)

    item with index 0 in second list is the CENTRAL compartment, index 1 is subcutaneous (if present), then other compartments

    within the basic parameters, the dose should be a list of two equal-length lists, one with time values, the other with dose values (doses first, then times)
    """
    def __init__(self, tokens):
        pass