<template>
  <section class="py-16">
    <div class="container-tight">
      <div class="card p-8">
        <UiBadge variant="accent" class="mb-4">Documentation</UiBadge>
        <h1 class="text-3xl font-mono text-surface-900 dark:text-surface-50 mb-3">Documentation</h1>
        <p class="text-surface-700 dark:text-surface-400 font-mono">
          We are polishing the docs. Use the API docs for now, and check back for full guides.
        </p>
        <div class="mt-6 flex flex-wrap gap-3">
          <a
            v-if="apiBase"
            :href="`${apiBase}/docs`"
            target="_blank"
            rel="noopener"
            class="btn-accent btn-md font-mono"
          >
            API Docs
          </a>
          <a
            v-if="apiBase"
            :href="`${apiBase}/redoc`"
            target="_blank"
            rel="noopener"
            class="btn-secondary btn-md font-mono"
          >
            ReDoc
          </a>
          <NuxtLink :to="localePath('/')" class="btn-secondary btn-md font-mono">Back to home</NuxtLink>
        </div>
        <p v-if="!apiBase" class="mt-4 text-sm text-surface-600 dark:text-surface-500 font-mono">
          Set `NUXT_PUBLIC_API_URL` to enable API links.
        </p>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
useSeoMeta({
  title: 'Documentation - Elevo',
  description: 'Elevo documentation and developer resources.',
})

const localePath = useLocalePath()
const config = useRuntimeConfig()
const apiBase = computed(() => (config.public.apiUrl || '').replace(/\/api\/v1\/?$/, ''))
</script>
