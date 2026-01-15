/**
 * Auth store for managing user authentication state.
 */

import { defineStore } from 'pinia'

interface User {
  id: string
  email: string
  name?: string
  avatar_url?: string
}

interface AuthState {
  user: User | null
  loading: boolean
  initialized: boolean
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    user: null,
    loading: false,
    initialized: false,
  }),

  getters: {
    isAuthenticated: (state) => !!state.user,
    currentUser: (state) => state.user,
  },

  actions: {
    setUser(user: User | null) {
      this.user = user
      this.initialized = true
    },

    setLoading(loading: boolean) {
      this.loading = loading
    },

    async initialize() {
      if (this.initialized) return

      const supabase = useSupabaseClient()
      const { data: { user } } = await supabase.auth.getUser()

      if (user) {
        this.user = {
          id: user.id,
          email: user.email!,
          name: user.user_metadata?.name,
          avatar_url: user.user_metadata?.avatar_url,
        }
      }

      this.initialized = true
    },

    async logout() {
      const supabase = useSupabaseClient()
      await supabase.auth.signOut()
      this.user = null
      navigateTo('/')
    },
  },
})
