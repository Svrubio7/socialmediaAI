<template>
  <div class="container-wide py-8 lg:py-10">
    <NuxtLink
      :to="localePath('/dashboard')"
      class="inline-flex items-center gap-2 text-sm text-surface-400 hover:text-surface-200 mb-6 transition-colors"
    >
      <UiIcon name="ArrowLeft" :size="16" />
      Back to Dashboard
    </NuxtLink>

    <h1 class="text-xl lg:text-2xl font-mono font-normal text-surface-100">Profile</h1>
    <p class="text-surface-400 mt-1 text-sm mb-6">Your account information</p>

    <div v-if="loading" class="max-w-xl">
      <UiCard class="border-l-4 border-l-primary-500">
        <div class="flex flex-col sm:flex-row items-start gap-6">
          <UiSkeleton variant="rounded" width="96px" height="96px" />
          <div class="flex-1 space-y-4 w-full">
            <UiSkeleton variant="text" width="100%" height="32px" />
            <UiSkeleton variant="text" width="60%" height="24px" />
          </div>
        </div>
      </UiCard>
    </div>

    <div v-else-if="error" class="max-w-xl">
      <UiCard class="border-l-4 border-l-red-500">
        <p class="text-surface-100 font-medium">Could not load profile</p>
        <p class="text-surface-400 text-sm mt-1">{{ error }}</p>
        <UiButton variant="secondary" class="mt-4" @click="fetchProfile">Retry</UiButton>
      </UiCard>
    </div>

    <UiCard v-else class="max-w-xl border-l-4 border-l-primary-500">
      <form class="flex flex-col sm:flex-row items-start gap-6" @submit.prevent="save">
        <div class="w-24 h-24 rounded-2xl bg-primary-500/20 flex items-center justify-center flex-shrink-0 overflow-hidden">
          <img
            v-if="form.avatar_url"
            :src="form.avatar_url"
            alt="Avatar"
            class="w-full h-full object-cover"
          />
          <UiIcon v-else name="User" :size="48" class="text-primary-400" />
        </div>
        <div class="flex-1 min-w-0 space-y-4 w-full">
          <div>
            <label class="label">Email</label>
            <p class="font-medium text-surface-100">{{ profile?.email ?? '—' }}</p>
            <p class="text-surface-500 text-xs mt-1">Email cannot be changed here.</p>
          </div>
          <div>
            <label class="label" for="profile-name">Display name</label>
            <input
              id="profile-name"
              v-model="form.name"
              type="text"
              class="input"
              placeholder="Your name"
              maxlength="255"
            />
          </div>
          <div>
            <label class="label" for="profile-avatar">Avatar URL</label>
            <input
              id="profile-avatar"
              v-model="form.avatar_url"
              type="url"
              class="input"
              placeholder="https://..."
            />
          </div>
          <div class="flex items-center gap-3 pt-2">
            <UiButton type="submit" variant="primary" :disabled="saving">
              {{ saving ? 'Saving...' : 'Save' }}
            </UiButton>
            <UiButton type="button" variant="ghost" :disabled="saving" @click="resetForm">
              Reset
            </UiButton>
          </div>
        </div>
      </form>
    </UiCard>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
definePageMeta({
  layout: 'app-sidebar',
  middleware: 'auth',
})

const localePath = useLocalePath()
const api = useApi()
const auth = useAuthStore()

const loading = ref(true)
const error = ref<string | null>(null)
const saving = ref(false)
const profile = ref<{ id: string; email: string; name?: string; avatar_url?: string } | null>(null)

const form = ref({
  name: '',
  avatar_url: '',
})

async function fetchProfile() {
  loading.value = true
  error.value = null
  try {
    const res = await api.auth.getMe()
    profile.value = res
    form.value = {
      name: res.name ?? '',
      avatar_url: res.avatar_url ?? '',
    }
  } catch (e: any) {
    error.value = e?.data?.detail?.message ?? e?.message ?? 'Failed to load profile'
  } finally {
    loading.value = false
  }
}

function resetForm() {
  if (profile.value) {
    form.value = {
      name: profile.value.name ?? '',
      avatar_url: profile.value.avatar_url ?? '',
    }
  }
}

async function save() {
  saving.value = true
  try {
    const res = await api.auth.updateMe({
      name: form.value.name || undefined,
      avatar_url: form.value.avatar_url || undefined,
    })
    profile.value = res
    auth.setUser({
      id: auth.user!.id,
      email: auth.user!.email,
      name: res.name,
      avatar_url: res.avatar_url,
    })
  } catch (e: any) {
    error.value = e?.data?.detail?.message ?? e?.message ?? 'Failed to save profile'
  } finally {
    saving.value = false
  }
}

onMounted(fetchProfile)
</script>
