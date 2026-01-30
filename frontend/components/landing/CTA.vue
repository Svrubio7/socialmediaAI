<template>
  <section ref="sectionRef" class="section">
    <div class="container-wide">
      <div 
        class="relative overflow-hidden rounded-2xl border border-surface-800 bg-surface-900 transition-all duration-700"
        :class="isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-12'"
      >
        <!-- Subtle glow -->
        <div 
          class="absolute top-0 left-1/4 w-64 h-64 bg-primary-500/10 rounded-full blur-[100px] transition-opacity duration-1000"
          :class="isVisible ? 'opacity-100' : 'opacity-0'"
        />
        <div 
          class="absolute bottom-0 right-1/4 w-64 h-64 bg-accent-200/5 rounded-full blur-[100px] transition-opacity duration-1000 delay-300"
          :class="isVisible ? 'opacity-100' : 'opacity-0'"
        />
        
        <!-- Content -->
        <div class="relative px-8 py-16 sm:px-12 lg:px-16 lg:py-20 text-center">
          <h2 
            class="text-2xl sm:text-3xl lg:text-4xl font-mono text-balance mb-4 transition-all duration-500"
            :class="isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-6'"
            :style="{ transitionDelay: '200ms' }"
          >
            {{ $t('cta.title') }}
            <span class="gradient-text">{{ $t('cta.titleHighlight') }}</span>
          </h2>
          <p 
            class="text-surface-400 max-w-xl mx-auto mb-8 leading-relaxed font-mono transition-all duration-500"
            :class="isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-6'"
            :style="{ transitionDelay: '300ms' }"
          >
            {{ $t('cta.subtitle') }}
          </p>
          
          <div 
            class="flex flex-col sm:flex-row items-center justify-center gap-4 transition-all duration-500"
            :class="isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-6'"
            :style="{ transitionDelay: '400ms' }"
          >
            <NuxtLink :to="localePath('/auth/register')" class="btn-accent btn-lg">
              <span>{{ $t('cta.button1') }}</span>
              <UiIcon name="ArrowRight" :size="18" />
            </NuxtLink>
            <NuxtLink :to="localePath('/contact')" class="btn-secondary btn-lg">
              <span>{{ $t('cta.button2') }}</span>
            </NuxtLink>
          </div>
          
          <!-- Trust badges -->
          <div 
            class="mt-10 flex flex-wrap items-center justify-center gap-6 text-sm text-surface-500 font-mono transition-all duration-500"
            :class="isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-6'"
            :style="{ transitionDelay: '500ms' }"
          >
            <div class="flex items-center gap-2">
              <UiIcon name="Shield" :size="16" class="text-surface-500" />
              <span>{{ $t('cta.badge1') }}</span>
            </div>
            <div class="flex items-center gap-2">
              <UiIcon name="Zap" :size="16" class="text-surface-500" />
              <span>{{ $t('cta.badge2') }}</span>
            </div>
            <div class="flex items-center gap-2">
              <UiIcon name="Headphones" :size="16" class="text-surface-500" />
              <span>{{ $t('cta.badge3') }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
const localePath = useLocalePath()

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
    { threshold: 0.2 }
  )
  
  if (sectionRef.value) {
    observer.observe(sectionRef.value)
  }
  
  onUnmounted(() => {
    observer.disconnect()
  })
})
</script>
