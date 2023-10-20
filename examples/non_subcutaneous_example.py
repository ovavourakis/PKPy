import PKPy as pk

if __name__ == "__main__":

    model = pk.Model('non_subcutaneous_example.json')
    timeseries = model.solve()      # saves dictionary of timeseries data per compartment
    model.plot()                    # plots timeseries data for each compartment