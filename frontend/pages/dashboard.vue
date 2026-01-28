<template>
  <div class="container-wide py-8 lg:py-12">
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-3xl lg:text-4xl font-display font-bold text-surface-100">Dashboard</h1>
      <p class="text-surface-400 mt-2">Welcome back! Here's an overview of your content.</p>
    </div>

    <!-- Stats Grid -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6 mb-8">
      <Card v-for="stat in stats" :key="stat.label">
        <div class="flex items-start justify-between">
          <div>
            <p class="text-surface-400 text-sm mb-1">{{ stat.label }}</p>
            <p class="text-2xl lg:text-3xl font-display font-bold text-surface-100">{{ stat.value }}</p>
          </div>
          <div 
            class="w-10 h-10 lg:w-12 lg:h-12 rounded-xl flex items-center justify-center"
            :class="stat.iconBg"
          >
            <Icon :name="stat.icon" :size="20" :class="stat.iconColor" />
          </div>
        </div>
        <p 
          v-if="stat.change !== undefined" 
          class="text-sm mt-3 flex items-center gap-1"
          :class="stat.change >= 0 ? 'text-emerald-400' : 'text-red-400'"
        >
          <Icon :name="stat.change >= 0 ? 'TrendingUp' : 'TrendingDown'" :size="14" />
          <span>{{ stat.change >= 0 ? '+' : '' }}{{ stat.change }}% from last week</span>
        </p>
      </Card>
    </div>

    <!-- Quick Actions -->
    <div class="grid md:grid-cols-3 gap-4 lg:gap-6 mb-8">
      <Card variant="interactive" to="/videos" class="group">
        <div class="flex items-center gap-4">
          <div class="w-12 h-12 rounded-xl bg-primary-500/10 flex items-center justify-center transition-transform duration-300 group-hover:scale-110">
            <Icon name="Upload" :size="24" class="text-primary-400" />
          </div>
          <div>
            <h3 class="font-display font-semibold text-surface-100">Upload Video</h3>
            <p class="text-surface-400 text-sm">Analyze patterns in your content</p>
          </div>
        </div>
      </Card>

      <Card variant="interactive" to="/strategies" class="group">
        <div class="flex items-center gap-4">
          <div class="w-12 h-12 rounded-xl bg-accent-500/10 flex items-center justify-center transition-transform duration-300 group-hover:scale-110">
            <Icon name="Target" :size="24" class="text-accent-400" />
          </div>
          <div>
            <h3 class="font-display font-semibold text-surface-100">Generate Strategy</h3>
            <p class="text-surface-400 text-sm">Get AI-powered recommendations</p>
          </div>
        </div>
      </Card>

      <Card variant="interactive" to="/publish" class="group">
        <div class="flex items-center gap-4">
          <div class="w-12 h-12 rounded-xl bg-emerald-500/10 flex items-center justify-center transition-transform duration-300 group-hover:scale-110">
            <Icon name="Send" :size="24" class="text-emerald-400" />
          </div>
          <div>
            <h3 class="font-display font-semibold text-surface-100">Publish Content</h3>
            <p class="text-surface-400 text-sm">Share to all platforms</p>
          </div>
        </div>
      </Card>
    </div>

    <!-- Recent Videos & Platform Connections -->
    <div class="grid lg:grid-cols-2 gap-6 lg:gap-8">
      <!-- Recent Videos -->
      <Card>
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-display font-semibold text-surface-100">Recent Videos</h2>
          <Button variant="ghost" size="sm" to="/videos">
            View all
            <Icon name="ArrowRight" :size="16" />
          </Button>
        </div>
        
        <EmptyState
          v-if="recentVideos.length === 0"
          icon="Video"
          title="No videos yet"
          description="Upload your first video to start analyzing patterns"
          action-label="Upload Video"
          action-icon="Upload"
          variant="primary"
          @action="navigateTo('/videos')"
        />

        <div v-else class="space-y-3">
          <div 
            v-for="video in recentVideos" 
            :key="video.id" 
            class="flex items-center gap-4 p-3 rounded-xl bg-surface-800/50 hover:bg-surface-800 transition-colors"
          >
            <div class="w-16 h-12 bg-surface-700 rounded-lg flex items-center justify-center overflow-hidden flex-shrink-0">
              <img 
                v-if="video.thumbnail_url" 
                :src="video.thumbnail_url" 
                :alt="video.filename"
                class="w-full h-full object-cover"
              />
              <Icon v-else name="Video" :size="20" class="text-surface-500" />
            </div>
            <div class="flex-1 min-w-0">
              <p class="font-medium text-surface-100 truncate">{{ video.filename }}</p>
              <div class="flex items-center gap-2 mt-1">
                <StatusBadge :status="video.status" :show-dot="false" />
              </div>
            </div>
          </div>
        </div>
      </Card>

      <!-- Platform Connections -->
      <Card>
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-display font-semibold text-surface-100">Connected Platforms</h2>
          <Button variant="ghost" size="sm" to="/publish">
            Manage
            <Icon name="ArrowRight" :size="16" />
          </Button>
        </div>

        <div class="space-y-3">
          <div 
            v-for="platform in platforms" 
            :key="platform.id" 
            class="flex items-center justify-between p-3 rounded-xl bg-surface-800/50"
          >
            <div class="flex items-center gap-3">
              <PlatformIcon :platform="platform.id" size="md" :variant="platform.connected ? 'filled' : 'outline'" />
              <span class="font-medium text-surface-100">{{ platform.name }}</span>
            </div>
            <StatusBadge :status="platform.connected ? 'connected' : 'disconnected'" />
          </div>
        </div>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  middleware: 'auth',
})

const stats = [
  { 
    label: 'Total Videos', 
    value: '0', 
    icon: 'Video',
    iconBg: 'bg-primary-500/10',
    iconColor: 'text-primary-400',
    change: 0,
  },
  { 
    label: 'Patterns Found', 
    value: '0', 
    icon: 'Target',
    iconBg: 'bg-accent-500/10',
    iconColor: 'text-accent-400',
    change: 0,
  },
  { 
    label: 'Posts Published', 
    value: '0', 
    icon: 'Send',
    iconBg: 'bg-emerald-500/10',
    iconColor: 'text-emerald-400',
    change: 0,
  },
  { 
    label: 'Total Views', 
    value: '0', 
    icon: 'Eye',
    iconBg: 'bg-amber-500/10',
    iconColor: 'text-amber-400',
    change: 0,
  },
]

const recentVideos = ref<any[]>([])

const platforms = [
  { id: 'instagram' as const, name: 'Instagram', connected: false },
  { id: 'tiktok' as const, name: 'TikTok', connected: false },
  { id: 'youtube' as const, name: 'YouTube', connected: false },
  { id: 'facebook' as const, name: 'Facebook', connected: false },
]
</script>
