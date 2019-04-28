import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta


def time_to_float(time):
    time_now = datetime.now()
    td = time_now - time
    hour = np.round(td.total_seconds() / timedelta(hours=1).total_seconds(), decimals=2)
    return hour


def wage_time(time, k=0.01):
    # function returns a 'wage' value - between (1, 0)
    # y=np.tanh(k*x)/(np.pi/2)
    # y=x/(k+x);
    wage = np.exp(-k*time)
    return wage


def visualize_wage_func(k=0.01, func_type="exp"):
    # use k value to determine the aggressiveness of the function
    x = np.linspace(0, 1e6, 100000)
    if func_type == "tanh":
        y = np.tanh(k*x) / (np.pi/2)
    if func_type == "exp":
        y = np.exp(-k*x)
    if func_type == "1/x":
        y = x / (k+x)
    plt.plot(x[:30], y[:30])
    plt.xlabel('hours')
    plt.ylabel('wage')
    plt.show()

# wage_time(time_to_float(datetime(2019, 4, 28, 9, 13)))
# visualize_wage_func()
