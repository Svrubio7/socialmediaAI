<template>
  <div class="flex flex-col h-[calc(100vh-3.5rem)] lg:h-[calc(100vh-4rem)]">
    <div class="container-wide flex-1 flex flex-col min-h-0 py-4 lg:py-6">
      <div class="mb-4">
        <h1 class="text-2xl lg:text-3xl font-mono font-normal text-surface-100">Strategies</h1>
        <p class="text-surface-400 text-sm mt-1">Describe your goals and the assistant will help with schedules, scripts, and strategies.</p>
      </div>

      <div class="flex-1 grid grid-cols-1 lg:grid-cols-5 gap-4 lg:gap-6 min-h-0">
        <!-- Left: Chat -->
        <div class="lg:col-span-2 flex flex-col min-h-0 border border-surface-800 rounded-xl bg-surface-900/50 overflow-hidden">
          <div class="flex-1 overflow-y-auto p-4 space-y-4">
            <div
              v-for="(msg, i) in messages"
              :key="i"
              class="flex"
              :class="msg.role === 'user' ? 'justify-end' : 'justify-start'"
            >
              <div
                class="max-w-[85%] rounded-xl px-4 py-2.5 text-sm font-mono"
                :class="msg.role === 'user' ? 'bg-primary-500/20 text-surface-100 border border-primary-500/30' : 'bg-surface-800 text-surface-200 border border-surface-700'"
              >
                {{ msg.content }}
              </div>
            </div>
            <div v-if="sending" class="flex justify-start">
              <div class="rounded-xl px-4 py-2.5 text-sm text-surface-400 border border-surface-700 bg-surface-800">
                Thinking...
              </div>
            </div>
          </div>
          <div class="p-4 border-t border-surface-800">
            <form @submit.prevent="sendMessage" class="flex gap-2">
              <input
                v-model="inputText"
                type="text"
                placeholder="Ask to schedule a post, create a script, or generate a strategy..."
                class="input flex-1 min-w-0"
                :disabled="sending"
              />
              <Button type="submit" variant="primary" size="sm" :disabled="sending || !inputText.trim()">
                <UiIcon name="Send" :size="16" />
                <span>Send</span>
              </Button>
            </form>
          </div>
        </div>

        <!-- Right: Result cards -->
        <div class="lg:col-span-3 flex flex-col min-h-0 overflow-hidden">
          <div class="flex items-center justify-between mb-3">
            <h2 class="text-lg font-mono font-medium text-surface-100">Results</h2>
            <Button v-if="cards.length > 0" variant="ghost" size="sm" @click="cards = []">
              Clear
            </Button>
          </div>
          <div class="flex-1 overflow-y-auto space-y-3 pr-1">
            <Card
              v-for="(card, i) in cards"
              :key="i"
              class="border-l-4 flex-shrink-0"
              :class="cardBorderClass(card.type)"
            >
              <div class="flex items-start gap-3">
                <div
                  class="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0"
                  :class="cardIconBg(card.type)"
                >
                  <UiIcon :name="cardIcon(card.type)" :size="20" :class="cardIconColor(card.type)" />
                </div>
                <div class="min-w-0 flex-1">
                  <p class="font-mono font-medium text-surface-100">{{ cardTitle(card) }}</p>
                  <p class="text-surface-400 text-sm mt-0.5">{{ cardSummary(card) }}</p>
                  <div class="flex flex-wrap gap-2 mt-3">
                    <template v-if="card.type === 'schedule'">
                      <Button variant="ghost" size="sm" :to="localePath('/schedule')">View schedule</Button>
                    </template>
                    <template v-else-if="card.type === 'script'">
                      <Button variant="ghost" size="sm" :to="localePath('/scripts')">View scripts</Button>
                    </template>
                    <template v-else-if="card.type === 'strategy'">
                      <Button variant="ghost" size="sm" :to="localePath(`/strategies/${card.payload?.id ?? ''}`)">View strategy</Button>
                    </template>
                    <template v-else-if="card.type === 'oauth'">
                      <a
                        v-if="card.payload?.url"
                        :href="card.payload.url"
                        target="_blank"
                        rel="noopener"
                        class="btn btn-primary btn-sm"
                      >
                        Connect {{ card.payload?.platform }}
                      </a>
                    </template>
                  </div>
                </div>
              </div>
            </Card>
            <div
              v-if="cards.length === 0 && !sending && messages.length <= 1"
              class="flex flex-col items-center justify-center py-12 text-center text-surface-500"
            >
              <UiIcon name="Target" :size="48" class="mb-3 opacity-50" />
              <p class="font-mono text-sm">Results from the assistant will appear here.</p>
              <p class="text-xs mt-1">Try: "List my scheduled posts" or "Create a script for a 60s TikTok."</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'app-sidebar',
  middleware: 'auth',
})

const localePath = useLocalePath()
const api = useApi()
const messages = ref<{ role: string; content: string }[]>([
  { role: 'assistant', content: 'I can help you schedule posts, create scripts, and generate strategies. What would you like to do?' },
])
const inputText = ref('')
const sending = ref(false)
const cards = ref<{ type: string; payload: Record<string, unknown> }[]>([])

function cardBorderClass(type: string) {
  switch (type) {
    case 'schedule': return 'border-l-primary-500'
    case 'script': return 'border-l-accent-500'
    case 'strategy': return 'border-l-emerald-500'
    case 'oauth': return 'border-l-amber-500'
    default: return 'border-l-surface-600'
  }
}

function cardIcon(type: string) {
  switch (type) {
    case 'schedule': return 'Calendar'
    case 'script': return 'FileText'
    case 'strategy': return 'Target'
    case 'oauth': return 'Link'
    default: return 'FileText'
  }
}

function cardIconBg(type: string) {
  switch (type) {
    case 'schedule': return 'bg-primary-500/10'
    case 'script': return 'bg-accent-500/10'
    case 'strategy': return 'bg-emerald-500/10'
    case 'oauth': return 'bg-amber-500/10'
    default: return 'bg-surface-700'
  }
}

function cardIconColor(type: string) {
  switch (type) {
    case 'schedule': return 'text-primary-400'
    case 'script': return 'text-accent-400'
    case 'strategy': return 'text-emerald-400'
    case 'oauth': return 'text-amber-400'
    default: return 'text-surface-400'
  }
}

function cardTitle(card: { type: string; payload: Record<string, unknown> }) {
  switch (card.type) {
    case 'schedule':
      if (card.payload?.cancelled) return 'Post cancelled'
      if (card.payload?.created?.length) return 'Posts scheduled'
      if (card.payload?.scheduled_at) return 'Post rescheduled'
      return 'Schedule updated'
    case 'script':
      return (card.payload?.concept as string) || 'Script created'
    case 'strategy':
      return `Strategy for ${(card.payload?.platforms as string[])?.join(', ') || 'platforms'}`
    case 'oauth':
      return `Connect ${(card.payload?.platform as string) || 'platform'}`
    default:
      return 'Result'
  }
}

function cardSummary(card: { type: string; payload: Record<string, unknown> }) {
  switch (card.type) {
    case 'schedule':
      if (card.payload?.scheduled_at) return `New time: ${new Date(card.payload.scheduled_at as string).toLocaleString()}`
      if (Array.isArray(card.payload?.created) && card.payload.created.length) {
        return `${(card.payload.created as { platform: string }[]).map((p: { platform: string }) => p.platform).join(', ')} at ${card.payload.scheduled_at ? new Date(card.payload.scheduled_at as string).toLocaleString() : 'scheduled time'}`
      }
      return 'View your schedule to manage posts.'
    case 'script':
      return (card.payload?.platform as string) ? `Platform: ${card.payload.platform}` : 'Saved to your scripts.'
    case 'strategy':
      return 'View full strategy to export or refine.'
    case 'oauth':
      return (card.payload?.url as string) ? 'Open the link to complete connection.' : 'Complete connection in Account.'
    default:
      return ''
  }
}

async function sendMessage() {
  const text = inputText.value.trim()
  if (!text || sending.value) return
  messages.value.push({ role: 'user', content: text })
  inputText.value = ''
  sending.value = true
  try {
    const payload = await api.chat.send(messages.value)
    if (payload.message) {
      messages.value.push({ role: 'assistant', content: payload.message })
    }
    if (payload.cards?.length) {
      cards.value.push(...payload.cards)
    }
  } catch (e) {
    messages.value.push({
      role: 'assistant',
      content: `Sorry, something went wrong: ${e instanceof Error ? e.message : 'Request failed'}.`,
    })
  } finally {
    sending.value = false
  }
}
</script>
