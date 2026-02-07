<template>
  <div>
    <!-- Hero Section -->
    <section class="relative pt-16 pb-8 lg:pt-20 lg:pb-10">
      <!-- Background -->
      
      <div class="relative container-wide">
        <div class="max-w-2xl mx-auto text-center">
          <UiBadge variant="accent" class="mb-6">{{ $t('about.badge') }}</UiBadge>
          <h1 class="text-3xl sm:text-4xl lg:text-5xl font-mono tracking-tight text-balance mb-4">
            {{ $t('about.title') }}
            <span class="gradient-text">{{ $t('about.titleHighlight') }}</span>
          </h1>
          <p class="text-lg text-surface-600 dark:text-surface-400 leading-relaxed font-mono">
            {{ $t('about.subtitle') }}
          </p>
        </div>
      </div>
    </section>

    <!-- Our Story -->
    <section class="py-6 md:py-8">
      <div class="container-tight">
        <!-- Divider -->
        <div class="section-divider mb-6" />
        
        <div class="max-w-2xl mx-auto">
          <h2 class="text-2xl font-mono text-surface-900 dark:text-surface-50 mb-6">
            {{ $t('about.story.title') }}
          </h2>
          <div class="space-y-4 text-surface-700 dark:text-surface-400 leading-relaxed font-mono">
            <p>{{ $t('about.story.p1') }}</p>
            <p>{{ $t('about.story.p2') }}</p>
            <p>{{ $t('about.story.p3') }}</p>
          </div>
        </div>
        
        <!-- Divider -->
        <div class="section-divider mt-6" />
      </div>
    </section>

    <!-- Mission -->
    <section class="py-6 md:py-8">
      <div class="container-wide">
        <div class="max-w-3xl mx-auto">
          <div class="card p-8 lg:p-10 text-center">
            <div class="w-14 h-14 rounded-xl bg-primary-500/15 flex items-center justify-center mx-auto mb-6">
              <UiIcon name="Target" :size="28" class="text-primary-400" />
            </div>
            <h2 class="text-2xl font-mono text-surface-900 dark:text-surface-50 mb-4">
              {{ $t('about.mission.title') }}
            </h2>
            <p class="text-surface-700 dark:text-surface-400 max-w-xl mx-auto leading-relaxed font-mono">
              {{ $t('about.mission.description') }}
            </p>
          </div>
        </div>
        
        <!-- Divider -->
        <div class="section-divider mt-6" />
      </div>
    </section>

    <!-- Values -->
    <section class="py-6 md:py-8">
      <div class="container-wide">
        <h2 class="text-2xl font-mono text-surface-900 dark:text-surface-50 text-center mb-10">
          {{ $t('about.values.title') }}
        </h2>
        
        <div class="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto">
          <div v-for="value in values" :key="value.titleKey" class="card">
            <div 
              class="w-12 h-12 rounded-lg flex items-center justify-center mb-5"
              :class="value.iconBg"
            >
              <UiIcon :name="value.icon" :size="24" :class="value.iconColor" />
            </div>
            <h3 class="text-lg font-mono text-surface-900 dark:text-surface-50 mb-2">
              {{ $t(value.titleKey) }}
            </h3>
            <p class="text-surface-700 dark:text-surface-400 text-sm leading-relaxed font-mono">
              {{ $t(value.descKey) }}
            </p>
          </div>
        </div>
        
        <!-- Divider -->
        <div class="section-divider mt-6" />
      </div>
    </section>

    <!-- Image placeholder -->
    <section class="py-6 md:py-8">
      <div class="container-wide">
        <div class="image-placeholder aspect-[2/1] max-w-4xl mx-auto p-8">
          <div class="flex flex-col items-center gap-3">
            <UiIcon name="Users" :size="48" class="text-surface-600 dark:text-surface-500" />
            <span class="text-sm text-surface-600 dark:text-surface-500 font-mono">Team Photo Placeholder</span>
          </div>
        </div>
      </div>
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
