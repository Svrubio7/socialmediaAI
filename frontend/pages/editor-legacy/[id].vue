<script setup lang="ts">
definePageMeta({
  middleware: 'auth',
})

const route = useRoute()
const localePath = useLocalePath()

await navigateTo(localePath(`/editor/${route.params.id as string}`), {
  replace: true,
})
</script>
