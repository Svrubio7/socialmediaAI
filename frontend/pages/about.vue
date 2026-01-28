<template>
  <div>
    <!-- Hero Section -->
    <section class="relative overflow-hidden pt-32 pb-20 lg:pt-40 lg:pb-28">
      <!-- Background -->
      <div class="absolute inset-0 bg-surface-900" />
      <div class="absolute inset-0 bg-gradient-radial-top" />
      <div class="absolute top-1/3 left-1/3 w-[500px] h-[500px] bg-primary-500/8 rounded-full blur-[150px]" />
      <div class="absolute bottom-1/3 right-1/3 w-[400px] h-[400px] bg-accent-200/5 rounded-full blur-[150px]" />
      
      <div class="relative container-wide">
        <div class="max-w-3xl mx-auto text-center">
          <UiBadge variant="accent" class="mb-6">{{ $t('about.badge') }}</UiBadge>
          <h1 class="text-4xl sm:text-5xl lg:text-6xl font-display font-bold tracking-tight text-balance mb-6">
            {{ $t('about.title') }}
            <span class="gradient-text">{{ $t('about.titleHighlight') }}</span>
          </h1>
          <p class="text-xl text-surface-400 max-w-2xl mx-auto">
            {{ $t('about.subtitle') }}
          </p>
        </div>
      </div>
      
      <div class="absolute bottom-0 left-0 right-0 section-divider" />
    </section>

    <!-- Our Story -->
    <section class="section bg-surface-800/30 relative">
      <div class="absolute top-0 left-0 right-0 section-divider" />
      
      <div class="container-tight">
        <div class="max-w-3xl mx-auto">
          <h2 class="text-3xl font-display font-bold text-surface-100 mb-8">
            {{ $t('about.story.title') }}
          </h2>
          <div class="space-y-6 text-lg text-surface-400 leading-relaxed">
            <p>{{ $t('about.story.p1') }}</p>
            <p>{{ $t('about.story.p2') }}</p>
            <p>{{ $t('about.story.p3') }}</p>
          </div>
        </div>
      </div>
      
      <div class="absolute bottom-0 left-0 right-0 section-divider" />
    </section>

    <!-- Mission -->
    <section class="section bg-surface-900 relative">
      <div class="absolute top-0 left-0 right-0 section-divider" />
      
      <div class="container-wide">
        <div class="max-w-4xl mx-auto">
          <UiCard class="p-10 lg:p-14 text-center bg-gradient-to-br from-surface-800 to-surface-800/50 border-surface-600">
            <div class="w-16 h-16 rounded-2xl bg-primary-500/15 flex items-center justify-center mx-auto mb-6">
              <UiIcon name="Target" :size="32" class="text-primary-400" />
            </div>
            <h2 class="text-2xl lg:text-3xl font-display font-bold text-surface-100 mb-4">
              {{ $t('about.mission.title') }}
            </h2>
            <p class="text-lg text-surface-400 max-w-2xl mx-auto">
              {{ $t('about.mission.description') }}
            </p>
          </UiCard>
        </div>
      </div>
      
      <div class="absolute bottom-0 left-0 right-0 section-divider" />
    </section>

    <!-- Values -->
    <section class="section bg-surface-800/30 relative">
      <div class="absolute top-0 left-0 right-0 section-divider" />
      
      <div class="container-wide">
        <h2 class="text-3xl font-display font-bold text-surface-100 text-center mb-16">
          {{ $t('about.values.title') }}
        </h2>
        
        <div class="grid md:grid-cols-3 gap-8">
          <UiCard v-for="value in values" :key="value.titleKey" variant="hover">
            <div 
              class="w-14 h-14 rounded-xl flex items-center justify-center mb-6"
              :class="value.iconBg"
            >
              <UiIcon :name="value.icon" :size="26" :class="value.iconColor" />
            </div>
            <h3 class="text-xl font-display font-semibold text-surface-100 mb-3">
              {{ $t(value.titleKey) }}
            </h3>
            <p class="text-surface-400">
              {{ $t(value.descKey) }}
            </p>
          </UiCard>
        </div>
      </div>
      
      <div class="absolute bottom-0 left-0 right-0 section-divider" />
    </section>

    <!-- CTA -->
    <LandingCTA />
  </div>
</template>

<script setup lang="ts">
useSeoMeta({
  title: 'About Us - ElevoAI',
  description: 'Learn about ElevoAI and our mission to empower businesses with AI-driven marketing tools.',
})

const values = [
  {
    icon: 'Sparkles',
    titleKey: 'about.values.v1.title',
    descKey: 'about.values.v1.description',
    iconBg: 'bg-primary-500/15',
    iconColor: 'text-primary-400',
  },
  {
    icon: 'Lightbulb',
    titleKey: 'about.values.v2.title',
    descKey: 'about.values.v2.description',
    iconBg: 'bg-accent-200/15',
    iconColor: 'text-accent-200',
  },
  {
    icon: 'Shield',
    titleKey: 'about.values.v3.title',
    descKey: 'about.values.v3.description',
    iconBg: 'bg-emerald-500/15',
    iconColor: 'text-emerald-400',
  },
]
</script>
