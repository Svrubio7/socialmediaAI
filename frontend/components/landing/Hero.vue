<template>
  <section class="relative min-h-[75vh] flex items-center justify-center overflow-hidden bg-transparent">
    <!-- Content -->
    <div class="relative container-wide py-16 lg:py-20">
      <div class="max-w-4xl mx-auto text-center">
        <!-- Top badge with typewriter -->
        <div 
          class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-surface-200 border border-surface-300 dark:bg-surface-900 dark:border-surface-800 mb-8 opacity-0 animate-fade-in-down animate-fill-both"
          style="animation-delay: 0.3s"
        >
          <span class="relative flex h-2 w-2">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary-400 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-2 w-2 bg-primary-500"></span>
          </span>
          <UiTypewriterText 
            :text="$t('hero.badge')" 
            :speed="30" 
            :delay="800"
            class="text-sm text-surface-700 font-mono dark:text-surface-300"
          />
        </div>

        <!-- Main headline - translated -->
        <h1 class="text-4xl sm:text-5xl lg:text-6xl font-mono tracking-tight text-balance mb-6">
          <span class="text-surface-900 dark:text-surface-50">{{ $t('hero.title1') }}</span>
          <br />
          <span class="text-surface-900 dark:text-surface-50">{{ $t('hero.title2') }}</span>
          <br />
          <span class="gradient-text">{{ $t('hero.title3') }}</span>
        </h1>
        
        <!-- Subheadline with reveal animation -->
        <p 
          class="text-lg lg:text-xl text-surface-600 max-w-2xl mx-auto mb-10 leading-relaxed font-mono opacity-0 animate-fade-in-up animate-fill-both dark:text-surface-400"
          style="animation-delay: 0.8s"
        >
          {{ $t('hero.subtitle') }}
        </p>

        <!-- CTA Buttons with staggered animation -->
        <div 
          class="flex flex-col sm:flex-row items-center justify-center gap-4 mb-12"
        >
          <NuxtLink 
            :to="localePath('/auth/register')" 
            class="btn-accent btn-lg group font-mono opacity-0 animate-fade-in-up animate-fill-both"
            style="animation-delay: 1s"
          >
            <span>{{ $t('hero.cta1') }}</span>
            <UiIcon name="ArrowRight" :size="18" class="transition-transform group-hover:translate-x-1" />
          </NuxtLink>
          <NuxtLink 
            :to="localePath('/#how-it-works')" 
            class="btn-secondary btn-lg font-mono opacity-0 animate-fade-in-up animate-fill-both"
            style="animation-delay: 1.2s"
          >
            <UiIcon name="Play" :size="18" />
            <span>{{ $t('hero.cta2') }}</span>
          </NuxtLink>
        </div>

        <!-- Trust line with typewriter -->
        <div 
          class="opacity-0 animate-fade-in animate-fill-both"
          style="animation-delay: 1.5s"
        >
          <p class="text-sm text-surface-500 font-mono dark:text-surface-500">
            <UiTypewriterText 
              :text="$t('hero.trustLine') || 'Free to start. No credit card required.'" 
              :speed="25" 
              :delay="2000"
              :show-cursor="true"
            />
          </p>
        </div>

        <!-- Image placeholder with animation -->
        <div 
          class="mt-16 opacity-0 animate-fade-in-up animate-fill-both"
          style="animation-delay: 1.8s"
        >
          <div class="image-placeholder aspect-video max-w-3xl mx-auto p-8 hover:border-surface-600 transition-colors duration-300 bg-surface-100 border-surface-200 dark:bg-surface-800 dark:border-surface-700 dark:hover:border-surface-600">
            <div class="flex flex-col items-center gap-3 text-surface-600 dark:text-surface-500">
              <UiIcon name="Image" :size="48" class="text-surface-600 dark:text-surface-500" />
              <span class="text-sm font-mono">Dashboard Preview</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
const localePath = useLocalePath()
</script>
