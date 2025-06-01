import numpy as np

def sigmoid(x):
    x = np.clip(x, -500, 500)
    return 1 / (1 + np.exp(-x))

def hidden_propagation(normalized_patterns, wij, theta_j):
    rj = np.dot(normalized_patterns, wij) + theta_j
    sj = sigmoid(rj)
    return sj

def output_propagation(sj, wjk, theta_k):
    rk = np.dot(sj, wjk) + theta_k
    sk = sigmoid(rk)
    return sk