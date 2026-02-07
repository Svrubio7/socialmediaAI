<template>
  <section class="py-16">
    <div class="container-tight">
      <div class="card p-8">
        <UiBadge variant="accent" class="mb-4">Changelog</UiBadge>
        <h1 class="text-3xl font-mono text-surface-900 dark:text-surface-50 mb-3">Changelog</h1>
        <p class="text-surface-700 dark:text-surface-400 font-mono">
          No public releases yet. Check back soon for product updates and release notes.
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
  title: 'Changelog - ElevoAI',
  description: 'Product updates and release notes for ElevoAI.',
})

const localePath = useLocalePath()
</script>
