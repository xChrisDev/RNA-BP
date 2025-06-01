from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from schemas.train_scheme import TrainRequest
from schemas.predict_scheme import PredictRequest
from services.train_service import train
from services.predict_service import predict

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/train")
def post_training(train_data: TrainRequest):
    return train(
        lower_limit=train_data.lower_limit,
        upper_limit=train_data.upper_limit,
        hidden_neurons=train_data.hidden_neurons,
        rms=train_data.rms,
        niu=train_data.niu,
        alfa=train_data.alfa,
        max_epochs=train_data.epochs,
        training_patterns=train_data.training_patterns,
    )


@app.post("/api/predict")
def post_predict(predict_data: PredictRequest):
    return predict(
        input_neurons=predict_data.input_neurons,
        hidden_neurons=predict_data.hidden_neurons,
        output_neurons=predict_data.output_neurons,
        inputs=predict_data.inputs,
    )
