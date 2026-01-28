<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition duration-300 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition duration-200 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div v-if="modelValue" class="fixed inset-0 z-50 lg:hidden">
        <!-- Backdrop -->
        <div 
          class="absolute inset-0 bg-surface-900/95 backdrop-blur-sm"
          @click="close"
        />
        
        <!-- Drawer -->
        <Transition
          enter-active-class="transition duration-300 ease-out-expo"
          enter-from-class="translate-x-full"
          enter-to-class="translate-x-0"
          leave-active-class="transition duration-200 ease-in"
          leave-from-class="translate-x-0"
          leave-to-class="translate-x-full"
        >
          <div
            v-if="modelValue"
            class="absolute right-0 top-0 h-full w-80 max-w-[calc(100vw-3rem)] bg-surface-800 border-l border-surface-700 shadow-2xl"
          >
            <!-- Header -->
            <div class="flex items-center justify-between p-4 border-b border-surface-700">
              <UiLogo size="sm" />
              <button
                class="p-2 rounded-lg text-surface-400 hover:text-surface-100 hover:bg-surface-700 transition-colors"
                @click="close"
              >
                <UiIcon name="X" :size="24" />
              </button>
            </div>
            
            <!-- Navigation -->
            <nav class="p-4 space-y-1">
              <NuxtLink
                v-for="item in navItems"
                :key="item.to"
                :to="localePath(item.to)"
                class="flex items-center gap-3 px-4 py-3 rounded-xl text-surface-300 hover:text-surface-100 hover:bg-surface-700 transition-all"
                active-class="text-surface-100 bg-surface-700"
                @click="close"
              >
                <UiIcon :name="item.icon" :size="20" class="text-surface-500" />
                <span class="font-medium">{{ item.label }}</span>
              </NuxtLink>
            </nav>
            
            <!-- Language Switcher -->
            <div class="px-4 py-4 border-t border-surface-700">
              <p class="text-sm text-surface-500 mb-3 px-4">Language</p>
              <div class="grid grid-cols-2 gap-2">
                <button
                  v-for="loc in availableLocales"
                  :key="loc.code"
                  class="px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                  :class="loc.code === currentLocale 
                    ? 'bg-primary-500/20 text-primary-400 border border-primary-500/30' 
                    : 'bg-surface-700 text-surface-300 hover:bg-surface-600'"
                  @click="switchLocale(loc.code)"
                >
                  {{ loc.name }}
                </button>
              </div>
            </div>
            
            <!-- Footer -->
            <div class="absolute bottom-0 left-0 right-0 p-4 border-t border-surface-700">
              <template v-if="user">
                <div class="mb-4 px-4 py-3 rounded-xl bg-surface-700/50">
                  <p class="text-sm text-surface-400">Signed in as</p>
                  <p class="text-sm font-medium text-surface-100 truncate">{{ user.email }}</p>
                </div>
                <UiButton variant="ghost" full-width @click="$emit('logout')">
                  <UiIcon name="LogOut" :size="18" />
                  <span>Sign out</span>
                </UiButton>
              </template>
              <template v-else>
                <div class="space-y-2">
                  <NuxtLink :to="localePath('/dashboard')" class="btn-accent w-full justify-center" @click="close">
                    Go to App
                  </NuxtLink>
                  <NuxtLink :to="localePath('/auth/login')" class="btn-ghost w-full justify-center" @click="close">
                    Sign in
                  </NuxtLink>
                </div>
              </template>
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import type { User } from '@supabase/supabase-js'

const { locale, locales, setLocale } = useI18n()
const localePath = useLocalePath()

interface NavItem {
  label: string
  to: string
  icon: string
}

interface Props {
  modelValue: boolean
  navItems: NavItem[]
  user: User | null
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'logout'): void
}>()

const close = () => {
  emit('update:modelValue', false)
}

const currentLocale = computed(() => locale.value)

const availableLocales = computed(() => {
  return (locales.value as Array<{ code: string; name: string }>).map(l => ({
    code: l.code,
    name: l.name,
  }))
})

const switchLocale = (code: string) => {
  setLocale(code)
}

// Prevent body scroll when open
watch(() => props.modelValue, (isOpen) => {
  if (isOpen) {
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
  }
})
</script>
