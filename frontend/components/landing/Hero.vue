<template>
  <section class="relative overflow-hidden min-h-screen flex items-center">
    <!-- Background Effects -->
    <div class="absolute inset-0 bg-surface-900" />
    <div class="absolute inset-0 bg-gradient-radial-top" />
    <div class="absolute top-1/4 left-1/4 w-[600px] h-[600px] bg-primary-500/8 rounded-full blur-[150px] animate-pulse-slow" />
    <div class="absolute bottom-1/4 right-1/4 w-[500px] h-[500px] bg-accent-200/5 rounded-full blur-[150px] animate-pulse-slow animate-delay-1000" />
    
    <!-- Grid pattern overlay -->
    <div class="absolute inset-0 bg-[linear-gradient(rgba(105,117,101,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(105,117,101,0.03)_1px,transparent_1px)] bg-[size:64px_64px]" />

    <div class="relative container-wide pt-32 pb-24 lg:pt-40 lg:pb-32">
      <div class="max-w-4xl mx-auto text-center">
        <!-- Badge -->
        <div class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-surface-800/60 border border-surface-700/50 mb-8 animate-fade-in-up animate-fill-both">
          <span class="relative flex h-2 w-2">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary-400 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-2 w-2 bg-primary-500"></span>
          </span>
          <span class="text-sm text-surface-300">{{ $t('hero.badge') }}</span>
        </div>

        <!-- Headline -->
        <h1 class="text-4xl sm:text-5xl lg:text-6xl xl:text-7xl font-display font-bold tracking-tight text-balance animate-fade-in-up animate-fill-both animate-delay-100">
          <span class="text-surface-100">{{ $t('hero.title1') }}</span>
          <br class="hidden sm:block" />
          <span class="gradient-text">{{ $t('hero.title2') }}</span>
          <br class="hidden sm:block" />
          <span class="text-surface-100">{{ $t('hero.title3') }}</span>
        </h1>
        
        <!-- Subheadline -->
        <p class="mt-6 lg:mt-8 text-lg lg:text-xl text-surface-400 max-w-2xl mx-auto text-balance animate-fade-in-up animate-fill-both animate-delay-200">
          {{ $t('hero.subtitle') }}
        </p>

        <!-- CTA Buttons -->
        <div class="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4 animate-fade-in-up animate-fill-both animate-delay-300">
          <NuxtLink :to="localePath('/auth/register')" class="btn-accent btn-lg min-w-[180px] group">
            <span>{{ $t('hero.cta1') }}</span>
            <Icon name="ArrowRight" :size="18" class="transition-transform group-hover:translate-x-1" />
          </NuxtLink>
          <NuxtLink :to="localePath('/#how-it-works')" class="btn-secondary btn-lg min-w-[180px]">
            <Icon name="Play" :size="18" />
            <span>{{ $t('hero.cta2') }}</span>
          </NuxtLink>
        </div>
      </div>
    </div>
    
    <!-- Bottom section divider -->
    <div class="absolute bottom-0 left-0 right-0 section-divider" />
  </section>
</template>

<script setup lang="ts">
const localePath = useLocalePath()
</script>
