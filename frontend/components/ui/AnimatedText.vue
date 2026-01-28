<template>
  <component :is="tag" ref="containerRef" class="inline-block">
    <template v-if="animation === 'letter'">
      <span 
        v-for="(char, index) in characters" 
        :key="index"
        class="inline-block"
        :class="[
          animationClass,
          { 'opacity-0': !isVisible }
        ]"
        :style="{ animationDelay: `${delay + (index * stagger)}ms` }"
      >{{ char === ' ' ? '\u00A0' : char }}</span>
    </template>
    
    <template v-else-if="animation === 'word'">
      <span 
        v-for="(word, index) in words" 
        :key="index"
        class="inline-block overflow-hidden mr-[0.25em]"
      >
        <span 
          class="inline-block"
          :class="[
            animationClass,
            { 'opacity-0': !isVisible }
          ]"
          :style="{ animationDelay: `${delay + (index * stagger)}ms` }"
        >{{ word }}</span>
      </span>
    </template>
    
    <template v-else>
      <span 
        :class="[
          animationClass,
          { 'opacity-0': !isVisible }
        ]"
        :style="{ animationDelay: `${delay}ms` }"
      >
        <slot>{{ text }}</slot>
      </span>
    </template>
  </component>
</template>

<script setup lang="ts">
interface Props {
  text?: string
  tag?: string
  animation?: 'letter' | 'word' | 'fade' | 'reveal'
  delay?: number
  stagger?: number
  triggerOnView?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  text: '',
  tag: 'span',
  animation: 'fade',
  delay: 0,
  stagger: 50,
  triggerOnView: true,
})

const containerRef = ref<HTMLElement | null>(null)
const isVisible = ref(!props.triggerOnView)

const characters = computed(() => props.text.split(''))
const words = computed(() => props.text.split(' '))

const animationClass = computed(() => {
  switch (props.animation) {
    case 'letter':
      return 'animate-letter-bounce animate-fill-both'
    case 'word':
      return 'animate-word-reveal animate-fill-both'
    case 'reveal':
      return 'animate-text-reveal animate-fill-both'
    default:
      return 'animate-fade-in-up animate-fill-both'
  }
})

onMounted(() => {
  if (props.triggerOnView && containerRef.value) {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            isVisible.value = true
            observer.disconnect()
          }
        })
      },
      { threshold: 0.1 }
    )
    
    observer.observe(containerRef.value)
    
    onUnmounted(() => {
      observer.disconnect()
    })
  }
})
</script>
