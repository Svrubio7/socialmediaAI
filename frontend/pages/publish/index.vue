<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-display font-bold">Publish</h1>
      <p class="text-surface-400 mt-1">Connect accounts and publish content across platforms</p>
    </div>

    <!-- Connected Accounts -->
    <div class="card mb-8">
      <h2 class="text-xl font-display font-semibold mb-6">Connected Accounts</h2>
      
      <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div v-for="platform in platforms" :key="platform.name" class="p-4 rounded-xl bg-surface-800/50 border border-surface-700">
          <div class="flex items-center justify-between mb-4">
            <span class="text-3xl">{{ platform.icon }}</span>
            <span 
              class="badge"
              :class="platform.connected ? 'badge-success' : 'badge-warning'"
            >
              {{ platform.connected ? 'Connected' : 'Not connected' }}
            </span>
          </div>
          <h3 class="font-medium mb-1">{{ platform.name }}</h3>
          <p v-if="platform.username" class="text-surface-400 text-sm mb-3">
            @{{ platform.username }}
          </p>
          <button
            v-if="!platform.connected"
            @click="connectAccount(platform.id)"
            class="btn-primary w-full text-sm"
          >
            Connect
          </button>
          <button
            v-else
            @click="disconnectAccount(platform.id)"
            class="btn-ghost w-full text-sm text-red-400 hover:text-red-300"
          >
            Disconnect
          </button>
        </div>
      </div>
    </div>

    <!-- Publish Content -->
    <div class="grid lg:grid-cols-2 gap-8">
      <!-- Publish Form -->
      <div class="card">
        <h2 class="text-xl font-display font-semibold mb-6">Publish Content</h2>
        
        <form @submit.prevent="publishContent" class="space-y-4">
          <div>
            <label class="label">Select Video</label>
            <select v-model="selectedVideo" class="input">
              <option value="">Select a video...</option>
              <!-- Videos will be populated here -->
            </select>
          </div>

          <div>
            <label class="label">Platforms</label>
            <div class="flex flex-wrap gap-2">
              <button
                v-for="platform in platforms.filter(p => p.connected)"
                :key="platform.id"
                type="button"
                class="px-3 py-1 rounded-full text-sm transition-colors"
                :class="selectedPublishPlatforms.includes(platform.id) 
                  ? 'bg-primary-500 text-white' 
                  : 'bg-surface-800 text-surface-300 hover:bg-surface-700'"
                @click="togglePublishPlatform(platform.id)"
              >
                {{ platform.icon }} {{ platform.name }}
              </button>
            </div>
            <p v-if="platforms.filter(p => p.connected).length === 0" class="text-surface-500 text-sm mt-2">
              Connect at least one account to publish
            </p>
          </div>

          <div>
            <label for="caption" class="label">Caption</label>
            <textarea
              id="caption"
              v-model="caption"
              class="input min-h-[100px]"
              placeholder="Write your caption..."
            />
          </div>

          <div>
            <label for="hashtags" class="label">Hashtags</label>
            <input
              id="hashtags"
              v-model="hashtags"
              type="text"
              class="input"
              placeholder="#viral #fyp #trending"
            />
          </div>

          <div class="flex gap-3">
            <button type="submit" class="btn-primary flex-1" :disabled="!canPublish">
              Publish Now
            </button>
            <button type="button" @click="showSchedule = true" class="btn-secondary" :disabled="!canPublish">
              Schedule
            </button>
          </div>
        </form>
      </div>

      <!-- Scheduled Posts -->
      <div class="card">
        <h2 class="text-xl font-display font-semibold mb-6">Scheduled Posts</h2>
        
        <div v-if="scheduledPosts.length === 0" class="text-center py-8 text-surface-500">
          <p>No scheduled posts</p>
        </div>

        <div v-else class="space-y-4">
          <div v-for="post in scheduledPosts" :key="post.id" class="p-4 rounded-lg bg-surface-800/50">
            <div class="flex items-center justify-between mb-2">
              <span class="font-medium">{{ post.video_title }}</span>
              <span class="badge badge-primary">{{ post.platform }}</span>
            </div>
            <p class="text-surface-400 text-sm mb-2">
              Scheduled for {{ formatDateTime(post.scheduled_at) }}
            </p>
            <button @click="cancelScheduled(post.id)" class="text-red-400 hover:text-red-300 text-sm">
              Cancel
            </button>
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

const selectedVideo = ref('')
const selectedPublishPlatforms = ref<string[]>([])
const caption = ref('')
const hashtags = ref('')
const showSchedule = ref(false)

const platforms = ref([
  { id: 'instagram', name: 'Instagram', icon: '📸', connected: false, username: '' },
  { id: 'tiktok', name: 'TikTok', icon: '🎵', connected: false, username: '' },
  { id: 'youtube', name: 'YouTube', icon: '▶️', connected: false, username: '' },
  { id: 'facebook', name: 'Facebook', icon: '📘', connected: false, username: '' },
])

const scheduledPosts = ref<any[]>([])

const canPublish = computed(() => {
  return selectedVideo.value && selectedPublishPlatforms.value.length > 0
})

const togglePublishPlatform = (platformId: string) => {
  const index = selectedPublishPlatforms.value.indexOf(platformId)
  if (index > -1) {
    selectedPublishPlatforms.value.splice(index, 1)
  } else {
    selectedPublishPlatforms.value.push(platformId)
  }
}

const connectAccount = async (platformId: string) => {
  // TODO: Implement OAuth connection
  console.log('Connecting:', platformId)
}

const disconnectAccount = async (platformId: string) => {
  // TODO: Implement account disconnection
  console.log('Disconnecting:', platformId)
}

const publishContent = async () => {
  // TODO: Implement publishing
  console.log('Publishing to:', selectedPublishPlatforms.value)
}

const cancelScheduled = async (postId: string) => {
  // TODO: Implement cancel scheduled
  console.log('Canceling:', postId)
}

const formatDateTime = (date: string) => {
  return new Date(date).toLocaleString()
}
</script>
