<template>
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
</template>

<style>
/* Page transitions */
.page-enter-active,
.page-leave-active {
  transition: all 0.2s ease-out;
}

.page-enter-from {
  opacity: 0;
  transform: translateY(8px);
}

.page-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

/* Layout transitions */
.layout-enter-active,
.layout-leave-active {
  transition: all 0.3s ease-out;
}

.layout-enter-from,
.layout-leave-to {
  opacity: 0;
}
</style>
