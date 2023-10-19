# Functions to visualise the PK data

import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
#import matplotlib.colors as mcolors
import numpy as np
import pickle
# Global font settings
plt.rcParams["font.family"] = "serif"
plt.rcParams["mathtext.fontset"] = "dejavuserif"

# LOAD PICKLE DATA
# Filename
data_eg = 'example_timeseries.pkl'
# Load the data
with open(data_eg, 'rb') as handle:
    d = pickle.load(handle)


# Extract the compartments from data
def get_compartments(data):
    """
    Extract the compartments from the data.

    Parameters
    ----------
    data : dict
        Dictionary of the data.

    Returns
    -------
    compartments : list
        List of the compartments.
    """

    # Get the compartments
    compartments = list(data.keys())
    return compartments


# Generate an overall plot for the compartments
def combined_plot(data, title='PK Model', zoom_start=0, zoom_end=100):
    """
    Generate a plot of the PK model.

    Parameters
    ----------
    data : dict
        Dictionary of the data.
    title : str
        Title of the plot.
    zoom_start : int
        Start of the zoomed in plot.
    zoom_end : int
        End of the zoomed in plot.
    
    Returns
    -------
    None
    """

    ## DATA
    # Get the compartments from the data
    compartments = get_compartments(data)

    ## FIGURE
    # Create figure
    fig, ax = plt.subplots(dpi=300, figsize=(9, 3.5))

    # Plot the full data on the main axis
    for i in compartments:
        ax.plot(d[i], label=i)

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
    for i in compartments:
        ax_zm.plot(d[i][zoom_start:zoom_end])

    ## LABELS
    # Show y-labels on ax_zm
    ax_zm.set_ylabel('Concentration (mg/L)', fontsize="medium")
    ax_zm.set_xlabel('Timestep', fontsize="medium")
    ax.set_xlabel('Timestep', fontsize="medium")
    # Show legend
    ax.legend(loc='upper left', fontsize="x-small", frameon=False)

    # Save the figure
    plt.savefig('bloodstream.png', dpi=300, bbox_inches='tight')

# Testing
combined_plot(d)
