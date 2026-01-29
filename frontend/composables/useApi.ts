/**
 * API client composable for making requests to the backend.
 */

interface ApiOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH'
  body?: any
  headers?: Record<string, string>
}

export const useApi = () => {
  const config = useRuntimeConfig()
  const supabase = useSupabaseClient()

  const getAuthHeaders = async (): Promise<Record<string, string>> => {
    const { data: { session } } = await supabase.auth.getSession()
    if (session?.access_token) {
      return {
        'Authorization': `Bearer ${session.access_token}`,
      }
    }
    return {}
  }

  const request = async <T>(endpoint: string, options: ApiOptions = {}): Promise<T> => {
    const { method = 'GET', body, headers = {} } = options
    
    const authHeaders = await getAuthHeaders()
    
    const response = await $fetch<T>(`${config.public.apiUrl}${endpoint}`, {
      method,
      body: body ? JSON.stringify(body) : undefined,
      headers: {
        'Content-Type': 'application/json',
        ...authHeaders,
        ...headers,
      },
    })

    return response
  }

  const get = <T>(endpoint: string, headers?: Record<string, string>) => 
    request<T>(endpoint, { method: 'GET', headers })

  const post = <T>(endpoint: string, body?: any, headers?: Record<string, string>) => 
    request<T>(endpoint, { method: 'POST', body, headers })

  const put = <T>(endpoint: string, body?: any, headers?: Record<string, string>) => 
    request<T>(endpoint, { method: 'PUT', body, headers })

  const del = <T>(endpoint: string, headers?: Record<string, string>) => 
    request<T>(endpoint, { method: 'DELETE', headers })

  const patch = <T>(endpoint: string, body?: any, headers?: Record<string, string>) => 
    request<T>(endpoint, { method: 'PATCH', body, headers })

  // Auth / user profile endpoints
  const authApi = {
    getMe: () => get<{ id: string; email: string; name?: string; avatar_url?: string; is_active: boolean; created_at: string }>('/auth/me'),
    updateMe: (body: { name?: string; avatar_url?: string }) => patch<{ id: string; email: string; name?: string; avatar_url?: string; is_active: boolean; created_at: string }>('/auth/me', body),
  }

  // Video endpoints
  const videos = {
    list: (params?: { page?: number; limit?: number; status?: string }) => {
      const query = new URLSearchParams()
      if (params?.page) query.set('page', params.page.toString())
      if (params?.limit) query.set('limit', params.limit.toString())
      if (params?.status) query.set('status', params.status)
      return get<any>(`/videos?${query}`)
    },
    get: (id: string) => get<any>(`/videos/${id}`),
    upload: async (file: File, title?: string) => {
      const formData = new FormData()
      formData.append('file', file)
      if (title) formData.append('title', title)
      
      const authHeaders = await getAuthHeaders()
      return $fetch(`${config.public.apiUrl}/videos/upload`, {
        method: 'POST',
        body: formData,
        headers: authHeaders,
      })
    },
    delete: (id: string) => del(`/videos/${id}`),
    analyze: (id: string) => post(`/videos/${id}/analyze`),
    edit: (id: string, data: any) => post(`/videos/${id}/edit`, data),
  }

  // Pattern endpoints
  const patterns = {
    list: (params?: { video_id?: string; min_score?: number }) => {
      const query = new URLSearchParams()
      if (params?.video_id) query.set('video_id', params.video_id)
      if (params?.min_score) query.set('min_score', params.min_score.toString())
      return get<any>(`/patterns?${query}`)
    },
    get: (id: string) => get<any>(`/patterns/${id}`),
    getByVideo: (videoId: string) => get<any>(`/patterns/video/${videoId}`),
  }

  // Strategy endpoints
  const strategies = {
    list: () => get<any>('/strategies'),
    get: (id: string) => get<any>(`/strategies/${id}`),
    generate: (data: { video_ids: string[]; platforms: string[]; goals?: string[]; niche?: string }) =>
      post<any>('/strategies/generate', data),
    export: (id: string, format: string = 'markdown') =>
      get<any>(`/strategies/${id}/export?format=${format}`),
  }

  // Script endpoints
  const scripts = {
    list: () => get<any>('/scripts'),
    get: (id: string) => get<any>(`/scripts/${id}`),
    generate: (data: { concept: string; platform: string; duration: number; target_patterns?: string[] }) =>
      post<any>('/scripts/generate', data),
    export: (id: string, format: string = 'json') =>
      get<any>(`/scripts/${id}/export?format=${format}`),
  }

  // OAuth endpoints
  const oauth = {
    connect: (platform: string) => get<any>(`/oauth/${platform}/connect`),
    accounts: () => get<any>('/oauth/accounts'),
    disconnect: (accountId: string) => del(`/oauth/accounts/${accountId}`),
    refresh: (accountId: string) => post(`/oauth/accounts/${accountId}/refresh`),
  }

  // Publishing endpoints
  const posts = {
    list: (params?: { status?: string; platform?: string }) => {
      const query = new URLSearchParams()
      if (params?.status) query.set('status', params.status)
      if (params?.platform) query.set('platform', params.platform)
      return get<any>(`/posts?${query}`)
    },
    scheduled: () => get<any>('/posts/scheduled'),
    publish: (data: { video_id: string; platforms: string[]; caption?: string; hashtags?: string[]; publish_now?: boolean }) =>
      post<any>('/posts/publish', data),
    schedule: (data: { video_id: string; platforms: string[]; scheduled_at: string; caption?: string; hashtags?: string[] }) =>
      post<any>('/posts/schedule', data),
    cancel: (scheduleId: string) => del(`/posts/scheduled/${scheduleId}`),
    retry: (postId: string) => post(`/posts/${postId}/retry`),
  }

  // Chat endpoint (Strategies conversational UI)
  const chat = {
    send: (messages: { role: string; content: string }[]) =>
      post<{ message: string; cards: { type: string; payload: Record<string, unknown> }[] }>('/chat', { messages }),
  }

  // Materials endpoints (user assets: logos, images)
  const materials = {
    list: (params?: { type?: string }) => {
      const query = new URLSearchParams()
      if (params?.type) query.set('type', params.type)
      return get<any>(`/materials?${query}`)
    },
    get: (id: string) => get<any>(`/materials/${id}`),
    upload: async (file: File, assetType: string = 'image') => {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('asset_type', assetType)
      const authHeaders = await getAuthHeaders()
      return $fetch(`${config.public.apiUrl}/materials/upload`, {
        method: 'POST',
        body: formData,
        headers: authHeaders,
      })
    },
    delete: (id: string) => del(`/materials/${id}`),
  }

  // Editor ops (foundation clip/transform/export)
  const editorOps = {
    execute: (videoId: string, op: string, params: Record<string, unknown> = {}) =>
      post<{ op: string; output_path?: string; result?: Record<string, unknown>; error?: string }>(
        `/editor/${videoId}/op`,
        { op, params }
      ),
  }

  // Edit templates (content library)
  const editTemplates = {
    list: (params?: { limit?: number; offset?: number }) => {
      const query = new URLSearchParams()
      if (params?.limit) query.set('limit', params.limit.toString())
      if (params?.offset) query.set('offset', params.offset.toString())
      return get<{ items: any[]; total: number }>(`/edit-templates?${query}`)
    },
    get: (id: string) => get<any>(`/edit-templates/${id}`),
    create: (body: { name: string; description?: string; style_spec?: Record<string, unknown> }) =>
      post<any>('/edit-templates', body),
    update: (id: string, body: { name?: string; description?: string; style_spec?: Record<string, unknown> }) =>
      patch<any>(`/edit-templates/${id}`, body),
    delete: (id: string) => del(`/edit-templates/${id}`),
    apply: (templateId: string, videoId: string) =>
      post<any>(`/edit-templates/${templateId}/apply`, { video_id: videoId }),
  }

  // Analytics endpoints
  const analytics = {
    video: (videoId: string) => get<any>(`/analytics/videos/${videoId}`),
    dashboard: (params?: { start_date?: string; end_date?: string; platform?: string }) => {
      const query = new URLSearchParams()
      if (params?.start_date) query.set('start_date', params.start_date)
      if (params?.end_date) query.set('end_date', params.end_date)
      if (params?.platform) query.set('platform', params.platform)
      return get<any>(`/analytics/dashboard?${query}`)
    },
    trends: (params?: { start_date?: string; end_date?: string; platform?: string }) => {
      const query = new URLSearchParams()
      if (params?.start_date) query.set('start_date', params.start_date)
      if (params?.end_date) query.set('end_date', params.end_date)
      if (params?.platform) query.set('platform', params.platform)
      return get<any>(`/analytics/trends?${query}`)
    },
    topPerformers: (params?: { limit?: number; platform?: string }) => {
      const query = new URLSearchParams()
      if (params?.limit) query.set('limit', params.limit.toString())
      if (params?.platform) query.set('platform', params.platform)
      return get<any>(`/analytics/top-performers?${query}`)
    },
  }

  return {
    request,
    get,
    post,
    put,
    del,
    patch,
    auth: authApi,
    videos,
    patterns,
    strategies,
    scripts,
    oauth,
    posts,
    chat,
    materials,
    editTemplates,
    editorOps,
    analytics,
  }
}
