from model import *

if __name__ == "__main__":

    model = Model('system.json')
    sol = model.solve()
    print(sol)