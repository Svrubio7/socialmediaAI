<template>
  <span :class="badgeClasses">
    <span v-if="dot" class="w-1.5 h-1.5 rounded-full" :class="dotClass" />
    <slot />
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  variant?: 'primary' | 'success' | 'warning' | 'danger' | 'accent' | 'neutral'
  size?: 'sm' | 'md'
  dot?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'neutral',
  size: 'md',
  dot: false,
})

const variantClasses = computed(() => {
  const variants = {
    primary: 'badge-primary',
    success: 'badge-success',
    warning: 'badge-warning',
    danger: 'badge-danger',
    accent: 'badge bg-accent-200/15 text-accent-200 border border-accent-200/20',
    neutral: 'badge bg-surface-700 text-surface-300 border border-surface-600',
  }
  return variants[props.variant]
})

const sizeClasses = computed(() => {
  const sizes = {
    sm: 'text-[10px] px-2 py-0.5',
    md: '',
  }
  return sizes[props.size]
})

const dotClass = computed(() => {
  const colors = {
    primary: 'bg-primary-400',
    success: 'bg-emerald-400',
    warning: 'bg-amber-400',
    danger: 'bg-red-400',
    accent: 'bg-accent-200',
    neutral: 'bg-surface-400',
  }
  return colors[props.variant]
})

const badgeClasses = computed(() => [
  variantClasses.value,
  sizeClasses.value,
])
</script>
