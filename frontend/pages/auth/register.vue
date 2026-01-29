<template>
  <NuxtLayout name="auth">
    <Card class="backdrop-blur-xl bg-surface-900/80 border-surface-700/50">
      <div class="text-center mb-8">
        <h1 class="text-2xl font-mono font-normal text-surface-100">Create account</h1>
        <p class="text-surface-400 mt-2">Start your free trial with ElevoAI</p>
      </div>

      <form @submit.prevent="handleRegister" class="space-y-5">
        <Input
          v-model="name"
          label="Full name"
          type="text"
          placeholder="John Doe"
          required
        >
          <template #icon-left>
            <UiIcon name="User" :size="18" />
          </template>
        </Input>

        <Input
          v-model="email"
          label="Email"
          type="email"
          placeholder="you@example.com"
          required
        >
          <template #icon-left>
            <UiIcon name="Mail" :size="18" />
          </template>
        </Input>

        <Input
          v-model="password"
          label="Password"
          type="password"
          placeholder="Create a strong password"
          required
          hint="At least 6 characters"
        >
          <template #icon-left>
            <UiIcon name="Lock" :size="18" />
          </template>
        </Input>

        <div v-if="error" class="p-3 rounded-lg bg-red-500/10 border border-red-500/20">
          <p class="text-red-400 text-sm text-center">{{ error }}</p>
        </div>

        <div v-if="success" class="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20">
          <div class="flex items-center gap-2 justify-center">
            <UiIcon name="CheckCircle" :size="18" class="text-emerald-400" />
            <p class="text-emerald-400 text-sm">{{ success }}</p>
          </div>
        </div>

        <Button
          type="submit"
          variant="primary"
          full-width
          :loading="loading"
        >
          Create account
        </Button>
      </form>

      <div class="relative my-6">
        <div class="absolute inset-0 flex items-center">
          <div class="w-full border-t border-surface-700"></div>
        </div>
        <div class="relative flex justify-center text-sm">
          <span class="px-4 bg-surface-900 text-surface-500">or sign up with</span>
        </div>
      </div>

      <div class="grid grid-cols-2 gap-3">
        <Button variant="secondary" @click="signUpWithGoogle">
          <svg class="w-5 h-5" viewBox="0 0 24 24">
            <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
            <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
            <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
            <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
          </svg>
          <span>Google</span>
        </Button>
        <Button variant="secondary" @click="signUpWithGithub">
          <UiIcon name="Github" :size="20" />
          <span>GitHub</span>
        </Button>
      </div>

      <p class="text-center text-surface-400 text-sm mt-6">
        Already have an account?
        <NuxtLink to="/auth/login" class="text-primary-400 hover:text-primary-300 font-medium">
          Sign in
        </NuxtLink>
      </p>

      <p class="text-center text-surface-500 text-xs mt-4">
        By creating an account, you agree to our
        <NuxtLink to="/terms" class="text-surface-400 hover:text-surface-300">Terms of Service</NuxtLink>
        and
        <NuxtLink to="/privacy" class="text-surface-400 hover:text-surface-300">Privacy Policy</NuxtLink>
      </p>
    </Card>
  </NuxtLayout>
</template>

<script setup lang="ts">
definePageMeta({
  layout: false,
  middleware: 'guest',
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

const signUpWithGoogle = async () => {
  const { error } = await supabase.auth.signInWithOAuth({
    provider: 'google',
    options: {
      redirectTo: `${window.location.origin}/auth/callback`,
    },
  })
  if (error) console.error('Error signing up with Google:', error)
}

const signUpWithGithub = async () => {
  const { error } = await supabase.auth.signInWithOAuth({
    provider: 'github',
    options: {
      redirectTo: `${window.location.origin}/auth/callback`,
    },
  })
  if (error) console.error('Error signing up with GitHub:', error)
}
</script>
