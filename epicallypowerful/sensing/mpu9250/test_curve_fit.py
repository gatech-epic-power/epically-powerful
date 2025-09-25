"""Test curve fitting with scipy.optimize. Use case is to provide """

import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

def my_model_function(x, m, b):
    # Your mathematical expression involving x and parameters
    return m*x + b

measured_data = np.array([
    [1.01, 1.2, 0.9, 0.85, 0.95],
    [-0.9, -0.89, -1.15, -1, -1.2],
    [0.01, 0.2, -0.15, 0.1, -0.05],
]).transpose().flatten()

ref_data = np.array([
    [1, 1, 1, 1, 1],
    [-1, -1, -1, -1, -1],
    [0, 0, 0, 0, 0],
]).transpose().flatten()

# Initial guess for params (optional but rec. for complex models)
initial_guess = [1.0, 0.1]

# Perform the fit
params, covariance = curve_fit(
    f=my_model_function,
    xdata=measured_data,
    ydata=ref_data,
    p0=initial_guess,
)

m_fit, b_fit = params

fit_data = my_model_function(measured_data, m_fit, b_fit)

print(f"y = m*x + b: m = {m_fit}, b = {b_fit}")
print(f"fit_data: {fit_data}")

plt.scatter(measured_data, ref_data, color='k')
plt.axhline(y=-1, xmin=-1, xmax=1, color='r', linestyle=':', linewidth=1)
plt.axhline(y=0, xmin=-1, xmax=1, color='r', linestyle=':', linewidth=1)
plt.axhline(y=1, xmin=-1, xmax=1, color='r', linestyle=':', linewidth=1)
plt.plot(measured_data, fit_data)
plt.xlabel('measured')
plt.ylabel('reference')
plt.show()