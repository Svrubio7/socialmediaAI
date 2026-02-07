<template>
  <div class="container-wide py-6 lg:py-8">
    <NuxtLink
      :to="localePath('/dashboard')"
      class="inline-flex items-center gap-2 text-sm text-surface-400 hover:text-surface-200 mb-5 transition-colors"
    >
      <UiIcon name="ArrowLeft" :size="14" />
      Back to Dashboard
    </NuxtLink>

    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
      <div>
        <h1 class="text-xl lg:text-2xl font-mono font-normal text-surface-100">Editor Hub</h1>
        <p class="text-surface-400 mt-1 text-sm">Create projects, upload media, and export finished videos to your library.</p>
      </div>
      <div class="flex flex-wrap items-center gap-3">
        <UiButton variant="secondary" :to="localePath('/videos')">
          <template #icon-left><UiIcon name="Video" :size="16" /></template>
          Media library
        </UiButton>
        <UiButton variant="primary" @click="showCreateProject = true">
          <template #icon-left><UiIcon name="Plus" :size="16" /></template>
          New project
        </UiButton>
      </div>
    </div>

    <UiCard class="border border-accent-500/30 bg-accent-100/70 dark:bg-surface-700/40 rounded-2xl mb-8">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-5">
        <h2 class="text-base font-mono font-medium text-surface-100">Projects</h2>
        <UiButton variant="secondary" size="sm" class="rounded-xl" @click="showCreateProject = true">
          <template #icon-left><UiIcon name="Plus" :size="14" /></template>
          Create project
        </UiButton>
      </div>
      <div v-if="projectsLoading" class="py-10 flex justify-center">
        <div class="flex flex-col items-center gap-3">
          <UiSkeleton variant="rounded" width="64px" height="64px" />
          <UiSkeleton variant="text" width="160px" />
        </div>
      </div>
      <SharedEmptyState
        v-else-if="projects.length === 0"
        icon="FolderPlus"
        title="No projects yet"
        description="Start your first editor project and add media from your library."
        action-label="Create project"
        action-icon="Plus"
        variant="primary"
        @action="showCreateProject = true"
      />
      <div v-else class="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="p in projects"
          :key="p.id"
          class="p-4 rounded-xl bg-surface-50/70 dark:bg-surface-600/30 border border-surface-300/70 dark:border-surface-600/50 flex flex-col"
        >
          <div class="flex items-center gap-3 mb-2">
            <div class="w-9 h-9 rounded-lg bg-accent-500/20 flex items-center justify-center flex-shrink-0">
              <UiIcon name="FolderOpen" :size="18" class="text-accent-400" />
            </div>
            <div class="min-w-0 flex-1">
              <p class="font-medium text-surface-100 truncate text-sm">{{ p.name }}</p>
              <p class="text-surface-500 text-xs truncate">
                Updated {{ formatDate(p.updated_at) }}
              </p>
            </div>
          </div>
          <div class="mt-auto pt-3 flex flex-wrap gap-2">
            <UiButton
              variant="secondary"
              size="sm"
              class="rounded-xl"
              :href="localePath(`/editor/${p.id}`)"
              target="_blank"
              rel="noopener"
            >
              <template #icon-left><UiIcon name="ExternalLink" :size="14" /></template>
              Open workspace
            </UiButton>
          </div>
        </div>
      </div>
    </UiCard>

    <!-- Edit templates (content library) -->
    <UiCard class="border-l-4 border-l-accent-500 border border-accent-500/30 bg-accent-100/70 dark:bg-surface-700/40 rounded-2xl">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-5">
        <h2 class="text-base font-mono font-medium text-surface-100">Edit templates</h2>
        <UiButton variant="secondary" size="sm" class="rounded-xl" @click="showCreateTemplate = true">
          <template #icon-left><UiIcon name="Plus" :size="14" /></template>
          Create template
        </UiButton>
      </div>
      <div v-if="templatesLoading" class="py-10 flex justify-center">
        <div class="flex flex-col items-center gap-3">
          <UiSkeleton variant="rounded" width="64px" height="64px" />
          <UiSkeleton variant="text" width="140px" />
        </div>
      </div>
      <SharedEmptyState
        v-else-if="editTemplates.length === 0"
        icon="FileStack"
        title="No edit templates yet"
        description="Create reusable edit styles to apply to raw footage"
        action-label="Create template"
        action-icon="Plus"
        variant="primary"
        @action="showCreateTemplate = true"
      />
      <div v-else class="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="t in editTemplates"
          :key="t.id"
          class="p-4 rounded-xl bg-surface-50/70 dark:bg-surface-600/30 border border-surface-300/70 dark:border-surface-600/50 flex flex-col"
        >
          <div class="flex items-center gap-3 mb-2">
            <div class="w-9 h-9 rounded-lg bg-accent-500/20 flex items-center justify-center flex-shrink-0">
              <UiIcon name="FileStack" :size="18" class="text-accent-400" />
            </div>
            <div class="min-w-0 flex-1">
              <p class="font-medium text-surface-100 truncate text-sm">{{ t.name }}</p>
              <p v-if="t.description" class="text-surface-500 text-xs truncate">{{ t.description }}</p>
            </div>
          </div>
          <div class="mt-auto pt-3 flex flex-wrap gap-2">
            <UiButton
              variant="ghost"
              size="sm"
              class="rounded-xl text-red-400 hover:text-red-300 hover:bg-red-500/10"
              :disabled="deletingTemplate === t.id"
              @click="deleteTemplate(t.id)"
            >
              <template #icon-left><UiIcon name="Trash2" :size="14" /></template>
              Delete
            </UiButton>
          </div>
        </div>
      </div>
    </UiCard>

    <!-- Create project modal -->
    <UiModal v-model="showCreateProject" title="Create project" size="md">
      <form @submit.prevent="createProject" class="space-y-4">
        <div>
          <label class="label text-sm">Project name</label>
          <UiInput v-model="newProjectName" placeholder="e.g. March campaign cutdown" required />
        </div>
        <div class="flex justify-end gap-3 pt-2">
          <UiButton variant="ghost" type="button" class="rounded-xl" @click="showCreateProject = false">Cancel</UiButton>
          <UiButton variant="primary" type="submit" class="rounded-xl" :disabled="creatingProject">
            {{ creatingProject ? 'Creating...' : 'Create' }}
          </UiButton>
        </div>
      </form>
    </UiModal>

    <!-- Create edit template modal -->
    <UiModal v-model="showCreateTemplate" title="Create edit template" size="md">
      <form @submit.prevent="createTemplate" class="space-y-4">
        <div>
          <label class="label text-sm">Name</label>
          <UiInput v-model="newTemplateName" placeholder="e.g. TikTok fast cuts" required />
        </div>
        <div>
          <label class="label text-sm">Description (optional)</label>
          <UiInput v-model="newTemplateDescription" placeholder="Short description of this edit style" />
        </div>
        <div class="flex justify-end gap-3 pt-2">
          <UiButton variant="ghost" type="button" class="rounded-xl" @click="showCreateTemplate = false">Cancel</UiButton>
          <UiButton variant="primary" type="submit" class="rounded-xl" :disabled="creatingTemplate">
            {{ creatingTemplate ? 'Creating...' : 'Create' }}
          </UiButton>
        </div>
      </form>
    </UiModal>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
definePageMeta({
  layout: 'app-sidebar',
  middleware: 'auth',
})

const localePath = useLocalePath()
const api = useApi()
const toast = useToast()

const projects = ref<any[]>([])
const projectsLoading = ref(true)
const showCreateProject = ref(false)
const creatingProject = ref(false)
const newProjectName = ref('')

const showCreateTemplate = ref(false)
const templatesLoading = ref(true)
const creatingTemplate = ref(false)
const deletingTemplate = ref<string | null>(null)
const editTemplates = ref<any[]>([])
const newTemplateName = ref('')
const newTemplateDescription = ref('')

function formatDate(value?: string) {
  if (!value) return 'just now'
  try {
    return new Date(value).toLocaleDateString()
  } catch {
    return 'just now'
  }
}

async function fetchProjects() {
  projectsLoading.value = true
  try {
    const res = await api.projects.list({ limit: 50 })
    projects.value = res?.items ?? []
  } catch {
    projects.value = []
  } finally {
    projectsLoading.value = false
  }
}

async function createProject() {
  const name = newProjectName.value.trim()
  if (!name) return
  creatingProject.value = true
  try {
    const project = await api.projects.create({ name })
    showCreateProject.value = false
    newProjectName.value = ''
    toast.success('Project created')
    if (project?.id) {
      navigateTo(localePath(`/editor/${project.id}`))
    } else {
      await fetchProjects()
    }
  } catch (e: any) {
    toast.error(e?.data?.detail ?? 'Failed to create project')
  } finally {
    creatingProject.value = false
  }
}

async function fetchTemplates() {
  templatesLoading.value = true
  try {
    const res = await api.editTemplates.list({ limit: 50 })
    editTemplates.value = res?.items ?? []
  } catch {
    editTemplates.value = []
  } finally {
    templatesLoading.value = false
  }
}

async function createTemplate() {
  const name = newTemplateName.value.trim()
  if (!name) return
  creatingTemplate.value = true
  try {
    await api.editTemplates.create({
      name,
      description: newTemplateDescription.value.trim() || undefined,
      style_spec: {},
    })
    showCreateTemplate.value = false
    newTemplateName.value = ''
    newTemplateDescription.value = ''
    await fetchTemplates()
    toast.success('Template created')
  } catch (e: any) {
    toast.error(e?.data?.detail ?? 'Failed to create template')
  } finally {
    creatingTemplate.value = false
  }
}

async function deleteTemplate(id: string) {
  deletingTemplate.value = id
  try {
    await api.editTemplates.delete(id)
    editTemplates.value = editTemplates.value.filter((t) => t.id !== id)
    toast.success('Template deleted')
  } catch (e: any) {
    toast.error(e?.data?.detail ?? 'Failed to delete')
  } finally {
    deletingTemplate.value = null
  }
}

onMounted(async () => {
  await fetchProjects()
  await fetchTemplates()
})
</script>
