from typing import Any
import scipy

class Compartment():
    def __init__(self, name, type, volume, initial_amount, rate_in, rate_out):
        self.name = name
        self.type = type
        self.volume = volume
        self.initial_amount = initial_amount
        self.rate_in = rate_in
        self.rate_out = rate_out

class Model():
    def __init__(self):

        dose, subcutaneous, compartments = None # calls the parser

        # turn dictionaries into Compartment() objects

        

        equations = None # do stuff with the compartment objects

    def solve(self):
        """
        passes the equations to scipy.integrate.solve_ivp and
        return solutions (timeseries)
        """


    #     sol = scipy.integrate.solve_ivp( fun=lambda t, y: rhs(t, y, *args),
    #     t_span=[t_eval[0], t_eval[-1]],
    #     y0=y0, t_eval=t_eval
    # )
        
    def plot(self):
        """
        plots the solutions returned by self.solve()
        """
        


# def rhs(t, y, Q_p1, V_c, V_p1, CL, X):
#     q_c, q_p1 = y

#     transition = Q_p1 * (q_c / V_c - q_p1 / V_p1)

#     dqc_dt = dose(t, X) - q_c / V_c * CL - transition
#     dqp1_dt = transition
#     return [dqc_dt, dqp1_dt]