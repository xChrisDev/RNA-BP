<script setup>
import { ref, onMounted } from 'vue'
import { Button } from 'primevue'

// Estado reactivo del modo oscuro
const isDark = ref(false)

const toggleDarkMode = () => {
  isDark.value = !isDark.value
  document.documentElement.classList.toggle('my-app-dark', isDark.value)
  localStorage.setItem('darkMode', isDark.value)
}

onMounted(() => {
  const saved = localStorage.getItem('darkMode')
  isDark.value = saved === 'true'
  if (isDark.value) {
    document.documentElement.classList.add('my-app-dark')
  }
})
</script>

<template>
  <Button
    :icon="isDark ? 'pi pi-sun' : 'pi pi-moon'"
    iconPos="left"
    rounded
    severity="contrast"
    class="transition-all duration-300"
    @click="toggleDarkMode"
    aria-label="Alternar modo oscuro"
  />
</template>
