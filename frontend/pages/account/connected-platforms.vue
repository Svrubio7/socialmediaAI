<template>
  <div class="container-wide py-8 lg:py-10">
    <NuxtLink
      :to="localePath('/dashboard')"
      class="inline-flex items-center gap-2 text-sm text-surface-400 hover:text-surface-200 mb-6 transition-colors"
    >
      <UiIcon name="ArrowLeft" :size="16" />
      Back to Dashboard
    </NuxtLink>

    <h1 class="text-3xl lg:text-4xl font-mono font-bold text-surface-100 mb-2">Connected Platforms</h1>
    <p class="text-surface-400 mb-8">Connect your social accounts to publish content</p>

    <Card class="border-l-4 border-l-primary-500">
      <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div
          v-for="platform in platforms"
          :key="platform.id"
          class="p-5 rounded-2xl bg-surface-800/50 border border-surface-700 hover:border-surface-600 transition-colors"
        >
          <div class="flex items-center justify-between mb-4">
            <PlatformIcon :platform="platform.id" size="lg" :variant="platform.connected ? 'filled' : 'outline'" />
            <StatusBadge :status="platform.connected ? 'connected' : 'disconnected'" :show-dot="false" />
          </div>
          <h3 class="font-semibold text-surface-100 mb-1">{{ platform.name }}</h3>
          <p v-if="platform.username" class="text-surface-400 text-sm mb-4 truncate">@{{ platform.username }}</p>
          <p v-else class="text-surface-500 text-sm mb-4">Not connected</p>
          <Button
            v-if="!platform.connected"
            variant="primary"
            size="sm"
            full-width
            :loading="connecting === platform.id"
            @click="connectAccount(platform.id)"
          >
            <UiIcon name="Link" :size="16" />
            Connect
          </Button>
          <Button
            v-else
            variant="ghost"
            size="sm"
            full-width
            class="text-red-400 hover:text-red-300 hover:bg-red-500/10"
            :loading="disconnecting === platform.id"
            @click="disconnectAccount(platform.id)"
          >
            <UiIcon name="Unlink" :size="16" />
            Disconnect
          </Button>
        </div>
      </div>
    </Card>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'app',
  middleware: 'auth',
})

const localePath = useLocalePath()
const api = useApi()

const connecting = ref<string | null>(null)
const disconnecting = ref<string | null>(null)

const platformIds = [
  { id: 'instagram' as const, name: 'Instagram' },
  { id: 'tiktok' as const, name: 'TikTok' },
  { id: 'youtube' as const, name: 'YouTube' },
  { id: 'facebook' as const, name: 'Facebook' },
]

const platforms = ref<
  { id: 'instagram' | 'tiktok' | 'youtube' | 'facebook'; name: string; connected: boolean; username: string }[]
>(platformIds.map((p) => ({ ...p, connected: false, username: '' })))

async function fetchAccounts() {
  try {
    const res = await api.oauth.accounts() as { accounts?: { platform: string; username?: string }[] }
    const accounts = res?.accounts ?? []
    const byPlatform: Record<string, { username?: string }> = {}
    accounts.forEach((a: { platform: string; username?: string }) => {
      byPlatform[a.platform?.toLowerCase()] = { username: a.username }
    })
    platforms.value = platformIds.map((p) => ({
      ...p,
      connected: !!byPlatform[p.id],
      username: byPlatform[p.id]?.username ?? '',
    }))
  } catch {
    platforms.value = platformIds.map((p) => ({ ...p, connected: false, username: '' }))
  }
}

async function connectAccount(platformId: string) {
  connecting.value = platformId
  try {
    const res = await api.oauth.connect(platformId) as { auth_url?: string }
    if (res?.auth_url) window.location.href = res.auth_url
    else await fetchAccounts()
  } catch {
    await fetchAccounts()
  } finally {
    connecting.value = null
  }
}

async function disconnectAccount(platformId: string) {
  disconnecting.value = platformId
  try {
    const res = await api.oauth.accounts() as { accounts?: { id: string; platform: string }[] }
    const account = res?.accounts?.find((a: { platform: string }) => a.platform?.toLowerCase() === platformId)
    if (account?.id) await api.oauth.disconnect(account.id)
    await fetchAccounts()
  } catch {
    await fetchAccounts()
  } finally {
    disconnecting.value = null
  }
}

onMounted(fetchAccounts)
</script>
