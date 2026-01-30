<template>
  <div :class="skeletonClasses" :style="customStyle">
    <slot />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  variant?: 'text' | 'circular' | 'rectangular' | 'rounded'
  width?: string | number
  height?: string | number
  lines?: number
  animated?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'text',
  animated: true,
})

const variantClasses = computed(() => {
  const variants = {
    text: 'h-4 rounded',
    circular: 'rounded-full aspect-square',
    rectangular: 'rounded-none',
    rounded: 'rounded-lg',
  }
  return variants[props.variant]
})

const skeletonClasses = computed(() => [
  'skeleton',
  variantClasses.value,
  props.animated ? '' : 'after:hidden',
])

const customStyle = computed(() => {
  const style: Record<string, string> = {}
  if (props.width) {
    style.width = typeof props.width === 'number' ? `${props.width}px` : props.width
  }
  if (props.height) {
    style.height = typeof props.height === 'number' ? `${props.height}px` : props.height
  }
  return style
})
</script>
