<template>
  <section id="features" class="section bg-surface-900 relative">
    <!-- Top divider -->
    <div class="absolute top-0 left-0 right-0 section-divider" />
    
    <div class="container-wide">
      <!-- Section Header -->
      <div class="text-center max-w-3xl mx-auto mb-20">
        <UiBadge variant="primary" class="mb-4">{{ $t('features.badge') }}</UiBadge>
        <h2 class="text-3xl sm:text-4xl lg:text-5xl font-display font-bold text-balance mb-6">
          {{ $t('features.title') }}
          <span class="gradient-text">{{ $t('features.titleHighlight') }}</span>
          {{ $t('features.titleEnd') }}
        </h2>
        <p class="text-lg text-surface-400">
          {{ $t('features.subtitle') }}
        </p>
      </div>

      <!-- Features Grid -->
      <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6 lg:gap-8">
        <UiCard 
          v-for="(feature, index) in features" 
          :key="feature.titleKey"
          variant="hover"
          class="group"
        >
          <div 
            class="w-14 h-14 rounded-xl flex items-center justify-center mb-6 transition-transform duration-300 group-hover:scale-110"
            :class="feature.iconBg"
          >
            <UiIcon :name="feature.icon" :size="26" :class="feature.iconColor" />
          </div>
          <h3 class="text-xl font-display font-semibold text-surface-100 mb-3">
            {{ $t(feature.titleKey) }}
          </h3>
          <p class="text-surface-400 leading-relaxed">
            {{ $t(feature.descKey) }}
          </p>
        </UiCard>
      </div>
    </div>
    
    <!-- Bottom divider -->
    <div class="absolute bottom-0 left-0 right-0 section-divider" />
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
</script>
