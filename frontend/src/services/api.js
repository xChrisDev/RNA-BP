import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000/api",
  headers: {
    "Content-Type": "application/json",
  },
});

export const trainModel = async (data) => {
  try {
    const response = await api.post("/train", data);
    return response.data;
  } catch (error) {
    console.error("Error al entrenar el modelo:", error);
    throw new Error(
      error.response?.data?.detail || "Error al entrenar el modelo"
    );
  }
};

export const trainModelWithProgress = async (data) => {
  try {
    const response = await api.post("/train-progress", data);
    return response.data;
  } catch (error) {
    console.error("Error al entrenar el modelo:", error);
    throw new Error(
      error.response?.data?.detail || "Error al entrenar el modelo"
    );
  }
};

export const connectToTrainingProgress = (onProgress, onError, onComplete) => {
  const eventSource = new EventSource("http://localhost:8000/api/training-progress");
  
  eventSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onProgress(data);
      
      if (data.completed) {
        eventSource.close();
        onComplete(data);
      }
    } catch (error) {
      console.error("Error parsing SSE data:", error);
      onError(error);
    }
  };
  
  eventSource.onerror = (error) => {
    console.error("SSE Error:", error);
    eventSource.close();
    onError(error);
  };
  
  return eventSource;
};

export const predictPattern = async (data) => {
  try {
    const response = await api.post("/predict", data);
    return response.data;
  } catch (error) {
    console.error("Error al realizar la predicción:", error);
    throw new Error(
      error.response?.data?.detail || "Error al realizar la predicción"
    );
  }
};

export const getHistoricRMS = async () => {
  try {
    const response = await api.get("/rms");
    return response.data;
  } catch (error) {
    console.error("Error al obtener el historico de RMS: ", error);
    throw new Error(
      error.response?.data?.detail || "Error al obtener RMS´s"
    );
  }
};