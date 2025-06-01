import pandas as pd
import numpy as np

def adapt_weights(
    input_neurons,
    hidden_neurons,
    output_neurons,
    num_patterns,
    sj,
    sk,
    normalized_patterns,
    alfa,
    niu,
    wjk,
    theta_k,
    wij,
    theta_j,
):
    tk = pd.read_csv("config/target_patterns.csv", header=None).values
    delta_wij = np.zeros((input_neurons, hidden_neurons))
    delta_wjk = np.zeros((hidden_neurons, output_neurons))
    delta_theta_j = np.zeros(hidden_neurons)
    delta_theta_k = np.zeros(output_neurons)
    temp_delta_wij = np.zeros((input_neurons, hidden_neurons))
    temp_delta_wjk = np.zeros((hidden_neurons, output_neurons))
    temp_delta_theta_j = np.zeros(hidden_neurons)
    temp_delta_theta_k = np.zeros(output_neurons)
    error_k = np.zeros((num_patterns, output_neurons))
    error_j = np.zeros((num_patterns, hidden_neurons))

    # Errores en K
    for i in range(num_patterns):
        for k in range(output_neurons):
            error_k[i][k] = (tk[i][k] - sk[i][k]) * sk[i][k] * (1 - sk[i][k])

    # Errores en J
    for i in range(num_patterns):
        for j in range(hidden_neurons):
            sum_k = 0.0
            for k in range(output_neurons):
                sum_k += error_k[i][k] * wjk[j][k]
            error_j[i][j] = sj[i][j] * (1 - sj[i][j]) * sum_k

    # Ajuste de pesos capa de salida
    for i in range(num_patterns):
        for j in range(hidden_neurons):
            for k in range(output_neurons):
                delta_wjk[j][k] = (niu * error_k[i][k] * sj[i][j]) + (
                    alfa * temp_delta_wjk[j][k]
                )
                temp_delta_wjk[j][k] = delta_wjk[j][k]
                wjk[j][k] += delta_wjk[j][k]

        for k in range(output_neurons):
            delta_theta_k[k] = (niu * error_k[i][k]) + (alfa * temp_delta_theta_k[k])
            temp_delta_theta_k[k] = delta_theta_k[k]
            theta_k[k] += delta_theta_k[k]

    # Ajuste de pesos capa oculta
    for i in range(num_patterns):
        for n in range(input_neurons):
            for j in range(hidden_neurons):
                delta_wij[n][j] = (niu * error_j[i][j] * normalized_patterns[i][n]) + (
                    alfa * temp_delta_wij[n][j]
                )
                temp_delta_wij[n][j] = delta_wij[n][j]
                wij[n][j] += delta_wij[n][j]

        for j in range(hidden_neurons):
            delta_theta_j[j] = (niu * error_j[i][j]) + (alfa * temp_delta_theta_j[j])
            temp_delta_theta_j[j] = delta_theta_j[j]
            theta_j[j] += delta_theta_j[j]

    return wij, wjk, theta_j, theta_k

def adapt_weights_fast(
    input_neurons,
    hidden_neurons,
    output_neurons,
    num_patterns,
    sj,
    sk,
    normalized_patterns,
    alfa,
    niu,
    wjk,
    theta_k,
    wij,
    theta_j,
):
    tk = pd.read_csv("config/target_patterns.csv", header=None).values

    delta_wij = np.zeros((input_neurons, hidden_neurons))
    delta_wjk = np.zeros((hidden_neurons, output_neurons))
    delta_theta_j = np.zeros(hidden_neurons)
    delta_theta_k = np.zeros(output_neurons)
    temp_delta_wij = np.zeros((input_neurons, hidden_neurons))
    temp_delta_wjk = np.zeros((hidden_neurons, output_neurons))
    temp_delta_theta_j = np.zeros(hidden_neurons)
    temp_delta_theta_k = np.zeros(output_neurons)

    # Error en capa salida K (vectorizado)
    error_k = (tk - sk) * sk * (1 - sk)  

    # Error en capa oculta J (vectorizado)
    sum_k = np.dot(error_k, wjk.T)  
    error_j = sj * (1 - sj) * sum_k  

    # Ajuste de pesos capa de salida (vectorizado por patrones)
    for i in range(num_patterns):
        delta_wjk = (niu * np.outer(sj[i], error_k[i])) + (alfa * temp_delta_wjk)
        wjk += delta_wjk
        temp_delta_wjk = delta_wjk

        delta_theta_k = (niu * error_k[i]) + (alfa * temp_delta_theta_k)
        theta_k += delta_theta_k
        temp_delta_theta_k = delta_theta_k

    # Ajuste de pesos capa oculta (vectorizado por patrones)
    for i in range(num_patterns):
        delta_wij = (niu * np.outer(normalized_patterns[i], error_j[i])) + (alfa * temp_delta_wij)
        wij += delta_wij
        temp_delta_wij = delta_wij

        delta_theta_j = (niu * error_j[i]) + (alfa * temp_delta_theta_j)
        theta_j += delta_theta_j
        temp_delta_theta_j = delta_theta_j

    return wij, wjk, theta_j, theta_k