<template>
  <section class="py-16">
    <div class="container-tight">
      <div class="card p-8">
        <UiBadge variant="accent" class="mb-4">API</UiBadge>
        <h1 class="text-3xl font-mono text-surface-900 dark:text-surface-50 mb-3">API Reference</h1>
        <p class="text-surface-700 dark:text-surface-400 font-mono">
          Explore the REST API schema, endpoints, and examples.
        </p>
        <div class="mt-6 flex flex-wrap gap-3">
          <a
            v-if="apiBase"
            :href="`${apiBase}/docs`"
            target="_blank"
            rel="noopener"
            class="btn-accent btn-md font-mono"
          >
            Swagger UI
          </a>
          <a
            v-if="apiBase"
            :href="`${apiBase}/openapi.json`"
            target="_blank"
            rel="noopener"
            class="btn-secondary btn-md font-mono"
          >
            OpenAPI JSON
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
  title: 'API Reference - ElevoAI',
  description: 'ElevoAI REST API documentation and schema.',
})

const localePath = useLocalePath()
const config = useRuntimeConfig()
const apiBase = computed(() => (config.public.apiUrl || '').replace(/\/api\/v1\/?$/, ''))
</script>
