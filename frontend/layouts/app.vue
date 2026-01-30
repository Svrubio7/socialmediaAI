<template>
  <div class="min-h-screen flex flex-col bg-surface-950">
    <!-- App header: logo, back link, account dropdown -->
    <header class="sticky top-0 z-50 border-b border-surface-800/80 bg-surface-950/90 backdrop-blur-md">
      <div class="container-wide">
        <div class="flex items-center justify-between h-14">
          <UiLogo size="sm" />
          <div class="flex items-center gap-4">
            <NuxtLink
              :to="localePath('/')"
              class="flex items-center gap-2 font-mono text-sm text-surface-400 hover:text-surface-200 transition-colors"
            >
              <UiIcon name="ExternalLink" :size="14" />
              <span>Back to website</span>
            </NuxtLink>
            <UiDropdown align="right" width="sm">
              <template #trigger="{ open }">
                <button
                  type="button"
                  class="flex items-center gap-2 p-1.5 rounded-xl text-surface-400 hover:text-surface-100 hover:bg-surface-800 transition-colors"
                  :class="{ 'bg-surface-800 text-surface-100': open }"
                  aria-haspopup="true"
                  :aria-expanded="open"
                >
                  <span v-if="auth.user?.avatar_url" class="w-8 h-8 rounded-lg overflow-hidden flex-shrink-0">
                    <img :src="auth.user.avatar_url" :alt="auth.user.name ?? 'Avatar'" class="w-full h-full object-cover" />
                  </span>
                  <span v-else class="w-8 h-8 rounded-lg bg-primary-500/20 flex items-center justify-center">
                    <UiIcon name="User" :size="18" class="text-primary-400" />
                  </span>
                  <UiIcon name="ChevronDown" :size="14" class="transition-transform" :class="{ 'rotate-180': open }" />
                </button>
              </template>
              <template #default="{ close }">
                <div class="py-1">
                  <NuxtLink
                    v-for="item in accountLinks"
                    :key="item.to"
                    :to="localePath(item.to)"
                    class="flex items-center gap-3 px-4 py-2.5 text-sm font-medium text-surface-300 hover:text-surface-100 hover:bg-surface-800 transition-colors"
                    @click="close()"
                  >
                    <UiIcon :name="item.icon" :size="18" class="text-surface-500 flex-shrink-0" />
                    {{ item.label }}
                  </NuxtLink>
                  <button
                    type="button"
                    class="flex w-full items-center gap-3 px-4 py-2.5 text-sm font-medium text-surface-300 hover:text-surface-100 hover:bg-surface-800 transition-colors border-t border-surface-800 mt-1 pt-1"
                    @click="close(); signOut()"
                  >
                    <UiIcon name="LogOut" :size="18" class="text-surface-500 flex-shrink-0" />
                    Sign out
                  </button>
                </div>
              </template>
            </UiDropdown>
          </div>
        </div>
      </div>
    </header>

    <main class="flex-1">
      <slot />
    </main>

    <UiToast />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
const localePath = useLocalePath()
const auth = useAuthStore()

onMounted(() => {
  auth.initialize()
})

const accountLinks = [
  { to: '/account/profile', label: 'Profile', icon: 'User' },
  { to: '/account/preferences', label: 'Preferences', icon: 'Settings' },
  { to: '/account/branding', label: 'Branding', icon: 'Image' },
  { to: '/account/connected-platforms', label: 'Connected Platforms', icon: 'Link2' },
]

async function signOut() {
  await auth.logout()
}
</script>

