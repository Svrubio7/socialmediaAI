<template>
  <section class="relative py-20 lg:py-24 bg-surface-800/50">
    <div class="container-wide">
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-8 lg:gap-12">
        <div 
          v-for="(stat, index) in stats" 
          :key="stat.labelKey"
          class="text-center"
        >
          <div class="text-3xl lg:text-4xl xl:text-5xl font-display font-bold gradient-text mb-2">
            {{ stat.value }}
          </div>
          <div class="text-sm lg:text-base text-surface-400">
            {{ $t(stat.labelKey) }}
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
const stats = [
  { value: '10x', labelKey: 'stats.faster' },
  { value: '4+', labelKey: 'stats.platforms' },
  { value: '90%', labelKey: 'stats.timeSaved' },
  { value: '24/7', labelKey: 'stats.analysis' },
]
</script>
