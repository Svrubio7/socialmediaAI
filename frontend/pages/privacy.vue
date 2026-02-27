<template>
  <section class="py-16">
    <div class="container-tight">
      <div class="card p-8">
        <UiBadge variant="accent" class="mb-4">Legal</UiBadge>
        <h1 class="text-3xl font-mono text-surface-900 dark:text-surface-50 mb-3">Privacy Policy</h1>
        <p class="text-surface-700 dark:text-surface-400 font-mono">
          The full privacy policy is being finalized. For now, contact support if you need details
          about data handling, retention, or deletion.
        </p>
        <div class="mt-6">
          <NuxtLink :to="localePath('/contact')" class="btn-accent btn-md font-mono">Contact support</NuxtLink>
          <NuxtLink :to="localePath('/')" class="btn-secondary btn-md font-mono ml-3">Back to home</NuxtLink>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
useSeoMeta({
  title: 'Privacy Policy - Elevo',
  description: 'Elevo privacy policy and data handling information.',
})

const localePath = useLocalePath()
</script>
