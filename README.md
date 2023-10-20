PKPy is a small Python package to solve simple, compartment-based pharmacokinetic models. It was developed as a three-day exercise in collaborative software engineering as part of the SABS Doctoral Training Programme at Oxford University.

PKPy currently supports bolus (one-time) or continuous drug administration and an arbitrary number of peripheral compartments. Drugs can be administered directly into a central compartment, or alternatively flow first into a special subcutaneous compartment and thence into the central one.

See the full documentation in the `docs/build/html/` directory (open `index.html` in a browser of your choice).

### Installation
After cloning PKPy, you can use `pip` to install it:

```
git clone git@github.com:ovavourakis/PKPy.git
cd /path/to/PKPy/
pip install .
```

### Usage

#### Specify your Model
Specify all parameters of the model to be solved in a JSON configuration file, with the following structure:

```json
{
    "basic_parameters" : {
        "time_span": 10000,
        "subcutaneous" : 1,
        "dose" : [10, "continuous"]
    },
    
    "compartment_1" : {
        "name" : "Bloodstream",
        "type" : "central",
        "volume" : 5000,
        "initial_amount" : 0.0,
        "rate_out": 10
    },

    "compartment_3" : {
        "name" : "Liver",
        "type" : "peripheral",
        "volume" : 2000,
        "initial_amount" : 0.0,
        "rate_in" : 1.0,
        "rate_out": 0.5
    },

    "compartment_4" : {
        "name" : "Subcutaneous",
        "type" : "subcutaneous",
        "volume" : 3000,
        "initial_amount" : 0.0,
        "rate_in" : 1.0,
        "rate_out": 0.1
    }
...
}
```

In `"basic_parameters"`, you specify the desired time-span for which to propagate the system with `"time_span"`. The `"dose"` parameter specifies the administration protocol as a list; you may pass a numeric dosage amount as the first list item, followed by one of `"continuous"` (for constant administration) or `"bolus"` (for one-time administration at time 0). 
Alternatively, specify a custom dosage protocol as an arbitrary function of time 'x' as a string. Refer to any `numpy` functions as `np.`. For example:

```json
"basic_parameters" : {
        "subcutaneous" : 1,
        "dose" : "np.sin(x) + 100"
    }
```

Compartment names may be freely chosen, but their type must be one of `"central"`, `"subcutaneous"` and `"peripheral"`. 
If a `"subcutaneous"`-type compartment is present, the boolean flag `"subcutaneous"` in the `"basic_parameters"` dictionary must be set to 1; otherwise, it must be set to 0.

See the `examples/` folder for inspiration.

#### Usage from Python

After specifying the model parameters in a `json` configuration as described above, use the package from Python, like so:

```python
import PKPy as pk

model = pk.Model('/path/to/model_paramters.json') # initialise model from json
solution_timeseries = model.solve() # solve model
model.plot() # plot the results
```

This will generate a plot of individual compartment concentrations over time. Individual time-series can then be accessed from within `Python` as `solution_timeseries['compartment_name']` for further analysis.

License
PKPy is released under the MIT License. See LICENSE for details.
