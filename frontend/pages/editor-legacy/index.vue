<script setup lang="ts">
definePageMeta({
  middleware: 'auth',
})

const localePath = useLocalePath()

await navigateTo(localePath('/editor'), {
  replace: true,
})
</script>
