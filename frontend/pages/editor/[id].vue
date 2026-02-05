<template>
  <div class="h-screen w-screen bg-surface-950 text-surface-100 overflow-hidden">
    <header class="h-14 border-b border-surface-800 px-4 lg:px-6 flex items-center justify-between gap-3">
      <div class="flex items-center gap-2 min-w-0">
        <UiButton variant="ghost" size="sm" :to="localePath('/editor')">
          <template #icon-left><UiIcon name="ArrowLeft" :size="14" /></template>
          Editor Hub
        </UiButton>
        <div class="hidden sm:block w-px h-5 bg-surface-700" />
        <p class="truncate text-sm font-medium">
          {{ video?.original_filename || video?.filename || 'Editor Workspace' }}
        </p>
      </div>
      <div class="flex items-center gap-3">
        <label class="inline-flex items-center gap-2 text-xs text-surface-400">
          <input v-model="saveToLibrary" type="checkbox" class="accent-primary-500" />
          Save edits to library
        </label>
        <UiButton v-if="lastOutputUrl" variant="secondary" size="sm" :href="lastOutputUrl" target="_blank" rel="noopener">
          <template #icon-left><UiIcon name="ExternalLink" :size="14" /></template>
          Open output
        </UiButton>
      </div>
    </header>

    <div class="h-[calc(100vh-56px)] grid grid-cols-1 xl:grid-cols-[360px_1fr_360px]">
      <!-- Left tools panel -->
      <aside class="border-r border-surface-800 overflow-y-auto p-4 space-y-4 bg-surface-900/60">
        <UiCard class="bg-surface-800/50 border border-surface-700">
          <p class="text-sm font-medium mb-3">Timeline</p>
          <div class="grid grid-cols-2 gap-3 mb-3">
            <UiInput v-model.number="trimStart" label="Start (s)" type="number" min="0" step="0.1" />
            <UiInput v-model.number="trimEnd" label="End (s)" type="number" min="0" step="0.1" />
          </div>
          <div class="grid grid-cols-2 gap-2">
            <UiButton size="sm" variant="secondary" :disabled="opRunning" @click="applyTrim">Trim</UiButton>
            <UiButton size="sm" variant="secondary" :disabled="opRunning" @click="applyClipOut">Clip out</UiButton>
            <UiButton size="sm" variant="ghost" :disabled="opRunning" @click="runSimple('duplicate_clip')">Duplicate</UiButton>
            <UiButton size="sm" variant="ghost" :disabled="opRunning" @click="runSimple('reverse_clip')">Reverse</UiButton>
          </div>
          <div class="grid grid-cols-2 gap-3 mt-3">
            <UiInput v-model.number="freezeAt" label="Freeze at (s)" type="number" min="0" step="0.1" />
            <UiInput v-model.number="freezeDuration" label="Hold (s)" type="number" min="0.1" step="0.1" />
          </div>
          <UiButton class="mt-2 w-full" size="sm" variant="ghost" :disabled="opRunning" @click="applyFreeze">
            Freeze frame
          </UiButton>
        </UiCard>

        <UiCard class="bg-surface-800/50 border border-surface-700">
          <p class="text-sm font-medium mb-3">Transform</p>
          <div class="grid grid-cols-2 gap-3">
            <UiInput v-model.number="cropX" label="Crop X" type="number" min="0" />
            <UiInput v-model.number="cropY" label="Crop Y" type="number" min="0" />
            <UiInput v-model.number="cropW" label="Crop W" type="number" min="1" />
            <UiInput v-model.number="cropH" label="Crop H" type="number" min="1" />
          </div>
          <UiButton class="mt-2 w-full" size="sm" variant="secondary" :disabled="opRunning" @click="applyCrop">Crop</UiButton>
          <div class="grid grid-cols-2 gap-3 mt-3">
            <UiInput v-model.number="rotateDegrees" label="Rotate°" type="number" step="1" />
            <UiInput v-model.number="speed" label="Speed" type="number" min="0.25" max="4" step="0.05" />
          </div>
          <div class="grid grid-cols-2 gap-2 mt-2">
            <UiButton size="sm" variant="ghost" :disabled="opRunning" @click="applyRotate">Rotate</UiButton>
            <UiButton size="sm" variant="ghost" :disabled="opRunning" @click="applySpeed">Speed</UiButton>
          </div>
          <div class="grid grid-cols-2 gap-3 mt-3">
            <UiInput v-model.number="canvasW" label="Canvas W" type="number" min="1" />
            <UiInput v-model.number="canvasH" label="Canvas H" type="number" min="1" />
          </div>
          <div class="grid grid-cols-2 gap-2 mt-2">
            <UiButton size="sm" variant="secondary" :disabled="opRunning" @click="applyCanvas">Canvas</UiButton>
            <UiButton size="sm" variant="ghost" :disabled="opRunning" @click="applyMirror">Mirror</UiButton>
          </div>
          <p class="text-xs text-surface-500 mt-4 mb-2">Color and transitions</p>
          <div class="grid grid-cols-2 gap-3">
            <UiInput v-model.number="brightness" label="Brightness" type="number" step="0.05" />
            <UiInput v-model.number="contrast" label="Contrast" type="number" min="0" step="0.05" />
            <UiInput v-model.number="saturation" label="Saturation" type="number" min="0" step="0.05" />
            <UiInput v-model.number="gamma" label="Gamma" type="number" min="0" step="0.05" />
          </div>
          <UiButton class="mt-2 w-full" size="sm" variant="ghost" :disabled="opRunning" @click="applyColor">
            Apply color
          </UiButton>
          <div class="grid grid-cols-2 gap-3 mt-3">
            <UiInput v-model.number="fadeIn" label="Fade in (s)" type="number" min="0" step="0.1" />
            <UiInput v-model.number="fadeOut" label="Fade out (s)" type="number" min="0" step="0.1" />
          </div>
          <UiButton class="mt-2 w-full" size="sm" variant="ghost" :disabled="opRunning" @click="applyFade">
            Apply fades
          </UiButton>
        </UiCard>

        <UiCard class="bg-surface-800/50 border border-surface-700">
          <p class="text-sm font-medium mb-3">Text & Effects</p>
          <UiInput v-model="overlayText" label="Text" placeholder="Type overlay text" />
          <div class="grid grid-cols-3 gap-2 mt-3">
            <UiInput v-model.number="overlayStart" label="Start" type="number" min="0" step="0.1" />
            <UiInput v-model.number="overlayEnd" label="End" type="number" min="0" step="0.1" />
            <div>
              <label class="label text-xs">Position</label>
              <select v-model="overlayPosition" class="input w-full text-sm py-2">
                <option value="center">Center</option>
                <option value="top">Top</option>
                <option value="bottom">Bottom</option>
              </select>
            </div>
          </div>
          <UiButton class="mt-2 w-full" size="sm" variant="secondary" :disabled="opRunning || !overlayText" @click="applyText">
            Add text overlay
          </UiButton>
        </UiCard>

        <UiCard class="bg-surface-800/50 border border-surface-700">
          <p class="text-sm font-medium mb-3">Media Overlays</p>
          <label class="label text-xs">Branding assets</label>
          <div class="max-h-28 overflow-y-auto space-y-1 mb-2">
            <button
              v-for="asset in brandingAssets"
              :key="asset.id"
              type="button"
              class="w-full text-left px-2 py-1.5 rounded text-xs border transition-colors"
              :class="selectedAssetPath === asset.storage_path ? 'border-primary-500 bg-primary-500/10' : 'border-surface-700 bg-surface-800/40 hover:border-surface-600'"
              @click="selectedAssetPath = asset.storage_path"
            >
              {{ asset.filename }}
            </button>
          </div>
          <div class="grid grid-cols-2 gap-2">
            <UiButton size="sm" variant="ghost" :disabled="opRunning || !selectedAssetPath" @click="applyInsertImage">Insert image</UiButton>
            <UiButton size="sm" variant="ghost" :disabled="opRunning || !selectedAssetPath" @click="applySticker">Add sticker</UiButton>
          </div>
          <UiInput v-model="audioPath" class="mt-3" label="Audio path" placeholder="storage path or absolute server path" />
          <UiButton class="mt-2 w-full" size="sm" variant="ghost" :disabled="opRunning || !audioPath" @click="applyInsertAudio">
            Insert audio
          </UiButton>
        </UiCard>

        <UiCard class="bg-surface-800/50 border border-surface-700">
          <p class="text-sm font-medium mb-3">Presets & Export</p>
          <div>
            <label class="label text-xs">Platform preset</label>
            <select v-model="platformPreset" class="input w-full text-sm py-2">
              <option value="tiktok">TikTok</option>
              <option value="instagram">Instagram Reels</option>
              <option value="youtube_shorts">YouTube Shorts</option>
              <option value="youtube">YouTube</option>
              <option value="facebook">Facebook</option>
            </select>
          </div>
          <UiButton class="mt-2 w-full" size="sm" variant="secondary" :disabled="opRunning" @click="applyPlatformPreset">
            Apply platform preset
          </UiButton>
          <div class="grid grid-cols-2 gap-3 mt-3">
            <UiInput v-model.number="exportW" label="Export W" type="number" min="1" />
            <UiInput v-model.number="exportH" label="Export H" type="number" min="1" />
            <UiInput v-model.number="exportFps" label="FPS" type="number" min="1" />
            <UiInput v-model="exportBitrate" label="Bitrate" placeholder="4M" />
          </div>
          <UiButton class="mt-2 w-full" size="sm" variant="primary" :disabled="opRunning" @click="applyExport">
            Export video
          </UiButton>
        </UiCard>
      </aside>

      <!-- Center preview -->
      <main class="overflow-hidden flex flex-col">
        <div class="flex-1 bg-black/60 flex items-center justify-center p-4">
          <div v-if="previewUrl" class="w-full h-full max-h-full flex items-center justify-center">
            <video
              :src="previewUrl"
              controls
              autoplay
              muted
              loop
              class="max-w-full max-h-full rounded-lg border border-surface-700 bg-black"
            />
          </div>
          <div v-else class="text-surface-500 text-sm">No preview available</div>
        </div>
        <div class="border-t border-surface-800 p-3 bg-surface-900/70">
          <div class="flex items-center justify-between text-xs text-surface-400 mb-1">
            <span>Trim start: {{ trimStart.toFixed(1) }}s</span>
            <span>Trim end: {{ trimEnd.toFixed(1) }}s</span>
          </div>
          <input v-model.number="trimStart" type="range" min="0" :max="durationMax" step="0.1" class="w-full mb-1" />
          <input v-model.number="trimEnd" type="range" min="0" :max="durationMax" step="0.1" class="w-full" />
        </div>
      </main>

      <!-- Right output panel -->
      <aside class="border-l border-surface-800 overflow-y-auto p-4 space-y-4 bg-surface-900/60">
        <UiCard class="bg-surface-800/50 border border-surface-700">
          <div class="flex items-center justify-between mb-2">
            <p class="text-sm font-medium">Operation Status</p>
            <UiButton size="sm" variant="ghost" :disabled="opRunning" @click="refreshVideoInfo">Refresh info</UiButton>
          </div>
          <p v-if="opRunning" class="text-xs text-primary-300">Running operation...</p>
          <p v-else class="text-xs text-surface-400">Ready</p>
          <p v-if="opError" class="text-xs text-red-400 mt-2">{{ opError }}</p>
        </UiCard>

        <UiCard class="bg-surface-800/50 border border-surface-700">
          <p class="text-sm font-medium mb-2">Video diagnostics</p>
          <UiButton size="sm" variant="ghost" class="mb-2" :disabled="opRunning" @click="loadVideoInfo">Get video info</UiButton>
          <pre v-if="videoInfo" class="text-[11px] leading-relaxed text-surface-300 bg-surface-900/80 rounded p-2 overflow-x-auto">{{ videoInfo }}</pre>
        </UiCard>

        <UiCard class="bg-surface-800/50 border border-surface-700">
          <p class="text-sm font-medium mb-3">Output history</p>
          <div v-if="history.length === 0" class="text-xs text-surface-500">No edits yet</div>
          <div v-else class="space-y-2">
            <div v-for="item in history" :key="item.output_path" class="p-2 rounded border border-surface-700 bg-surface-900/70">
              <p class="text-xs font-medium">{{ item.op }}</p>
              <div class="flex flex-wrap gap-2 mt-2">
                <UiButton size="sm" variant="ghost" :href="item.output_url" target="_blank" rel="noopener">
                  Open file
                </UiButton>
                <UiButton
                  v-if="item.output_video_id"
                  size="sm"
                  variant="secondary"
                  :to="localePath(`/videos/${item.output_video_id}`)"
                >
                  Open video
                </UiButton>
              </div>
            </div>
          </div>
        </UiCard>
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch, onMounted } from 'vue'

definePageMeta({
  layout: false,
  middleware: 'auth',
})

const route = useRoute()
const localePath = useLocalePath()
const api = useApi()
const toast = useToast()

const video = ref<any>(null)
const brandingAssets = ref<any[]>([])
const previewUrl = ref('')
const lastOutputUrl = ref('')
const opRunning = ref(false)
const opError = ref('')
const history = ref<any[]>([])
const videoInfo = ref('')

const saveToLibrary = ref(true)
const trimStart = ref(0)
const trimEnd = ref(10)
const freezeAt = ref(0)
const freezeDuration = ref(1)
const cropX = ref(0)
const cropY = ref(0)
const cropW = ref(1080)
const cropH = ref(1920)
const rotateDegrees = ref(90)
const speed = ref(1)
const canvasW = ref(1080)
const canvasH = ref(1920)
const brightness = ref(0)
const contrast = ref(1)
const saturation = ref(1)
const gamma = ref(1)
const fadeIn = ref(0.3)
const fadeOut = ref(0.3)
const overlayText = ref('')
const overlayStart = ref(0)
const overlayEnd = ref(3)
const overlayPosition = ref('center')
const selectedAssetPath = ref('')
const audioPath = ref('')
const platformPreset = ref('tiktok')
const exportW = ref(1080)
const exportH = ref(1920)
const exportFps = ref(30)
const exportBitrate = ref('4M')

const durationMax = computed(() => {
  const d = Number(video.value?.duration || 60)
  return d > 0 ? d : 60
})

watch(durationMax, (d) => {
  trimEnd.value = Math.min(trimEnd.value, d)
  overlayEnd.value = Math.min(overlayEnd.value, d)
  freezeAt.value = Math.min(freezeAt.value, d)
})

async function fetchVideo() {
  const id = route.params.id as string
  video.value = await api.videos.get(id)
  previewUrl.value = video.value?.video_url || video.value?.thumbnail_url || ''
  trimStart.value = 0
  trimEnd.value = Number(video.value?.duration || 10)
  overlayEnd.value = Math.min(3, trimEnd.value)
}

async function fetchBranding() {
  try {
    const res = await api.branding.list()
    brandingAssets.value = ((res as { items?: any[] })?.items ?? []).filter((a) => !!a.storage_path)
  } catch {
    brandingAssets.value = []
  }
}

async function execute(op: string, params: Record<string, unknown>, outputTitle?: string) {
  opRunning.value = true
  opError.value = ''
  try {
    const id = route.params.id as string
    const res = await api.editorOps.execute(id, op, params, {
      saveToLibrary: saveToLibrary.value,
      outputTitle,
    })
    if (res?.error) throw new Error(res.error)

    if (res?.output_url) {
      previewUrl.value = res.output_url
      lastOutputUrl.value = res.output_url
    }
    history.value.unshift({
      op,
      output_path: res?.output_path,
      output_url: res?.output_url,
      output_video_id: res?.output_video_id,
    })
    toast.success(`${op} completed`)
  } catch (e: any) {
    const msg = e?.data?.detail ?? e?.message ?? 'Editor operation failed'
    opError.value = msg
    toast.error(msg)
  } finally {
    opRunning.value = false
  }
}

function runSimple(op: string) {
  execute(op, {})
}

function applyTrim() {
  if (trimEnd.value <= trimStart.value) {
    toast.error('Trim end must be greater than trim start')
    return
  }
  execute('trim_clip', { start: trimStart.value, end: trimEnd.value }, `Trim ${video.value?.filename || ''}`.trim())
}

function applyClipOut() {
  if (trimEnd.value <= trimStart.value) {
    toast.error('Clip-out end must be greater than start')
    return
  }
  execute('clip_out', { start: trimStart.value, end: trimEnd.value })
}

function applyFreeze() {
  execute('freeze_frame', { at_time: freezeAt.value, duration: freezeDuration.value })
}

function applyCrop() {
  execute('crop_clip', {
    x: cropX.value,
    y: cropY.value,
    width: cropW.value,
    height: cropH.value,
  })
}

function applyRotate() {
  execute('rotate_clip', { degrees: rotateDegrees.value })
}

function applyMirror() {
  execute('mirror_clip', { horizontal: true })
}

function applyCanvas() {
  execute('set_canvas_size', { width: canvasW.value, height: canvasH.value })
}

function applyColor() {
  execute('adjust_color', {
    brightness: brightness.value,
    contrast: contrast.value,
    saturation: saturation.value,
    gamma: gamma.value,
  })
}

function applyFade() {
  execute('fade_in_out', { fade_in: fadeIn.value, fade_out: fadeOut.value })
}

function applySpeed() {
  execute('set_clip_speed', { speed: speed.value })
}

function applyText() {
  execute('add_text_overlay', {
    text: overlayText.value,
    start_time: overlayStart.value,
    end_time: overlayEnd.value,
    position: overlayPosition.value,
  })
}

function applyInsertImage() {
  execute('insert_image', {
    image_path: selectedAssetPath.value,
    at_time: 0,
    duration: 3,
    position: 'center',
  })
}

function applySticker() {
  execute('add_sticker', {
    image_path: selectedAssetPath.value,
    at_time: 0,
    duration: 3,
    x: 40,
    y: 40,
  })
}

function applyInsertAudio() {
  execute('insert_audio', {
    audio_path: audioPath.value,
    at_time: 0,
    volume: 1,
  })
}

function applyPlatformPreset() {
  execute('platform_preset', { platform: platformPreset.value })
}

function applyExport() {
  execute('export_video', {
    width: exportW.value,
    height: exportH.value,
    fps: exportFps.value,
    bitrate: exportBitrate.value,
  }, `Export ${video.value?.filename || ''}`.trim())
}

async function loadVideoInfo() {
  const id = route.params.id as string
  try {
    const res = await api.editorOps.execute(id, 'video_info', {}, { saveToLibrary: false })
    videoInfo.value = JSON.stringify(res?.result || {}, null, 2)
  } catch (e: any) {
    videoInfo.value = ''
    toast.error(e?.data?.detail ?? e?.message ?? 'Could not load video info')
  }
}

async function refreshVideoInfo() {
  await fetchVideo()
}

onMounted(async () => {
  await Promise.all([fetchVideo(), fetchBranding()])
})
</script>
