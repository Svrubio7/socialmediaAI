/**
 * Toast notification composable.
 * Use for success, error, and info feedback without modals.
 */

export type ToastType = 'success' | 'error' | 'info'

export interface Toast {
  id: string
  message: string
  type: ToastType
  duration?: number
}

const toasts = ref<Toast[]>([])
const defaultDuration = 5000

let dismissTimer: ReturnType<typeof setTimeout> | null = null

export function useToast() {
  function add(message: string, type: ToastType = 'info', duration: number = defaultDuration) {
    const id = `toast-${Date.now()}-${Math.random().toString(36).slice(2)}`
    const toast: Toast = { id, message, type, duration }
    toasts.value = [...toasts.value, toast]
    if (duration > 0) {
      dismissTimer = setTimeout(() => {
        remove(id)
        dismissTimer = null
      }, duration)
    }
    return id
  }

  function remove(id: string) {
    toasts.value = toasts.value.filter((t) => t.id !== id)
  }

  function success(message: string, duration?: number) {
    return add(message, 'success', duration ?? defaultDuration)
  }

  function error(message: string, duration?: number) {
    return add(message, 'error', duration ?? defaultDuration)
  }

  function info(message: string, duration?: number) {
    return add(message, 'info', duration ?? defaultDuration)
  }

  return {
    toasts: readonly(toasts),
    add,
    remove,
    success,
    error,
    info,
  }
}
