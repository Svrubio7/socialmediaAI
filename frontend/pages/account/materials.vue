<template>
  <div class="container-wide py-8 lg:py-10">
    <NuxtLink
      :to="localePath('/dashboard')"
      class="inline-flex items-center gap-2 text-sm text-surface-400 hover:text-surface-200 mb-6 transition-colors"
    >
      <UiIcon name="ArrowLeft" :size="16" />
      Back to Dashboard
    </NuxtLink>

    <h1 class="text-3xl lg:text-4xl font-mono font-bold text-surface-100 mb-2">My Materials</h1>
    <p class="text-surface-400 mb-8">Logos and brand assets for your content</p>

    <Card class="mb-8 border-l-4 border-l-primary-500">
      <div class="flex flex-col sm:flex-row sm:items-center gap-4 mb-6">
        <label class="flex items-center gap-2 px-4 py-2 rounded-xl bg-primary-500/20 text-primary-300 border border-primary-500/30 cursor-pointer hover:bg-primary-500/25 transition-colors">
          <UiIcon name="Upload" :size="18" />
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
          <Skeleton variant="rounded" width="80px" height="80px" />
          <Skeleton variant="text" width="160px" />
        </div>
      </div>
      <EmptyState
        v-else-if="items.length === 0"
        icon="Image"
        title="No materials yet"
        description="Upload logos or images to use in your content"
        variant="default"
      />
      <div v-else class="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div
          v-for="asset in items"
          :key="asset.id"
          class="p-4 rounded-xl bg-surface-800/50 border border-surface-700 flex flex-col items-center"
        >
          <div class="w-20 h-20 rounded-xl bg-surface-700 flex items-center justify-center mb-3 overflow-hidden">
            <UiIcon name="Image" :size="32" class="text-surface-500" />
          </div>
          <p class="font-medium text-surface-100 text-sm truncate w-full text-center">{{ asset.filename }}</p>
          <p class="text-surface-500 text-xs mt-0.5">{{ asset.type }}</p>
          <Button
            variant="ghost"
            size="sm"
            class="mt-3 text-red-400 hover:text-red-300 hover:bg-red-500/10"
            :disabled="deleting === asset.id"
            @click="deleteAsset(asset.id)"
          >
            <UiIcon name="Trash2" :size="16" />
            Delete
          </Button>
        </div>
      </div>
    </Card>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'app',
  middleware: 'auth',
})

const localePath = useLocalePath()
const api = useApi()

const loading = ref(true)
const uploading = ref(false)
const deleting = ref<string | null>(null)
const uploadType = ref('image')
const items = ref<any[]>([])

async function fetchMaterials() {
  loading.value = true
  try {
    const res = await api.materials.list()
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
    await api.materials.upload(file, uploadType.value)
    await fetchMaterials()
    input.value = ''
  } catch {
    // error feedback via toast later
  } finally {
    uploading.value = false
  }
}

async function deleteAsset(id: string) {
  deleting.value = id
  try {
    await api.materials.delete(id)
    items.value = items.value.filter((a) => a.id !== id)
  } catch {
    // keep list
  } finally {
    deleting.value = null
  }
}

onMounted(fetchMaterials)
</script>
