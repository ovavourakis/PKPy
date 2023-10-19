import scipy, numpy

from system_parser import Parser

class Compartment():
    def __init__(self, dict): # name, type, volume, initial_amount, rate_in, rate_out):
        self.name = dict['name']
        self.type = dict['type']
        self.volume = dict['volume']
        self.initial_amount = dict['initial_amount']
        self.rate_in = dict.get('rate_in', None)
        self.rate_out = dict['rate_out']

class Model():
    def __init__(self, systemfile):

        parser = Parser(systemfile)
        basic_params, compartment_list = parser.construct()

        # basic parameters
        self.subcutaneous = basic_params['subcutaneous']            # boolean
        self.dose_constant = basic_params['dose'][0]                # amount
        self.dose_type = basic_params['dose'][1]                    # dosage schedule

        # create compartment objects
        self.compartment_list = [Compartment(dict) for dict in compartment_list]
        if self.subcutaneous:
            self.central = self.compartment_list[0]
            self.subcutaneous = self.compartment_list[-1]
            self.other_compartments = self.compartment_list[1:-1]
        else:
            self.central, *self.other_compartments = self.compartment_list            # TODO: check if this works

    def dose(t):
        if self.dose_type == "continuous":
            return self.dose_constant
        elif self.dose_type == "once":
            return self.dose_constant if t==0 else 0
        else:
            raise ValueError("some error occured in dose(t)")
    
    def ode_system(t, y):
        if self.subcutaneous:
            central_amount, subcutaneous_amount = y[0], y[-1]
            other_amounts = y[1:-1]
        else:
            central_amount, *other_amounts = y

        # calculate derivatives for peripheral compartments
        derivatives = []
        for amount, C in zip(y0, self.other_compartments):
            deriv = C.rate_in * (y[0] / self.central.volume - amount / C.volume)
            derivatives.append(deriv)
        # calculate derivative for subcutaneous and central compartments
        if self.subcutaneous:
            der_central = self.subcutaneous.rate_out * y[-1] - y[0] / self.central.volume * self.central.rate_out - sum(derivatives)
            der_subcutaneous = dose(t) - self.subcutaneous.rate_out * y[-1]
            return [der_central] + derivatives + [der_subcutaneous]
        else:
            der_central = dose(t) - y[0] / self.central.volume * self.central.rate_out - sum(derivatives)
            return [der_central] + derivatives

    def solve(self):
        """
        passes the equations to scipy.integrate.solve_ivp and
        return solutions (timeseries)
        """
        # time span to project over (change to user-input TODO)
        t_span = 1000
        
        # define initial conditions
        if self.subcutaneous:
            y0 = [self.central.initial_amount, self.subcutaneous.initial_amount]
            for c in self.other_compartments:
                y0.append(c.initial_amount)
        else:
            y0 = [self.central.initial_amount]
            for c in self.other_compartments:
                y0.append(c.initial_amount)

        sol = scipy.integrate.solve_ivp(self.ode_system, t_span, y0)

        return sol
        
    def plot(self):
        """
        plots the solutions returned by self.solve()
        """
        pass