from pydantic import BaseModel
from typing import List

class PredictRequest(BaseModel):
    hidden_neurons: int
    input_neurons: int
    output_neurons: int
    inputs: List[float]
