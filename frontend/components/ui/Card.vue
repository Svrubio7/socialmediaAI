<template>
  <NuxtLink
    v-if="to"
    :to="to"
    :class="cardClasses"
    v-bind="$attrs"
  >
    <div v-if="$slots.header" class="px-6 py-4 border-b border-surface-200 dark:border-surface-800">
      <slot name="header" />
    </div>
    <div :class="bodyClass">
      <slot />
    </div>
    <div v-if="$slots.footer" class="px-6 py-4 border-t border-surface-200 bg-accent-100/60 dark:border-surface-800 dark:bg-surface-900/50">
      <slot name="footer" />
    </div>
  </NuxtLink>
  <div
    v-else
    :class="cardClasses"
    v-bind="$attrs"
  >
    <div v-if="$slots.header" class="px-6 py-4 border-b border-surface-200 dark:border-surface-800">
      <slot name="header" />
    </div>
    <div :class="bodyClass">
      <slot />
    </div>
    <div v-if="$slots.footer" class="px-6 py-4 border-t border-surface-200 bg-accent-100/60 dark:border-surface-800 dark:bg-surface-900/50">
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  variant?: 'default' | 'hover' | 'interactive' | 'gradient'
  padding?: 'none' | 'sm' | 'md' | 'lg'
  to?: string
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'default',
  padding: 'md',
})

const variantClasses = computed(() => {
  const variants = {
    default: 'card',
    hover: 'card-hover',
    interactive: 'card-interactive',
    gradient: 'card bg-gradient-to-br from-surface-900 to-surface-900/50',
  }
  return variants[props.variant]
})

const bodyClass = computed(() => {
  if (props.padding === 'none') return ''
  const paddings = {
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
  }
  return paddings[props.padding]
})

const cardClasses = computed(() => [
  variantClasses.value,
  props.padding === 'none' ? 'p-0' : '',
  props.to ? 'block w-full no-underline cursor-pointer' : '',
])
</script>
