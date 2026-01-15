<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-display font-bold">Dashboard</h1>
      <p class="text-surface-400 mt-1">Welcome back! Here's an overview of your content.</p>
    </div>

    <!-- Stats Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <div v-for="stat in stats" :key="stat.label" class="card">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-surface-400 text-sm">{{ stat.label }}</p>
            <p class="text-2xl font-display font-bold mt-1">{{ stat.value }}</p>
          </div>
          <div class="w-12 h-12 bg-surface-800 rounded-lg flex items-center justify-center text-2xl">
            {{ stat.icon }}
          </div>
        </div>
        <p v-if="stat.change" class="text-sm mt-2" :class="stat.change > 0 ? 'text-green-400' : 'text-red-400'">
          {{ stat.change > 0 ? '+' : '' }}{{ stat.change }}% from last week
        </p>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="grid md:grid-cols-3 gap-6 mb-8">
      <NuxtLink to="/videos" class="card-hover group">
        <div class="flex items-center space-x-4">
          <div class="w-12 h-12 bg-primary-500/20 rounded-lg flex items-center justify-center text-2xl group-hover:bg-primary-500/30 transition-colors">
            📹
          </div>
          <div>
            <h3 class="font-display font-semibold">Upload Video</h3>
            <p class="text-surface-400 text-sm">Analyze patterns in your content</p>
          </div>
        </div>
      </NuxtLink>

      <NuxtLink to="/strategies" class="card-hover group">
        <div class="flex items-center space-x-4">
          <div class="w-12 h-12 bg-accent-500/20 rounded-lg flex items-center justify-center text-2xl group-hover:bg-accent-500/30 transition-colors">
            📊
          </div>
          <div>
            <h3 class="font-display font-semibold">Generate Strategy</h3>
            <p class="text-surface-400 text-sm">Get AI-powered recommendations</p>
          </div>
        </div>
      </NuxtLink>

      <NuxtLink to="/publish" class="card-hover group">
        <div class="flex items-center space-x-4">
          <div class="w-12 h-12 bg-green-500/20 rounded-lg flex items-center justify-center text-2xl group-hover:bg-green-500/30 transition-colors">
            🚀
          </div>
          <div>
            <h3 class="font-display font-semibold">Publish Content</h3>
            <p class="text-surface-400 text-sm">Share to all platforms</p>
          </div>
        </div>
      </NuxtLink>
    </div>

    <!-- Recent Videos & Analytics -->
    <div class="grid lg:grid-cols-2 gap-8">
      <!-- Recent Videos -->
      <div class="card">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-display font-semibold">Recent Videos</h2>
          <NuxtLink to="/videos" class="text-primary-400 hover:text-primary-300 text-sm">
            View all →
          </NuxtLink>
        </div>
        
        <div v-if="recentVideos.length === 0" class="text-center py-8 text-surface-500">
          <p>No videos yet. Upload your first video to get started!</p>
          <NuxtLink to="/videos" class="btn-primary mt-4">
            Upload Video
          </NuxtLink>
        </div>

        <div v-else class="space-y-4">
          <div v-for="video in recentVideos" :key="video.id" class="flex items-center space-x-4 p-3 rounded-lg bg-surface-800/50">
            <div class="w-16 h-12 bg-surface-700 rounded-lg flex items-center justify-center">
              📹
            </div>
            <div class="flex-1 min-w-0">
              <p class="font-medium truncate">{{ video.filename }}</p>
              <p class="text-surface-400 text-sm">{{ video.status }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Platform Connections -->
      <div class="card">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-display font-semibold">Connected Platforms</h2>
          <NuxtLink to="/publish" class="text-primary-400 hover:text-primary-300 text-sm">
            Manage →
          </NuxtLink>
        </div>

        <div class="space-y-4">
          <div v-for="platform in platforms" :key="platform.name" class="flex items-center justify-between p-3 rounded-lg bg-surface-800/50">
            <div class="flex items-center space-x-3">
              <span class="text-2xl">{{ platform.icon }}</span>
              <span class="font-medium">{{ platform.name }}</span>
            </div>
            <span 
              class="badge"
              :class="platform.connected ? 'badge-success' : 'badge-warning'"
            >
              {{ platform.connected ? 'Connected' : 'Not connected' }}
            </span>
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

const stats = [
  { label: 'Total Videos', value: '0', icon: '📹', change: 0 },
  { label: 'Patterns Found', value: '0', icon: '🎯', change: 0 },
  { label: 'Posts Published', value: '0', icon: '🚀', change: 0 },
  { label: 'Total Views', value: '0', icon: '👁️', change: 0 },
]

const recentVideos: any[] = []

const platforms = [
  { name: 'Instagram', icon: '📸', connected: false },
  { name: 'TikTok', icon: '🎵', connected: false },
  { name: 'YouTube', icon: '▶️', connected: false },
  { name: 'Facebook', icon: '📘', connected: false },
]
</script>
