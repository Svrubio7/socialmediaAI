<template>
  <div class="min-h-screen flex flex-col bg-surface-50 dark:bg-surface-950">
    <!-- Compact top bar: logo, back link, theme, account, mobile menu -->
    <header class="sticky top-0 z-50 border-b border-surface-200 bg-surface-50/90 backdrop-blur-md dark:border-surface-800/80 dark:bg-surface-950/90">
      <div class="container-app flex items-center justify-between h-14">
        <div class="flex items-center gap-4">
          <button
            type="button"
            class="lg:hidden flex items-center justify-center w-10 h-10 rounded-xl text-surface-400 hover:text-surface-100 hover:bg-surface-800 transition-colors"
            aria-label="Open menu"
            @click="sidebarOpen = true"
          >
            <UiIcon name="Menu" :size="20" />
          </button>
          <UiLogo size="sm" />
        </div>
        <div class="flex items-center gap-4">
          <NuxtLink
            :to="localePath('/')"
            class="hidden sm:flex items-center gap-2 font-mono text-sm text-surface-500 hover:text-surface-900 dark:text-surface-400 dark:hover:text-surface-200 transition-colors"
          >
            <UiIcon name="ExternalLink" :size="14" />
            <span>Back to website</span>
          </NuxtLink>
          <button
            v-if="theme"
            type="button"
            class="flex items-center justify-center w-9 h-9 rounded-lg text-surface-500 hover:text-surface-900 dark:text-surface-400 dark:hover:text-surface-100 hover:bg-surface-200 dark:hover:bg-surface-800 transition-colors"
            :aria-label="theme.isDark ? 'Switch to light mode' : 'Switch to dark mode'"
            @click="theme.toggle()"
          >
            <UiIcon v-if="theme.isDark" name="Sun" :size="20" />
            <UiIcon v-else name="Moon" :size="20" />
          </button>
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
    </header>

    <div class="flex flex-1 min-h-0">
      <!-- Mobile overlay -->
      <div
        v-if="sidebarOpen"
        class="fixed inset-0 z-40 bg-surface-900/80 dark:bg-surface-950/80 backdrop-blur-sm lg:hidden"
        aria-hidden="true"
        @click="sidebarOpen = false"
      />

      <!-- Sidebar: drawer on mobile, fixed on desktop -->
      <aside
        class="fixed lg:sticky top-0 left-0 z-50 h-full w-64 flex-shrink-0 border-r border-surface-200 bg-surface-100 dark:border-surface-800 dark:bg-surface-900 flex flex-col transition-transform duration-300 ease-out lg:translate-x-0"
        :class="sidebarOpen ? 'translate-x-0' : '-translate-x-full'"
      >
        <div class="flex items-center justify-between h-14 px-4 border-b border-surface-800 lg:hidden">
          <span class="font-mono text-sm font-medium text-surface-300">Menu</span>
          <button
            type="button"
            class="flex items-center justify-center w-10 h-10 rounded-xl text-surface-400 hover:text-surface-100 hover:bg-surface-800 transition-colors"
            aria-label="Close menu"
            @click="sidebarOpen = false"
          >
            <UiIcon name="X" :size="20" />
          </button>
        </div>
        <nav class="flex-1 overflow-y-auto py-4">
          <div class="px-3 mb-4">
            <span class="text-xs font-mono font-medium uppercase tracking-wider text-surface-500 dark:text-surface-500">Dashboard</span>
          </div>
          <ul class="space-y-0.5 px-3">
            <li>
              <NuxtLink
                :to="localePath('/dashboard')"
                class="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-colors"
                :class="isActive('/dashboard') ? 'bg-surface-200 text-surface-900 border-l-2 border-primary-500 -ml-px pl-[11px] dark:bg-surface-800 dark:text-surface-100' : 'text-surface-600 hover:text-surface-900 hover:bg-surface-200 dark:text-surface-400 dark:hover:text-surface-100 dark:hover:bg-surface-800'"
                @click="sidebarOpen = false"
              >
                <UiIcon name="LayoutDashboard" :size="18" class="flex-shrink-0" />
                Overview
              </NuxtLink>
            </li>
          </ul>

          <div class="px-3 mt-6 mb-4">
            <span class="text-xs font-mono font-medium uppercase tracking-wider text-surface-500 dark:text-surface-500">Content</span>
          </div>
          <ul class="space-y-0.5 px-3">
            <li>
              <NuxtLink
                :to="localePath('/account/branding')"
                class="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-colors"
                :class="isActive('/account/branding') ? 'bg-surface-200 text-surface-900 border-l-2 border-primary-500 -ml-px pl-[11px] dark:bg-surface-800 dark:text-surface-100' : 'text-surface-600 hover:text-surface-900 hover:bg-surface-200 dark:text-surface-400 dark:hover:text-surface-100 dark:hover:bg-surface-800'"
                @click="sidebarOpen = false"
              >
                <UiIcon name="Image" :size="18" class="flex-shrink-0" />
                Branding
              </NuxtLink>
            </li>
            <li>
              <NuxtLink
                :to="localePath('/strategies')"
                class="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-colors"
                :class="isActive('/strategies') ? 'bg-surface-200 text-surface-900 border-l-2 border-primary-500 -ml-px pl-[11px] dark:bg-surface-800 dark:text-surface-100' : 'text-surface-600 hover:text-surface-900 hover:bg-surface-200 dark:text-surface-400 dark:hover:text-surface-100 dark:hover:bg-surface-800'"
                @click="sidebarOpen = false"
              >
                <UiIcon name="Target" :size="18" class="flex-shrink-0" />
                Strategies
              </NuxtLink>
            </li>
            <li>
              <NuxtLink
                :to="localePath('/publish')"
                class="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-colors"
                :class="isActive('/publish') ? 'bg-surface-200 text-surface-900 border-l-2 border-primary-500 -ml-px pl-[11px] dark:bg-surface-800 dark:text-surface-100' : 'text-surface-600 hover:text-surface-900 hover:bg-surface-200 dark:text-surface-400 dark:hover:text-surface-100 dark:hover:bg-surface-800'"
                @click="sidebarOpen = false"
              >
                <UiIcon name="Send" :size="18" class="flex-shrink-0" />
                Publish
              </NuxtLink>
            </li>
            <li>
              <NuxtLink
                :to="localePath('/schedule')"
                class="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-colors"
                :class="isActive('/schedule') ? 'bg-surface-200 text-surface-900 border-l-2 border-primary-500 -ml-px pl-[11px] dark:bg-surface-800 dark:text-surface-100' : 'text-surface-600 hover:text-surface-900 hover:bg-surface-200 dark:text-surface-400 dark:hover:text-surface-100 dark:hover:bg-surface-800'"
                @click="sidebarOpen = false"
              >
                <UiIcon name="Calendar" :size="18" class="flex-shrink-0" />
                Schedule
              </NuxtLink>
            </li>
            <li>
              <NuxtLink
                :to="localePath('/videos')"
                class="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-colors"
                :class="isActive('/videos') ? 'bg-surface-200 text-surface-900 border-l-2 border-primary-500 -ml-px pl-[11px] dark:bg-surface-800 dark:text-surface-100' : 'text-surface-600 hover:text-surface-900 hover:bg-surface-200 dark:text-surface-400 dark:hover:text-surface-100 dark:hover:bg-surface-800'"
                @click="sidebarOpen = false"
              >
                <UiIcon name="Video" :size="18" class="flex-shrink-0" />
                Videos
              </NuxtLink>
            </li>
            <li>
              <NuxtLink
                :to="localePath('/editor')"
                class="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-colors"
                :class="isActive('/editor') ? 'bg-surface-200 text-surface-900 border-l-2 border-primary-500 -ml-px pl-[11px] dark:bg-surface-800 dark:text-surface-100' : 'text-surface-600 hover:text-surface-900 hover:bg-surface-200 dark:text-surface-400 dark:hover:text-surface-100 dark:hover:bg-surface-800'"
                @click="sidebarOpen = false"
              >
                <UiIcon name="Scissors" :size="18" class="flex-shrink-0" />
                Editor
              </NuxtLink>
            </li>
            <li>
              <NuxtLink
                :to="localePath('/analytics')"
                class="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-colors"
                :class="isActive('/analytics') ? 'bg-surface-200 text-surface-900 border-l-2 border-primary-500 -ml-px pl-[11px] dark:bg-surface-800 dark:text-surface-100' : 'text-surface-600 hover:text-surface-900 hover:bg-surface-200 dark:text-surface-400 dark:hover:text-surface-100 dark:hover:bg-surface-800'"
                @click="sidebarOpen = false"
              >
                <UiIcon name="BarChart3" :size="18" class="flex-shrink-0" />
                Analytics
              </NuxtLink>
            </li>
          </ul>

          <div class="px-3 mt-6 mb-4">
            <span class="text-xs font-mono font-medium uppercase tracking-wider text-surface-500 dark:text-surface-500">Account</span>
          </div>
          <ul class="space-y-0.5 px-3">
            <li>
              <NuxtLink
                :to="localePath('/account/profile')"
                class="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-colors"
                :class="isActive('/account/profile') ? 'bg-surface-200 text-surface-900 border-l-2 border-primary-500 -ml-px pl-[11px] dark:bg-surface-800 dark:text-surface-100' : 'text-surface-600 hover:text-surface-900 hover:bg-surface-200 dark:text-surface-400 dark:hover:text-surface-100 dark:hover:bg-surface-800'"
                @click="sidebarOpen = false"
              >
                <UiIcon name="User" :size="18" class="flex-shrink-0" />
                Profile
              </NuxtLink>
            </li>
            <li>
              <NuxtLink
                :to="localePath('/account/preferences')"
                class="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-colors"
                :class="isActive('/account/preferences') ? 'bg-surface-200 text-surface-900 border-l-2 border-primary-500 -ml-px pl-[11px] dark:bg-surface-800 dark:text-surface-100' : 'text-surface-600 hover:text-surface-900 hover:bg-surface-200 dark:text-surface-400 dark:hover:text-surface-100 dark:hover:bg-surface-800'"
                @click="sidebarOpen = false"
              >
                <UiIcon name="Settings" :size="18" class="flex-shrink-0" />
                Preferences
              </NuxtLink>
            </li>
            <li>
              <NuxtLink
                :to="localePath('/account/connected-platforms')"
                class="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-colors"
                :class="isActive('/account/connected-platforms') ? 'bg-surface-200 text-surface-900 border-l-2 border-primary-500 -ml-px pl-[11px] dark:bg-surface-800 dark:text-surface-100' : 'text-surface-600 hover:text-surface-900 hover:bg-surface-200 dark:text-surface-400 dark:hover:text-surface-100 dark:hover:bg-surface-800'"
                @click="sidebarOpen = false"
              >
                <UiIcon name="Link2" :size="18" class="flex-shrink-0" />
                Connected Platforms
              </NuxtLink>
            </li>
          </ul>
        </nav>
      </aside>

      <!-- Main content -->
      <main class="flex-1 min-w-0">
        <slot />
      </main>
    </div>

    <UiToast />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
const localePath = useLocalePath()
const route = useRoute()
const auth = useAuthStore()
const theme = import.meta.client ? useThemeStore() : null

const sidebarOpen = ref(false)

onMounted(() => {
  auth.initialize()
})

const accountLinks = [
  { to: '/account/profile', label: 'Profile', icon: 'User' },
  { to: '/account/preferences', label: 'Preferences', icon: 'Settings' },
  { to: '/account/branding', label: 'Branding', icon: 'Image' },
  { to: '/account/connected-platforms', label: 'Connected Platforms', icon: 'Link2' },
]

function isActive(path: string): boolean {
  const current = route.path
  if (path === '/dashboard') return current === '/dashboard' || current === '/'
  return current === path || current.startsWith(path + '/')
}

async function signOut() {
  await auth.logout()
}
</script>
