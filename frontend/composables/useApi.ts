/**
 * API client composable for making requests to the backend.
 */

interface ApiOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH'
  body?: any
  headers?: Record<string, string>
}

const API_REQUEST_TIMEOUT_MS = 15000
const TOKEN_TIMEOUT_MS = 4000

const withTimeout = <T>(promise: Promise<T>, timeoutMs: number): Promise<T> =>
  new Promise<T>((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error(`Timed out after ${timeoutMs}ms`)), timeoutMs)
    promise
      .then((value) => {
        clearTimeout(timer)
        resolve(value)
      })
      .catch((error) => {
        clearTimeout(timer)
        reject(error)
      })
  })

const safeNumber = (value: number) => (Number.isFinite(value) ? value : undefined)

const generateId = () => {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
    return crypto.randomUUID()
  }
  return `vid_${Date.now()}_${Math.random().toString(16).slice(2)}`
}

const extensionFromType = (mime: string) => {
  const map: Record<string, string> = {
    'video/mp4': '.mp4',
    'video/quicktime': '.mov',
    'video/x-m4v': '.m4v',
    'video/webm': '.webm',
    'video/ogg': '.ogv',
  }
  return map[mime] || ''
}

const getFileExtension = (file: File) => {
  const name = file.name || ''
  const idx = name.lastIndexOf('.')
  if (idx > -1) return name.slice(idx).toLowerCase()
  return extensionFromType(file.type) || '.mp4'
}

const getVideoMetadata = async (file: File): Promise<{ duration?: number; width?: number; height?: number }> => {
  if (!process.client) return {}
  return new Promise((resolve) => {
    const url = URL.createObjectURL(file)
    const video = document.createElement('video')
    video.preload = 'metadata'
    video.muted = true
    video.src = url
    video.load()
    video.onloadedmetadata = () => {
      const duration = safeNumber(video.duration)
      const width = safeNumber(video.videoWidth)
      const height = safeNumber(video.videoHeight)
      URL.revokeObjectURL(url)
      resolve({ duration, width, height })
    }
    video.onerror = () => {
      URL.revokeObjectURL(url)
      resolve({})
    }
  })
}

const createVideoThumbnail = async (file: File, seekTime = 0.1): Promise<Blob | null> => {
  if (!process.client) return null
  return new Promise((resolve) => {
    const url = URL.createObjectURL(file)
    const video = document.createElement('video')
    video.preload = 'metadata'
    video.muted = true
    video.src = url
    video.load()
    video.onloadedmetadata = () => {
      const safeTime = Math.min(Math.max(seekTime, 0), Math.max(0, (video.duration || 0) - 0.1))
      try {
        video.currentTime = safeTime
      } catch {
        video.currentTime = 0
      }
    }
    video.onseeked = () => {
      const canvas = document.createElement('canvas')
      canvas.width = video.videoWidth || 1280
      canvas.height = video.videoHeight || 720
      const ctx = canvas.getContext('2d')
      if (!ctx) {
        URL.revokeObjectURL(url)
        resolve(null)
        return
      }
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height)
      canvas.toBlob(
        (blob) => {
          URL.revokeObjectURL(url)
          resolve(blob || null)
        },
        'image/jpeg',
        0.86
      )
    }
    video.onerror = () => {
      URL.revokeObjectURL(url)
      resolve(null)
    }
  })
}

export const useApi = () => {
  const config = useRuntimeConfig()
  const supabase = useSupabaseClient()
  const baseUrl = (config.public.apiUrl || '').replace(/\/$/, '')
  const signedUrlTtl = 3600

  const createSignedUrl = async (path?: string): Promise<string | undefined> => {
    if (!process.client || !path) return undefined
    const bucket = config.public.supabaseStorageBucket || 'videos'
    try {
      const { data, error } = await supabase.storage.from(bucket).createSignedUrl(path, signedUrlTtl)
      if (error) return undefined
      return data?.signedUrl || data?.signedURL || data?.signed_url
    } catch {
      return undefined
    }
  }

  const getAccessToken = async (): Promise<string | undefined> => {
    try {
      const { data: { session } } = await withTimeout(supabase.auth.getSession(), TOKEN_TIMEOUT_MS)
      return session?.access_token
    } catch {
      return undefined
    }
  }

  const withAccessToken = async (url?: string): Promise<string | undefined> => {
    if (!process.client || !url) return url
    if (!url.includes('/videos/') || !url.includes('/stream')) return url
    const token = await getAccessToken()
    if (!token) return url
    try {
      const parsed = new URL(url, window.location.origin)
      parsed.searchParams.set('token', token)
      if (/^https?:\/\//i.test(url)) {
        return parsed.toString()
      }
      return `${parsed.pathname}${parsed.search}${parsed.hash}`
    } catch {
      // Fallback for malformed/relative URLs that URL() cannot parse cleanly.
      let cleaned = url.replace(/([?&])token=[^&]*(&?)/, (_m, sep, tail) => (sep === '?' && tail ? '?' : sep))
      cleaned = cleaned.replace(/[?&]$/, '')
      const join = cleaned.includes('?') ? '&' : '?'
      return `${cleaned}${join}token=${encodeURIComponent(token)}`
    }
  }

  const hydrateVideoUrls = async (video: any) => {
    if (!process.client || !video) return video
    if (!video.video_url && video.storage_path) {
      video.video_url = await createSignedUrl(video.storage_path)
    }
    const thumbPath = video.thumbnail_storage_path
    if (!video.thumbnail_url && thumbPath) {
      video.thumbnail_url = await createSignedUrl(thumbPath)
    }
    if (video.video_url) {
      video.video_url = await withAccessToken(video.video_url)
    }
    return video
  }

  const getAuthHeaders = async (): Promise<Record<string, string>> => {
    const token = await getAccessToken()
    if (token) {
      return { 'Authorization': `Bearer ${token}` }
    }
    return {}
  }

  const request = async <T>(endpoint: string, options: ApiOptions = {}): Promise<T> => {
    const { method = 'GET', body, headers = {} } = options
    
    const authHeaders = await getAuthHeaders()
    const isFormData = typeof FormData !== 'undefined' && body instanceof FormData
    const shouldSetJsonContentType = !isFormData && body !== undefined && method !== 'GET'
    
    const response = await $fetch<T>(`${baseUrl}${endpoint}`, {
      method,
      body: body ?? undefined,
      timeout: API_REQUEST_TIMEOUT_MS,
      headers: {
        ...(shouldSetJsonContentType ? { 'Content-Type': 'application/json' } : {}),
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
      return get<any>(`/videos?${query}`).then(async (response) => {
        if (response?.items?.length) {
          response.items = await Promise.all(response.items.map(hydrateVideoUrls))
        }
        return response
      })
    },
    get: (id: string) => get<any>(`/videos/${id}`).then(hydrateVideoUrls),
    upload: async (file: File, title?: string) => {
      if (!process.client) throw new Error('Upload must run in the browser')
      const { data: { user }, error } = await supabase.auth.getUser()
      if (error || !user) throw new Error('Not authenticated')

      const bucket = config.public.supabaseStorageBucket || 'videos'
      const fileId = generateId()
      const ext = getFileExtension(file)
      const storagePath = `videos/${user.id}/${fileId}${ext}`

      const { error: uploadError } = await supabase.storage
        .from(bucket)
        .upload(storagePath, file, {
          upsert: false,
          contentType: file.type || 'video/mp4',
        })
      if (uploadError) {
        const details = uploadError.message || 'Supabase upload failed.'
        throw new Error(`${details} Verify the storage bucket name and RLS policies for '${bucket}'.`)
      }

      const metadata = await getVideoMetadata(file)
      let thumbPath: string | undefined
      const thumbBlob = await createVideoThumbnail(file)
      if (thumbBlob) {
        thumbPath = `thumbnails/${user.id}/${fileId}.jpg`
        const { error: thumbError } = await supabase.storage
          .from(bucket)
          .upload(thumbPath, thumbBlob, {
            upsert: true,
            contentType: 'image/jpeg',
          })
        if (thumbError) {
          thumbPath = undefined
        }
      }

      try {
        return await post('/videos/register', {
          storage_path: storagePath,
          thumbnail_storage_path: thumbPath,
          filename: title || file.name,
          original_filename: file.name,
          file_size: file.size,
          duration: metadata.duration,
          width: metadata.width,
          height: metadata.height,
        })
      } catch (err) {
        const paths = [storagePath, thumbPath].filter(Boolean) as string[]
        if (paths.length) {
          await supabase.storage.from(bucket).remove(paths)
        }
        throw err
      }
    },
    delete: (id: string) => del(`/videos/${id}`),
    analyze: (id: string) => post(`/videos/${id}/analyze`),
    edit: (id: string, data: any) => post(`/videos/${id}/edit`, data),
  }

  // Editor projects
  const projects = {
    list: (params?: { page?: number; limit?: number }) => {
      const query = new URLSearchParams()
      if (params?.page) query.set('page', params.page.toString())
      if (params?.limit) query.set('limit', params.limit.toString())
      return get<any>(`/projects?${query}`)
    },
    get: (id: string) => get<any>(`/projects/${id}`),
    create: (body: { name?: string; description?: string }) => post<any>('/projects', body),
    update: (id: string, body: { name?: string; description?: string; state?: Record<string, unknown> }) =>
      patch<any>(`/projects/${id}`, body),
    delete: (id: string) => del(`/projects/${id}`),
    export: (id: string, body?: { output_title?: string; output_settings?: Record<string, unknown> }) =>
      post<any>(`/projects/${id}/export`, body).then(async (response) => {
        if (process.client && response?.output_path && !response?.output_url) {
          response.output_url = await createSignedUrl(response.output_path)
        }
        return response
      }),
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

  // Branding endpoints (user assets: logos, images)
  const branding = {
    list: (params?: { type?: string }) => {
      const query = new URLSearchParams()
      if (params?.type) query.set('type_filter', params.type)
      return get<any>(`/branding?${query}`).then(async (response) => {
        if (!process.client || !response?.items?.length) return response
        response.items = await Promise.all(
          response.items.map(async (item: any) => {
            if (!item?.url && item?.storage_path) {
              item.url = await createSignedUrl(item.storage_path)
            }
            return item
          })
        )
        return response
      })
    },
    get: (id: string) =>
      get<any>(`/branding/${id}`).then(async (item) => {
        if (process.client && item?.storage_path && !item?.url) {
          item.url = await createSignedUrl(item.storage_path)
        }
        return item
      }),
    upload: async (file: File, assetType: string = 'image') => {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('asset_type', assetType)
      const authHeaders = await getAuthHeaders()
      return $fetch(`${baseUrl}/branding/upload`, {
        method: 'POST',
        body: formData,
        headers: authHeaders,
      })
    },
    delete: (id: string) => del(`/branding/${id}`),
  }

  // Editor ops (foundation clip/transform/export)
  const editorOps = {
    execute: (
      videoId: string,
      op: string,
      params: Record<string, unknown> = {},
      options?: { saveToLibrary?: boolean; outputTitle?: string }
    ) =>
      post<{
        op: string
        output_path?: string
        output_url?: string
        output_video_id?: string
        result?: Record<string, unknown>
        error?: string
      }>(
        `/editor/${videoId}/op`,
        {
          op,
          params,
          save_to_library: options?.saveToLibrary ?? true,
          output_title: options?.outputTitle,
        }
      ).then(async (response) => {
        if (process.client && response?.output_path && !response?.output_url) {
          response.output_url = await createSignedUrl(response.output_path)
        }
        return response
      }),
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
    withAccessToken,
    auth: authApi,
    videos,
    projects,
    patterns,
    strategies,
    scripts,
    oauth,
    posts,
    chat,
    branding,
    editTemplates,
    editorOps,
    analytics,
  }
}
