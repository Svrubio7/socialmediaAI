<template>
  <Teleport to="body">
    <div class="fixed bottom-4 right-4 z-[100] flex flex-col gap-2 max-w-sm w-full pointer-events-none">
      <TransitionGroup name="toast">
        <div
          v-for="toast in toasts"
          :key="toast.id"
          class="pointer-events-auto flex items-center gap-3 px-4 py-3 rounded-xl border shadow-lg"
          :class="toastClasses(toast.type)"
        >
          <UiIcon :name="toastIcon(toast.type)" :size="20" :class="toastIconClass(toast.type)" />
          <p class="flex-1 text-sm font-medium">{{ toast.message }}</p>
          <button
            type="button"
            class="p-1 rounded-lg text-surface-400 hover:text-surface-100 hover:bg-surface-800 transition-colors"
            aria-label="Dismiss"
            @click="remove(toast.id)"
          >
            <UiIcon name="X" :size="16" />
          </button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import type { ToastType } from '~/composables/useToast'

const { toasts, remove } = useToast()

function toastIcon(type: ToastType) {
  const icons = { success: 'Check', error: 'X', info: 'AlertCircle' } as const
  return icons[type]
}

function toastIconClass(type: ToastType) {
  const classes = {
    success: 'text-emerald-400',
    error: 'text-red-400',
    info: 'text-primary-400',
  }
  return classes[type]
}

function toastClasses(type: ToastType) {
  const base = 'bg-surface-900 border-surface-700'
  const byType = {
    success: 'border-l-4 border-l-emerald-500',
    error: 'border-l-4 border-l-red-500',
    info: 'border-l-4 border-l-primary-500',
  }
  return `${base} ${byType[type]}`
}
</script>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.2s ease;
}
.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateX(1rem);
}
.toast-move {
  transition: transform 0.2s ease;
}
</style>
