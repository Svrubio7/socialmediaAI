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
import { computed } from 'vue'
import * as icons from 'lucide-vue-next'

interface Props {
  name: keyof typeof icons | string
  size?: number
  strokeWidth?: number
  class?: string | Record<string, boolean> | Array<string | Record<string, boolean>>
}

const props = withDefaults(defineProps<Props>(), {
  size: 24,
  strokeWidth: 2,
})

const iconComponent = computed(() => {
  const comp = (icons as Record<string, any>)[props.name as string]
  return comp || icons.HelpCircle
})

const iconClasses = computed(() => props.class || '')
</script>
