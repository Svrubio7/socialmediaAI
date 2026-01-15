/**
 * Guest middleware - redirects authenticated users to dashboard.
 */

export default defineNuxtRouteMiddleware((to) => {
  const user = useSupabaseUser()

  if (user.value) {
    return navigateTo('/dashboard')
  }
})
