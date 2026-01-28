/**
 * User preferences from localStorage (language, timezone, notifications).
 * Used for schedule display and form defaults.
 */

const PREFS_KEY = 'elevo_preferences'

export interface UserPreferences {
  language?: string
  timezone?: string
  emailNotifications?: boolean
}

export function usePreferences() {
  const timezone = ref('UTC')

  function load() {
    if (import.meta.client) {
      try {
        const raw = localStorage.getItem(PREFS_KEY)
        if (raw) {
          const p = JSON.parse(raw) as UserPreferences
          timezone.value = p.timezone ?? 'UTC'
        }
      } catch {
        // ignore
      }
    }
  }

  function formatInUserTz(iso: string, options: Intl.DateTimeFormatOptions = {}) {
    load()
    return new Date(iso).toLocaleString('en-US', {
      timeZone: timezone.value,
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      ...options,
    })
  }

  onMounted(load)

  return {
    timezone: readonly(timezone),
    load,
    formatInUserTz,
  }
}
