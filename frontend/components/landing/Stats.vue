<template>
  <section ref="sectionRef" class="relative py-16">
    <div class="container-wide">
      <!-- Contained divider -->
      <div class="section-divider mb-16" />
      
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-8 lg:gap-12">
        <div 
          v-for="(stat, index) in stats" 
          :key="stat.labelKey"
          class="text-center transition-all duration-500"
          :class="isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'"
          :style="{ transitionDelay: `${index * 100}ms` }"
        >
          <div class="text-3xl lg:text-4xl text-surface-50 mb-2">
            <span ref="valueRefs" class="tabular-nums">{{ isVisible ? stat.value : '0' }}</span>
          </div>
          <div class="text-sm text-surface-500 font-mono">
            {{ $t(stat.labelKey) }}
          </div>
        </div>
      </div>
      
      <!-- Contained divider -->
      <div class="section-divider mt-16" />
    </div>
  </section>
</template>

<script setup lang="ts">
const stats = [
  { value: '10x', labelKey: 'stats.faster' },
  { value: '4+', labelKey: 'stats.platforms' },
  { value: '99%', labelKey: 'stats.timeSaved' },
  { value: '<50ms', labelKey: 'stats.analysis' },
]

const sectionRef = ref<HTMLElement | null>(null)
const isVisible = ref(false)

onMounted(() => {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          isVisible.value = true
          observer.disconnect()
        }
      })
    },
    { threshold: 0.3 }
  )
  
  if (sectionRef.value) {
    observer.observe(sectionRef.value)
  }
  
  onUnmounted(() => {
    observer.disconnect()
  })
})
</script>
