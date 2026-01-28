<template>
  <Card padding="none" class="overflow-hidden">
    <!-- Thumbnail skeleton -->
    <Skeleton variant="rectangular" class="aspect-video" />
    
    <!-- Content skeleton -->
    <div class="p-4 space-y-3">
      <Skeleton variant="text" width="70%" />
      <div class="flex items-center justify-between">
        <Skeleton variant="rounded" width="80px" height="24px" />
        <Skeleton variant="text" width="60px" />
      </div>
      <div class="flex gap-2 pt-2">
        <Skeleton variant="rounded" height="36px" class="flex-1" />
        <Skeleton variant="rounded" height="36px" class="flex-1" />
      </div>
    </div>
  </Card>
</template>
