import scipy, os, pickle
import matplotlib.pyplot as plt 
import numpy as np

from mpl_toolkits.axes_grid1 import make_axes_locatable
from .system_parser import Parser

class Compartment():
    """
    A class representing a compartment in a pharmacokinetic model.

    :ivar str name: The name of the compartment.
    :ivar str type: The type of the compartment ('central', 'subcutaneous', or 'peripheral').
    :ivar float volume: The volume of the compartment.
    :ivar float initial_amount: The initial amount of substance in the compartment.
    :ivar float rate_in: The rate of substance flowing into the compartment.
    :ivar float rate_out: The rate of substance flowing out of the compartment.
    """
    def __init__(self, dict):
        """
        Initializes a Compartment object with the given dictionary of parameters.

        :param dict: A dictionary containing the following keys:
            - name (str): The name of the compartment.
            - type (str): The type of the compartment.
            - volume (float): The volume of the compartment.
            - initial_amount (float): The initial amount of substance in the compartment.
            - rate_in (float, optional): The rate of substance flowing into the compartment. Defaults to None.
            - rate_out (float): The rate of substance flowing out of the compartment.
        :type dict: dict
        """
        self.name = dict['name']
        self.type = dict['type']
        self.volume = dict['volume']
        self.initial_amount = dict['initial_amount']
        self.rate_in = dict.get('rate_in', None)
        self.rate_out = dict['rate_out']

class Model():
    class Model():
        """
        A class representing a pharmacokinetic model.

        :ivar str systemfile: The name of the system file (compartment definitions).
        :ivar bool is_subcutaneous: Whether the model has a subcutaneous compartment or not.
        :ivar float dose_constant: The dose constant.
        :ivar str dose_type: The type dosage schedule ('bolus' or 'continuous').
        :ivar list compartment_list: A list of compartments in the model (as Compartment objects).
        :ivar Compartment central: The central compartment.
        :ivar Compartment subcutaneous: The subcutaneous compartment (if present).
        :ivar list other_compartments: A list of other (peripheral) compartments in the model.

        :method __init__(self, systemfile):
            Initializes a Model object with the given system file.

        :method dose(self, t):
            Returns the dose at time t.

        :method ode_system(self, t, y):
            Returns the system of ordinary differential equations (ODEs) that describe the model.

        :method solve(self):
            Solves the system of ODEs using scipy.integrate.solve_ivp and returns the solutions.

        :method plot(self, title='PK Model', zoom_start=0, zoom_end=100, output='pk_model.png'):
            Plots the time series data for the pharmacokinetic model.
        """
    def __init__(self, systemfile):
        """
        Initializes a Model object with the given system file (the specification of
        the ODE system in the form of compartments of particular types ("central", 
        "subcutaneous" or "peripheral") with associated rates, volumes and initial amounts).

        :param systemfile: The path to the system file.
        :type systemfile: str
        """
        parser = Parser(systemfile)
        basic_params, compartments = parser.construct()

        # basic parameters
        self.systemfile = systemfile.split('/')[-1].split('.')[0]
        self.is_subcutaneous = basic_params['subcutaneous']         # boolean
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
        Returns the dose at time t.

        :param t: The time at which to calculate the dose.
        :type t: float
        :return: The dose at time t.
        :rtype: float
        :raises ValueError: If an invalid dose type is specified.
        """
        if self.dose_type == "continuous":
            return self.dose_constant
        elif self.dose_type == "bolus":
            return self.dose_constant if t==0 else 0
        else:
            raise ValueError("Invalid dose type specified.")
    
    def ode_system(self, t, y):
        """
        Returns the system of ordinary differential equations (ODEs) that describe the model.

        :param t: The current time.
        :type t: float
        :param y: A list of the current amounts of substance in each compartment.
        :type y: list
        :return: A list of the derivatives of the amounts of substance in each compartment.
        :rtype: list
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
            der_central = self.subcutaneous.rate_out * subcutaneous_amount -central_amount / self.central.volume * self.central.rate_out - sum(derivatives)
            der_subcutaneous = self.dose(t) - self.subcutaneous.rate_out * subcutaneous_amount
            return [der_central] + derivatives + [der_subcutaneous]
        else:
            der_central = self.dose(t) - central_amount/ self.central.volume * self.central.rate_out - sum(derivatives)
            return [der_central] + derivatives

    def solve(self):
        """
        Solves the system of ODEs using scipy.integrate.solve_ivp and returns the solutions.

        :return: A dictionary containing the timeseries for each compartment.
        :rtype: dict
        """
        # time span to project over (change to user-input TODO)
        t_span = [0,1000]
        t_eval = np.linspace(t_span[0],t_span[1],1000)
        
        # define initial conditions
        if self.is_subcutaneous:
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

        os.makedirs('results/', exist_ok=True)
        with open(f'results/timeseries_{self.systemfile}.pickle', 'wb') as f:
            pickle.dump(compartment_timeseries, f)

        self.timeseries = compartment_timeseries

        return compartment_timeseries
        
    def plot(self, title='PK Model', zoom_start=0, zoom_end=100, output='pk_model.png'):       
        """
        Plots the time series data for the pharmacokinetic model.

        :param title: Title of the plot. Default is 'PK Model'.
        :type title: str
        :param zoom_start: Starting timestep for the zoomed in plot. Default is 0.
        :type zoom_start: int
        :param zoom_end: Ending timestep for the zoomed in plot. Default is 100.
        :type zoom_end: int
        :param output: Output file name for the plot. Default is 'pk_model.png'.
        :type output: str
        :raises ValueError: If no timeseries data is found, or if the pickle file is not a dictionary.
        """
        
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

        ## COLORS
        colors = ["#091326","#84AEBF","#F29966","#BF5D39","#59211C"]    

        ## FIGURE
        # Create figure
        fig, ax = plt.subplots(dpi=300, figsize=(9, 3.5))

        # Plot the full data on the main axis
        for i, j in enumerate(compartments):
            # Exceptions for more than 5 compartments (colors)
            try:
                ax.plot(data[j], label=j, c=colors[i])
            except:
                ax.plot(data[j], label=j)

        # Title 
        fig.suptitle(title, fontsize="large", y=1.05)

        ## MAIN AXIS TICKS
        # Turn off y tick labels and yaxis on axm (main axis/plot)
        axm = ax.axes.get_yaxis()
        axm.set_visible(False)
        axm.set_minor_locator(plt.NullLocator())

        ## LEFT ZOOMED AXIS
        # Create new axes on the left of the current axes
        divider = make_axes_locatable(ax)
        ax_zm = divider.append_axes("left", 2, pad=0.2, sharey=ax)
        ax_zm.set_title('Zoomed in', fontsize="medium")
        ax.set_title('Full Plot', fontsize="medium")

        # Plot the zoomed in data on the left axis
        for i, j in enumerate(compartments):
            # Exceptions for more than 5 compartments (colors)
            try:
                ax_zm.plot(data[j][zoom_start:zoom_end], label=j, c=colors[i])
            except:
                ax_zm.plot(data[j][zoom_start:zoom_end], label=j)

        ## LABELS
        # Show y-labels on ax_zm (zoomed axis)
        ax_zm.set_ylabel('Concentration (mg/L)', fontsize="medium")
        ax_zm.set_xlabel('Timestep', fontsize="medium")
        ax.set_xlabel('Timestep', fontsize="medium")
        # Show legend
        ax.legend(loc='upper left', fontsize="x-small", frameon=False) # full plot
        #ax_zm.legend(loc='upper left', fontsize="x-small", frameon=False)  # zoomed plot

        # Save the figure
        plt.savefig(output, dpi=300, bbox_inches='tight')