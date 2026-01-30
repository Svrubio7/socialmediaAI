<template><div class="p-8">Redirecting to Branding…</div></template>
<script setup lang="ts">
import { onMounted } from 'vue'
definePageMeta({ layout: 'app-sidebar', middleware: 'auth' })
const localePath = useLocalePath()
onMounted(() => {
  navigateTo(localePath('/account/branding'), { redirectCode: 302, replace: true })
})
</script>
