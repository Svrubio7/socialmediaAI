<template>
  <div class="container-wide py-8 lg:py-12">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
      <div>
        <h1 class="text-3xl lg:text-4xl font-mono font-bold text-surface-100">Scripts</h1>
        <p class="text-surface-400 mt-2">AI-generated filming and editing scripts</p>
      </div>
      <Button variant="primary" @click="showGenerate = true">
        <Icon name="FileText" :size="18" />
        <span>Generate Script</span>
      </Button>
    </div>

    <!-- Generate Modal -->
    <Modal v-model="showGenerate" title="Generate Script" size="lg">
      <form @submit.prevent="generateScript" class="space-y-5">
        <!-- Video Concept -->
        <Input
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
              class="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200"
              :class="selectedPlatform === platform.id 
                ? 'bg-primary-500/20 text-primary-300 border border-primary-500/30' 
                : 'bg-surface-800 text-surface-400 border border-surface-700 hover:border-surface-600'"
              @click="selectedPlatform = platform.id"
            >
              <PlatformIcon :platform="platform.platformId" size="sm" variant="outline" />
              <span>{{ platform.name }}</span>
            </button>
          </div>
        </div>

        <!-- Duration -->
        <Input
          v-model.number="duration"
          label="Target Duration (seconds)"
          type="number"
          min="15"
          max="180"
          required
        >
          <template #icon-left>
            <Icon name="Clock" :size="18" />
          </template>
        </Input>
      </form>

      <template #footer>
        <div class="flex justify-end gap-3">
          <Button variant="ghost" @click="showGenerate = false">Cancel</Button>
          <Button 
            variant="primary" 
            :disabled="generating || !concept || !selectedPlatform"
            :loading="generating"
            @click="generateScript"
          >
            Generate Script
          </Button>
        </div>
      </template>
    </Modal>

    <!-- Scripts List -->
    <div v-if="scriptsLoading" class="grid md:grid-cols-2 gap-4">
      <Card v-for="i in 4" :key="i" class="border-l-4 border-l-accent-500">
        <div class="flex items-start gap-4 mb-4">
          <Skeleton variant="rounded" width="48px" height="48px" />
          <div class="flex-1 space-y-2">
            <Skeleton variant="text" width="80%" />
            <Skeleton variant="text" width="40%" />
          </div>
        </div>
        <Skeleton variant="text" width="60px" class="mb-4" />
        <div class="flex gap-2">
          <Skeleton variant="rounded" width="100px" height="36px" />
          <Skeleton variant="rounded" width="40px" height="36px" />
        </div>
      </Card>
    </div>
    <EmptyState
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
      <Card v-for="script in scripts" :key="script.id" variant="hover" class="border-l-4 border-l-accent-500">
        <div class="flex items-start gap-4 mb-4">
          <div class="w-12 h-12 rounded-xl bg-accent-500/20 flex items-center justify-center flex-shrink-0">
            <Icon name="FileText" :size="24" class="text-accent-400" />
          </div>
          <div class="flex-1 min-w-0">
            <h3 class="font-semibold text-surface-100 truncate">{{ script.concept }}</h3>
            <div class="flex items-center gap-2 mt-1 text-sm text-surface-400">
              <PlatformIcon :platform="script.platform" size="sm" variant="outline" />
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
          <Button variant="secondary" size="sm" :to="`/scripts/${script.id}`" class="flex-1">
            <Icon name="Eye" :size="16" />
            <span>View Script</span>
          </Button>
          <Button variant="ghost" size="sm">
            <Icon name="Download" :size="16" />
          </Button>
        </div>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'app',
  middleware: 'auth',
})

const api = useApi()
const showGenerate = ref(false)
const generating = ref(false)
const scriptsLoading = ref(true)
const concept = ref('')
const selectedPlatform = ref('')
const duration = ref(60)

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
</script>
