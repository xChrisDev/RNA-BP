<template>
  <div class="flex justify-center items-center">
    <canvas ref="canvas" class="border-2 border-gray-300 rounded-lg cursor-crosshair bg-white" width="280" height="280"
      @mousedown="startDrawing" @mousemove="draw" @mouseup="stopDrawing" @mouseleave="stopDrawing"
      @touchstart="handleTouchStart" @touchmove="handleTouchMove" @touchend="stopDrawing"></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';

// Props y Emits
const props = defineProps({
  disabled: {
    type: Boolean,
    default: false
  },
  mode: {
    type: String,
    default: 'collection',
    validator: (value) => ['collection', 'prediction'].includes(value)
  }
});

const emit = defineEmits(['pattern-complete', 'predict']);

// Refs y variables de estado
const canvas = ref(null);
const ctx = ref(null);
const isDrawing = ref(false);
const lastX = ref(0);
const lastY = ref(0);

// Inicializar canvas al montar
onMounted(() => {
  if (canvas.value) {
    ctx.value = canvas.value.getContext('2d');
    ctx.value.lineJoin = 'round';
    ctx.value.lineCap = 'round';
    ctx.value.lineWidth = 15;
    ctx.value.strokeStyle = '#000000';
    clearCanvas();
  }
});

const getCanvas = () => {
  return canvas.value;
};

const getContext = () => {
  return ctx.value;
};

// Limpiar el canvas y dibujar borde guía
const clearCanvas = () => {
  if (!ctx.value) return;

  ctx.value.fillStyle = 'white';
  ctx.value.fillRect(0, 0, canvas.value.width, canvas.value.height);

  // ctx.value.strokeStyle = '#e0e0e0';
  // ctx.value.lineWidth = 1;
  // ctx.value.strokeRect(20, 20, canvas.value.width - 40, canvas.value.height - 40);

  // Restaurar para dibujar
  ctx.value.lineWidth = 15;
  ctx.value.strokeStyle = '#000000';
};

// Iniciar dibujo
const startDrawing = (e) => {
  if (props.disabled) return;

  isDrawing.value = true;
  const rect = canvas.value.getBoundingClientRect();
  lastX.value = e.clientX - rect.left;
  lastY.value = e.clientY - rect.top;
};

// Dibujar en canvas
const draw = (e) => {
  if (!isDrawing.value || props.disabled) return;

  const rect = canvas.value.getBoundingClientRect();
  const currentX = e.clientX - rect.left;
  const currentY = e.clientY - rect.top;

  ctx.value.beginPath();
  ctx.value.moveTo(lastX.value, lastY.value);
  ctx.value.lineTo(currentX, currentY);
  ctx.value.stroke();

  lastX.value = currentX;
  lastY.value = currentY;
};

// Detener dibujo y emitir evento
const stopDrawing = () => {
  if (isDrawing.value) {
    isDrawing.value = false;

    if (props.mode === 'collection') {
      emit('pattern-complete');
    } else if (props.mode === 'prediction') {
      emit('predict');
    }
  }
};

// Guardar patrón como array 28x28
const savePattern = async () => {
  if (!ctx.value || !canvas.value) return null;

  const originalCtx = ctx.value;
  const originalCanvas = canvas.value;
  const { width, height } = originalCanvas;

  // Obtener la imagen original
  const originalImageData = originalCtx.getImageData(0, 0, width, height).data;

  // Detectar el área de dibujo (bounding box)
  let minX = width, minY = height, maxX = 0, maxY = 0;
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      const index = (y * width + x) * 4;
      const r = originalImageData[index];
      const g = originalImageData[index + 1];
      const b = originalImageData[index + 2];
      const grayscale = (r + g + b) / 3;

      if (grayscale < 254) { // si no es blanco
        minX = Math.min(minX, x);
        minY = Math.min(minY, y);
        maxX = Math.max(maxX, x);
        maxY = Math.max(maxY, y);
      }
    }
  }

  // Si no hay dibujo
  if (minX > maxX || minY > maxY) return null;

  const boxWidth = maxX - minX + 1;
  const boxHeight = maxY - minY + 1;

  // Crear un canvas temporal con el recorte
  const croppedCanvas = document.createElement('canvas');
  croppedCanvas.width = boxWidth;
  croppedCanvas.height = boxHeight;
  const croppedCtx = croppedCanvas.getContext('2d');

  croppedCtx.drawImage(
    originalCanvas,
    minX, minY, boxWidth, boxHeight,
    0, 0, boxWidth, boxHeight
  );

  // Escalar a 28x28 en otro canvas
  const finalCanvas = document.createElement('canvas');
  finalCanvas.width = 28;
  finalCanvas.height = 28;
  const finalCtx = finalCanvas.getContext('2d');

  finalCtx.fillStyle = 'white';
  finalCtx.fillRect(0, 0, 28, 28);

  finalCtx.drawImage(croppedCanvas, 0, 0, 28, 28);

  // Extraer píxeles finales
  const finalData = finalCtx.getImageData(0, 0, 28, 28).data;
  const pattern = [];

  for (let i = 0; i < 28; i++) {
    const row = [];
    for (let j = 0; j < 28; j++) {
      const index = (i * 28 + j) * 4;
      const r = finalData[index];
      const g = finalData[index + 1];
      const b = finalData[index + 2];
      const grayscale = 255 - Math.floor((r + g + b) / 3);
      row.push(grayscale);
    }
    pattern.push(row);
  }
  // console.table(pattern)
  return pattern;
};



// Limpiar canvas cuando cambia el modo
watch(() => props.mode, () => {
  clearCanvas();
});

// Exponer funciones
defineExpose({
  clearCanvas,
  savePattern,
  getCanvas,
  getContext
});
</script>
