<template>
  <section class="py-16">
    <div class="container-tight">
      <div class="card p-8">
        <UiBadge variant="accent" class="mb-4">Careers</UiBadge>
        <h1 class="text-3xl font-mono text-surface-900 dark:text-surface-50 mb-3">Careers</h1>
        <p class="text-surface-700 dark:text-surface-400 font-mono">
          We are building the team. Check back soon for open roles.
        </p>
        <div class="mt-6">
          <NuxtLink :to="localePath('/contact')" class="btn-accent btn-md font-mono">Contact us</NuxtLink>
          <NuxtLink :to="localePath('/')" class="btn-secondary btn-md font-mono ml-3">Back to home</NuxtLink>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
useSeoMeta({
  title: 'Careers - ElevoAI',
  description: 'Join the ElevoAI team.',
})

const localePath = useLocalePath()
</script>
