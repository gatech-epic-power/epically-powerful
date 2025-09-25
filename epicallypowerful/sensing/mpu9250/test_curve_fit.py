# Test curve-fitting
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

def my_model_function(x, m, b):
    # Your mathematical expression involving x and parameters
    return m*x + b

# x_data = np.array([1, 2, 3, 4, 5])
# y_data = np.array([2.1, 3.9, 6.2, 8.1, 10.3])
x_data = np.array([
    [1.01, 1.2, 0.9, 0.85, 0.95],
    [-0.9, -0.89, -1.15, -1, -1.2],
    [0.01, 0.2, -0.15, 0.1, -0.05],
]).transpose()

y_data = np.array([
    [1, 1, 1, 1, 1],
    [-1, -1, -1, -1, -1],
    [0, 0, 0, 0, 0],
]).transpose()


# Initial guess for parameters (optional but recommended for complex models)
initial_guess = [1.0, 0.5]

# Perform the fit
params, covariance = curve_fit(my_model_function, x_data, y_data, p0=initial_guess)

m_fit, b_fit = params

y_fit = my_model_function(x_data, m_fit, b_fit)

print(y_fit)

plt.plot(x_data, y_data)
plt.plot(x_data, y_fit)
plt.show()