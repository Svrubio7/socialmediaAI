<template>
  <footer class="bg-surface-50 dark:bg-surface-950">
    <div class="container-wide">
      <!-- Main Footer -->
      <div class="py-16 grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-8 lg:gap-12">
        <!-- Brand -->
        <div class="col-span-2 lg:col-span-2">
          <UiLogo size="sm" class="mb-4" />
          <p class="font-mono text-surface-600 text-sm max-w-xs mb-6 leading-relaxed dark:text-surface-500">
            {{ $t('footer.description') }}
          </p>
          <div class="flex items-center gap-2">
            <a 
              v-for="social in socials" 
              :key="social.name"
              :href="social.href"
              target="_blank"
              rel="noopener noreferrer"
              class="p-2 rounded-lg text-surface-600 hover:text-surface-900 hover:bg-surface-200 dark:text-surface-500 dark:hover:text-surface-200 dark:hover:bg-surface-800 transition-colors"
              :aria-label="social.name"
            >
              <UiIcon :name="social.icon" :size="18" />
            </a>
          </div>
        </div>
        
        <!-- Links -->
        <div>
          <h4 class="font-mono text-surface-900 text-sm mb-4 dark:text-surface-200">{{ $t('footer.product') }}</h4>
          <ul class="space-y-3">
            <li>
              <NuxtLink :to="localePath('/#features')" class="font-mono text-sm text-surface-600 hover:text-surface-900 dark:text-surface-500 dark:hover:text-surface-200 transition-colors">
                {{ $t('footer.features') }}
              </NuxtLink>
            </li>
            <li>
              <NuxtLink :to="localePath('/pricing')" class="font-mono text-sm text-surface-600 hover:text-surface-900 dark:text-surface-500 dark:hover:text-surface-200 transition-colors">
                {{ $t('footer.pricing') }}
              </NuxtLink>
            </li>
            <li>
              <NuxtLink to="/changelog" class="font-mono text-sm text-surface-600 hover:text-surface-900 dark:text-surface-500 dark:hover:text-surface-200 transition-colors">
                {{ $t('footer.changelog') }}
              </NuxtLink>
            </li>
          </ul>
        </div>

        <div>
          <h4 class="font-mono text-surface-900 text-sm mb-4 dark:text-surface-200">{{ $t('footer.resources') }}</h4>
          <ul class="space-y-3">
            <li>
              <NuxtLink to="/docs" class="font-mono text-sm text-surface-600 hover:text-surface-900 dark:text-surface-500 dark:hover:text-surface-200 transition-colors">
                {{ $t('footer.documentation') }}
              </NuxtLink>
            </li>
            <li>
              <NuxtLink to="/api" class="font-mono text-sm text-surface-600 hover:text-surface-900 dark:text-surface-500 dark:hover:text-surface-200 transition-colors">
                {{ $t('footer.api') }}
              </NuxtLink>
            </li>
            <li>
              <NuxtLink to="/blog" class="font-mono text-sm text-surface-600 hover:text-surface-900 dark:text-surface-500 dark:hover:text-surface-200 transition-colors">
                {{ $t('footer.blog') }}
              </NuxtLink>
            </li>
          </ul>
        </div>

        <div>
          <h4 class="font-mono text-surface-900 text-sm mb-4 dark:text-surface-200">{{ $t('footer.company') }}</h4>
          <ul class="space-y-3">
            <li>
              <NuxtLink :to="localePath('/about')" class="font-mono text-sm text-surface-600 hover:text-surface-900 dark:text-surface-500 dark:hover:text-surface-200 transition-colors">
                {{ $t('footer.about') }}
              </NuxtLink>
            </li>
            <li>
              <NuxtLink :to="localePath('/contact')" class="font-mono text-sm text-surface-600 hover:text-surface-900 dark:text-surface-500 dark:hover:text-surface-200 transition-colors">
                {{ $t('footer.contact') }}
              </NuxtLink>
            </li>
            <li>
              <NuxtLink to="/careers" class="font-mono text-sm text-surface-600 hover:text-surface-900 dark:text-surface-500 dark:hover:text-surface-200 transition-colors">
                {{ $t('footer.careers') }}
              </NuxtLink>
            </li>
          </ul>
        </div>
      </div>
      
      <!-- Bottom Bar -->
      <div class="py-6">
        <div class="flex flex-col md:flex-row items-center justify-between gap-4">
          <p class="font-mono text-surface-600 text-sm dark:text-surface-600">
            © {{ new Date().getFullYear() }} {{ $t('footer.copyright') }}
          </p>
          <div class="flex items-center gap-6">
            <NuxtLink to="/privacy" class="font-mono text-surface-600 hover:text-surface-900 dark:hover:text-surface-400 text-sm transition-colors">
              {{ $t('footer.privacy') }}
            </NuxtLink>
            <NuxtLink to="/terms" class="font-mono text-surface-600 hover:text-surface-900 dark:hover:text-surface-400 text-sm transition-colors">
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
