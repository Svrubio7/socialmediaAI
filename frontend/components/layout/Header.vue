<template>
  <header 
    class="fixed top-0 left-0 right-0 z-50 transition-all duration-300"
    :class="isScrolled ? 'bg-surface-900/90 backdrop-blur-xl border-b border-surface-700/50' : 'bg-transparent'"
  >
    <div class="container-wide">
      <div class="flex items-center justify-between h-16 lg:h-20">
        <!-- Logo -->
        <UiLogo size="md" />

        <!-- Desktop Navigation -->
        <nav class="hidden lg:flex items-center gap-1">
          <NuxtLink
            v-for="item in navItems"
            :key="item.to"
            :to="localePath(item.to)"
            class="px-4 py-2 text-sm font-medium text-surface-300 hover:text-surface-100 transition-colors rounded-lg hover:bg-surface-700/30"
          >
            {{ $t(item.label) }}
          </NuxtLink>
        </nav>

        <!-- Desktop Actions -->
        <div class="hidden lg:flex items-center gap-3">
          <!-- Language Switcher -->
          <UiDropdown align="right" width="sm">
            <template #trigger="{ open }">
              <button 
                class="flex items-center gap-2 px-3 py-2 text-sm text-surface-300 hover:text-surface-100 rounded-lg hover:bg-surface-700/30 transition-colors"
              >
                <UiIcon name="Globe" :size="16" />
                <span>{{ currentLocaleName }}</span>
                <UiIcon name="ChevronDown" :size="14" :class="{ 'rotate-180': open }" class="transition-transform" />
              </button>
            </template>
            <div class="py-1">
              <button
                v-for="loc in availableLocales"
                :key="loc.code"
                class="w-full px-4 py-2 text-left text-sm text-surface-300 hover:text-surface-100 hover:bg-surface-700/50 transition-colors"
                :class="{ 'text-primary-400': loc.code === currentLocale }"
                @click="switchLocale(loc.code)"
              >
                {{ loc.name }}
              </button>
            </div>
          </UiDropdown>

          <NuxtLink :to="localePath('/dashboard')" class="btn-primary text-sm">
            {{ $t('nav.goToApp') }}
          </NuxtLink>
        </div>

        <!-- Mobile Menu Button -->
        <button
          class="lg:hidden p-2 rounded-lg text-surface-300 hover:text-surface-100 hover:bg-surface-700/30 transition-colors"
          @click="mobileMenuOpen = true"
        >
          <UiIcon name="Menu" :size="24" />
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
    isScrolled.value = window.scrollY > 50
  }
  window.addEventListener('scroll', handleScroll)
  handleScroll()
  
  onUnmounted(() => {
    window.removeEventListener('scroll', handleScroll)
  })
})
</script>
