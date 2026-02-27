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
    <img
      v-if="variant !== 'text'"
      src="/elevo_just_logo.png"
      alt="Elevo logo"
      class="rounded-lg object-contain"
      :class="iconSizeClass"
    />

    <!-- Logo Text -->
    <span 
      v-if="variant !== 'icon'"
      class="font-medium tracking-tight"
      :class="[textSizeClass, textColorClass]"
    >
      Elevo
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
