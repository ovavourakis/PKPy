import scipy
import numpy as np

from .system_parser import Parser

class Compartment():
    
    def __init__(self, dict): # name, type, volume, initial_amount, rate_in, rate_out):
        """
        Initializes a Compartment object with the given dictionary of parameters.

        Args:
        - dict (dict): A dictionary containing the following keys:
            - name (str): The name of the compartment.
            - type (str): The type of the compartment.
            - volume (float): The volume of the compartment.
            - initial_amount (float): The initial amount of substance in the compartment.
            - rate_in (float): The rate of substance flowing into the compartment.
            - rate_out (float): The rate of substance flowing out of the compartment.
        """
        self.name = dict['name']
        self.type = dict['type']
        self.volume = dict['volume']
        self.initial_amount = dict['initial_amount']
        self.rate_in = dict.get('rate_in', None)
        self.rate_out = dict['rate_out']

class Model():
    def __init__(self, systemfile):
        """
        Initializes a Model object with the given system file (the specification of
        the ODE system in the form of compartments of particular types ("central", 
        "subcutaneous" or "peripheral") with associated rates, volumes and initial amounts).

        Args:
        - systemfile (str): The path to the system file.
        """
        parser = Parser(systemfile)
        basic_params, compartments = parser.construct()

        # basic parameters
        self.subcutaneous = basic_params['subcutaneous']            # boolean
        self.dose_constant = basic_params['dose'][0]                # amount
        self.dose_type = basic_params['dose'][1]                    # dosage schedule

        # create compartment objects
        self.compartment_list = [Compartment(dict) for dict in compartments]
        if self.subcutaneous:
            self.central = self.compartment_list[0]
            self.subcutaneous = self.compartment_list[-1]
            self.other_compartments = self.compartment_list[1:-1]
        else:
            self.central, *self.other_compartments = self.compartment_list

    def dose(self,t):
        """
        Returns the dose at time t.

        Args:
        - t (float): The time at which to calculate the dose.

        Returns:
        - The dose at time t.
        """
        if self.dose_type == "continuous":
            return self.dose_constant
        elif self.dose_type == "bolus":
            return self.dose_constant if t==0 else 0
        else:
            raise ValueError("some error occured in dose(t)")
    
    def ode_system(self, t, y):
        """
        Returns the system of ordinary differential equations (ODEs) that describe the model.

        Args:
        - t (float): The current time.
        - y (list): A list of the current amounts of substance in each compartment.

        Returns:
        - A list of the derivatives of the amounts of substance in each compartment.
        """
        if self.subcutaneous:
            central_amount, subcutaneous_amount = y[0], y[-1]
            other_amounts = y[1:-1]
        else:
            self.central_amount, *self.other_amounts = y

        # calculate derivatives for peripheral compartments
        derivatives = []
        for amount, C in zip(other_amounts, self.other_compartments):
            deriv = C.rate_in * (central_amount / self.central.volume - amount / C.volume)
            derivatives.append(deriv)
        # calculate derivative for subcutaneous and central compartments
        if self.subcutaneous:
            der_central = self.subcutaneous.rate_out * subcutaneous_amount -central_amount / self.central.volume * self.central.rate_out - sum(derivatives)
            der_subcutaneous = self.dose(t) - self.subcutaneous.rate_out * subcutaneous_amount
            return [der_central] + derivatives + [der_subcutaneous]
        else:
            der_central = self.dose(t) - central_amount/ self.central.volume * self.central.rate_out - sum(derivatives)
            return [der_central] + derivatives

    def solve(self):
        """
        Solves the system of ODEs using scipy.integrate.solve_ivp and returns the solutions.

        Returns:
        - A dictionary containing the timeseries for each compartment.
        """
        # time span to project over (change to user-input TODO)
        t_span = [0,1000]
        t_eval = np.linspace(t_span[0],t_span[1],1000)
        
        # define initial conditions
        if self.subcutaneous:
            y0 = [self.central.initial_amount, self.subcutaneous.initial_amount]
            for c in self.other_compartments:
                y0.append(c.initial_amount)
        else:
            y0 = [self.central.initial_amount]
            for c in self.other_compartments:
                y0.append(c.initial_amount)

        sol = scipy.integrate.solve_ivp(self.ode_system, t_span, y0, t_eval=t_eval)

        compartment_timeseries = {}
        for i, C in enumerate(self.compartment_list):
            compartment_timeseries[C.name] = sol.y[i]

        return compartment_timeseries
        
    def plot(self):
        """
        Plots the solutions returned by self.solve().
        """
        pass