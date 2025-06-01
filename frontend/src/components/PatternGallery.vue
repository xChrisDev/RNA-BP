<template>
  <div class="h-[342px] overflow-y-auto pr-2">
    <div v-if="patterns.length === 0" class="text-center py-6 text-gray-500">
      <i class="pi pi-image text-4xl mb-2"></i>
      <p>No hay patrones guardados</p>
    </div>

    <div v-else class="grid grid-cols-2 gap-2">
      <div v-for="pattern in patterns" :key="pattern.id"
        class="pattern-item border border-gray-200 rounded-lg p-2 relative">
        <div class="flex justify-end">
          <Button class="!w-8 !h-8" size="small" icon="pi pi-times" severity="danger" aria-label="Borrar"
            @click="removePattern(pattern.id)" />
        </div>

        <div class="text-center mb-1 font-medium">
          Patrón {{ pattern.label + 1 }}
        </div>

        <canvas :ref="el => { if (el) canvasRefs[pattern.id] = el }" width="100" height="100"
          class="mx-auto border mb-2 rounded-lg border-white"></canvas>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import Button from 'primevue/button'

const props = defineProps({
  patterns: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['remove-pattern'])
const canvasRefs = ref({})

const drawPattern = (pattern) => {
  const canvas = canvasRefs.value[pattern.id]
  if (!canvas) return

  const ctx = canvas.getContext('2d')
  const patternData = pattern.data

  ctx.fillStyle = 'white'
  ctx.fillRect(0, 0, canvas.width, canvas.height)

  const cellSize = Math.floor(canvas.width / 28)

  for (let i = 0; i < patternData.length; i++) {
    for (let j = 0; j < patternData[i].length; j++) {
      const value = patternData[i][j]
      if (value > 0) {
        const grayValue = 255 - value
        ctx.fillStyle = `rgb(${grayValue}, ${grayValue}, ${grayValue})`
        ctx.fillRect(j * cellSize, i * cellSize, cellSize, cellSize)
      }
    }
  }
}

// Dibujar patrones al montar
onMounted(() => {
  props.patterns.forEach(drawPattern)
})

// Volver a dibujar si cambian los patrones
watch(() => props.patterns, (newPatterns) => {
  setTimeout(() => {
    newPatterns.forEach(drawPattern)
  }, 0)
}, { deep: true })

// Emitir eliminación
const removePattern = (id) => {
  emit('remove-pattern', id)
}
</script>
