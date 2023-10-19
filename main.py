from model import *

if __name__ == "__main__":

    model = Model('system.json')
    timeseries = model.solve()
    print(timeseries)