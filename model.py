import scipy

class Compartment():
    def __init__(self, compartment_dict): # name, type, volume, initial_amount, rate_in, rate_out):
        self.name = compartment_dict['name']
        self.type = compartment_dict['type']
        self.volume = compartment_dict['volume']
        self.initial_amount = compartment_dict['initial_amount']
        self.rate_in = compartment_dict['rate_in']
        self.rate_out = compartment_dict['rate_out']

class Model():
    def __init__(self):

        parser = Parser()
        basic_params, compartment_list = parser.construct()

        # basic parameters
        self.subcutaneous = basic_params['subcutaneous']
        self.dose_values = basic_params['dose']['dose_values']
        self.dose_times = basic_params['dose']['dose_time']

        # create compartment objects
        self.compartment_list = [Compartment(compartment_dict) for compartment_dict in compartment_list]
        if subcutaneous:
            self.central, self.subcutaneous, *self.other_compartments = compartment_list
        else:
            self.central, *self.other_compartments = compartment_list

        # compartment terms
        for C in self.compartment_list:
            transition = C.rate_in * (self.initiamount/ V_c - q_p1 / V_p1)
        


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