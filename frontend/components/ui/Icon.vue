<template>
  <component
    :is="iconComponent"
    :size="size"
    :stroke-width="strokeWidth"
    :class="iconClasses"
    v-bind="$attrs"
  />
</template>

<script setup lang="ts">
import * as icons from 'lucide-vue-next'

interface Props {
  name: keyof typeof icons
  size?: number | string
  strokeWidth?: number
  class?: string
}

const props = withDefaults(defineProps<Props>(), {
  size: 24,
  strokeWidth: 2,
})

const iconComponent = computed(() => {
  return icons[props.name] || icons.HelpCircle
})

const iconClasses = computed(() => props.class || '')
</script>
