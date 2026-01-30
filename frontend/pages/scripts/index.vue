<template>
  <div class="container-wide py-8 lg:py-12">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
      <div>
        <h1 class="text-xl lg:text-2xl font-mono font-normal text-surface-100">Scripts</h1>
        <p class="text-surface-400 mt-1 text-sm">AI-generated filming and editing scripts</p>
      </div>
      <UiButton variant="primary" @click="showGenerate = true">
        <UiIcon name="FileText" :size="18" />
        <span>Generate Script</span>
      </UiButton>
    </div>

    <!-- Generate Modal -->
    <UiModal v-model="showGenerate" title="Generate Script" size="lg">
      <form @submit.prevent="generateScript" class="space-y-5">
        <!-- Video Concept -->
        <UiInput
          v-model="concept"
          label="Video Concept"
          type="textarea"
          placeholder="e.g., 5 Tips for Better Sleep, Morning Routine Hacks..."
          :rows="3"
          required
        />

        <!-- Platform Selection -->
        <div>
          <label class="label">Target Platform</label>
          <div class="flex flex-wrap gap-2">
              <button
                v-for="platform in availablePlatforms"
                :key="platform.id"
                type="button"
                class="toggle-pill"
                :class="selectedPlatform === platform.id ? 'toggle-pill-active' : 'toggle-pill-inactive'"
                @click="selectedPlatform = platform.id"
              >
              <SharedPlatformIcon :platform="platform.platformId" size="sm" variant="outline" />
              <span>{{ platform.name }}</span>
            </button>
          </div>
        </div>

        <!-- Duration -->
        <UiInput
          v-model.number="duration"
          label="Target Duration (seconds)"
          type="number"
          min="15"
          max="180"
          required
        >
          <template #icon-left>
            <UiIcon name="Clock" :size="18" />
          </template>
        </UiInput>
      </form>

      <template #footer>
        <div class="flex justify-end gap-3">
          <UiButton variant="ghost" @click="showGenerate = false">Cancel</UiButton>
          <UiButton 
            variant="primary" 
            :disabled="generating || !concept || !selectedPlatform"
            :loading="generating"
            @click="generateScript"
          >
            Generate Script
          </UiButton>
        </div>
      </template>
    </UiModal>

    <!-- Scripts List -->
    <div v-if="scriptsLoading" class="grid md:grid-cols-2 gap-4">
      <UiCard v-for="i in 4" :key="i" class="border-l-4 border-l-accent-500">
        <div class="flex items-start gap-4 mb-4">
          <UiSkeleton variant="rounded" width="48px" height="48px" />
          <div class="flex-1 space-y-2">
            <UiSkeleton variant="text" width="80%" />
            <UiSkeleton variant="text" width="40%" />
          </div>
        </div>
        <UiSkeleton variant="text" width="60px" class="mb-4" />
        <div class="flex gap-2">
          <UiSkeleton variant="rounded" width="100px" height="36px" />
          <UiSkeleton variant="rounded" width="40px" height="36px" />
        </div>
      </UiCard>
    </div>
    <SharedEmptyState
      v-else-if="scripts.length === 0"
      icon="FileText"
      title="No scripts yet"
      description="Generate your first AI-powered filming and editing script"
      action-label="Generate Script"
      action-icon="FileText"
      variant="primary"
      @action="showGenerate = true"
    />
    <div v-else class="grid md:grid-cols-2 gap-4">
      <UiCard v-for="script in scripts" :key="script.id" variant="hover" class="border-l-4 border-l-accent-500">
        <div class="flex items-start gap-4 mb-4">
          <div class="w-12 h-12 rounded-xl bg-accent-500/20 flex items-center justify-center flex-shrink-0">
            <UiIcon name="FileText" :size="24" class="text-accent-400" />
          </div>
          <div class="flex-1 min-w-0">
            <h3 class="font-medium text-surface-100 truncate">{{ script.concept }}</h3>
            <div class="flex items-center gap-2 mt-1 text-sm text-surface-400">
              <SharedPlatformIcon :platform="script.platform" size="sm" variant="outline" />
              <span class="capitalize">{{ script.platform }}</span>
              <span class="text-surface-600">•</span>
              <span>{{ script.target_duration }}s</span>
            </div>
          </div>
        </div>
        
        <p class="text-surface-500 text-sm mb-4">
          Created {{ formatDate(script.created_at) }}
        </p>
        
        <div class="flex gap-2">
          <UiButton variant="secondary" size="sm" :to="localePath(`/scripts/${script.id}`)" class="flex-1">
            <UiIcon name="Eye" :size="16" />
            <span>View Script</span>
          </UiButton>
          <UiButton
            variant="ghost"
            size="sm"
            :loading="downloadingId === script.id"
            :disabled="downloadingId === script.id"
            @click="downloadScript(script.id)"
          >
            <UiIcon name="Download" :size="16" />
          </UiButton>
        </div>
      </UiCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
definePageMeta({
  layout: 'app-sidebar',
  middleware: 'auth',
})

const localePath = useLocalePath()
const api = useApi()
const toast = useToast()
const showGenerate = ref(false)
const generating = ref(false)
const scriptsLoading = ref(true)
const concept = ref('')
const selectedPlatform = ref('')
const duration = ref(60)
const downloadingId = ref<string | null>(null)

const availablePlatforms = [
  { id: 'tiktok', platformId: 'tiktok' as const, name: 'TikTok' },
  { id: 'instagram', platformId: 'instagram' as const, name: 'Instagram Reels' },
  { id: 'youtube_shorts', platformId: 'youtube' as const, name: 'YouTube Shorts' },
  { id: 'facebook', platformId: 'facebook' as const, name: 'Facebook Reels' },
]

const scripts = ref<any[]>([])

async function fetchScripts() {
  scriptsLoading.value = true
  try {
    const res = await api.scripts.list()
    scripts.value = (res as { items?: any[] })?.items ?? []
  } catch {
    scripts.value = []
  } finally {
    scriptsLoading.value = false
  }
}

const generateScript = async () => {
  generating.value = true
  try {
    await api.scripts.generate({
      concept: concept.value,
      platform: selectedPlatform.value,
      duration: duration.value,
    })
    concept.value = ''
    selectedPlatform.value = ''
    duration.value = 60
    showGenerate.value = false
    await fetchScripts()
  } catch {
    // toast when available
  } finally {
    generating.value = false
  }
}

onMounted(fetchScripts)

const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

async function downloadScript(id: string, format: 'json' | 'markdown' = 'json') {
  downloadingId.value = id
  try {
    const data = await api.scripts.export(id, format)
    const text = format === 'markdown'
      ? (typeof data === 'string' ? data : JSON.stringify(data, null, 2))
      : JSON.stringify(data, null, 2)
    const blob = new Blob([text], { type: format === 'markdown' ? 'text/markdown' : 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `script_${id.slice(0, 8)}.${format === 'markdown' ? 'md' : 'json'}`
    a.click()
    URL.revokeObjectURL(url)
    toast.success('Export downloaded')
  } catch (e: any) {
    toast.error(e?.data?.detail ?? e?.message ?? 'Export failed')
  } finally {
    downloadingId.value = null
  }
}
</script>
