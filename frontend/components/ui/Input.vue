<template>
  <div class="w-full">
    <label v-if="label" :for="inputId" class="label">
      {{ label }}
      <span v-if="required" class="text-red-400">*</span>
    </label>
    
    <div class="relative">
      <!-- Left icon -->
      <div v-if="$slots['icon-left']" class="absolute left-3 top-1/2 -translate-y-1/2 text-surface-500">
        <slot name="icon-left" />
      </div>
      
      <!-- Input -->
      <component
        :is="inputComponent"
        :id="inputId"
        :value="modelValue"
        :type="type"
        :placeholder="placeholder"
        :disabled="disabled"
        :readonly="readonly"
        :required="required"
        :rows="rows"
        :class="inputClasses"
        v-bind="$attrs"
        @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
      />
      
      <!-- Right icon -->
      <div v-if="$slots['icon-right']" class="absolute right-3 top-1/2 -translate-y-1/2 text-surface-500">
        <slot name="icon-right" />
      </div>
    </div>
    
    <!-- Error message -->
    <p v-if="error" class="mt-1.5 text-sm text-red-400">
      {{ error }}
    </p>
    
    <!-- Help text -->
    <p v-else-if="hint" class="mt-1.5 text-sm text-surface-500">
      {{ hint }}
    </p>
  </div>
</template>

<script setup lang="ts">
interface Props {
  modelValue?: string | number
  label?: string
  type?: 'text' | 'email' | 'password' | 'number' | 'tel' | 'url' | 'search' | 'textarea'
  placeholder?: string
  disabled?: boolean
  readonly?: boolean
  required?: boolean
  error?: string
  hint?: string
  rows?: number
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  rows: 4,
})

defineEmits<{
  (e: 'update:modelValue', value: string | number): void
}>()

const inputId = computed(() => `input-${Math.random().toString(36).substr(2, 9)}`)

const inputComponent = computed(() => {
  return props.type === 'textarea' ? 'textarea' : 'input'
})

const slots = useSlots()

const inputClasses = computed(() => [
  'input',
  props.error ? 'input-error' : '',
  slots['icon-left'] ? 'pl-10' : '',
  slots['icon-right'] ? 'pr-10' : '',
  props.type === 'textarea' ? 'min-h-[100px] resize-y' : '',
])
</script>
