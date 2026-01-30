<template>
  <div class="flex flex-col items-center justify-center text-center py-12 px-4">
    <!-- Icon -->
    <div 
      class="w-14 h-14 rounded-xl flex items-center justify-center mb-4"
      :class="iconBgClass"
    >
      <UiIcon :name="icon" :size="28" :class="iconColorClass" />
    </div>
    
    <!-- Title -->
    <h3 class="text-base font-mono font-medium text-surface-100 mb-1.5">
      {{ title }}
    </h3>
    
    <!-- Description -->
    <p class="text-surface-400 text-sm max-w-sm mb-6">
      {{ description }}
    </p>
    
    <!-- Action -->
    <slot name="action">
      <UiButton v-if="actionLabel" :variant="actionVariant" class="rounded-xl inline-flex items-center gap-2" @click="$emit('action')">
        <template v-if="actionIcon" #icon-left>
          <UiIcon :name="actionIcon" :size="16" />
        </template>
        {{ actionLabel }}
      </UiButton>
    </slot>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  icon: string
  title: string
  description: string
  actionLabel?: string
  actionIcon?: string
  actionVariant?: 'primary' | 'secondary' | 'accent'
  variant?: 'default' | 'primary' | 'accent'
}

const props = withDefaults(defineProps<Props>(), {
  actionVariant: 'primary',
  variant: 'default',
})

defineEmits<{
  (e: 'action'): void
}>()

const iconBgClass = computed(() => {
  const variants = {
    default: 'bg-surface-800',
    primary: 'bg-primary-500/10',
    accent: 'bg-accent-500/10',
  }
  return variants[props.variant]
})

const iconColorClass = computed(() => {
  const variants = {
    default: 'text-surface-500',
    primary: 'text-primary-400',
    accent: 'text-accent-400',
  }
  return variants[props.variant]
})
</script>
