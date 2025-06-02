from utils.normalize_values import normalize_patterns
from utils.propagation_values import hidden_propagation, output_propagation
from utils.weights_manager import save_weights, load_weights_random
from utils.back_propagation import adapt_weights, adapt_weights_fast
from utils.messages import (
    message_color,
    message_color_epochs,
    message_trained_success,
    ERROR_COLOR,
    INFO_COLOR,
    EPOCH_COLOR,
)
import pandas as pd
import numpy as np
import time
import asyncio

def train(
    lower_limit: float,
    upper_limit: float,
    hidden_neurons: int,
    rms: float,
    niu: float,
    alfa: float,
    max_epochs: int,
    training_patterns,
):
    # Inicialización de variables
    epochs = 1
    rms_history = []
    output_neurons = 5
    input_neurons = 784
    tk = pd.read_csv("config/target_patterns.csv", header=None).values
    pd.DataFrame(training_patterns).to_csv(
        "config/training_patterns.csv", index=False, header=False, mode="w"
    )

    # Normalización de los patrones de entrenamiento
    normalized_patterns, num_patterns = normalize_patterns("config/training_patterns.csv", is_training=False)
    
    # Obtención de los pesos y valores de theta
    wij, theta_j, wjk, theta_k = load_weights_random(
        input_neurons=input_neurons,
        hidden_neurons=hidden_neurons,
        output_neurons=output_neurons,
        lower_limit=lower_limit,
        upper_limit=upper_limit,
    )

    message_color("Iniciando el entrenamiento...", color=INFO_COLOR)
    print()
    training_start_time = time.time()

    while epochs < max_epochs:
        # Calcular valores de propagación
        sj = hidden_propagation(normalized_patterns, wij, theta_j)
        sk = output_propagation(sj, wjk, theta_k)

        # Calcular el RMS
        rms_obtained = 0.0
        for i in range(num_patterns):
            for k in range(output_neurons):
                rms_obtained += (tk[i][k] - sk[i][k]) ** 2
        rms_obtained /= (num_patterns * output_neurons)
        rms_obtained = np.sqrt(rms_obtained)
        rms_history.append(rms_obtained)

        message_color_epochs(
            f"Epoch: {epochs}, RMS: {rms_obtained}",
            color=EPOCH_COLOR,
        )

        if rms_obtained <= rms:
            message_color(
                f"RMS objetivo alcanzado: {rms_obtained} en {epochs} épocas.",
                color=INFO_COLOR,
            )
            save_weights(wij, wjk, theta_j, theta_k)
            break

        # Backpropagation (adaptación de pesos)
        wij, wjk, theta_j, theta_k = adapt_weights_fast(
            input_neurons=input_neurons,
            hidden_neurons=hidden_neurons,
            output_neurons=output_neurons,
            num_patterns=num_patterns,
            wjk=wjk,
            theta_k=theta_k,
            wij=wij,
            theta_j=theta_j,
            sj=sj,
            sk=sk,
            normalized_patterns=normalized_patterns,
            alfa=alfa,
            niu=niu,
        )

        epochs += 1

    if rms_obtained > rms and epochs >= max_epochs:
        message_color(
            f"RMS objetivo no alcanzado: {rms_obtained} después de {max_epochs} épocas.",
            color=ERROR_COLOR,
        )
        save_weights(wij, wjk, theta_j, theta_k)

    training_total_time = time.time() - training_start_time
    final_rms = rms_history[-1] if rms_history else rms_obtained

    message_trained_success(epochs, final_rms, training_total_time)

    return {"message": f"Red entrenada con {epochs} epocas", "rms_history": rms_history}

async def train_with_progress(
    lower_limit: float,
    upper_limit: float,
    hidden_neurons: int,
    rms: float,
    niu: float,
    alfa: float,
    max_epochs: int,
    training_patterns,
):
    from main import update_training_progress
    
    # Inicialización de variables
    epochs = 1
    rms_history = []
    output_neurons = 5
    input_neurons = 784
    tk = pd.read_csv("config/target_patterns.csv", header=None).values
    pd.DataFrame(training_patterns).to_csv(
        "config/training_patterns.csv", index=False, header=False, mode="w"
    )

    # Normalización de los patrones de entrenamiento
    normalized_patterns, num_patterns = normalize_patterns("config/training_patterns.csv", is_training=False)
    
    # Obtención de los pesos y valores de theta
    wij, theta_j, wjk, theta_k = load_weights_random(
        input_neurons=input_neurons,
        hidden_neurons=hidden_neurons,
        output_neurons=output_neurons,
        lower_limit=lower_limit,
        upper_limit=upper_limit,
    )

    message_color("Iniciando el entrenamiento...", color=INFO_COLOR)
    print()
    training_start_time = time.time()

    while epochs < max_epochs:
        # Calcular valores de propagación
        sj = hidden_propagation(normalized_patterns, wij, theta_j)
        sk = output_propagation(sj, wjk, theta_k)

        # Calcular el RMS
        rms_obtained = 0.0
        for i in range(num_patterns):
            for k in range(output_neurons):
                rms_obtained += (tk[i][k] - sk[i][k]) ** 2
        rms_obtained /= (num_patterns * output_neurons)
        rms_obtained = np.sqrt(rms_obtained)
        rms_history.append(rms_obtained)

        # Actualizar progreso
        update_training_progress(epochs, rms_obtained, rms_history)

        message_color_epochs(
            f"Epoch: {epochs}, RMS: {rms_obtained}",
            color=EPOCH_COLOR,
        )

        if rms_obtained <= rms:
            message_color(
                f"RMS objetivo alcanzado: {rms_obtained} en {epochs} épocas.",
                color=INFO_COLOR,
            )
            save_weights(wij, wjk, theta_j, theta_k)
            break

        # Backpropagation (adaptación de pesos)
        wij, wjk, theta_j, theta_k = adapt_weights_fast(
            input_neurons=input_neurons,
            hidden_neurons=hidden_neurons,
            output_neurons=output_neurons,
            num_patterns=num_patterns,
            wjk=wjk,
            theta_k=theta_k,
            wij=wij,
            theta_j=theta_j,
            sj=sj,
            sk=sk,
            normalized_patterns=normalized_patterns,
            alfa=alfa,
            niu=niu,
        )

        epochs += 1
        
        # Pequeña pausa para permitir que otros procesos se ejecuten
        await asyncio.sleep(0.01)

    if rms_obtained > rms and epochs >= max_epochs:
        message_color(
            f"RMS objetivo no alcanzado: {rms_obtained} después de {max_epochs} épocas.",
            color=ERROR_COLOR,
        )
        save_weights(wij, wjk, theta_j, theta_k)

    training_total_time = time.time() - training_start_time
    final_rms = rms_history[-1] if rms_history else rms_obtained

    message_trained_success(epochs, final_rms, training_total_time)

    return {"message": f"Red entrenada con {epochs} epocas", "rms_history": rms_history}