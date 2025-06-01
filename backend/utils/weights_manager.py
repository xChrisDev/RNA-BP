import pandas as pd
import numpy as np

def save_weights(wij, wjk, theta_j, theta_k):
    pd.DataFrame(wij).to_csv("config/weights_ij.csv", index=False, header=False, mode='w')
    pd.DataFrame(wjk).to_csv("config/weights_jk.csv", index=False, header=False, mode='w')
    pd.DataFrame(theta_j).to_csv("config/theta_j.csv", index=False, header=False, mode='w')
    pd.DataFrame(theta_k).to_csv("config/theta_k.csv", index=False, header=False, mode='w')

def load_weights():
    try:
        wij = pd.read_csv("config/weights_ij.csv", header=None).values
        wjk = pd.read_csv("config/weights_jk.csv", header=None).values
        theta_j = pd.read_csv("config/theta_j.csv", header=None).values.flatten()
        theta_k = pd.read_csv("config/theta_k.csv", header=None).values.flatten()
        return wij, wjk, theta_j, theta_k
    except FileNotFoundError:
        raise

def load_weights_random(input_neurons: int, hidden_neurons: int, output_neurons: int, lower_limit: float, upper_limit: float):
    wij = np.random.uniform(low=lower_limit, high=upper_limit, size=(input_neurons, hidden_neurons))
    theta_j = np.random.uniform(low=lower_limit, high=upper_limit, size=hidden_neurons)
    wjk = np.random.uniform(low=lower_limit, high=upper_limit, size=(hidden_neurons, output_neurons))
    theta_k = np.random.uniform(low=lower_limit, high=upper_limit, size=output_neurons)

    return wij, theta_j, wjk, theta_k