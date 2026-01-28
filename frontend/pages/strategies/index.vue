<template>
  <div class="container-wide py-8 lg:py-12">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
      <div>
        <h1 class="text-3xl lg:text-4xl font-mono font-bold text-surface-100">Strategies</h1>
        <p class="text-surface-400 mt-2">AI-generated marketing strategies based on your content</p>
      </div>
      <Button variant="primary" @click="showGenerate = true">
        <Icon name="Sparkles" :size="18" />
        <span>Generate Strategy</span>
      </Button>
    </div>

    <!-- Generate Modal -->
    <Modal v-model="showGenerate" title="Generate Strategy" size="lg">
      <form @submit.prevent="generateStrategy" class="space-y-5">
        <!-- Platform Selection -->
        <div>
          <label class="label">Target Platforms</label>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="platform in availablePlatforms"
              :key="platform.id"
              type="button"
              class="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200"
              :class="selectedPlatforms.includes(platform.id) 
                ? 'bg-primary-500/20 text-primary-300 border border-primary-500/30' 
                : 'bg-surface-800 text-surface-400 border border-surface-700 hover:border-surface-600'"
              @click="togglePlatform(platform.id)"
            >
              <PlatformIcon :platform="platform.id" size="sm" variant="outline" />
              <span>{{ platform.name }}</span>
            </button>
          </div>
        </div>

        <!-- Goals Selection -->
        <div>
          <label class="label">Goals</label>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="goal in availableGoals"
              :key="goal.id"
              type="button"
              class="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200"
              :class="selectedGoals.includes(goal.id) 
                ? 'bg-accent-500/20 text-accent-300 border border-accent-500/30' 
                : 'bg-surface-800 text-surface-400 border border-surface-700 hover:border-surface-600'"
              @click="toggleGoal(goal.id)"
            >
              <Icon :name="goal.icon" :size="16" />
              <span>{{ goal.label }}</span>
            </button>
          </div>
        </div>

        <!-- Niche Input -->
        <Input
          v-model="niche"
          label="Niche/Industry (optional)"
          placeholder="e.g., Fitness, Tech, Food..."
        />
      </form>

      <template #footer>
        <div class="flex justify-end gap-3">
          <Button variant="ghost" @click="showGenerate = false">Cancel</Button>
          <Button 
            variant="primary" 
            :disabled="generating || selectedPlatforms.length === 0"
            :loading="generating"
            @click="generateStrategy"
          >
            Generate Strategy
          </Button>
        </div>
      </template>
    </Modal>

    <!-- Strategies List -->
    <EmptyState
      v-if="strategies.length === 0"
      icon="Target"
      title="No strategies yet"
      description="Generate your first AI-powered marketing strategy based on your video patterns"
      action-label="Generate Strategy"
      action-icon="Sparkles"
      variant="primary"
      @action="showGenerate = true"
    />

    <div v-else class="space-y-4">
      <Card v-for="strategy in strategies" :key="strategy.id" variant="hover">
        <div class="flex items-start justify-between mb-4">
          <div>
            <h3 class="text-lg font-mono font-semibold text-surface-100">
              Strategy #{{ strategy.id.slice(0, 8) }}
            </h3>
            <p class="text-surface-400 text-sm mt-1">
              Created {{ formatDate(strategy.created_at) }}
            </p>
          </div>
          <div class="flex gap-2">
            <Badge v-for="platform in strategy.platforms" :key="platform" variant="primary">
              {{ platform }}
            </Badge>
          </div>
        </div>
        <div class="flex gap-3">
          <Button variant="secondary" size="sm" :to="`/strategies/${strategy.id}`">
            <Icon name="Eye" :size="16" />
            <span>View Details</span>
          </Button>
          <Button variant="ghost" size="sm">
            <Icon name="Download" :size="16" />
            <span>Export</span>
          </Button>
        </div>
      </Card>
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
  { id: 'instagram' as const, name: 'Instagram' },
  { id: 'tiktok' as const, name: 'TikTok' },
  { id: 'youtube' as const, name: 'YouTube' },
  { id: 'facebook' as const, name: 'Facebook' },
]

const availableGoals = [
  { id: 'engagement', label: 'Engagement', icon: 'Heart' },
  { id: 'views', label: 'Views', icon: 'Eye' },
  { id: 'followers', label: 'Followers', icon: 'Users' },
  { id: 'conversions', label: 'Conversions', icon: 'DollarSign' },
]

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
  await new Promise(resolve => setTimeout(resolve, 2000))
  generating.value = false
  showGenerate.value = false
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}
</script>
