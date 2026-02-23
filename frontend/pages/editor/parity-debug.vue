<template>
  <div class="min-h-screen bg-surface-950 text-surface-100 p-6 space-y-5">
    <div>
      <h1 class="text-xl font-semibold">Editor Parity Debug</h1>
      <p class="text-sm text-surface-300">
        Select a fixture and open the editor with diagnostics overlays enabled.
      </p>
    </div>

    <div class="rounded-lg border border-surface-800 bg-surface-900/70 p-4 space-y-3 max-w-2xl">
      <label class="block text-xs uppercase tracking-wide text-surface-400">Project ID</label>
      <input
        v-model.trim="projectId"
        type="text"
        class="w-full rounded border border-surface-700 bg-surface-950 px-3 py-2 text-sm"
        placeholder="Existing editor project UUID"
      >

      <label class="block text-xs uppercase tracking-wide text-surface-400">Fixture</label>
      <select v-model="fixtureId" class="w-full rounded border border-surface-700 bg-surface-950 px-3 py-2 text-sm">
        <option v-for="fixture in fixtures" :key="fixture.id" :value="fixture.id">
          {{ fixture.label }}
        </option>
      </select>

      <div class="flex flex-wrap gap-3 text-sm">
        <label class="inline-flex items-center gap-2">
          <input v-model="diagEnabled" type="checkbox" class="accent-primary-500">
          Diagnostics enabled
        </label>
        <label class="inline-flex items-center gap-2">
          <input v-model="diagLog" type="checkbox" class="accent-primary-500">
          Console traces
        </label>
      </div>

      <div class="flex items-center gap-2">
        <button
          type="button"
          class="rounded border border-primary-500 bg-primary-500/20 px-3 py-2 text-sm"
          :disabled="!projectId"
          @click="openFixture"
        >
          Open Fixture In Editor
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  middleware: 'auth',
})

const localePath = useLocalePath()
const router = useRouter()

const fixtures = [
  { id: 'adjacent_transition_crossfade_30fps', label: 'Adjacent transition crossfade' },
  { id: 'one_frame_gap_transition_attempt_30fps', label: 'One-frame gap transition attempt' },
  { id: 'five_frame_overlap_same_layer_30fps', label: 'Five-frame same-layer overlap' },
  { id: 'short_clip_transition_clamp_30fps', label: 'Short clip transition clamp' },
  { id: 'trim_with_transition_30fps', label: 'Trim with transition' },
  { id: 'drag_collision_create_layer_30fps', label: 'Drag collision creates layer' },
  { id: 'multitrack_transition_context_30fps', label: 'Multitrack transition context' },
  { id: 'long_scrub_no_drift_10min_30fps', label: 'Long scrub drift check (10 min)' },
]

const projectId = ref('')
const fixtureId = ref(fixtures[0].id)
const diagEnabled = ref(true)
const diagLog = ref(false)

function openFixture() {
  if (!projectId.value) return
  const query: Record<string, string> = {
    fixture: fixtureId.value,
  }
  if (diagEnabled.value) query.diag = '1'
  if (diagLog.value) query.diagLog = '1'

  router.push(localePath({
    path: `/editor/${projectId.value}`,
    query,
  }))
}
</script>
