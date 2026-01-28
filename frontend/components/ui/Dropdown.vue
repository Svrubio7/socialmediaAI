<template>
  <div class="relative" ref="dropdownRef">
    <!-- Trigger -->
    <div @click="toggle">
      <slot name="trigger" :open="isOpen" />
    </div>
    
    <!-- Dropdown content -->
    <Transition
      enter-active-class="transition duration-150 ease-out"
      enter-from-class="opacity-0 scale-95"
      enter-to-class="opacity-100 scale-100"
      leave-active-class="transition duration-100 ease-in"
      leave-from-class="opacity-100 scale-100"
      leave-to-class="opacity-0 scale-95"
    >
      <div
        v-if="isOpen"
        :class="contentClasses"
      >
        <slot :close="close" />
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { onClickOutside } from '@vueuse/core'

interface Props {
  align?: 'left' | 'right' | 'center'
  width?: 'auto' | 'trigger' | 'sm' | 'md' | 'lg'
}

const props = withDefaults(defineProps<Props>(), {
  align: 'left',
  width: 'auto',
})

const isOpen = ref(false)
const dropdownRef = ref<HTMLElement | null>(null)

const toggle = () => {
  isOpen.value = !isOpen.value
}

const close = () => {
  isOpen.value = false
}

onClickOutside(dropdownRef, close)

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape' && isOpen.value) {
    close()
  }
}

onMounted(() => {
  document.addEventListener('keydown', onKeydown)
})
onUnmounted(() => {
  document.removeEventListener('keydown', onKeydown)
})

const alignClasses = computed(() => {
  const aligns = {
    left: 'left-0',
    right: 'right-0',
    center: 'left-1/2 -translate-x-1/2',
  }
  return aligns[props.align]
})

const widthClasses = computed(() => {
  const widths = {
    auto: 'w-auto',
    trigger: 'w-full',
    sm: 'w-48',
    md: 'w-64',
    lg: 'w-80',
  }
  return widths[props.width]
})

const contentClasses = computed(() => [
  'absolute z-50 mt-2 bg-surface-900 border border-surface-800 rounded-xl shadow-xl overflow-hidden',
  alignClasses.value,
  widthClasses.value,
])
</script>
