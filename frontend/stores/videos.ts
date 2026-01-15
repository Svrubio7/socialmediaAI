/**
 * Videos store for managing video state.
 */

import { defineStore } from 'pinia'

interface Video {
  id: string
  filename: string
  original_filename?: string
  thumbnail_url?: string
  status: 'uploaded' | 'processing' | 'processed' | 'failed'
  duration?: number
  width?: number
  height?: number
  file_size?: number
  tags: string[]
  created_at: string
  updated_at: string
}

interface VideosState {
  videos: Video[]
  currentVideo: Video | null
  loading: boolean
  total: number
  page: number
  limit: number
}

export const useVideosStore = defineStore('videos', {
  state: (): VideosState => ({
    videos: [],
    currentVideo: null,
    loading: false,
    total: 0,
    page: 1,
    limit: 20,
  }),

  getters: {
    hasVideos: (state) => state.videos.length > 0,
    processedVideos: (state) => state.videos.filter(v => v.status === 'processed'),
    pendingVideos: (state) => state.videos.filter(v => v.status === 'processing'),
  },

  actions: {
    async fetchVideos(params?: { page?: number; limit?: number; status?: string }) {
      this.loading = true
      try {
        const api = useApi()
        const response = await api.videos.list({
          page: params?.page || this.page,
          limit: params?.limit || this.limit,
          status: params?.status,
        })
        this.videos = response.items
        this.total = response.total
        this.page = response.page
        this.limit = response.limit
      } catch (error) {
        console.error('Failed to fetch videos:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    async fetchVideo(id: string) {
      this.loading = true
      try {
        const api = useApi()
        this.currentVideo = await api.videos.get(id)
      } catch (error) {
        console.error('Failed to fetch video:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    async uploadVideo(file: File, title?: string) {
      this.loading = true
      try {
        const api = useApi()
        const response = await api.videos.upload(file, title)
        await this.fetchVideos()
        return response
      } catch (error) {
        console.error('Failed to upload video:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    async deleteVideo(id: string) {
      try {
        const api = useApi()
        await api.videos.delete(id)
        this.videos = this.videos.filter(v => v.id !== id)
        if (this.currentVideo?.id === id) {
          this.currentVideo = null
        }
      } catch (error) {
        console.error('Failed to delete video:', error)
        throw error
      }
    },

    async analyzeVideo(id: string) {
      try {
        const api = useApi()
        const response = await api.videos.analyze(id)
        // Update video status
        const video = this.videos.find(v => v.id === id)
        if (video) {
          video.status = 'processing'
        }
        return response
      } catch (error) {
        console.error('Failed to analyze video:', error)
        throw error
      }
    },

    clearCurrentVideo() {
      this.currentVideo = null
    },
  },
})
