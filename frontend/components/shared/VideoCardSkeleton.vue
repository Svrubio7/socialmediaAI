<template>
  <UiCard padding="none" class="overflow-hidden">
    <!-- Thumbnail skeleton -->
    <UiSkeleton variant="rectangular" class="aspect-video" />
    
    <!-- Content skeleton -->
    <div class="p-4 space-y-3">
      <UiSkeleton variant="text" width="70%" />
      <div class="flex items-center justify-between">
        <UiSkeleton variant="rounded" width="80px" height="24px" />
        <UiSkeleton variant="text" width="60px" />
      </div>
      <div class="flex gap-2 pt-2">
        <UiSkeleton variant="rounded" height="36px" class="flex-1" />
        <UiSkeleton variant="rounded" height="36px" class="flex-1" />
      </div>
    </div>
  </UiCard>
</template>
