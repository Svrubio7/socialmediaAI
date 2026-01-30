<template>
  <UiCard>
    <div class="flex items-center gap-4">
      <div class="flex-shrink-0">
        <UiSkeleton variant="rounded" width="48px" height="48px" />
      </div>
      <div class="min-w-0 flex-1 space-y-2">
        <UiSkeleton variant="text" width="80px" />
        <UiSkeleton variant="text" width="60px" height="28px" />
        <UiSkeleton variant="text" width="100px" class="mt-2" />
      </div>
    </div>
  </UiCard>
</template>
