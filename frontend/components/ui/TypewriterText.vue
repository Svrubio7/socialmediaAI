<template>
  <span class="inline-block">
    <span ref="textRef" class="font-mono">{{ displayText }}</span>
    <span 
      v-if="showCursor" 
      class="inline-block w-0.5 h-[1em] bg-current ml-0.5 align-middle"
      :class="{ 'animate-blink': !isTyping }"
    />
  </span>
</template>

<script setup lang="ts">
interface Props {
  text: string
  speed?: number
  delay?: number
  showCursor?: boolean
  loop?: boolean
  deleteSpeed?: number
  pauseTime?: number
}

const props = withDefaults(defineProps<Props>(), {
  speed: 50,
  delay: 0,
  showCursor: true,
  loop: false,
  deleteSpeed: 30,
  pauseTime: 2000,
})

const emit = defineEmits<{
  complete: []
  loopComplete: []
}>()

const displayText = ref('')
const isTyping = ref(false)
const textRef = ref<HTMLElement | null>(null)

let currentIndex = 0
let timeoutId: ReturnType<typeof setTimeout> | null = null

const typeText = () => {
  isTyping.value = true
  
  if (currentIndex < props.text.length) {
    displayText.value += props.text[currentIndex]
    currentIndex++
    timeoutId = setTimeout(typeText, props.speed)
  } else {
    isTyping.value = false
    emit('complete')
    
    if (props.loop) {
      timeoutId = setTimeout(deleteText, props.pauseTime)
    }
  }
}

const deleteText = () => {
  isTyping.value = true
  
  if (displayText.value.length > 0) {
    displayText.value = displayText.value.slice(0, -1)
    timeoutId = setTimeout(deleteText, props.deleteSpeed)
  } else {
    currentIndex = 0
    emit('loopComplete')
    timeoutId = setTimeout(typeText, props.speed)
  }
}

const startTyping = () => {
  timeoutId = setTimeout(typeText, props.delay)
}

onMounted(() => {
  startTyping()
})

onUnmounted(() => {
  if (timeoutId) {
    clearTimeout(timeoutId)
  }
})
</script>
