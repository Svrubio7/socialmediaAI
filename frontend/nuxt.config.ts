// @ts-nocheck
// https://nuxt.com/docs/api/configuration/nuxt-config
const supabaseUrl =
  process.env.NUXT_PUBLIC_SUPABASE_URL || 'https://example.supabase.co'
const supabaseKey =
  process.env.NUXT_PUBLIC_SUPABASE_KEY ||
  process.env.NUXT_PUBLIC_SUPABASE_ANON_KEY ||
  'sb_publishable_placeholder'

export default defineNuxtConfig({
  devtools: { enabled: process.env.NUXT_DEVTOOLS === 'true' },
  experimental: {
    appManifest: false,
  },

  modules: [
    '@nuxtjs/tailwindcss',
    '@nuxtjs/supabase',
    '@pinia/nuxt',
    '@vueuse/nuxt',
    '@nuxtjs/i18n',
  ],

  i18n: {
    locales: [
      { code: 'en', name: 'English', file: 'en.json' },
      { code: 'es', name: 'Español', file: 'es.json' },
      { code: 'fr', name: 'Français', file: 'fr.json' },
      { code: 'de', name: 'Deutsch', file: 'de.json' },
    ],
    defaultLocale: 'en',
    lazy: true,
    langDir: 'locales',
    strategy: 'prefix_except_default',
    detectBrowserLanguage: {
      useCookie: true,
      cookieKey: 'i18n_redirected',
      redirectOn: 'root',
    },
  },

  runtimeConfig: {
    public: {
      apiUrl: process.env.NUXT_PUBLIC_API_URL || '/api/v1',
      supabaseUrl,
      supabaseKey,
      supabaseStorageBucket: process.env.NUXT_PUBLIC_SUPABASE_STORAGE_BUCKET || 'videos',
      editorParityFlag: process.env.NUXT_PUBLIC_EDITOR_PARITY_FLAG || 'false',
      editorForkEnabled: process.env.NUXT_PUBLIC_EDITOR_FORK_ENABLED || 'false',
      editorForkRolloutPercent: process.env.NUXT_PUBLIC_EDITOR_FORK_ROLLOUT_PERCENT || '0',
      editorForkAllowlist: process.env.NUXT_PUBLIC_EDITOR_FORK_ALLOWLIST || '',
    },
  },

  supabase: {
    url: supabaseUrl,
    key: supabaseKey,
    redirectOptions: {
      login: '/auth/login',
      callback: '/auth/callback',
      exclude: ['/', '/about', '/pricing', '/contact', '/auth/*', '/es', '/es/*', '/fr', '/fr/*', '/de', '/de/*'],
    },
  },

  app: {
    pageTransition: { name: 'page', mode: 'out-in' },
    layoutTransition: { name: 'layout', mode: 'out-in' },
    head: {
      title: 'Elevo',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'description', content: 'Elevo - Elevate your business social media with AI-powered video analysis, strategy generation, and multi-platform publishing' },
      ],
      link: [
        { rel: 'icon', type: 'image/png', href: '/elevo_just_logo.png' },
        // Preconnect to Google Fonts for faster loading
        { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
        { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' },
        // Preload the actual font files for faster loading (prevents FOUT)
        { rel: 'preload', href: 'https://fonts.gstatic.com/s/spacemono/v14/i7dPIFZifjKcF5UAWdDRYEF8RQ.woff2', as: 'font', type: 'font/woff2', crossorigin: 'anonymous' },
        { rel: 'preload', href: 'https://fonts.gstatic.com/s/spacemono/v14/i7dMIFZifjKcF5UAWdDRaPpZUFWaHg.woff2', as: 'font', type: 'font/woff2', crossorigin: 'anonymous' },
        // Load Space Mono font CSS
        { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400;1,700&display=block' },
      ],
      // Add critical font-face CSS and loading screen inline
      style: [
        {
          children: `
            /* Critical font-face to ensure font is available immediately */
            @font-face {
              font-family: 'Space Mono';
              font-style: normal;
              font-weight: 400;
              font-display: block;
              src: url(https://fonts.gstatic.com/s/spacemono/v14/i7dPIFZifjKcF5UAWdDRYEF8RQ.woff2) format('woff2');
              unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;
            }
            @font-face {
              font-family: 'Space Mono';
              font-style: normal;
              font-weight: 700;
              font-display: block;
              src: url(https://fonts.gstatic.com/s/spacemono/v14/i7dMIFZifjKcF5UAWdDRaPpZUFWaHg.woff2) format('woff2');
              unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;
            }
            /* Ensure font is applied immediately */
            html, body {
              font-family: 'Space Mono', ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace !important;
            }
            /* Hide body until fonts are loaded */
            body {
              opacity: 0;
              transition: opacity 0.15s ease-in;
            }
            body.fonts-loaded {
              opacity: 1;
            }
          `,
        },
      ],
      // Theme: set dark class on <html> before paint to avoid flash
      script: [
        {
          children: `
            try {
              var t = localStorage.getItem('elevo-theme') || localStorage.getItem('elevoai-theme');
              if (t === 'light') document.documentElement.classList.remove('dark');
              else document.documentElement.classList.add('dark');
            } catch (e) {}
          `,
          type: 'text/javascript',
        },
        {
          children: `
            (function () {
              function markFontsLoaded() {
                if (!document.body) return false;
                document.body.classList.add('fonts-loaded');
                return true;
              }
              if (!markFontsLoaded()) {
                document.addEventListener('DOMContentLoaded', markFontsLoaded, { once: true });
              }
              if (document.fonts && document.fonts.ready) {
                document.fonts.ready.then(markFontsLoaded).catch(function () {});
              }
              setTimeout(markFontsLoaded, 500);
            })();
          `,
          type: 'text/javascript',
        },
      ],
    },
  },

  css: ['~/assets/css/main.css'],

  typescript: {
    strict: true,
    typeCheck: false,
  },

  compatibilityDate: '2024-11-01',
})
