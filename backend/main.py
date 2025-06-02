from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from schemas.train_scheme import TrainRequest
from schemas.predict_scheme import PredictRequest
from services.train_service import train, train_with_progress
from services.predict_service import predict
import asyncio
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Variable global para almacenar el progreso del entrenamiento
training_progress = {
    "epoch": 0,
    "rms": 0.0,
    "is_training": False,
    "completed": False,
    "message": "",
    "rms_history": []
}

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

@app.post("/api/train-progress")
async def post_training_with_progress(train_data: TrainRequest):
    global training_progress
    
    # Reiniciar el progreso
    training_progress = {
        "epoch": 0,
        "rms": 0.0,
        "is_training": True,
        "completed": False,
        "message": "Iniciando entrenamiento...",
        "rms_history": []
    }
    
    # Ejecutar entrenamiento en background
    asyncio.create_task(run_training_background(train_data))
    
    return {"status": "training_started", "message": "Entrenamiento iniciado"}

async def run_training_background(train_data: TrainRequest):
    global training_progress
    try:
        result = await train_with_progress(
            lower_limit=train_data.lower_limit,
            upper_limit=train_data.upper_limit,
            hidden_neurons=train_data.hidden_neurons,
            rms=train_data.rms,
            niu=train_data.niu,
            alfa=train_data.alfa,
            max_epochs=train_data.epochs,
            training_patterns=train_data.training_patterns,
        )
        
        training_progress.update({
            "completed": True,
            "is_training": False,
            "message": result["message"],
            "rms_history": result["rms_history"]
        })
    except Exception as e:
        training_progress.update({
            "completed": True,
            "is_training": False,
            "message": f"Error: {str(e)}",
            "error": True
        })

@app.get("/api/training-progress")
async def get_training_progress():
    async def generate():
        global training_progress
        last_epoch = -1
        
        while training_progress["is_training"] or not training_progress["completed"]:
            if training_progress["epoch"] != last_epoch:
                data = json.dumps(training_progress)
                yield f"data: {data}\n\n"
                last_epoch = training_progress["epoch"]
            
            if training_progress["completed"]:
                break
                
            await asyncio.sleep(0.1)
        
        # Enviar datos finales
        data = json.dumps(training_progress)
        yield f"data: {data}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

def update_training_progress(epoch: int, rms: float, rms_history: list):
    global training_progress
    training_progress.update({
        "epoch": epoch,
        "rms": rms,
        "rms_history": rms_history,
        "message": f"Época {epoch}, RMS: {rms:.6f}"
    })

@app.post("/api/predict")
def post_predict(predict_data: PredictRequest):
    return predict(
        input_neurons=predict_data.input_neurons,
        hidden_neurons=predict_data.hidden_neurons,
        output_neurons=predict_data.output_neurons,
        inputs=predict_data.inputs,
    )