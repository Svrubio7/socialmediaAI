<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- Header -->
    <div class="flex items-center justify-between mb-8">
      <div>
        <h1 class="text-3xl font-display font-bold">Strategies</h1>
        <p class="text-surface-400 mt-1">AI-generated marketing strategies based on your content</p>
      </div>
      <button @click="showGenerate = true" class="btn-primary">
        Generate Strategy
      </button>
    </div>

    <!-- Generate Modal -->
    <div v-if="showGenerate" class="fixed inset-0 bg-surface-950/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div class="card max-w-lg w-full">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-display font-semibold">Generate Strategy</h2>
          <button @click="showGenerate = false" class="text-surface-400 hover:text-surface-100">
            ✕
          </button>
        </div>

        <form @submit.prevent="generateStrategy" class="space-y-4">
          <div>
            <label class="label">Target Platforms</label>
            <div class="flex flex-wrap gap-2">
              <button
                v-for="platform in availablePlatforms"
                :key="platform.value"
                type="button"
                class="px-3 py-1 rounded-full text-sm transition-colors"
                :class="selectedPlatforms.includes(platform.value) 
                  ? 'bg-primary-500 text-white' 
                  : 'bg-surface-800 text-surface-300 hover:bg-surface-700'"
                @click="togglePlatform(platform.value)"
              >
                {{ platform.icon }} {{ platform.label }}
              </button>
            </div>
          </div>

          <div>
            <label class="label">Goals</label>
            <div class="flex flex-wrap gap-2">
              <button
                v-for="goal in availableGoals"
                :key="goal"
                type="button"
                class="px-3 py-1 rounded-full text-sm transition-colors"
                :class="selectedGoals.includes(goal) 
                  ? 'bg-accent-500 text-white' 
                  : 'bg-surface-800 text-surface-300 hover:bg-surface-700'"
                @click="toggleGoal(goal)"
              >
                {{ goal }}
              </button>
            </div>
          </div>

          <div>
            <label for="niche" class="label">Niche/Industry (optional)</label>
            <input
              id="niche"
              v-model="niche"
              type="text"
              class="input"
              placeholder="e.g., Fitness, Tech, Food..."
            />
          </div>

          <div class="flex justify-end gap-3 mt-6">
            <button type="button" @click="showGenerate = false" class="btn-secondary">
              Cancel
            </button>
            <button type="submit" class="btn-primary" :disabled="generating || selectedPlatforms.length === 0">
              {{ generating ? 'Generating...' : 'Generate' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Strategies List -->
    <div v-if="strategies.length === 0" class="card text-center py-16">
      <div class="text-6xl mb-4">📊</div>
      <h3 class="text-xl font-display font-semibold mb-2">No strategies yet</h3>
      <p class="text-surface-400 mb-6">Generate your first strategy based on your video patterns</p>
      <button @click="showGenerate = true" class="btn-primary">
        Generate Strategy
      </button>
    </div>

    <div v-else class="space-y-6">
      <div v-for="strategy in strategies" :key="strategy.id" class="card">
        <div class="flex items-start justify-between mb-4">
          <div>
            <h3 class="text-lg font-display font-semibold">Strategy #{{ strategy.id.slice(0, 8) }}</h3>
            <p class="text-surface-400 text-sm">Created {{ formatDate(strategy.created_at) }}</p>
          </div>
          <div class="flex gap-2">
            <span v-for="platform in strategy.platforms" :key="platform" class="badge badge-primary">
              {{ platform }}
            </span>
          </div>
        </div>
        <div class="flex gap-3">
          <NuxtLink :to="`/strategies/${strategy.id}`" class="btn-secondary text-sm">
            View Details
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
const niche = ref('')

const selectedPlatforms = ref<string[]>([])
const selectedGoals = ref<string[]>(['engagement'])

const availablePlatforms = [
  { value: 'instagram', label: 'Instagram', icon: '📸' },
  { value: 'tiktok', label: 'TikTok', icon: '🎵' },
  { value: 'youtube', label: 'YouTube', icon: '▶️' },
  { value: 'facebook', label: 'Facebook', icon: '📘' },
]

const availableGoals = ['engagement', 'views', 'followers', 'conversions']

const strategies = ref<any[]>([])

const togglePlatform = (platform: string) => {
  const index = selectedPlatforms.value.indexOf(platform)
  if (index > -1) {
    selectedPlatforms.value.splice(index, 1)
  } else {
    selectedPlatforms.value.push(platform)
  }
}

const toggleGoal = (goal: string) => {
  const index = selectedGoals.value.indexOf(goal)
  if (index > -1) {
    selectedGoals.value.splice(index, 1)
  } else {
    selectedGoals.value.push(goal)
  }
}

const generateStrategy = async () => {
  generating.value = true
  // TODO: Implement strategy generation
  await new Promise(resolve => setTimeout(resolve, 2000))
  generating.value = false
  showGenerate.value = false
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString()
}
</script>
