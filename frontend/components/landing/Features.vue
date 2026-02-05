<template>
  <section id="features" class="section">
    <div class="container-wide">
      <!-- Section Header -->
      <div 
        ref="headerRef"
        class="text-center max-w-2xl mx-auto mb-16 transition-all duration-700"
        :class="headerVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'"
      >
        <UiBadge variant="primary" class="mb-4">{{ $t('features.badge') }}</UiBadge>
        <h2 class="text-3xl sm:text-4xl font-mono text-balance mb-4">
          {{ $t('features.title') }}
          <span class="gradient-text">{{ $t('features.titleHighlight') }}</span>
          {{ $t('features.titleEnd') }}
        </h2>
        <p class="text-surface-400 leading-relaxed font-mono">
          {{ $t('features.subtitle') }}
        </p>
      </div>

      <!-- Features Grid with staggered scroll animation -->
      <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div 
          v-for="(feature, index) in features" 
          :key="feature.titleKey"
          ref="featureRefs"
          class="card group transition-all duration-500"
          :class="visibleFeatures[index] ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'"
          :style="{ transitionDelay: `${(index % 3) * 100}ms` }"
        >
          <div 
            class="w-12 h-12 rounded-lg flex items-center justify-center mb-5 transition-all duration-300 group-hover:scale-110"
            :class="feature.iconBg"
          >
            <UiIcon :name="feature.icon" :size="24" :class="feature.iconColor" />
          </div>
          <h3 class="text-lg font-mono text-surface-900 dark:text-surface-50 mb-2">
            {{ $t(feature.titleKey) }}
          </h3>
          <p class="text-surface-400 text-sm leading-relaxed font-mono">
            {{ $t(feature.descKey) }}
          </p>
        </div>
      </div>
      
      <!-- Contained divider -->
      <div class="section-divider mt-24" />
    </div>
  </section>
</template>

<script setup lang="ts">
const features = [
  {
    icon: 'Target',
    titleKey: 'features.pattern.title',
    descKey: 'features.pattern.description',
    iconBg: 'bg-primary-500/15',
    iconColor: 'text-primary-400',
  },
  {
    icon: 'BarChart3',
    titleKey: 'features.strategy.title',
    descKey: 'features.strategy.description',
    iconBg: 'bg-accent-200/15',
    iconColor: 'text-accent-200',
  },
  {
    icon: 'FileText',
    titleKey: 'features.script.title',
    descKey: 'features.script.description',
    iconBg: 'bg-emerald-500/15',
    iconColor: 'text-emerald-400',
  },
  {
    icon: 'Scissors',
    titleKey: 'features.editing.title',
    descKey: 'features.editing.description',
    iconBg: 'bg-amber-500/15',
    iconColor: 'text-amber-400',
  },
  {
    icon: 'Send',
    titleKey: 'features.publishing.title',
    descKey: 'features.publishing.description',
    iconBg: 'bg-rose-500/15',
    iconColor: 'text-rose-400',
  },
  {
    icon: 'TrendingUp',
    titleKey: 'features.analytics.title',
    descKey: 'features.analytics.description',
    iconBg: 'bg-cyan-500/15',
    iconColor: 'text-cyan-400',
  },
]

const headerRef = ref<HTMLElement | null>(null)
const featureRefs = ref<HTMLElement[]>([])
const headerVisible = ref(false)
const visibleFeatures = ref<boolean[]>(new Array(features.length).fill(false))

onMounted(() => {
  // Header observer
  const headerObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          headerVisible.value = true
          headerObserver.disconnect()
        }
      })
    },
    { threshold: 0.2 }
  )
  
  if (headerRef.value) {
    headerObserver.observe(headerRef.value)
  }
  
  // Features observer
  const featuresObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const index = featureRefs.value.indexOf(entry.target as HTMLElement)
          if (index !== -1) {
            visibleFeatures.value[index] = true
          }
        }
      })
    },
    { 
      threshold: 0.1,
      rootMargin: '0px 0px -50px 0px'
    }
  )
  
  featureRefs.value.forEach((el) => {
    if (el) featuresObserver.observe(el)
  })
  
  onUnmounted(() => {
    headerObserver.disconnect()
    featuresObserver.disconnect()
  })
})
</script>
