<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- Header -->
    <div class="flex items-center justify-between mb-8">
      <div>
        <h1 class="text-3xl font-display font-bold">Scripts</h1>
        <p class="text-surface-400 mt-1">AI-generated filming and editing scripts</p>
      </div>
      <button @click="showGenerate = true" class="btn-primary">
        Generate Script
      </button>
    </div>

    <!-- Generate Modal -->
    <div v-if="showGenerate" class="fixed inset-0 bg-surface-950/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div class="card max-w-lg w-full">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-display font-semibold">Generate Script</h2>
          <button @click="showGenerate = false" class="text-surface-400 hover:text-surface-100">
            ✕
          </button>
        </div>

        <form @submit.prevent="generateScript" class="space-y-4">
          <div>
            <label for="concept" class="label">Video Concept</label>
            <textarea
              id="concept"
              v-model="concept"
              class="input min-h-[100px]"
              placeholder="e.g., 5 Tips for Better Sleep, Morning Routine Hacks..."
              required
            />
          </div>

          <div>
            <label class="label">Target Platform</label>
            <div class="flex flex-wrap gap-2">
              <button
                v-for="platform in availablePlatforms"
                :key="platform.value"
                type="button"
                class="px-3 py-1 rounded-full text-sm transition-colors"
                :class="selectedPlatform === platform.value 
                  ? 'bg-primary-500 text-white' 
                  : 'bg-surface-800 text-surface-300 hover:bg-surface-700'"
                @click="selectedPlatform = platform.value"
              >
                {{ platform.icon }} {{ platform.label }}
              </button>
            </div>
          </div>

          <div>
            <label for="duration" class="label">Target Duration (seconds)</label>
            <input
              id="duration"
              v-model.number="duration"
              type="number"
              class="input"
              min="15"
              max="180"
              required
            />
          </div>

          <div class="flex justify-end gap-3 mt-6">
            <button type="button" @click="showGenerate = false" class="btn-secondary">
              Cancel
            </button>
            <button type="submit" class="btn-primary" :disabled="generating || !concept || !selectedPlatform">
              {{ generating ? 'Generating...' : 'Generate' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Scripts List -->
    <div v-if="scripts.length === 0" class="card text-center py-16">
      <div class="text-6xl mb-4">📝</div>
      <h3 class="text-xl font-display font-semibold mb-2">No scripts yet</h3>
      <p class="text-surface-400 mb-6">Generate your first script with AI assistance</p>
      <button @click="showGenerate = true" class="btn-primary">
        Generate Script
      </button>
    </div>

    <div v-else class="space-y-6">
      <div v-for="script in scripts" :key="script.id" class="card">
        <div class="flex items-start justify-between mb-4">
          <div>
            <h3 class="text-lg font-display font-semibold">{{ script.concept }}</h3>
            <p class="text-surface-400 text-sm">
              {{ script.platform }} • {{ script.target_duration }}s • {{ formatDate(script.created_at) }}
            </p>
          </div>
        </div>
        <div class="flex gap-3">
          <NuxtLink :to="`/scripts/${script.id}`" class="btn-secondary text-sm">
            View Script
          </NuxtLink>
          <button class="btn-ghost text-sm">
            Export
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  middleware: 'auth',
})

const showGenerate = ref(false)
const generating = ref(false)
const concept = ref('')
const selectedPlatform = ref('')
const duration = ref(60)

const availablePlatforms = [
  { value: 'tiktok', label: 'TikTok', icon: '🎵' },
  { value: 'instagram', label: 'Instagram', icon: '📸' },
  { value: 'youtube_shorts', label: 'YouTube Shorts', icon: '▶️' },
  { value: 'facebook', label: 'Facebook', icon: '📘' },
]

const scripts = ref<any[]>([])

const generateScript = async () => {
  generating.value = true
  // TODO: Implement script generation
  await new Promise(resolve => setTimeout(resolve, 2000))
  generating.value = false
  showGenerate.value = false
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString()
}
</script>
