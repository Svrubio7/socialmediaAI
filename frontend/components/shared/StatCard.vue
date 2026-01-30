<template>
  <UiCard :class="cardClass">
    <div class="flex items-center gap-3">
      <div
        class="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
        :class="iconBg"
      >
        <UiIcon :name="icon" :size="20" :class="iconColor" />
      </div>
      <div class="min-w-0 flex-1">
        <p class="text-surface-400 text-xs mb-0.5">{{ label }}</p>
        <p class="text-lg font-mono font-normal text-surface-100 truncate">{{ value }}</p>
        <p
          v-if="change !== undefined"
          class="text-xs mt-1.5 flex items-center gap-1"
          :class="change >= 0 ? 'text-emerald-400' : 'text-red-400'"
        >
          <UiIcon :name="change >= 0 ? 'TrendingUp' : 'TrendingDown'" :size="12" />
          <span>{{ change >= 0 ? '+' : '' }}{{ change }}% from last week</span>
        </p>
      </div>
    </div>
  </UiCard>
</template>

<script setup lang="ts">
interface Props {
  label: string
  value: string | number
  icon: string
  iconBg: string
  iconColor: string
  change?: number
  cardClass?: string
}

const props = withDefaults(defineProps<Props>(), {
  cardClass: '',
})
</script>
