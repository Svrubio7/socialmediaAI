<template>
  <div class="container-wide py-8 lg:py-12">
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-xl lg:text-2xl font-mono font-normal text-surface-100">Publish</h1>
      <p class="text-surface-400 mt-1 text-sm">Connect accounts and publish content across platforms</p>
    </div>

    <!-- Connected Accounts summary -->
    <UiCard class="mb-8 border-l-4 border-l-primary-500">
      <div class="flex items-center justify-between flex-wrap gap-4">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-primary-500/20 flex items-center justify-center">
            <UiIcon name="Link2" :size="20" class="text-primary-400" />
          </div>
          <div>
            <h2 class="text-lg font-mono font-medium text-surface-100">Connected Platforms</h2>
            <p class="text-surface-400 text-sm">
              {{ connectedCount }} of {{ platforms.length }} platforms connected
            </p>
          </div>
        </div>
        <NuxtLink :to="localePath('/account/connected-platforms')" class="inline-flex items-center gap-2 text-sm font-medium text-primary-400 hover:text-primary-300 transition-colors">
          <UiIcon name="Settings" :size="16" />
          Manage in Account
        </NuxtLink>
      </div>
    </UiCard>

    <!-- Publish Content -->
    <div class="grid lg:grid-cols-2 gap-6 lg:gap-8">
      <!-- Publish Form -->
      <UiCard>
        <h2 class="text-xl font-mono font-medium text-surface-100 mb-6">Publish Content</h2>
        
        <form @submit.prevent="publishContent" class="space-y-5">
          <!-- Video Selection -->
          <div>
            <label class="label">Select Video</label>
            <div class="relative">
              <select v-model="selectedVideo" class="input pr-10 appearance-none cursor-pointer">
                <option value="">Select a video...</option>
                <option v-for="video in availableVideos" :key="video.id" :value="video.id">
                  {{ video.original_filename || video.filename }}
                </option>
              </select>
              <UiIcon name="ChevronDown" :size="16" class="absolute right-3 top-1/2 -translate-y-1/2 text-surface-500 pointer-events-none" />
            </div>
          </div>

          <!-- Platform Selection -->
          <div>
            <label class="label">Platforms</label>
            <div class="flex flex-wrap gap-2">
              <button
                v-for="platform in connectedPlatforms"
                :key="platform.id"
                type="button"
                class="toggle-pill"
                :class="selectedPublishPlatforms.includes(platform.id) ? 'toggle-pill-active' : 'toggle-pill-inactive'"
                @click="togglePublishPlatform(platform.id)"
              >
                <SharedPlatformIcon :platform="platform.id" size="sm" variant="outline" />
                <span>{{ platform.name }}</span>
                <UiIcon 
                  :name="selectedPublishPlatforms.includes(platform.id) ? 'Check' : 'Plus'" 
                  :size="14" 
                />
              </button>
            </div>
            <p v-if="connectedPlatforms.length === 0" class="text-surface-500 text-sm mt-2">
              Connect at least one account to publish
            </p>
          </div>

          <!-- Caption -->
          <UiInput
            v-model="caption"
            label="Caption"
            type="textarea"
            placeholder="Write your caption..."
            :rows="4"
          />

          <!-- Hashtags -->
          <UiInput
            v-model="hashtags"
            label="Hashtags"
            placeholder="#viral #fyp #trending"
          >
            <template #icon-left>
              <UiIcon name="Hash" :size="18" />
            </template>
          </UiInput>

          <!-- Actions -->
          <div class="flex gap-3 pt-2">
            <UiButton 
              type="submit" 
              variant="primary" 
              class="flex-1 rounded-xl"
              :disabled="!canPublish || publishing"
              :loading="publishing"
            >
              <template #icon-left><UiIcon name="Send" :size="16" /></template>
              Publish Now
            </UiButton>
            <UiButton 
              type="button" 
              variant="secondary"
              class="rounded-xl"
              :disabled="!canPublish"
              @click="showSchedule = true"
            >
              <template #icon-left><UiIcon name="Calendar" :size="16" /></template>
              Schedule
            </UiButton>
          </div>
        </form>
      </UiCard>

      <!-- Scheduled Posts -->
      <UiCard class="border-l-4 border-l-amber-500">
        <h2 class="text-xl font-mono font-medium text-surface-100 mb-6">Scheduled Posts</h2>
        
        <SharedEmptyState
          v-if="scheduledPosts.length === 0"
          icon="Calendar"
          title="No scheduled posts"
          description="Schedule content to be published automatically at the perfect time"
          variant="default"
        />

        <div v-else class="space-y-4">
          <div 
            v-for="post in scheduledPosts" 
            :key="post.id" 
            class="p-4 rounded-xl bg-surface-800/50 border border-surface-700"
          >
            <div class="flex items-start justify-between mb-3">
              <div class="flex-1 min-w-0">
                <p class="font-medium text-surface-100 truncate">{{ post.video_title || 'Video' }}</p>
                <div class="flex items-center gap-2 mt-1">
                  <SharedPlatformIcon :platform="post.platform" size="sm" variant="outline" />
                  <span class="text-surface-400 text-sm">{{ post.platform }}</span>
                </div>
              </div>
              <UiBadge variant="accent">Scheduled</UiBadge>
            </div>
            
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2 text-sm text-surface-400">
                <UiIcon name="Clock" :size="14" />
                <span>{{ formatDateTime(post.scheduled_at) }}</span>
              </div>
              <UiButton 
                variant="ghost" 
                size="sm" 
                class="rounded-xl text-red-400 hover:text-red-300 hover:bg-red-500/10"
                :disabled="cancelling === post.id"
                @click="cancelScheduled(post.id)"
              >
                <template #icon-left><UiIcon name="X" :size="14" /></template>
                Cancel
              </UiButton>
            </div>
          </div>
        </div>
      </UiCard>
    </div>

    <!-- Schedule modal -->
    <UiModal v-model="showSchedule" title="Schedule post" size="md">
      <form @submit.prevent="submitSchedule" class="space-y-4">
        <div>
          <label class="label text-sm">Date & time</label>
          <input
            v-model="scheduleDatetime"
            type="datetime-local"
            class="input w-full"
            required
          />
        </div>
        <div class="flex justify-end gap-3 pt-2">
          <UiButton variant="ghost" type="button" class="rounded-xl" @click="showSchedule = false">Cancel</UiButton>
          <UiButton variant="primary" type="submit" class="rounded-xl" :disabled="scheduling">
            {{ scheduling ? 'Scheduling…' : 'Schedule' }}
          </UiButton>
        </div>
      </form>
    </UiModal>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
definePageMeta({
  layout: 'app-sidebar',
  middleware: 'auth',
})

const localePath = useLocalePath()
const api = useApi()
const toast = useToast()

const selectedVideo = ref('')
const selectedPublishPlatforms = ref<string[]>([])
const caption = ref('')
const hashtags = ref('')
const showSchedule = ref(false)
const scheduleDatetime = ref('')
const publishing = ref(false)
const scheduling = ref(false)
const cancelling = ref<string | null>(null)

const platforms = ref([
  { id: 'instagram' as const, name: 'Instagram', connected: false, username: '' },
  { id: 'tiktok' as const, name: 'TikTok', connected: false, username: '' },
  { id: 'youtube' as const, name: 'YouTube', connected: false, username: '' },
  { id: 'facebook' as const, name: 'Facebook', connected: false, username: '' },
])

const availableVideos = ref<any[]>([])
const scheduledPosts = ref<any[]>([])

const connectedCount = computed(() => platforms.value.filter(p => p.connected).length)
const connectedPlatforms = computed(() => platforms.value.filter(p => p.connected))

async function fetchPlatforms() {
  try {
    const res = await api.oauth.accounts() as { accounts?: { platform: string; username?: string }[] }
    const accounts = res?.accounts ?? []
    const byPlatform: Record<string, { username?: string }> = {}
    accounts.forEach((a: { platform: string; username?: string }) => {
      byPlatform[a.platform?.toLowerCase()] = { username: a.username }
    })
    platforms.value = platforms.value.map((p) => ({
      ...p,
      connected: !!byPlatform[p.id],
      username: byPlatform[p.id]?.username ?? '',
    }))
  } catch {
    // keep defaults
  }
}

async function fetchVideos() {
  try {
    const res = await api.videos.list({ limit: 100 })
    availableVideos.value = (res as { items?: any[] })?.items ?? []
  } catch {
    availableVideos.value = []
  }
}

async function fetchScheduled() {
  try {
    const res = await api.posts.scheduled()
    scheduledPosts.value = (res as { items?: any[] })?.items ?? []
  } catch {
    scheduledPosts.value = []
  }
}

onMounted(() => {
  fetchPlatforms()
  fetchVideos()
  fetchScheduled()
})

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
  try {
    const res = await api.oauth.connect(platformId) as { auth_url?: string }
    if (res?.auth_url) window.location.href = res.auth_url
    else await fetchPlatforms()
  } catch {
    await fetchPlatforms()
  }
}

const publishContent = async () => {
  if (!canPublish.value) return
  publishing.value = true
  try {
    await api.posts.publish({
      video_id: selectedVideo.value,
      platforms: selectedPublishPlatforms.value,
      caption: caption.value || undefined,
      hashtags: hashtags.value ? hashtags.value.trim().split(/\s+/).filter(Boolean) : undefined,
      publish_now: true,
    })
    toast.success('Publish queued')
    await fetchScheduled()
  } catch (e: any) {
    toast.error(e?.data?.detail ?? e?.message ?? 'Publish failed')
  } finally {
    publishing.value = false
  }
}

async function submitSchedule() {
  if (!canPublish.value || !scheduleDatetime.value) return
  scheduling.value = true
  try {
    const at = new Date(scheduleDatetime.value).toISOString()
    await api.posts.schedule({
      video_id: selectedVideo.value,
      platforms: selectedPublishPlatforms.value,
      scheduled_at: at,
      caption: caption.value || undefined,
      hashtags: hashtags.value ? hashtags.value.trim().split(/\s+/).filter(Boolean) : undefined,
    })
    toast.success('Post scheduled')
    showSchedule.value = false
    scheduleDatetime.value = ''
    await fetchScheduled()
  } catch (e: any) {
    toast.error(e?.data?.detail ?? e?.message ?? 'Schedule failed')
  } finally {
    scheduling.value = false
  }
}

const cancelScheduled = async (postId: string) => {
  cancelling.value = postId
  try {
    await api.posts.cancel(postId)
    toast.success('Schedule cancelled')
    await fetchScheduled()
  } catch (e: any) {
    toast.error(e?.data?.detail ?? e?.message ?? 'Cancel failed')
  } finally {
    cancelling.value = null
  }
}

const formatDateTime = (date: string) => {
  return new Date(date).toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
}
</script>
