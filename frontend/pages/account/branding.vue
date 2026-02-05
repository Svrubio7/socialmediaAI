<template>
  <div class="container-wide py-6 lg:py-8">
    <NuxtLink
      :to="localePath('/dashboard')"
      class="inline-flex items-center gap-2 text-sm text-surface-400 hover:text-surface-200 mb-5 transition-colors"
    >
      <UiIcon name="ArrowLeft" :size="14" />
      Back to Dashboard
    </NuxtLink>

    <h1 class="text-xl lg:text-2xl font-mono font-normal text-surface-100">Branding</h1>
    <p class="text-surface-400 mt-1 text-sm mb-6">Logos and brand assets for your content</p>

    <UiCard class="mb-8 border-l-4 border-l-primary-500 bg-surface-700/30 dark:bg-surface-700/40 rounded-2xl">
      <div class="flex flex-col sm:flex-row sm:items-center gap-4 mb-6">
        <label class="flex items-center gap-2 px-4 py-2 rounded-xl bg-primary-500/20 text-primary-300 border border-primary-500/30 cursor-pointer hover:bg-primary-500/25 transition-colors">
          <UiIcon name="Upload" :size="16" />
          <span>Upload file</span>
          <input
            type="file"
            accept=".png,.jpg,.jpeg,.gif,.webp,.svg"
            class="hidden"
            @change="onFileSelect"
          />
        </label>
        <select v-model="uploadType" class="input w-auto">
          <option value="logo">Logo</option>
          <option value="image">Image</option>
          <option value="watermark">Watermark</option>
        </select>
        <p v-if="uploading" class="text-surface-400 text-sm">Uploading...</p>
      </div>

      <div v-if="loading" class="py-12 flex justify-center">
        <div class="flex flex-col items-center gap-3">
          <UiSkeleton variant="rounded" width="80px" height="80px" />
          <UiSkeleton variant="text" width="160px" />
        </div>
      </div>
      <SharedEmptyState
        v-else-if="items.length === 0"
        icon="Image"
        title="No branding yet"
        description="Upload logos or images to use in your content"
        variant="default"
      />
      <div v-else class="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div
          v-for="asset in items"
          :key="asset.id"
          class="p-4 rounded-xl bg-surface-600/25 dark:bg-surface-600/30 border border-surface-600/50 flex flex-col items-center"
        >
          <div class="w-20 h-20 rounded-xl bg-surface-600/40 flex items-center justify-center mb-3 overflow-hidden">
            <img v-if="asset.url" :src="asset.url" :alt="asset.filename" class="w-full h-full object-cover" />
            <UiIcon v-else name="Image" :size="32" class="text-surface-500" />
          </div>
          <p class="font-medium text-surface-100 text-sm truncate w-full text-center">{{ asset.filename }}</p>
          <p class="text-surface-500 text-xs mt-0.5">{{ asset.type }}</p>
          <UiButton
            variant="ghost"
            size="sm"
            class="rounded-xl mt-3 text-red-400 hover:text-red-300 hover:bg-red-500/10"
            :disabled="deleting === asset.id"
            @click="deleteAsset(asset.id)"
          >
            <template #icon-left><UiIcon name="Trash2" :size="14" /></template>
            Delete
          </UiButton>
        </div>
      </div>
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
const toast = useToast()

const loading = ref(true)
const uploading = ref(false)
const deleting = ref<string | null>(null)
const uploadType = ref('image')
const items = ref<any[]>([])

async function fetchBranding() {
  loading.value = true
  try {
    const res = await api.branding.list()
    items.value = (res as { items?: any[] })?.items ?? []
  } catch {
    items.value = []
  } finally {
    loading.value = false
  }
}

async function onFileSelect(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  uploading.value = true
  try {
    await api.branding.upload(file, uploadType.value)
    await fetchBranding()
    input.value = ''
    toast.success('File uploaded')
  } catch (e: any) {
    toast.error(e?.data?.detail ?? 'Upload failed')
  } finally {
    uploading.value = false
  }
}

async function deleteAsset(id: string) {
  deleting.value = id
  try {
    await api.branding.delete(id)
    items.value = items.value.filter((a) => a.id !== id)
    toast.success('Deleted')
  } catch (e: any) {
    toast.error(e?.data?.detail ?? 'Delete failed')
  } finally {
    deleting.value = null
  }
}

onMounted(fetchBranding)
</script>
