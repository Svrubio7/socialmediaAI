<template>
  <div class="flex flex-col items-center justify-center text-center py-16 px-4">
    <!-- Icon -->
    <div 
      class="w-20 h-20 rounded-2xl flex items-center justify-center mb-6"
      :class="iconBgClass"
    >
      <UiIcon :name="icon" :size="40" :class="iconColorClass" />
    </div>
    
    <!-- Title -->
    <h3 class="text-xl font-mono font-medium text-surface-100 mb-2">
      {{ title }}
    </h3>
    
    <!-- Description -->
    <p class="text-surface-400 max-w-sm mb-8">
      {{ description }}
    </p>
    
    <!-- Action -->
    <slot name="action">
      <Button v-if="actionLabel" :variant="actionVariant" @click="$emit('action')">
        <UiIcon v-if="actionIcon" :name="actionIcon" :size="18" />
        <span>{{ actionLabel }}</span>
      </Button>
    </slot>
  </div>
</template>

<script setup lang="ts">
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
