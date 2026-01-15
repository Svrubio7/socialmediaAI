<template>
  <div class="min-h-screen flex flex-col items-center justify-center px-4 py-12 relative overflow-hidden">
    <!-- Background gradient -->
    <div class="absolute inset-0 bg-gradient-to-br from-surface-950 via-surface-900 to-surface-950" />
    <div class="absolute top-0 left-1/4 w-96 h-96 bg-primary-500/10 rounded-full blur-3xl" />
    <div class="absolute bottom-0 right-1/4 w-96 h-96 bg-accent-500/10 rounded-full blur-3xl" />

    <!-- Logo -->
    <NuxtLink to="/" class="flex items-center space-x-2 mb-8 relative z-10">
      <div class="w-10 h-10 bg-gradient-to-br from-primary-500 to-accent-500 rounded-lg flex items-center justify-center">
        <span class="text-white font-bold text-xl">S</span>
      </div>
      <span class="font-display font-bold text-2xl gradient-text">SocialAI</span>
    </NuxtLink>

    <!-- Content -->
    <div class="w-full max-w-md relative z-10">
      <slot />
    </div>

    <!-- Back to home -->
    <NuxtLink
      to="/"
      class="mt-8 text-surface-500 hover:text-surface-300 text-sm relative z-10"
    >
      ← Back to home
    </NuxtLink>
  </div>
</template>
