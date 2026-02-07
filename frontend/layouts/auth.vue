<template>
  <div class="min-h-screen flex flex-col items-center justify-center px-4 py-12 relative overflow-hidden">
    <!-- Background -->
    <div class="absolute inset-0 bg-gradient-radial-top opacity-50" />
    
    <!-- Grid pattern -->
    <div
      class="absolute inset-0"
      style="background-image: linear-gradient(to right, var(--grid-line) 1px, transparent 1px), linear-gradient(to bottom, var(--grid-line) 1px, transparent 1px); background-size: var(--grid-size) var(--grid-size);"
    />

    <!-- Logo -->
    <UiLogo size="lg" class="mb-8 relative z-10" />

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
