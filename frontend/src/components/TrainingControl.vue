<template>
  <div class="flex">
    <div class="w-full flex items-center justify-between">
      <div class="bg-gray-200 p-3 rounded-lg text-center">
        <div v-if="!isTrained">
          <div v-if="patternsNeeded > 0" class=" text-amber-600">
            <i class="pi pi-exclamation-triangle mr-2"></i>
            Necesitas {{ patternsNeeded }} patrones
          </div>
          <div v-else class="text-green-600">
            <i class="pi pi-check-circle mr-2"></i>
            Listo para entrenar
          </div>
        </div>
        <div v-else class="text-green-600">
          <i class="pi pi-check-circle mr-2"></i>
          Modelo entrenado y listo
        </div>
      </div>

      <div class="flex gap-2">
        <Button label="Iniciar Entrenamiento" icon="pi pi-cog" :disabled="!trainingEnabled || isTraining || isTrained"
          :loading="isTraining" @click="startTraining" />

        <Button :label="isTrained ? 'Entrenar' : 'Predecir'" icon="pi pi-sync"
          :loading="isTraining" @click="predictPattern" severity="info" />

        <Button label="Reiniciar Todo" icon="pi pi-refresh" :disabled="isTraining" @click="resetModel"
          class="p-button-danger p-button-outlined" />
      </div>

      <div v-if="isTraining" class="mt-4">
        <div class="relative pt-1">
          <div class="flex mb-2 items-center justify-between">
            <div>
              <span
                class="text-sm font-semibold inline-block py-1 px-2 uppercase rounded-full text-green-600 bg-green-200">
                Entrenando...
              </span>
            </div>
          </div>
          <div class="overflow-hidden h-2 mb-4 text-xs flex rounded bg-green-200">
            <div :style="{ width: '100%' }"
              class="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-green-500 animate-pulse">
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Button } from 'primevue'

// Props
const props = defineProps({
  trainingEnabled: {
    type: Boolean,
    default: false
  },
  isTraining: {
    type: Boolean,
    default: false
  },
  isTrained: {
    type: Boolean,
    default: false
  },
  requiredPatterns: {
    type: Number,
    default: 5
  }
})

// Emits
const emit = defineEmits(['start-training', 'reset', 'predict-pattern'])

// Computed: patrones faltantes
const patternsNeeded = computed(() => {
  return props.trainingEnabled ? 0 : props.requiredPatterns
})

// Métodos
const startTraining = () => {
  if (props.trainingEnabled && !props.isTraining && !props.isTrained) {
    emit('start-training')
  }
}

const predictPattern = () =>{
  emit('predict-pattern')
}

const resetModel = () => {
  if (!props.isTraining) {
    emit('reset')
  }
}
</script>

<style scoped>
.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {

  0%,
  100% {
    opacity: 1;
  }

  50% {
    opacity: 0.5;
  }
}
</style>
