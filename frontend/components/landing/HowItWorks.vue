<template>
  <section id="how-it-works" class="section bg-surface-800/30">
    <!-- Top divider -->
    <div class="absolute top-0 left-0 right-0 section-divider" />
    
    <div class="container-wide">
      <!-- Section Header -->
      <div class="text-center max-w-3xl mx-auto mb-20">
        <UiBadge variant="accent" class="mb-4">{{ $t('howItWorks.badge') }}</UiBadge>
        <h2 class="text-3xl sm:text-4xl lg:text-5xl font-display font-bold text-balance mb-6">
          {{ $t('howItWorks.title') }}
          <span class="gradient-text">{{ $t('howItWorks.titleHighlight') }}</span>
        </h2>
        <p class="text-lg text-surface-400">
          {{ $t('howItWorks.subtitle') }}
        </p>
      </div>

      <!-- Steps -->
      <div class="grid lg:grid-cols-3 gap-8 lg:gap-6 max-w-6xl mx-auto">
        <div 
          v-for="(step, index) in steps" 
          :key="step.titleKey"
          class="relative text-center lg:text-left"
        >
          <!-- Connector line (hidden on mobile, visible on desktop) -->
          <div 
            v-if="index < steps.length - 1"
            class="hidden lg:block absolute top-16 left-[calc(50%+60px)] w-[calc(100%-120px)] h-px bg-gradient-to-r from-surface-600 via-surface-500 to-surface-600 z-0"
          />
          
          <div class="relative z-10 flex flex-col items-center lg:items-start">
            <!-- Step number -->
            <div class="w-28 h-28 rounded-2xl bg-gradient-to-br from-surface-700 to-surface-800 border border-surface-600 flex items-center justify-center mb-8 mx-auto lg:mx-0">
              <span class="text-4xl font-display font-bold gradient-text">{{ String(index + 1).padStart(2, '0') }}</span>
            </div>
            
            <!-- Content -->
            <h3 class="text-xl font-display font-semibold text-surface-100 mb-3">
              {{ $t(step.titleKey) }}
            </h3>
            <p class="text-surface-400 leading-relaxed mb-6 max-w-sm mx-auto lg:mx-0">
              {{ $t(step.descKey) }}
            </p>
            
            <!-- Features list -->
            <ul class="space-y-2 text-left">
              <li 
                v-for="feature in step.features" 
                :key="feature"
                class="flex items-center gap-2 text-sm text-surface-400"
              >
                <UiIcon name="Check" :size="16" class="text-primary-400 flex-shrink-0" />
                <span>{{ $t(feature) }}</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Bottom divider -->
    <div class="absolute bottom-0 left-0 right-0 section-divider" />
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
</script>
