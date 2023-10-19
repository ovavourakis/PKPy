import PKPy as pk

if __name__ == "__main__":

    model = pk.Model('system.json')
    timeseries = model.solve()
    print(timeseries)