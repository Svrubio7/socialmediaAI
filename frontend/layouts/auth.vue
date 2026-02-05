<template>
  <div class="min-h-screen flex flex-col items-center justify-center px-4 py-12 relative overflow-hidden">
    <!-- Background -->
    <div class="absolute inset-0 bg-surface-50 dark:bg-surface-950" />
    <div class="absolute inset-0 bg-gradient-radial-top" />
    <div class="absolute top-0 left-1/4 w-96 h-96 bg-primary-500/10 rounded-full blur-[120px] animate-pulse-slow" />
    <div class="absolute bottom-0 right-1/4 w-96 h-96 bg-accent-500/10 rounded-full blur-[120px] animate-pulse-slow animate-delay-1000" />
    
    <!-- Grid pattern -->
    <div
      class="absolute inset-0"
      style="background-image: linear-gradient(to right, var(--grid-line) 1px, transparent 1px), linear-gradient(to bottom, var(--grid-line) 1px, transparent 1px); background-size: var(--grid-size) var(--grid-size);"
    />

    <!-- Logo -->
    <Logo size="lg" class="mb-8 relative z-10" />

    <!-- Content -->
    <div class="w-full max-w-md relative z-10">
      <slot />
    </div>

    <!-- Back to home -->
    <NuxtLink
      to="/"
      class="mt-8 flex items-center gap-2 text-surface-500 hover:text-surface-300 text-sm transition-colors relative z-10"
    >
      <UiIcon name="ArrowLeft" :size="16" />
      <span>Back to home</span>
    </NuxtLink>
  </div>
</template>
