<template>
  <div class="min-h-screen">
    <Toast position="bottom-right" />
    <div class="container mx-auto py-6 px-4">

      <Card class="mb-6">
        <template #content>
          <div class=" flex justify-between items-center gap-2">
            <h1 class="text-2xl font-bold">
              RNA BackPropagation - Reconocimiento de Patrones
            </h1>
            <ButtonDarkMode />
          </div>
          <Divider />
          <TrainingControl :trainingEnabled="patterns.length >= 5" :isTraining="isTraining" :isTrained="isTrained"
            @start-training="startTraining" @reset="resetModel" @predict-pattern="turnPredict" />
        </template>
      </Card>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Panel Izquierdo: Parámetros y Entrenamiento -->
        <div class="col-span-1">
          <Card class="h-[420px]">
            <template #title>Parámetros RNA</template>
            <template #content>
              <ParameterSettings :modelParams="modelParams" @update:modelParams="modelParams = $event" />
            </template>
          </Card>
        </div>

        <!-- Panel Central: Canvas de Dibujo -->
        <div class="col-span-1">
          <Card>
            <template #title>
              <div class="flex justify-between items-center">
                <span>{{ isTrained ? 'Predicción' : `Patrón ${patterns.length}/5` }}</span>
              </div>
            </template>
            <template #content>
              <div class="flex justify-center mb-2 gap-2">
                <Button size="small" v-for="btn in buttons" :key="btn.value" :label="btn.label"
                  :disabled="!patterns[btn.value]" @click="drawPattern(patterns[btn.value]?.data)" />

              </div>

              <CanvasDrawing ref="canvasRef" :disabled="isTraining" :mode="isTrained ? 'prediction' : 'collection'" />

              <div class="flex gap-2 mt-4 justify-center items-center">
                <Button icon="pi pi-trash" severity="danger" @click="clearCanvas" />
                <Button label="Guardar Patrón" v-if="!isTrained"
                  :disabled="isDrawing || isTraining || patterns.length >= 5" @click="savePattern" icon="pi pi-save" />
                <Button label="Predecir" v-else :disabled="isDrawing || isTraining" @click="makePrediction"
                  icon="pi pi-sync" />
              </div>
            </template>
          </Card>
        </div>

        <!-- Panel Derecho: Galería y Resultados -->
        <div class="col-span-1" v-if="!isTrained">
          <Card>
            <template #title>Patrones Guardados</template>
            <template #content>
              <PatternGallery :patterns="patterns" @remove-pattern="removePattern" />
            </template>
          </Card>
        </div>
        <div v-else>
          <Card>
            <template #title>Resultado</template>
            <template #content>
              <div>
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
                      <canvas ref="resultCanvas" width="280" height="280"
                        class="border-2 border-gray-300 rounded-lg cursor-crosshair bg-white"></canvas>
                    </div>
                  </div>
                </div>
              </div>
            </template>
          </Card>
        </div>
      </div>

      <div v-if="isTrained" class="grid grid-cols-3 gap-6 mt-6">
        <Card class="col-span-3">
          <template #title>Grafica</template>
          <template #content>
            <Chart type="line" :data="chartData" :options="chartOptions" class="h-[30rem]" />
          </template>
        </Card>
      </div>

    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, ref, watch } from 'vue';
import { useToast } from 'primevue/usetoast';

import CanvasDrawing from './components/CanvasDrawing.vue';
import ParameterSettings from './components/ParameterSettings.vue';
import TrainingControl from './components/TrainingControl.vue';
import PatternGallery from './components/PatternGallery.vue';

import { trainModel, predictPattern } from './services/api';
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

const modelParams = ref({
  alfa: 0.6,
  niu: 0.3,
  rms: 0.001,
  epochs: 1000,
  hiddenNeurons: 128,
  upper_limit: 0.3,
  lower_limit: -0.3
});

const buttons = computed(() =>
  patterns.value.map((p, index) => ({ label: `P${index + 1}`, value: index }))
);


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

watch(rms_history, (newHistory) => {
  if (newHistory.length > 0) {
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

    predictionValues.value = { input_neurons: 784, output_neurons: 3, hidden_neurons: parseFloat(modelParams.value.hiddenNeurons), }

    const result = await trainModel(data);
    console.log(result)
    rms_history.value = result.rms_history

    isTraining.value = false;
    isTrained.value = true;
    toast.add({
      severity: 'success',
      summary: 'Entrenamiento completo',
      detail: result.message,
      life: 5000
    });
  } catch (error) {
    isTraining.value = false;
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
  patterns.value = [];
  targets.value = [];
  isTrained.value = false;
  predictionValues.value = { hidden_neurons: 0, output_neurons: 0, input_neurons: 0 }
  prediction.value = null;
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

      // console.table(data.inputs)

      const result = await predictPattern(data);
      prediction.value = result.prediction.patternData
      console.table(prediction.value)
      toast.add({
        severity: 'success',
        summary: 'Predicción completada',
        life: 3000
      });
      isLoading.value = false;
    }
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Error de predicción',
      detail: error.message || 'Ocurrió un error durante la predicción',
      life: 5000
    });
  }
};
</script>
