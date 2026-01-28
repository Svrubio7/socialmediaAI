<template>
  <section class="section relative">
    <div class="container-wide">
      <div class="relative overflow-hidden rounded-3xl">
        <!-- Background -->
        <div class="absolute inset-0 bg-gradient-to-br from-surface-800 via-surface-800 to-primary-900/30" />
        <div class="absolute inset-0 bg-[linear-gradient(rgba(105,117,101,0.05)_1px,transparent_1px),linear-gradient(90deg,rgba(105,117,101,0.05)_1px,transparent_1px)] bg-[size:32px_32px]" />
        
        <!-- Glow effects -->
        <div class="absolute top-0 left-1/4 w-64 h-64 bg-primary-500/15 rounded-full blur-[100px]" />
        <div class="absolute bottom-0 right-1/4 w-64 h-64 bg-accent-200/10 rounded-full blur-[100px]" />
        
        <!-- Content -->
        <div class="relative px-6 py-20 sm:px-12 lg:px-20 lg:py-28 text-center">
          <h2 class="text-3xl sm:text-4xl lg:text-5xl font-display font-bold text-balance mb-6">
            {{ $t('cta.title') }}
            <span class="gradient-text">{{ $t('cta.titleHighlight') }}</span>
          </h2>
          <p class="text-lg text-surface-300 max-w-2xl mx-auto mb-10">
            {{ $t('cta.subtitle') }}
          </p>
          
          <div class="flex flex-col sm:flex-row items-center justify-center gap-4">
            <NuxtLink :to="localePath('/auth/register')" class="btn-accent btn-lg">
              <span>{{ $t('cta.button1') }}</span>
              <UiIcon name="ArrowRight" :size="18" />
            </NuxtLink>
            <NuxtLink :to="localePath('/contact')" class="btn-ghost btn-lg text-surface-200 hover:text-white">
              <UiIcon name="MessageCircle" :size="18" />
              <span>{{ $t('cta.button2') }}</span>
            </NuxtLink>
          </div>
          
          <!-- Trust badges -->
          <div class="mt-12 flex flex-wrap items-center justify-center gap-6 text-sm text-surface-400">
            <div class="flex items-center gap-2">
              <UiIcon name="Shield" :size="16" class="text-emerald-400" />
              <span>{{ $t('cta.badge1') }}</span>
            </div>
            <div class="flex items-center gap-2">
              <UiIcon name="Zap" :size="16" class="text-amber-400" />
              <span>{{ $t('cta.badge2') }}</span>
            </div>
            <div class="flex items-center gap-2">
              <UiIcon name="Headphones" :size="16" class="text-primary-400" />
              <span>{{ $t('cta.badge3') }}</span>
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
