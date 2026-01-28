<template>
  <div class="container-wide py-8 lg:py-10">
    <NuxtLink
      :to="localePath('/strategies')"
      class="inline-flex items-center gap-2 text-sm text-surface-400 hover:text-surface-200 mb-6 transition-colors"
    >
      <UiIcon name="ArrowLeft" :size="16" />
      Back to Strategies
    </NuxtLink>

    <div v-if="loading" class="py-12 flex justify-center">
      <div class="flex flex-col items-center gap-3">
        <Skeleton variant="rounded" width="64px" height="48px" />
        <Skeleton variant="text" width="200px" />
      </div>
    </div>
    <div v-else-if="error" class="text-red-400">{{ error }}</div>
    <template v-else-if="strategy">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
        <h1 class="text-3xl lg:text-4xl font-mono font-bold text-surface-100">Strategy</h1>
        <div class="flex gap-2">
          <Button variant="secondary" size="sm" :disabled="exporting" @click="exportAs('markdown')">
            <UiIcon name="FileText" :size="16" />
            Export as Markdown
          </Button>
          <Button variant="ghost" size="sm" :disabled="exporting" @click="exportAs('json')">
            <UiIcon name="Download" :size="16" />
            Export as JSON
          </Button>
        </div>
      </div>

      <Card class="border-l-4 border-l-accent-500 mb-6">
        <div class="grid sm:grid-cols-2 gap-4 mb-6">
          <div>
            <p class="label">Platforms</p>
            <p class="text-surface-100 font-medium">{{ (strategy.platforms || []).join(', ') || '—' }}</p>
          </div>
          <div>
            <p class="label">Goals</p>
            <p class="text-surface-100 font-medium">{{ (strategy.goals || []).join(', ') || '—' }}</p>
          </div>
          <div>
            <p class="label">Niche</p>
            <p class="text-surface-100 font-medium">{{ strategy.niche || '—' }}</p>
          </div>
          <div>
            <p class="label">Created</p>
            <p class="text-surface-100 font-medium">{{ formatDate(strategy.created_at) }}</p>
          </div>
        </div>

        <div v-if="strategy.strategy_data && Object.keys(strategy.strategy_data).length" class="space-y-6">
          <div v-if="strategy.strategy_data.recommendations?.length" class="border-t border-surface-800 pt-6">
            <h2 class="text-xl font-mono font-semibold text-surface-100 mb-4">Recommendations</h2>
            <div class="space-y-4">
              <div
                v-for="(rec, i) in strategy.strategy_data.recommendations"
                :key="i"
                class="p-4 rounded-xl bg-surface-800/50 border-l-4 border-primary-500/50"
              >
                <h3 class="font-medium text-surface-100">{{ rec.category || 'General' }}</h3>
                <p class="text-surface-300 mt-1">{{ rec.recommendation }}</p>
                <p v-if="rec.rationale" class="text-surface-500 text-sm mt-2 italic">{{ rec.rationale }}</p>
              </div>
            </div>
          </div>
          <div v-if="strategy.strategy_data.posting_schedule" class="border-t border-surface-800 pt-6">
            <h2 class="text-xl font-mono font-semibold text-surface-100 mb-4">Posting Schedule</h2>
            <p class="text-surface-300">{{ strategy.strategy_data.posting_schedule.frequency || 'Daily' }}</p>
            <p v-if="strategy.strategy_data.posting_schedule.optimal_times?.length" class="text-surface-400 text-sm mt-1">
              Optimal times: {{ strategy.strategy_data.posting_schedule.optimal_times.join(', ') }}
            </p>
          </div>
          <div v-if="strategy.strategy_data.hashtag_strategy" class="border-t border-surface-800 pt-6">
            <h2 class="text-xl font-mono font-semibold text-surface-100 mb-4">Hashtag Strategy</h2>
            <p v-if="strategy.strategy_data.hashtag_strategy.primary_hashtags?.length" class="text-surface-300">
              Primary: {{ strategy.strategy_data.hashtag_strategy.primary_hashtags.join(' ') }}
            </p>
            <p v-if="strategy.strategy_data.hashtag_strategy.secondary_hashtags?.length" class="text-surface-400 text-sm mt-1">
              Secondary: {{ strategy.strategy_data.hashtag_strategy.secondary_hashtags.join(' ') }}
            </p>
          </div>
          <div v-if="strategy.strategy_data.content_themes?.length" class="border-t border-surface-800 pt-6">
            <h2 class="text-xl font-mono font-semibold text-surface-100 mb-4">Content Themes</h2>
            <ul class="list-disc list-inside text-surface-300 space-y-1">
              <li v-for="(theme, i) in strategy.strategy_data.content_themes" :key="i">{{ theme }}</li>
            </ul>
          </div>
        </div>
        <p v-else class="text-surface-500">No strategy content.</p>
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
const strategy = ref<any>(null)

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

async function fetchStrategy() {
  loading.value = true
  error.value = ''
  try {
    strategy.value = await api.strategies.get(route.params.id as string)
  } catch {
    error.value = 'Strategy not found'
    strategy.value = null
  } finally {
    loading.value = false
  }
}

async function exportAs(format: 'markdown' | 'json') {
  exporting.value = true
  try {
    const data = await api.strategies.export(route.params.id as string, format)
    const text = format === 'markdown'
      ? (typeof data === 'string' ? data : JSON.stringify(data, null, 2))
      : JSON.stringify(data, null, 2)
    const blob = new Blob([text], { type: format === 'markdown' ? 'text/markdown' : 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `strategy_${(route.params.id as string).slice(0, 8)}.${format === 'markdown' ? 'md' : 'json'}`
    a.click()
    URL.revokeObjectURL(url)
  } catch {
    // use toast when available
  } finally {
    exporting.value = false
  }
}

onMounted(fetchStrategy)
</script>
