<template>
  <section id="how-it-works" class="section overflow-hidden">
    <div class="container-wide">
      <!-- Section Header -->
      <div class="text-center max-w-2xl mx-auto mb-20">
        <UiBadge variant="accent" class="mb-4">{{ $t('howItWorks.badge') }}</UiBadge>
        <h2 class="text-3xl sm:text-4xl font-mono text-balance mb-4">
          {{ $t('howItWorks.title') }}
          <span class="gradient-text">{{ $t('howItWorks.titleHighlight') }}</span>
        </h2>
        <p class="text-surface-400 leading-relaxed font-mono">
          {{ $t('howItWorks.subtitle') }}
        </p>
      </div>

      <!-- Steps - horizontally distributed with stair effect -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-8 md:gap-6 max-w-6xl mx-auto">
        <div 
          v-for="(step, index) in steps" 
          :key="step.titleKey"
          ref="stepRefs"
          class="step-item relative transition-all duration-700 ease-out"
          :class="visibleSteps[index] ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-12'"
          :style="{ 
            transitionDelay: `${index * 200}ms`,
            marginTop: `${index * 3}rem`
          }"
        >
          <!-- Step card -->
          <div class="bg-surface-900/60 border border-surface-800 rounded-2xl p-6 relative h-full">
            <!-- Step number -->
            <div 
              class="absolute -top-3 -left-3 w-12 h-12 rounded-xl bg-surface-950 border border-surface-700 flex items-center justify-center shadow-lg z-10 transition-all duration-500"
              :class="visibleSteps[index] ? 'opacity-100 scale-100' : 'opacity-0 scale-75'"
              :style="{ transitionDelay: `${index * 200 + 100}ms` }"
            >
              <span class="text-lg font-mono text-surface-50">{{ String(index + 1).padStart(2, '0') }}</span>
            </div>
            
            <!-- Content -->
            <div class="pt-6">
              <h3 
                class="text-lg font-mono text-surface-50 mb-2 transition-all duration-500"
                :class="visibleSteps[index] ? 'opacity-100' : 'opacity-0'"
                :style="{ transitionDelay: `${index * 200 + 200}ms` }"
              >
                {{ $t(step.titleKey) }}
              </h3>
              <p 
                class="text-surface-400 text-sm leading-relaxed mb-4 font-mono transition-all duration-500"
                :class="visibleSteps[index] ? 'opacity-100' : 'opacity-0'"
                :style="{ transitionDelay: `${index * 200 + 300}ms` }"
              >
                {{ $t(step.descKey) }}
              </p>
              
              <!-- Features list -->
              <ul class="space-y-2">
                <li 
                  v-for="(feature, fIndex) in step.features" 
                  :key="feature"
                  class="flex items-start gap-2 text-sm text-surface-400 font-mono transition-all duration-500"
                  :class="visibleSteps[index] ? 'opacity-100 translate-x-0' : 'opacity-0 -translate-x-4'"
                  :style="{ transitionDelay: `${index * 200 + 400 + fIndex * 75}ms` }"
                >
                  <UiIcon name="Check" :size="14" class="text-primary-400 flex-shrink-0 mt-0.5" />
                  <span>{{ $t(feature) }}</span>
                </li>
              </ul>
            </div>
          </div>
          
          <!-- Connecting line to next step (desktop only) -->
          <div 
            v-if="index < steps.length - 1"
            class="hidden md:block absolute top-1/2 -right-3 w-6 h-px bg-surface-700"
          />
        </div>
      </div>
      
      <!-- Contained divider -->
      <div class="section-divider mt-24" />
    </div>
  </section>
</template>

<script setup lang="ts">
const steps = [
  {
    titleKey: 'howItWorks.step1.title',
    descKey: 'howItWorks.step1.description',
    features: [
      'howItWorks.step1.feature1',
      'howItWorks.step1.feature2',
      'howItWorks.step1.feature3',
    ],
  },
  {
    titleKey: 'howItWorks.step2.title',
    descKey: 'howItWorks.step2.description',
    features: [
      'howItWorks.step2.feature1',
      'howItWorks.step2.feature2',
      'howItWorks.step2.feature3',
    ],
  },
  {
    titleKey: 'howItWorks.step3.title',
    descKey: 'howItWorks.step3.description',
    features: [
      'howItWorks.step3.feature1',
      'howItWorks.step3.feature2',
      'howItWorks.step3.feature3',
    ],
  },
]

const stepRefs = ref<HTMLElement[]>([])
const visibleSteps = ref<boolean[]>(new Array(steps.length).fill(false))

onMounted(() => {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const index = stepRefs.value.indexOf(entry.target as HTMLElement)
          if (index !== -1) {
            visibleSteps.value[index] = true
          }
        }
      })
    },
    { 
      threshold: 0.15,
      rootMargin: '0px 0px -30px 0px'
    }
  )
  
  stepRefs.value.forEach((el) => {
    if (el) observer.observe(el)
  })
  
  onUnmounted(() => {
    observer.disconnect()
  })
})
</script>
