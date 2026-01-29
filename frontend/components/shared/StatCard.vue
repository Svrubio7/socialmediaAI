<template>
  <Card>
    <div class="flex items-center gap-4">
      <div
        class="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0"
        :class="iconBg"
      >
        <UiIcon :name="icon" :size="24" :class="iconColor" />
      </div>
      <div class="min-w-0 flex-1">
        <p class="text-surface-400 text-sm mb-0.5">{{ label }}</p>
        <p class="text-2xl font-mono font-normal text-surface-100 truncate">{{ value }}</p>
        <p
          v-if="change !== undefined"
          class="text-sm mt-2 flex items-center gap-1"
          :class="change >= 0 ? 'text-emerald-400' : 'text-red-400'"
        >
          <UiIcon :name="change >= 0 ? 'TrendingUp' : 'TrendingDown'" :size="14" />
          <span>{{ change >= 0 ? '+' : '' }}{{ change }}% from last week</span>
        </p>
      </div>
    </div>
  </Card>
</template>

<script setup lang="ts">
interface Props {
  label: string
  value: string | number
  icon: string
  iconBg: string
  iconColor: string
  change?: number
}

defineProps<Props>()
</script>
