<template>
  <div class="min-h-screen flex flex-col relative overflow-hidden">
    <div class="absolute inset-0 bg-surface-50 dark:bg-surface-950" />
    <div class="absolute inset-0 bg-gradient-radial-top opacity-60 dark:opacity-100" />
    <div class="absolute top-0 left-1/4 w-96 h-96 bg-primary-500/10 rounded-full blur-[140px] animate-pulse-slow" />
    <div class="absolute bottom-0 right-1/4 w-96 h-96 bg-accent-500/10 rounded-full blur-[140px] animate-pulse-slow animate-delay-1000" />
    <div
      class="absolute inset-0"
      style="background-image: linear-gradient(to right, var(--grid-line) 1px, transparent 1px), linear-gradient(to bottom, var(--grid-line) 1px, transparent 1px); background-size: var(--grid-size) var(--grid-size);"
    />

    <!-- Header -->
    <LayoutHeader class="relative z-10" />

    <!-- Main content -->
    <main class="flex-1 relative z-10">
      <slot />
    </main>

    <!-- Footer -->
    <LayoutFooter class="relative z-10" />
  </div>
</template>
