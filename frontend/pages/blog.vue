<template>
  <section class="py-16">
    <div class="container-tight">
      <div class="card p-8">
        <UiBadge variant="accent" class="mb-4">Blog</UiBadge>
        <h1 class="text-3xl font-mono text-surface-900 dark:text-surface-50 mb-3">Blog</h1>
        <p class="text-surface-700 dark:text-surface-400 font-mono">
          Stories, product updates, and tips are coming soon.
        </p>
        <div class="mt-6">
          <NuxtLink :to="localePath('/')" class="btn-secondary btn-md font-mono">Back to home</NuxtLink>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
useSeoMeta({
  title: 'Blog - Elevo',
  description: 'Product stories and updates from Elevo.',
})

const localePath = useLocalePath()
</script>
