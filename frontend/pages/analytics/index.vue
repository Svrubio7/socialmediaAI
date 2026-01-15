<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- Header -->
    <div class="flex items-center justify-between mb-8">
      <div>
        <h1 class="text-3xl font-display font-bold">Analytics</h1>
        <p class="text-surface-400 mt-1">Track your content performance across platforms</p>
      </div>
      <select v-model="dateRange" class="input w-auto">
        <option value="7">Last 7 days</option>
        <option value="30">Last 30 days</option>
        <option value="90">Last 90 days</option>
      </select>
    </div>

    <!-- Overview Stats -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <div v-for="stat in overviewStats" :key="stat.label" class="card">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-surface-400 text-sm">{{ stat.label }}</p>
            <p class="text-2xl font-display font-bold mt-1">{{ formatNumber(stat.value) }}</p>
          </div>
          <div class="w-12 h-12 bg-surface-800 rounded-lg flex items-center justify-center text-2xl">
            {{ stat.icon }}
          </div>
        </div>
        <p v-if="stat.change !== undefined" class="text-sm mt-2" :class="stat.change >= 0 ? 'text-green-400' : 'text-red-400'">
          {{ stat.change >= 0 ? '+' : '' }}{{ stat.change }}% from last period
        </p>
      </div>
    </div>

    <!-- Platform Breakdown -->
    <div class="grid lg:grid-cols-2 gap-8 mb-8">
      <div class="card">
        <h2 class="text-xl font-display font-semibold mb-6">Platform Performance</h2>
        
        <div class="space-y-4">
          <div v-for="platform in platformStats" :key="platform.name" class="p-4 rounded-lg bg-surface-800/50">
            <div class="flex items-center justify-between mb-2">
              <div class="flex items-center space-x-3">
                <span class="text-2xl">{{ platform.icon }}</span>
                <span class="font-medium">{{ platform.name }}</span>
              </div>
              <span class="text-surface-400">{{ formatNumber(platform.views) }} views</span>
            </div>
            <div class="flex items-center gap-6 text-sm text-surface-400">
              <span>❤️ {{ formatNumber(platform.likes) }}</span>
              <span>💬 {{ formatNumber(platform.comments) }}</span>
              <span>🔄 {{ formatNumber(platform.shares) }}</span>
              <span class="text-primary-400">{{ platform.engagement }}% engagement</span>
            </div>
          </div>
        </div>
      </div>

      <div class="card">
        <h2 class="text-xl font-display font-semibold mb-6">Top Performing Content</h2>
        
        <div v-if="topVideos.length === 0" class="text-center py-8 text-surface-500">
          <p>No data available yet</p>
        </div>

        <div v-else class="space-y-4">
          <div v-for="(video, index) in topVideos" :key="video.id" class="flex items-center space-x-4">
            <span class="text-2xl font-display font-bold text-surface-600">#{{ index + 1 }}</span>
            <div class="w-16 h-12 bg-surface-800 rounded-lg flex items-center justify-center">
              📹
            </div>
            <div class="flex-1 min-w-0">
              <p class="font-medium truncate">{{ video.title }}</p>
              <p class="text-surface-400 text-sm">{{ formatNumber(video.views) }} views</p>
            </div>
            <span class="badge badge-success">{{ video.engagement }}%</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Pattern Insights -->
    <div class="card">
      <h2 class="text-xl font-display font-semibold mb-6">Pattern Insights</h2>
      
      <div v-if="patternInsights.length === 0" class="text-center py-8 text-surface-500">
        <p>Analyze more videos to get pattern insights</p>
      </div>

      <div v-else class="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div v-for="insight in patternInsights" :key="insight.pattern" class="p-4 rounded-lg bg-surface-800/50">
          <h3 class="font-medium mb-1">{{ insight.pattern }}</h3>
          <p class="text-surface-400 text-sm mb-2">{{ insight.description }}</p>
          <div class="flex items-center gap-2">
            <div class="flex-1 h-2 bg-surface-700 rounded-full overflow-hidden">
              <div 
                class="h-full bg-gradient-to-r from-primary-500 to-accent-500"
                :style="{ width: `${insight.score}%` }"
              />
            </div>
            <span class="text-sm font-medium">{{ insight.score }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  middleware: 'auth',
})

const dateRange = ref('30')

const overviewStats = [
  { label: 'Total Views', value: 0, icon: '👁️', change: 0 },
  { label: 'Total Engagement', value: 0, icon: '❤️', change: 0 },
  { label: 'Posts Published', value: 0, icon: '🚀', change: 0 },
  { label: 'Avg. Engagement Rate', value: 0, icon: '📈', change: 0 },
]

const platformStats = [
  { name: 'Instagram', icon: '📸', views: 0, likes: 0, comments: 0, shares: 0, engagement: 0 },
  { name: 'TikTok', icon: '🎵', views: 0, likes: 0, comments: 0, shares: 0, engagement: 0 },
  { name: 'YouTube', icon: '▶️', views: 0, likes: 0, comments: 0, shares: 0, engagement: 0 },
  { name: 'Facebook', icon: '📘', views: 0, likes: 0, comments: 0, shares: 0, engagement: 0 },
]

const topVideos: any[] = []
const patternInsights: any[] = []

const formatNumber = (num: number) => {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num.toString()
}
</script>
