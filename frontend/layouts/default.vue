<template>
  <div class="min-h-screen flex flex-col bg-surface-950">
    <!-- Header -->
    <LayoutHeader />

    <!-- Main content -->
    <main class="flex-1">
      <slot />
    </main>

    <!-- Footer -->
    <LayoutFooter />
  </div>
</template>
