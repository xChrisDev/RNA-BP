<template>
  <div class="min-h-screen">
    <Toast position="top-right" />
    <div class="container mx-auto py-6 px-4">
      <!-- Header -->
      <Card class="mb-6">
        <template #content>
          <div class="flex flex-col sm:flex-row justify-between items-center gap-4">
            <h1 class="text-2xl font-bold text-center sm:text-left">
              RNA BP - Reconocimiento de Patrones
            </h1>
            <ButtonDarkMode />
          </div>
          <Divider />
          <TrainingControl
            :trainingEnabled="patterns.length >= 5"
            :isTraining="isTraining"
            :isTrained="isTrained"
            @start-training="startTraining"
            @reset="resetModel"
            @predict-pattern="turnPredict"
          />
        </template>
      </Card>

      <!-- Contenido principal -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Panel Parámetros -->
        <Card class="h-full">
          <template #title>Parámetros RNA</template>
          <template #content>
            <ParameterSettings :modelParams="modelParams" @update:modelParams="modelParams = $event" />
          </template>
        </Card>

        <!-- Panel de trabajo: Canvas + Resultados -->
        <div class="grid grid-cols-1 col-span-2 md:grid-cols-2 gap-6">
          <!-- Canvas -->
          <Card>
            <template #title>
              <div class="flex justify-between items-center">
                <span>{{ isTrained ? 'Predicción' : `Patrón ${patterns.length}/5` }}</span>
              </div>
            </template>
            <template #content>
              <CanvasDrawing
                ref="canvasRef"
                :disabled="isTraining"
                :mode="isTrained ? 'prediction' : 'collection'"
                class="w-full"
              />
              <div class="flex flex-wrap gap-2 pt-4 justify-center items-center">
                <Button icon="pi pi-trash" severity="danger" @click="clearCanvas" />
                <Button
                  label="Guardar Patrón"
                  v-if="!isTrained"
                  :disabled="isDrawing || isTraining || patterns.length >= 5"
                  @click="savePattern"
                  icon="pi pi-save"
                />
                <Button
                  label="Predecir"
                  v-else
                  :disabled="isDrawing || isTraining"
                  @click="makePrediction"
                  icon="pi pi-sync"
                />
              </div>
            </template>
          </Card>

          <!-- Resultado / Entrenamiento -->
          <Card>
            <template #title>
              {{ isTrained ? 'Resultado' : 'Entrenamiento' }}
            </template>
            <template #content>
              <div v-if="!isTrained">
                <!-- Estado cuando no está entrenando -->
                <div v-if="!isTraining && trainingProgress.epoch === 0" class="text-center py-6 text-gray-500">
                  <i class="pi pi-lightbulb text-4xl mb-2"></i>
                  <p>No ha iniciado el entrenamiento</p>
                </div>

                <!-- Progreso del entrenamiento -->
                <div v-else class="flex flex-col h-[342px] p-4">
                  <div class="mb-4">
                    <!-- Indicador de progreso -->
                    <div class="mb-4">
                      <div class="flex justify-between text-sm mb-1">
                        <span>Época {{ trainingProgress.epoch }}</span>
                        <span>{{ modelParams.epochs }}</span>
                      </div>
                      <div class="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          class="bg-blue-600 h-2 rounded-full transition-all duration-300" 
                          :style="{ width: `${(trainingProgress.epoch / modelParams.epochs) * 100}%` }"
                        ></div>
                      </div>
                    </div>

                    <!-- Estado actual -->
                    <div class=" rounded-lg p-3 mb-4">
                      <div class="text-sm">
                        <div class="flex justify-between mb-1">
                          <span class="font-medium">Estado:</span>
                          <span class="text-blue-600">
                            {{ isTraining ? 'Entrenando...' : (trainingProgress.completed ? 'Completado' : 'Preparando...') }}
                          </span>
                        </div>
                        <div class="flex justify-between mb-1">
                          <span class="font-medium">Época actual:</span>
                          <span>{{ trainingProgress.epoch }}</span>
                        </div>
                        <div class="flex justify-between">
                          <span class="font-medium">RMS actual:</span>
                          <span>{{ trainingProgress.rms.toFixed(6) }}</span>
                        </div>
                      </div>
                    </div>

                    <!-- Mensaje del entrenamiento -->
                    <div class="text-xs text-gray-500 border rounded p-2 font-mono">
                      {{ trainingProgress.message }}
                    </div>

                    <!-- Spinner cuando está entrenando -->
                    <div v-if="isTraining" class="flex justify-center mt-4">
                      <div class="loader"></div>
                    </div>

                    <!-- Mensaje de finalización -->
                    <div v-if="trainingProgress.completed && !isTraining" class="mt-4">
                      <div class="text-center">
                        <div class="text-green-600 font-medium">
                          <i class="pi pi-check-circle mr-1"></i>
                          Entrenamiento completado
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div v-else>
                <div v-if="!prediction" class="text-center py-6 text-gray-500">
                  <i class="pi pi-search text-4xl mb-2"></i>
                  <p>Dibuja un patrón para ver la predicción</p>
                </div>

                <div v-else class="flex flex-col items-center h-[342px]">
                  <div class="mb-4">
                    <div v-if="isLoading" class="flex justify-center items-center h-[300px]">
                      <div class="loader"></div>
                    </div>
                    <div v-else>
                      <canvas
                        ref="resultCanvas"
                        width="280"
                        height="280"
                        class="border-2 border-gray-300 rounded-lg bg-white"
                      ></canvas>
                    </div>
                  </div>
                </div>
              </div>
            </template>
          </Card>

          <!-- Galería -->
          <Card class="md:col-span-2">
            <template #title>Patrones de entrenamiento</template>
            <template #content>
              <PatternGallery
                class="w-full"
                :patterns="patterns"
                @pattern="(n) => drawPattern(patterns[n]?.data)"
                @remove-pattern="removePattern"
                :disabled="isTrained"
              />
            </template>
          </Card>
        </div>
      </div>

      <!-- Gráfica -->
      <div v-if="isTrained" class="mt-6">
        <Card>
          <template #title>Gráfica</template>
          <template #content>
            <Chart type="line" :data="chartData" :options="chartOptions" class="h-[30rem]" />
          </template>
        </Card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { nextTick, ref, watch, onUnmounted } from 'vue';
import { useToast } from 'primevue/usetoast';

import CanvasDrawing from './components/CanvasDrawing.vue';
import ParameterSettings from './components/ParameterSettings.vue';
import TrainingControl from './components/TrainingControl.vue';
import PatternGallery from './components/PatternGallery.vue';

import { predictPattern, trainModelWithProgress, connectToTrainingProgress } from './services/api';
import { Card, Button, Toast, Divider } from 'primevue';
import ButtonDarkMode from './components/ButtonDarkMode.vue';
import Chart from 'primevue/chart';

const toast = useToast();
const canvasRef = ref(null);
const patterns = ref([]);
const isDrawing = ref(false);
const isTraining = ref(false);
const isTrained = ref(false);
const prediction = ref([]);
const targets = ref([])
const rms_history = ref([])
const resultCanvas = ref(null)
const isLoading = ref(false)
const predictionValues = ref({ hidden_neurons: 0, output_neurons: 0, input_neurons: 0 })

// Estado del progreso del entrenamiento
const trainingProgress = ref({
  epoch: 0,
  rms: 0.0,
  is_training: false,
  completed: false,
  message: "",
  rms_history: []
});

let eventSource = null;

const modelParams = ref({
  alfa: 0.35,
  niu: 0.25,
  rms: 0.01,
  epochs: 10000,
  hiddenNeurons: 128,
  upper_limit: 0.3,
  lower_limit: -0.3
});

const drawPattern = (pattern) => {
  if (!pattern || !Array.isArray(pattern)) return;

  const canvas = canvasRef.value.getCanvas();
  if (!canvas) return;

  const ctx = canvasRef.value.getContext();

  ctx.fillStyle = 'white';
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  const cellSize = Math.floor(canvas.width / 28);

  for (let i = 0; i < 28; i++) {
    for (let j = 0; j < 28; j++) {
      const value = pattern[i][j];
      if (value > 0) {
        const grayValue = 255 - value;
        ctx.fillStyle = `rgb(${grayValue}, ${grayValue}, ${grayValue})`;
        ctx.fillRect(j * cellSize, i * cellSize, cellSize, cellSize);
      }
    }
  }
};

watch(prediction, async (newPrediction) => {
  if (newPrediction && newPrediction.length === 28) {
    await nextTick();
    drawPrediction(newPrediction);
  }
});

watch(() => trainingProgress.value.rms_history, (newHistory) => {
  if (newHistory && newHistory.length > 0) {
    rms_history.value = newHistory;
    chartData.value = setChartData();
    chartOptions.value = setChartOptions();
  }
});

const chartData = ref({});
const chartOptions = ref({});

const setChartData = () => {
  const documentStyle = getComputedStyle(document.documentElement);

  return {
    labels: rms_history.value.map((_, i) => `Epoca ${i + 1}`),
    datasets: [
      {
        label: 'RMS Error',
        data: rms_history.value,
        fill: false,
        borderColor: documentStyle.getPropertyValue('--p-cyan-500') || '#06b6d4',
        tension: 0.4
      }
    ]
  };
};

const setChartOptions = () => {
  const documentStyle = getComputedStyle(document.documentElement);
  const textColor = documentStyle.getPropertyValue('--p-text-color');
  const textColorSecondary = documentStyle.getPropertyValue('--p-text-muted-color');
  const surfaceBorder = documentStyle.getPropertyValue('--p-content-border-color');

  return {
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: {
          color: textColor
        }
      }
    },
    scales: {
      x: {
        ticks: {
          color: textColorSecondary
        },
        grid: {
          color: surfaceBorder
        }
      },
      y: {
        ticks: {
          color: textColorSecondary
        },
        grid: {
          color: surfaceBorder
        }
      }
    }
  };
};

const clearCanvas = () => {
  canvasRef.value?.clearCanvas();
};

const savePattern = async () => {
  if (patterns.value.length >= 5) {
    toast.add({ severity: 'warn', summary: 'Límite alcanzado', detail: 'Ya has dibujado 5 patrones', life: 3000 });
    return;
  }

  const patternData = await canvasRef.value?.savePattern();
  if (patternData) {
    patterns.value.push({
      id: Date.now(),
      data: patternData,
      label: patterns.value.length,
    });
    clearCanvas();
    toast.add({ severity: 'success', summary: 'Éxito', detail: `Patrón ${patterns.value.length} guardado`, life: 3000 });
  }
};

const removePattern = (id) => {
  const index = patterns.value.findIndex(p => p.id === id);
  if (index !== -1) {
    patterns.value.splice(index, 1);
    patterns.value.forEach((pattern, i) => {
      pattern.label = i;
    });

    toast.add({
      severity: 'info',
      summary: 'Patrón eliminado',
      detail: `Patrón ${index + 1} eliminado`,
      life: 3000
    });

  } else {
    console.warn(`No se encontró ningún patrón con id ${id}`);
  }
};

const startTraining = async () => {
  if (patterns.value.length < 5) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Necesitas al menos 5 patrones para entrenar',
      life: 3000
    });
    return;
  }

  try {
    isTraining.value = true;
    
    // Reiniciar progreso
    trainingProgress.value = {
      epoch: 0,
      rms: 0.0,
      is_training: true,
      completed: false,
      message: "Iniciando entrenamiento...",
      rms_history: []
    };

    toast.add({ severity: 'info', summary: 'Entrenando', detail: 'Entrenamiento iniciado...', life: 3000 });

    const trainingData = patterns.value.map(p => ({
      pattern: p.data,
      label: p.label,
    }));

    const newDataTraining = []
    trainingData.forEach((data) => newDataTraining.push(data.pattern.flat()))

    const data = {
      alfa: parseFloat(modelParams.value.alfa),
      niu: parseFloat(modelParams.value.niu),
      rms: parseFloat(modelParams.value.rms),
      epochs: parseFloat(modelParams.value.epochs),
      hidden_neurons: parseFloat(modelParams.value.hiddenNeurons),
      input_neurons: 784,
      upper_limit: parseFloat(modelParams.value.upper_limit),
      lower_limit: parseFloat(modelParams.value.lower_limit),
      training_patterns: newDataTraining
    }

    predictionValues.value = { 
      input_neurons: 784, 
      output_neurons: 3, 
      hidden_neurons: parseFloat(modelParams.value.hiddenNeurons), 
    }

    // Iniciar entrenamiento con progreso
    await trainModelWithProgress(data);

    // Conectar a SSE para recibir actualizaciones en tiempo real
    eventSource = connectToTrainingProgress(
      // onProgress
      (progressData) => {
        trainingProgress.value = progressData;
      },
      // onError
      (error) => {
        console.error('Error en SSE:', error);
        isTraining.value = false;
        toast.add({
          severity: 'error',
          summary: 'Error de conexión',
          detail: 'Error al recibir actualizaciones del entrenamiento',
          life: 5000
        });
      },
      // onComplete
      (finalData) => {
        trainingProgress.value = finalData;
        rms_history.value = finalData.rms_history || [];
        isTraining.value = false;
        isTrained.value = true;
        
        toast.add({
          severity: 'success',
          summary: 'Entrenamiento completo',
          detail: finalData.message,
          life: 5000
        });
      }
    );

  } catch (error) {
    isTraining.value = false;
    trainingProgress.value.completed = true;
    trainingProgress.value.is_training = false;
    toast.add({
      severity: 'error',
      summary: 'Error de entrenamiento',
      detail: error.message || 'Ocurrió un error durante el entrenamiento',
      life: 5000
    });
  }
};

const turnPredict = () => {
  isTrained.value = !isTrained.value;
}

const resetModel = () => {
  // Cerrar conexión SSE si existe
  if (eventSource) {
    eventSource.close();
    eventSource = null;
  }

  patterns.value = [];
  targets.value = [];
  isTrained.value = false;
  isTraining.value = false;
  predictionValues.value = { hidden_neurons: 0, output_neurons: 0, input_neurons: 0 }
  prediction.value = null;
  
  // Reiniciar progreso del entrenamiento
  trainingProgress.value = {
    epoch: 0,
    rms: 0.0,
    is_training: false,
    completed: false,
    message: "",
    rms_history: []
  };
  
  clearCanvas();
  toast.add({ severity: 'info', summary: 'Reinicio', detail: 'Todos los datos han sido borrados', life: 3000 });
};

const drawPrediction = (pattern) => {
  const canvas = resultCanvas.value;
  if (!canvas) return

  const ctx = canvas.getContext('2d')

  ctx.fillStyle = 'white'
  ctx.fillRect(0, 0, canvas.width, canvas.height)

  const cellSize = Math.floor(canvas.width / 28)

  for (let i = 0; i < 28; i++) {
    for (let j = 0; j < 28; j++) {
      const value = pattern[i][j]
      if (value > 0) {
        const grayValue = 255 - value
        ctx.fillStyle = `rgb(${grayValue}, ${grayValue}, ${grayValue})`
        ctx.fillRect(j * cellSize, i * cellSize, cellSize, cellSize)
      }
    }
  }
}

const makePrediction = async () => {
  if (!isTrained.value) {
    toast.add({ severity: 'warn', summary: 'No entrenado', detail: 'Entrena el modelo primero', life: 3000 });
    return;
  }

  try {
    const patternData = await canvasRef.value?.savePattern();
    isLoading.value = true;

    if (patternData) {
      const data = {
        hidden_neurons: predictionValues.value.hidden_neurons,
        input_neurons: predictionValues.value.input_neurons,
        output_neurons: predictionValues.value.output_neurons,
        inputs: patternData.flat()
      }

      const result = await predictPattern(data);
      prediction.value = result.prediction.patternData
      toast.add({
        severity: 'success',
        summary: 'Predicción completada',
        life: 3000
      });
      isLoading.value = false;
    }
  } catch (error) {
    isLoading.value = false;
    toast.add({
      severity: 'error',
      summary: 'Error de predicción',
      detail: error.message || 'Ocurrió un error durante la predicción',
      life: 5000
    });
  }
};

// Limpiar recursos al desmontar el componente
onUnmounted(() => {
  if (eventSource) {
    eventSource.close();
  }
});
</script>