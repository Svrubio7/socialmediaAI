<template>
  <header 
    class="fixed top-0 left-0 right-0 z-50 transition-colors duration-200"
    :class="isScrolled 
      ? 'bg-white/90 dark:bg-surface-950/90 backdrop-blur-[24px] border-b border-surface-200/80 dark:border-white/10 shadow-sm dark:shadow-black/20' 
      : 'bg-transparent'"
  >
    <div class="container-wide">
      <div class="flex items-center justify-between h-16">
        <!-- Logo -->
        <UiLogo size="sm" />

        <!-- Desktop Navigation -->
        <nav class="hidden lg:flex items-center" style="gap: 32px;">
          <NuxtLink
            v-for="item in navItems"
            :key="item.to"
            :to="localePath(item.to)"
            class="font-mono text-sm text-surface-600 hover:text-surface-950 dark:text-surface-300 dark:hover:text-surface-50"
            style="white-space: nowrap;"
          >
            {{ $t(item.label) }}
          </NuxtLink>
        </nav>

        <!-- Desktop Actions -->
        <div class="hidden lg:flex items-center" style="gap: 20px;">
          <!-- Theme toggle -->
          <button
            v-if="theme"
            type="button"
            class="flex items-center justify-center w-9 h-9 rounded-lg text-surface-500 hover:text-surface-900 dark:text-surface-400 dark:hover:text-surface-100 hover:bg-surface-200/80 dark:hover:bg-surface-800/50 transition-colors"
            :aria-label="theme.isDark ? 'Switch to light mode' : 'Switch to dark mode'"
            @click="theme.toggle()"
          >
            <UiIcon v-if="theme.isDark" name="Sun" :size="20" />
            <UiIcon v-else name="Moon" :size="20" />
          </button>
          <!-- Language Switcher -->
          <UiDropdown align="right" width="sm">
            <template #trigger="{ open }">
              <button 
                class="flex items-center font-mono text-sm text-surface-600 hover:text-surface-950 dark:text-surface-300 dark:hover:text-surface-50"
                style="gap: 6px;"
              >
                <span>{{ currentLocaleName }}</span>
                <UiIcon name="ChevronDown" :size="14" :class="{ 'rotate-180': open }" class="transition-transform" />
              </button>
            </template>
            <div class="py-1">
              <button
                v-for="loc in availableLocales"
                :key="loc.code"
                class="w-full px-4 py-2 text-left font-mono text-sm text-surface-600 hover:text-surface-950 dark:text-surface-300 dark:hover:text-surface-50 hover:bg-surface-200/50 dark:hover:bg-white/5"
                :class="{ 'text-primary-500 dark:text-primary-400': loc.code === currentLocale }"
                @click="switchLocale(loc.code)"
              >
                {{ loc.name }}
              </button>
            </div>
          </UiDropdown>

          <NuxtLink :to="localePath('/dashboard')" class="btn-accent btn-sm font-mono">
            {{ $t('nav.goToApp') }}
          </NuxtLink>
        </div>

        <!-- Mobile: theme + menu -->
        <div class="lg:hidden flex items-center gap-2">
          <button
            v-if="theme"
            type="button"
            class="p-2 rounded-lg text-surface-500 hover:text-surface-900 dark:text-surface-400 dark:hover:text-surface-100"
            :aria-label="theme.isDark ? 'Switch to light mode' : 'Switch to dark mode'"
            @click="theme.toggle()"
          >
            <UiIcon v-if="theme.isDark" name="Sun" :size="20" />
            <UiIcon v-else name="Moon" :size="20" />
          </button>
          <button
            class="p-2 rounded-lg text-surface-600 hover:text-surface-950 dark:text-surface-300 dark:hover:text-surface-50 hover:bg-surface-200/50 dark:hover:bg-white/5"
            @click="mobileMenuOpen = true"
          >
            <UiIcon name="Menu" :size="22" />
          </button>
        </div>
      </div>
    </div>

    <!-- Mobile Navigation -->
    <LayoutMobileNav 
      v-model="mobileMenuOpen" 
      :nav-items="mobileNavItems" 
      :user="user" 
      @logout="handleLogout" 
    />
  </header>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
const { locale, locales, setLocale } = useI18n()
const localePath = useLocalePath()
const user = useSupabaseUser()
const supabase = useSupabaseClient()
const theme = import.meta.client ? useThemeStore() : null

const mobileMenuOpen = ref(false)
const isScrolled = ref(false)

const navItems = [
  { label: 'nav.home', to: '/' },
  { label: 'nav.about', to: '/about' },
  { label: 'nav.pricing', to: '/pricing' },
  { label: 'nav.contact', to: '/contact' },
]

const mobileNavItems = computed(() => [
  { label: 'Home', to: '/', icon: 'Home' },
  { label: 'About Us', to: '/about', icon: 'Users' },
  { label: 'Pricing', to: '/pricing', icon: 'CreditCard' },
  { label: 'Contact', to: '/contact', icon: 'Mail' },
])

type LocaleCode = 'en' | 'es' | 'fr' | 'de'
const currentLocale = computed(() => locale.value as LocaleCode)
const currentLocaleName = computed(() => {
  const loc = availableLocales.value.find(l => l.code === currentLocale.value)
  return loc?.name || 'EN'
})

const availableLocales = computed(() => {
  return (locales.value as Array<{ code: LocaleCode; name: string }>).map(l => ({
    code: l.code,
    name: l.name,
  }))
})

const switchLocale = (code: LocaleCode) => {
  setLocale(code)
}

const handleLogout = async () => {
  await supabase.auth.signOut()
  mobileMenuOpen.value = false
  navigateTo('/')
}

// Handle scroll for header background
onMounted(() => {
  const handleScroll = () => {
    isScrolled.value = window.scrollY > 20
  }
  window.addEventListener('scroll', handleScroll)
  handleScroll()
  
  onUnmounted(() => {
    window.removeEventListener('scroll', handleScroll)
  })
})
</script>

<style scoped>
/* Backdrop blur for scrolled header (Tailwind handles colors) */
header:not(.bg-transparent) {
  backdrop-filter: blur(24px) saturate(180%);
  -webkit-backdrop-filter: blur(24px) saturate(180%);
}
</style>
