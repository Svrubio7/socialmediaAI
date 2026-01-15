<template>
  <div class="min-h-screen flex flex-col">
    <!-- Header -->
    <header class="sticky top-0 z-50 bg-surface-950/80 backdrop-blur-lg border-b border-surface-800">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <!-- Logo -->
          <NuxtLink to="/" class="flex items-center space-x-2">
            <div class="w-8 h-8 bg-gradient-to-br from-primary-500 to-accent-500 rounded-lg flex items-center justify-center">
              <span class="text-white font-bold text-lg">S</span>
            </div>
            <span class="font-display font-bold text-xl gradient-text">SocialAI</span>
          </NuxtLink>

          <!-- Navigation -->
          <nav v-if="user" class="hidden md:flex items-center space-x-1">
            <NuxtLink
              v-for="item in navItems"
              :key="item.to"
              :to="item.to"
              class="px-4 py-2 rounded-lg text-surface-400 hover:text-surface-100 hover:bg-surface-800 transition-colors"
              active-class="text-surface-100 bg-surface-800"
            >
              {{ item.label }}
            </NuxtLink>
          </nav>

          <!-- User menu -->
          <div class="flex items-center space-x-4">
            <template v-if="user">
              <button
                @click="handleLogout"
                class="btn-ghost text-sm"
              >
                Logout
              </button>
            </template>
            <template v-else>
              <NuxtLink to="/auth/login" class="btn-ghost text-sm">
                Login
              </NuxtLink>
              <NuxtLink to="/auth/register" class="btn-primary text-sm">
                Get Started
              </NuxtLink>
            </template>
          </div>
        </div>
      </div>
    </header>

    <!-- Main content -->
    <main class="flex-1">
      <slot />
    </main>

    <!-- Footer -->
    <footer class="border-t border-surface-800 py-8 mt-auto">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex flex-col md:flex-row items-center justify-between gap-4">
          <p class="text-surface-500 text-sm">
            © {{ new Date().getFullYear() }} Social Media AI. All rights reserved.
          </p>
          <div class="flex items-center space-x-6">
            <NuxtLink to="/privacy" class="text-surface-500 hover:text-surface-300 text-sm">
              Privacy
            </NuxtLink>
            <NuxtLink to="/terms" class="text-surface-500 hover:text-surface-300 text-sm">
              Terms
            </NuxtLink>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
const user = useSupabaseUser()
const supabase = useSupabaseClient()

const navItems = [
  { label: 'Dashboard', to: '/dashboard' },
  { label: 'Videos', to: '/videos' },
  { label: 'Strategies', to: '/strategies' },
  { label: 'Scripts', to: '/scripts' },
  { label: 'Publish', to: '/publish' },
  { label: 'Analytics', to: '/analytics' },
]

const handleLogout = async () => {
  await supabase.auth.signOut()
  navigateTo('/')
}
</script>
