<template>
  <div class="min-h-screen flex flex-col relative overflow-hidden">
    <div class="absolute inset-0 bg-gradient-radial-top opacity-50" />
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
