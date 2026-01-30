<template>
  <NuxtLink 
    :to="localePath('/')" 
    class="flex items-center"
    :class="[
      gapClass,
      linkClass
    ]"
  >
    <!-- Logo Icon -->
    <div 
      v-if="variant !== 'text'"
      class="relative flex items-center justify-center rounded-lg bg-gradient-to-br from-primary-500 to-primary-600"
      :class="iconSizeClass"
    >
      <span class="font-normal text-surface-950" :class="iconTextClass">E</span>
    </div>

    <!-- Logo Text -->
    <span 
      v-if="variant !== 'icon'"
      class="font-medium tracking-tight"
      :class="[textSizeClass, textColorClass]"
    >
      Elevo<span class="text-primary-400">AI</span>
    </span>
  </NuxtLink>
</template>

<script setup lang="ts">
import { computed } from 'vue'
const localePath = useLocalePath()

interface Props {
  variant?: 'full' | 'icon' | 'text'
  size?: 'sm' | 'md' | 'lg' | 'xl'
  class?: string
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'full',
  size: 'md',
})

const linkClass = computed(() => props.class || '')

const gapClass = computed(() => {
  if (props.variant === 'icon' || props.variant === 'text') return ''
  switch (props.size) {
    case 'sm': return 'gap-2'
    case 'md': return 'gap-2'
    case 'lg': return 'gap-2.5'
    case 'xl': return 'gap-3'
    default: return 'gap-2'
  }
})

const iconSizeClass = computed(() => {
  switch (props.size) {
    case 'sm': return 'w-7 h-7'
    case 'md': return 'w-8 h-8'
    case 'lg': return 'w-10 h-10'
    case 'xl': return 'w-12 h-12'
    default: return 'w-8 h-8'
  }
})

const iconTextClass = computed(() => {
  switch (props.size) {
    case 'sm': return 'text-base'
    case 'md': return 'text-lg'
    case 'lg': return 'text-xl'
    case 'xl': return 'text-2xl'
    default: return 'text-lg'
  }
})

const textSizeClass = computed(() => {
  switch (props.size) {
    case 'sm': return 'text-lg'
    case 'md': return 'text-xl'
    case 'lg': return 'text-2xl'
    case 'xl': return 'text-3xl'
    default: return 'text-xl'
  }
})

const textColorClass = computed(() => 'text-surface-950 dark:text-surface-50')
</script>
