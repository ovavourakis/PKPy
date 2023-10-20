import scipy, os, pickle
import matplotlib.pyplot as plt 
import numpy as np

from mpl_toolkits.axes_grid1 import make_axes_locatable
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
        self.systemfile = systemfile.split('/')[-1].split('.')[0]
        self.is_subcutaneous = basic_params['subcutaneous']         # boolean
        self.time_span = basic_params['time_span']                  # int
        self.dose_constant = basic_params['dose'][0]                # amount
        self.dose_type = basic_params['dose'][1]                    # dosage schedule

        # create compartment objects
        self.compartment_list = [Compartment(dict) for dict in compartments]
        if self.is_subcutaneous:
            self.central = self.compartment_list[0]
            self.subcutaneous = self.compartment_list[-1]
            self.other_compartments = self.compartment_list[1:-1]
        else:
            self.central, *self.other_compartments = self.compartment_list

    def dose(self,t):
        """
        Returns the dose at time t using specified dosage function by user:
            bolus: Rapid one time injection
            continuous: Continuous injection
            specified function: The dose function will turn your expression containing 'x'
                into a lambda function and a dose based on it. If you use numpy functions, please refer to it as 'np.'
        Args:
        - t (float): The time at which to calculate the dose.

        Returns:
        - The dose at time t.Ad

        """
        if self.dose_type == "continuous":
            return self.dose_constant
        elif self.dose_type == "bolus":
            return self.dose_constant if t == 0 else 0
        else:
            dosage_function = lambda x: eval(self.dose_type)
            return dosage_function(t)
            # raise ValueError("some error occurred in dose(t)")
    
    def ode_system(self, t, y):
        """
        Returns the system of ordinary differential equations (ODEs) that describe the model.

        Args:
        - t (float): The current time.
        - y (list): A list of the current amounts of substance in each compartment.

        Returns:
        - A list of the derivatives of the amounts of substance in each compartment.
        """
        if self.is_subcutaneous:
            central_amount, subcutaneous_amount = y[0], y[-1]
            other_amounts = y[1:-1]
        else:
            central_amount, *other_amounts = y

        # calculate derivatives for peripheral compartments
        derivatives = []
        for amount, C in zip(other_amounts, self.other_compartments):
            deriv = C.rate_in * (central_amount / self.central.volume - amount / C.volume)
            derivatives.append(deriv)
        # calculate derivative for subcutaneous and central compartments
        if self.is_subcutaneous:
            der_central = self.subcutaneous.rate_out * subcutaneous_amount - (central_amount * self.central.rate_out) /self.central.volume - sum(derivatives)
            der_subcutaneous = self.dose(t) - self.subcutaneous.rate_out * subcutaneous_amount
            return [der_central] + derivatives + [der_subcutaneous]
        else:
            der_central = self.dose(t) - (central_amount * self.central.rate_out) / self.central.volume - sum(derivatives)
            return [der_central] + derivatives

    def solve(self):
        """
        Solves the system of ODEs using scipy.integrate.solve_ivp and returns the solutions.

        Returns:
        - A dictionary containing the timeseries for each compartment.
        """
        t_span = [0, self.time_span]
        t_eval = np.arange(0, self.time_span, 1)

        # define initial conditions
        if self.is_subcutaneous:
            y0 = [self.central.initial_amount, self.subcutaneous.initial_amount]
            y0.extend([c.initial_amount for c in self.other_compartments])
        else:
            y0 = [self.central.initial_amount]
            y0.extend([c.initial_amount for c in self.other_compartments])

        sol = scipy.integrate.solve_ivp(self.ode_system, t_span, y0, t_eval=t_eval, method='RK45')

        compartment_timeseries = {}
        for i, C in enumerate(self.compartment_list):
            compartment_timeseries[C.name] = sol.y[i]

        os.makedirs('results/', exist_ok=True)
        with open(f'results/timeseries_{self.systemfile}.pickle', 'wb') as f:
            pickle.dump(compartment_timeseries, f)

        self.timeseries = compartment_timeseries

        return compartment_timeseries

    @staticmethod
    def random_color_generator():
        color = np.random.randint(0, 256, size=3)
        return tuple(color/255)
        
    def plot(self, title='PK Model', zoom_start=0, zoom_end=300, output='pk_model.png'):
        if hasattr(self, 'timeseries'):
            data = self.timeseries
        elif os.path.exists(f'results/timeseries_{self.systemfile}.pickle'):
            with open(f'results/timeseries_{self.systemfile}.pickle', 'rb') as handle:
                data = pickle.load(handle)
                if type(data) != dict:
                    raise ValueError(f"Pickle file 'results/timeseries_{self.systemfile}.pickle' is not a dictionary.")
        else:   
            raise ValueError("No timeseries data found. Please run solve() first.")
        
        plt.rcParams["font.family"] = "serif"
        plt.rcParams["mathtext.fontset"] = "dejavuserif"

        ## DATA
        # Get the compartments from the data
        compartments = list(data.keys())

        ## COlOURS
        colors_p = ["#091326","#84AEBF","#F29966","#BF5D39","#59211C"]
        colors_gen = [self.random_color_generator() for i in range(len(compartments))]
        colors = colors_p + colors_gen


        ## FIGURE
        # Create figure
        fig, ax = plt.subplots(dpi=300, figsize=(9, 3.5))

        # Plot the full data on the main axis
        for i, j in enumerate(compartments):
            ax.plot(data[j], label=j, c=colors[i])

        # Title 
        fig.suptitle(title, fontsize="large", y=1.05)

        ## MAIN AXIS TICKS
        # Set y-axis ticks on the right side of the plot
        ax.yaxis.tick_right()
        
        # Turn off y tick labels and yaxis on axm (main axis/plot)
        # axm = ax.axes.get_yaxis()
        # axm.set_visible(False)
        # axm.set_minor_locator(plt.NullLocator())

        ## LEFT ZOOMED AXIS
        # Create new axes on the left of the current axes
        divider = make_axes_locatable(ax)
        ax_zm = divider.append_axes("left", 2, pad=0.2)
        ax_zm.set_title('Zoomed in', fontsize="medium")
        ax_zm.set_ylim(-25, 50*self.dose_constant)
        ax.set_title('Full Plot', fontsize="medium")

        # Plot the zoomed in data on the left axis
        for i, j in enumerate(compartments):
            ax_zm.plot(data[j][zoom_start:zoom_end], label=j, c=colors[i])

        ## LABELS
        # Show y-labels on ax_zm (zoomed axis)
        ax_zm.set_ylabel('Concentration (mg/L)', fontsize="medium")
        ax_zm.set_xlabel('Timestep', fontsize="medium")
        ax.set_xlabel('Timestep', fontsize="medium")

        # Show legend
        ax.legend(loc='upper left', fontsize="x-small", frameon=False) # full plot # 


        # Save the figure
        plt.savefig(output, dpi=300, bbox_inches='tight')
