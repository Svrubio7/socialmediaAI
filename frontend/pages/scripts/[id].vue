<template>
  <div class="container-wide py-8 lg:py-10">
    <NuxtLink
      :to="localePath('/scripts')"
      class="inline-flex items-center gap-2 text-sm text-surface-400 hover:text-surface-200 mb-6 transition-colors"
    >
      <UiIcon name="ArrowLeft" :size="16" />
      Back to Scripts
    </NuxtLink>

    <div v-if="loading" class="py-12 flex justify-center">
      <div class="flex flex-col items-center gap-3">
        <Skeleton variant="rounded" width="64px" height="48px" />
        <Skeleton variant="text" width="200px" />
      </div>
    </div>
    <div v-else-if="error" class="text-red-400">{{ error }}</div>
    <template v-else-if="script">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
        <h1 class="text-3xl lg:text-4xl font-mono font-bold text-surface-100 truncate">{{ script.concept }}</h1>
        <div class="flex gap-2">
          <Button variant="secondary" size="sm" :disabled="exporting" @click="exportAs('json')">
            <UiIcon name="Download" :size="16" />
            Export JSON
          </Button>
          <Button variant="ghost" size="sm" :disabled="exporting" @click="exportAs('markdown')">
            <UiIcon name="FileText" :size="16" />
            Export Markdown
          </Button>
        </div>
      </div>

      <Card class="border-l-4 border-l-accent-500 mb-6">
        <div class="grid sm:grid-cols-2 gap-4 mb-6">
          <div>
            <p class="label">Platform</p>
            <p class="text-surface-100 font-medium capitalize flex items-center gap-2">
              <PlatformIcon :platform="script.platform" size="sm" variant="outline" />
              {{ script.platform }}
            </p>
          </div>
          <div>
            <p class="label">Target duration</p>
            <p class="text-surface-100 font-medium">{{ script.target_duration }}s</p>
          </div>
          <div>
            <p class="label">Created</p>
            <p class="text-surface-100 font-medium">{{ formatDate(script.created_at) }}</p>
          </div>
        </div>

        <div v-if="script.script_data?.segments?.length" class="border-t border-surface-800 pt-6 space-y-4">
          <h2 class="text-xl font-mono font-semibold text-surface-100 mb-4">Script segments</h2>
          <div
            v-for="(seg, i) in script.script_data.segments"
            :key="i"
            class="p-4 rounded-xl bg-surface-800/50 border-l-4 border-accent-500/50"
          >
            <p class="text-surface-500 text-sm">{{ seg.start_time }}s – {{ seg.end_time }}s · {{ seg.type || 'content' }}</p>
            <p class="text-surface-200 mt-1">{{ seg.content || seg.instructions || '—' }}</p>
            <p v-if="seg.visual" class="text-surface-400 text-sm mt-1">Visual: {{ seg.visual }}</p>
            <p v-if="seg.audio" class="text-surface-400 text-sm mt-0.5">Audio: {{ seg.audio }}</p>
          </div>
        </div>
        <p v-else class="text-surface-500">No script content.</p>
      </Card>
    </template>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'app',
  middleware: 'auth',
})

const route = useRoute()
const localePath = useLocalePath()
const api = useApi()

const loading = ref(true)
const error = ref('')
const exporting = ref(false)
const script = ref<any>(null)

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

async function fetchScript() {
  loading.value = true
  error.value = ''
  try {
    script.value = await api.scripts.get(route.params.id as string)
  } catch {
    error.value = 'Script not found'
    script.value = null
  } finally {
    loading.value = false
  }
}

async function exportAs(format: 'markdown' | 'json') {
  exporting.value = true
  try {
    const data = await api.scripts.export(route.params.id as string, format)
    const text = format === 'markdown'
      ? (typeof data === 'string' ? data : JSON.stringify(data, null, 2))
      : JSON.stringify(data, null, 2)
    const blob = new Blob([text], { type: format === 'markdown' ? 'text/markdown' : 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `script_${(route.params.id as string).slice(0, 8)}.${format === 'markdown' ? 'md' : 'json'}`
    a.click()
    URL.revokeObjectURL(url)
  } catch {
    // use toast when available
  } finally {
    exporting.value = false
  }
}

onMounted(fetchScript)
</script>
