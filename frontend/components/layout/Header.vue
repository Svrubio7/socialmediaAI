<template>
  <header 
    class="fixed top-0 left-0 right-0 z-50"
    :class="isScrolled ? 'header-scrolled' : 'bg-transparent'"
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
            class="font-mono text-sm text-surface-300 hover:text-surface-50"
            style="white-space: nowrap;"
          >
            {{ $t(item.label) }}
          </NuxtLink>
        </nav>

        <!-- Desktop Actions -->
        <div class="hidden lg:flex items-center" style="gap: 20px;">
          <!-- Language Switcher -->
          <UiDropdown align="right" width="sm">
            <template #trigger="{ open }">
              <button 
                class="flex items-center font-mono text-sm text-surface-300 hover:text-surface-50"
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
                class="w-full px-4 py-2 text-left font-mono text-sm text-surface-300 hover:text-surface-50 hover:bg-white/5"
                :class="{ 'text-primary-400': loc.code === currentLocale }"
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

        <!-- Mobile Menu Button -->
        <button
          class="lg:hidden p-2 rounded-lg text-surface-300 hover:text-surface-50 hover:bg-white/5"
          @click="mobileMenuOpen = true"
        >
          <UiIcon name="Menu" :size="22" />
        </button>
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
const { locale, locales, setLocale } = useI18n()
const localePath = useLocalePath()
const user = useSupabaseUser()
const supabase = useSupabaseClient()

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

const currentLocale = computed(() => locale.value)
const currentLocaleName = computed(() => {
  const loc = availableLocales.value.find(l => l.code === locale.value)
  return loc?.name || 'EN'
})

const availableLocales = computed(() => {
  return (locales.value as Array<{ code: string; name: string }>).map(l => ({
    code: l.code,
    name: l.name,
  }))
})

const switchLocale = (code: string) => {
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
.header-scrolled {
  background: rgba(10, 10, 9, 0.7);
  backdrop-filter: blur(24px) saturate(180%);
  -webkit-backdrop-filter: blur(24px) saturate(180%);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  box-shadow: 
    0 4px 30px rgba(0, 0, 0, 0.15),
    inset 0 1px 0 rgba(255, 255, 255, 0.05);
}
</style>
