<template>
  <div class="flex items-center justify-center min-h-[400px]">
    <div class="flex flex-col items-center gap-4">
      <div class="relative">
        <div class="w-12 h-12 rounded-full border-2 border-surface-700" />
        <div class="absolute inset-0 w-12 h-12 rounded-full border-2 border-primary-500 border-t-transparent animate-spin" />
      </div>
      <p v-if="message" class="text-surface-400 text-sm">{{ message }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  message?: string
}

defineProps<Props>()
</script>
