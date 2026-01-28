<template>
  <div class="container-wide py-8 lg:py-10">
    <NuxtLink
      :to="localePath('/dashboard')"
      class="inline-flex items-center gap-2 text-sm text-surface-400 hover:text-surface-200 mb-6 transition-colors"
    >
      <UiIcon name="ArrowLeft" :size="16" />
      Back to Dashboard
    </NuxtLink>

    <h1 class="text-3xl lg:text-4xl font-mono font-bold text-surface-100 mb-2">Preferences</h1>
    <p class="text-surface-400 mb-8">Language, timezone, and notification settings</p>

    <Card class="max-w-xl border-l-4 border-l-accent-500">
      <form @submit.prevent="savePreferences" class="space-y-6">
        <div>
          <label class="label">Language</label>
          <select v-model="language" class="input w-full max-w-xs">
            <option value="en">English</option>
            <option value="es">Español</option>
            <option value="fr">Français</option>
            <option value="de">Deutsch</option>
          </select>
        </div>
        <div>
          <label class="label">Timezone</label>
          <select v-model="timezone" class="input w-full max-w-xs">
            <option v-for="tz in commonTimezones" :key="tz.value" :value="tz.value">{{ tz.label }}</option>
          </select>
          <p class="text-surface-500 text-sm mt-1">Used for scheduling and displaying post times</p>
        </div>
        <div>
          <label class="flex items-center gap-3 cursor-pointer">
            <input v-model="emailNotifications" type="checkbox" class="rounded border-surface-600 bg-surface-800 text-primary-500 focus:ring-primary-500" />
            <span class="text-surface-200">Email notifications for scheduled posts</span>
          </label>
        </div>
        <div class="pt-2">
          <Button type="submit" variant="primary" :loading="saving" :disabled="saving">
            <UiIcon name="Save" :size="18" />
            Save preferences
          </Button>
        </div>
      </form>
    </Card>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'app',
  middleware: 'auth',
})

const localePath = useLocalePath()
const saving = ref(false)

const language = ref('en')
const timezone = ref('UTC')
const emailNotifications = ref(true)

const commonTimezones = [
  { value: 'UTC', label: 'UTC' },
  { value: 'Europe/Madrid', label: 'Europe/Madrid' },
  { value: 'Europe/Paris', label: 'Europe/Paris' },
  { value: 'America/New_York', label: 'America/New_York' },
  { value: 'America/Los_Angeles', label: 'America/Los_Angeles' },
  { value: 'America/Mexico_City', label: 'America/Mexico_City' },
  { value: 'Asia/Tokyo', label: 'Asia/Tokyo' },
  { value: 'Australia/Sydney', label: 'Australia/Sydney' },
]

function loadPreferences() {
  if (import.meta.client) {
    const stored = localStorage.getItem('elevo_preferences')
    if (stored) {
      try {
        const p = JSON.parse(stored)
        language.value = p.language ?? language.value
        timezone.value = p.timezone ?? timezone.value
        emailNotifications.value = p.emailNotifications ?? emailNotifications.value
      } catch {
        // ignore
      }
    }
  }
}

async function savePreferences() {
  saving.value = true
  try {
    if (import.meta.client) {
      localStorage.setItem(
        'elevo_preferences',
        JSON.stringify({
          language: language.value,
          timezone: timezone.value,
          emailNotifications: emailNotifications.value,
        })
      )
    }
    await new Promise((r) => setTimeout(r, 400))
  } finally {
    saving.value = false
  }
}

onMounted(loadPreferences)
</script>
