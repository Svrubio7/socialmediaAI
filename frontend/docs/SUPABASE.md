# Nuxt + Supabase

## Where the keys go

| Supabase doc name | In this project | Where |
|-------------------|-----------------|--------|
| `SUPABASE_URL` | `NUXT_PUBLIC_SUPABASE_URL` | `frontend/.env` |
| `SUPABASE_KEY` (anon/publishable) | `NUXT_PUBLIC_SUPABASE_ANON_KEY` | `frontend/.env` |

Backend uses `SUPABASE_URL`, `SUPABASE_KEY` (service role), and `SUPABASE_JWT_SECRET` in `backend/.env`.

## Using Supabase in Nuxt (no manual client)

We use `@nuxtjs/supabase`, so you **don’t** create a client with `createClient()`. The module reads `NUXT_PUBLIC_SUPABASE_URL` and `NUXT_PUBLIC_SUPABASE_ANON_KEY` and provides composables.

### Get the client

```vue
<script setup>
const supabase = useSupabaseClient()
</script>
```

### Auth (login, signup, signOut)

```vue
<script setup>
const supabase = useSupabaseClient()

// Sign up
const { error } = await supabase.auth.signUp({ email, password })

// Sign in
const { error } = await supabase.auth.signInWithPassword({ email, password })

// Sign out
await supabase.auth.signOut()
</script>
```

### Query a table (e.g. todos)

```vue
<script setup>
const supabase = useSupabaseClient()
const todos = ref([])

async function getTodos() {
  const { data } = await supabase.from('todos').select()
  todos.value = data ?? []
}

onMounted(() => {
  getTodos()
})
</script>

<template>
  <ul>
    <li v-for="todo in todos" :key="todo.id">{{ todo.name }}</li>
  </ul>
</template>
```

### Other composables

- `useSupabaseUser()` – current user
- `useSupabaseSession()` – current session

All of these use the URL and anon key from your `.env` automatically.
