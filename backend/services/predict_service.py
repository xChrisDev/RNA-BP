import time
import pandas as pd
import numpy as np
from utils.normalize_values import normalize_patterns
from utils.weights_manager import load_weights
from utils.propagation_values import hidden_propagation, output_propagation
from utils.messages import message_prediction_result
from PIL import Image


def load_default_pattern(path="config/default_pattern.png"):
    img = Image.open(path).convert("L").resize((28, 28))
    img_array = np.array(img)
    inverted_array = 255 - img_array 
    return inverted_array.flatten()

def predict(input_neurons, hidden_neurons, output_neurons, inputs):
    start_time = time.time()

    input_path = "config/input_values.csv"
    pd.DataFrame([inputs]).to_csv(input_path, index=False, header=False)

    wij, wjk, theta_j, theta_k = load_weights()
    normalized_patterns, num_patterns = normalize_patterns(input_path, is_training=False)

    training_patterns = pd.read_csv("config/training_patterns.csv", header=None, dtype=float).values

    sj = hidden_propagation(normalized_patterns, wij, theta_j)
    sk = output_propagation(sj, wjk, theta_k)

    # Procesar solo un patrón
    pred = [1 if val >= 0.5 else 0 for val in sk[0]]

    # Obtener índice del patrón
    pattern_idx = pred.index(1) if pred.count(1) == 1 else -1 
    
    if pattern_idx != -1:
        result = training_patterns[pattern_idx]
    else:
        result = load_default_pattern()

    result_formatted = result.reshape((28, 28)).tolist()

    prediction_time = time.time() - start_time
    message_prediction_result(pattern_idx=pattern_idx, binary_output=pred, prediction_time=prediction_time)

    return {
        "prediction": {"patternData": result_formatted},
        "values": pred,
    }
