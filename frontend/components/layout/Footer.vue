<template>
  <footer class="border-t border-surface-700/50 bg-surface-900">
    <!-- Main Footer -->
    <div class="container-wide section-tight">
      <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-8 lg:gap-12">
        <!-- Brand -->
        <div class="col-span-2 lg:col-span-2">
          <UiLogo size="md" class="mb-4" />
          <p class="text-surface-400 text-sm max-w-xs mb-6">
            {{ $t('footer.description') }}
          </p>
          <div class="flex items-center gap-3">
            <a 
              v-for="social in socials" 
              :key="social.name"
              :href="social.href"
              target="_blank"
              rel="noopener noreferrer"
              class="p-2 rounded-lg text-surface-500 hover:text-surface-100 hover:bg-surface-700 transition-colors"
              :aria-label="social.name"
            >
              <UiIcon :name="social.icon" :size="20" />
            </a>
          </div>
        </div>
        
        <!-- Links -->
        <div>
          <h4 class="font-display font-semibold text-surface-100 mb-4">{{ $t('footer.product') }}</h4>
          <ul class="space-y-3">
            <li>
              <NuxtLink :to="localePath('/#features')" class="text-sm text-surface-400 hover:text-surface-100 transition-colors">
                {{ $t('footer.features') }}
              </NuxtLink>
            </li>
            <li>
              <NuxtLink :to="localePath('/pricing')" class="text-sm text-surface-400 hover:text-surface-100 transition-colors">
                {{ $t('footer.pricing') }}
              </NuxtLink>
            </li>
            <li>
              <NuxtLink to="/changelog" class="text-sm text-surface-400 hover:text-surface-100 transition-colors">
                {{ $t('footer.changelog') }}
              </NuxtLink>
            </li>
          </ul>
        </div>

        <div>
          <h4 class="font-display font-semibold text-surface-100 mb-4">{{ $t('footer.resources') }}</h4>
          <ul class="space-y-3">
            <li>
              <NuxtLink to="/docs" class="text-sm text-surface-400 hover:text-surface-100 transition-colors">
                {{ $t('footer.documentation') }}
              </NuxtLink>
            </li>
            <li>
              <NuxtLink to="/api" class="text-sm text-surface-400 hover:text-surface-100 transition-colors">
                {{ $t('footer.api') }}
              </NuxtLink>
            </li>
            <li>
              <NuxtLink to="/blog" class="text-sm text-surface-400 hover:text-surface-100 transition-colors">
                {{ $t('footer.blog') }}
              </NuxtLink>
            </li>
          </ul>
        </div>

        <div>
          <h4 class="font-display font-semibold text-surface-100 mb-4">{{ $t('footer.company') }}</h4>
          <ul class="space-y-3">
            <li>
              <NuxtLink :to="localePath('/about')" class="text-sm text-surface-400 hover:text-surface-100 transition-colors">
                {{ $t('footer.about') }}
              </NuxtLink>
            </li>
            <li>
              <NuxtLink :to="localePath('/contact')" class="text-sm text-surface-400 hover:text-surface-100 transition-colors">
                {{ $t('footer.contact') }}
              </NuxtLink>
            </li>
            <li>
              <NuxtLink to="/careers" class="text-sm text-surface-400 hover:text-surface-100 transition-colors">
                {{ $t('footer.careers') }}
              </NuxtLink>
            </li>
          </ul>
        </div>
      </div>
    </div>
    
    <!-- Bottom Bar -->
    <div class="border-t border-surface-700/50">
      <div class="container-wide py-6">
        <div class="flex flex-col md:flex-row items-center justify-between gap-4">
          <p class="text-surface-500 text-sm">
            © {{ new Date().getFullYear() }} {{ $t('footer.copyright') }}
          </p>
          <div class="flex items-center gap-6">
            <NuxtLink to="/privacy" class="text-surface-500 hover:text-surface-300 text-sm transition-colors">
              {{ $t('footer.privacy') }}
            </NuxtLink>
            <NuxtLink to="/terms" class="text-surface-500 hover:text-surface-300 text-sm transition-colors">
              {{ $t('footer.terms') }}
            </NuxtLink>
          </div>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
const localePath = useLocalePath()

const socials = [
  { name: 'Twitter', icon: 'Twitter', href: '#' },
  { name: 'GitHub', icon: 'Github', href: '#' },
  { name: 'LinkedIn', icon: 'Linkedin', href: '#' },
]
</script>
