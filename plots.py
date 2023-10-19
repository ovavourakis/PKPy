# Functions to visualise the PK data

import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.colors as mcolors
import numpy as np
#import json
import pickle

# LOAD PICKLE DATA
# Filename
data_eg = 'example_timeseries.pkl'
# Load the data
with open(data_eg, 'rb') as handle:
    d = pickle.load(handle)


# Extract the compartments from data
def get_compartments(data):
    # Get the compartments
    compartments = list(data.keys())
    return compartments

# eg
compartments = get_compartments(d)
print(compartments)

# Generate an overall plot for the compartments
def combined_plot(data, title='PK Model'):


    # Create figure
    fig, ax = plt.subplots(dpi=300, figsize=(8.5, 3.5))
    axm = ax.plot(d[compartments[0]])

    # create new axes on the right and on the top of the current axes
    divider = make_axes_locatable(ax)
    ax_zm = divider.append_axes("left", 1.5, pad=0.2, sharey=ax)

    #yaxm = axm.axes.get_yaxis()
    #yax = yax.set_visible(False)
    #yaxm.set_ticklabels([])
    #axm.axes.set_ylabel('')

    # Plot the timeseries data
    #plt.figure(figsize=(10, 7))
    #plt.title(title)
    #plt.plot(d[keys[0]])
    #plt.plot(d[keys[1]])
    #plt.plot(d[keys[2]])
    #plt.title('Bloodstream')
    #plt.xlabel('Time (hours)')
    #plt.ylabel('Concentration (mg/L)')
    plt.savefig('bloodstream.png')

combined_plot(d)
