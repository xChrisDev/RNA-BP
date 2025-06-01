<template>

  <div class="flex flex-col gap-6 mt-8">
    <!-- Niu -->
    <div class="mb-2">
      <FloatLabel>
        <label for="niu">Niu</label>
        <InputText id="niu" type="Number" v-model="localParams.niu" :step="0.01" :min="0.01" :max="1" mode="decimal"
          :disabled="disabled" class="w-full" @update:modelValue="updateParams" />
      </FloatLabel>
    </div>

    <!-- Alfa -->
    <div class="mb-2">
      <FloatLabel>
        <label for="alfa">Alfa</label>
        <InputText id="alfa" type="Number" v-model="localParams.alfa" :step="0.01" :min="0.01" :max="1" mode="decimal"
          :disabled="disabled" class="w-full" @update:modelValue="updateParams" />
      </FloatLabel>
    </div>

    <!-- RMS -->
    <div class="mb-2">
      <FloatLabel>
        <label for="rms">RMS</label>
        <InputText id="rms" type="Number" v-model="localParams.rms" :step="0.01" :min="0.01" mode="decimal"
          :disabled="disabled" class="w-full" @update:modelValue="updateParams" />
      </FloatLabel>
    </div>


    <!-- Épocas -->
    <div class="mb-2">
      <FloatLabel>
        <label for="epochs">Épocas (n)</label>
        <InputText id="epochs" type="Number" v-model="localParams.epochs" :min="1" :step="1" :disabled="disabled"
          class="w-full" @update:modelValue="updateParams" />
      </FloatLabel>
    </div>

    <!-- Neuronas Ocultas -->
    <div class="mb-2">
      <FloatLabel>
        <label for="hiddenNeurons">Neuronas Ocultas</label>
        <InputText id="hiddenNeurons" type="Number" v-model="localParams.hiddenNeurons" mode="decimal"
          :disabled="disabled" class="w-full" @update:modelValue="updateParams" />
      </FloatLabel>
    </div>


    <div class="grid grid-cols-2 gap-3 mb-8">
      <!-- Límite Inferior -->
      <div class="mb-2">
        <FloatLabel>
          <label for="lowerLimit">Límite Inferior</label>
          <InputText id="lowerLimit" type="Number" v-model="localParams.lower_limit" :step="0.01" :min="-0.3" :max="0.3"
            mode="decimal" :disabled="disabled" class="w-full" @update:modelValue="updateParams" />
        </FloatLabel>
      </div>

      <!-- Límite Superior -->
      <div class="mb-2">
        <FloatLabel>
          <label for="upperLimit">Límite Superior</label>
          <InputText id="upperLimit" type="Number" v-model="localParams.upper_limit" :step="0.01" :min="-0.3" :max="0.3"
            mode="decimal" :disabled="disabled" class="w-full" @update:modelValue="updateParams" />
        </FloatLabel>
      </div>
    </div>
  </div>

</template>


<script setup>
import { ref, watch } from 'vue';
import InputText from 'primevue/InputText';
import { FloatLabel } from 'primevue';

// Props y emits
const props = defineProps({
  modelParams: {
    type: Object,
    required: true
  },
  disabled: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['update:modelParams']);

// Copia local reactiva de los parámetros
const localParams = ref({ ...props.modelParams });

// Reactualizar si props cambian desde el padre
watch(() => props.modelParams, (newParams) => {
  localParams.value = { ...newParams };
}, { deep: true });

// Emitir cambios hacia el padre
const updateParams = () => {
  emit('update:modelParams', { ...localParams.value });
};
</script>
