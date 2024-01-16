import matplotlib
import matplotlib.pyplot as plt
import numpy as np


def test():
    matplotlib.use('TkAgg')
    x = np.arange(0, 5, 0.1)
    y = np.sin(x)
    plt.plot(x, y)
    plt.show()


if __name__ == "__main__":
    test()



