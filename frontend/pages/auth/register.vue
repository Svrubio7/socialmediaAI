<template>
  <NuxtLayout name="auth">
    <div class="card">
      <h1 class="text-2xl font-display font-bold text-center mb-2">Create account</h1>
      <p class="text-surface-400 text-center mb-8">Start your free trial today</p>

      <form @submit.prevent="handleRegister" class="space-y-4">
        <div>
          <label for="name" class="label">Full name</label>
          <input
            id="name"
            v-model="name"
            type="text"
            class="input"
            placeholder="John Doe"
            required
          />
        </div>

        <div>
          <label for="email" class="label">Email</label>
          <input
            id="email"
            v-model="email"
            type="email"
            class="input"
            placeholder="you@example.com"
            required
          />
        </div>

        <div>
          <label for="password" class="label">Password</label>
          <input
            id="password"
            v-model="password"
            type="password"
            class="input"
            placeholder="••••••••"
            required
            minlength="6"
          />
          <p class="text-surface-500 text-xs mt-1">At least 6 characters</p>
        </div>

        <div v-if="error" class="text-red-400 text-sm text-center">
          {{ error }}
        </div>

        <div v-if="success" class="text-green-400 text-sm text-center">
          {{ success }}
        </div>

        <button
          type="submit"
          class="btn-primary w-full"
          :disabled="loading"
        >
          <span v-if="loading">Creating account...</span>
          <span v-else>Create account</span>
        </button>
      </form>

      <div class="mt-6 text-center">
        <p class="text-surface-400 text-sm">
          Already have an account?
          <NuxtLink to="/auth/login" class="text-primary-400 hover:text-primary-300">
            Sign in
          </NuxtLink>
        </p>
      </div>
    </div>
  </NuxtLayout>
</template>

<script setup lang="ts">
definePageMeta({
  layout: false,
})

const supabase = useSupabaseClient()

const name = ref('')
const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')
const success = ref('')

const handleRegister = async () => {
  loading.value = true
  error.value = ''
  success.value = ''

  try {
    const { error: authError } = await supabase.auth.signUp({
      email: email.value,
      password: password.value,
      options: {
        data: {
          name: name.value,
        },
      },
    })

    if (authError) {
      error.value = authError.message
      return
    }

    success.value = 'Account created! Check your email to confirm.'
  } catch (err: any) {
    error.value = err.message || 'An error occurred'
  } finally {
    loading.value = false
  }
}
</script>
