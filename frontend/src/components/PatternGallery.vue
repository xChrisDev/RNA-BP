<template>
  <div class="overflow-y-auto pr-2">
    <div v-if="patterns.length === 0" class="text-center py-6 text-gray-500">
      <i class="pi pi-image text-4xl mb-2"></i>
      <p>No hay patrones guardados</p>
    </div>

    <div v-else class="grid grid-cols-5 gap-1">
      <div v-for="pattern in patterns" :key="pattern.id" @click="disabled ? handlePatternClick(pattern) : null" :class="[
        'pattern-item border border-gray-300 rounded p-1 relative transition-all duration-200',
        disabled ? 'disabled-filter cursor-pointer' : 'cursor-default'
      ]">
        <div v-if="!disabled" class="flex justify-end">
          <Button class="!w-6 !h-6" size="small" icon="pi pi-times" severity="danger" aria-label="Borrar"
            @click.stop="removePattern(pattern.id)" />
        </div>

        <canvas :ref="el => { if (el) canvasRefs[pattern.id] = el }" width="50" height="50"
          :class="['mx-auto border rounded border-white',disabled ? 'mt-5 mb-2': 'mt-0']" />

        <div class="text-xs text-center mt-1">Patrón {{ pattern.label + 1 }}</div>
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
  },
  disabled: {
    type: Boolean,
    default: false
  }
})

const handlePatternClick = (pattern) => {
  emit('pattern', pattern.label)
}

const emit = defineEmits(['remove-pattern', 'pattern'])
const canvasRefs = ref({})

const drawPattern = (pattern) => {
  const canvas = canvasRefs.value[pattern.id]
  if (!canvas) return

  const ctx = canvas.getContext('2d')
  const patternData = pattern.data

  ctx.fillStyle = 'white'
  ctx.fillRect(0, 0, canvas.width, canvas.height)

  const cellWidth = canvas.width / patternData[0].length
  const cellHeight = canvas.height / patternData.length

  for (let i = 0; i < patternData.length; i++) {
    for (let j = 0; j < patternData[i].length; j++) {
      const value = patternData[i][j]
      if (value > 0) {
        const grayValue = 255 - value
        ctx.fillStyle = `rgb(${grayValue}, ${grayValue}, ${grayValue})`
        ctx.fillRect(j * cellWidth, i * cellHeight, cellWidth, cellHeight)
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