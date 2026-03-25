import { beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'

// Global setup for all tests
beforeEach(() => {
  // Ensure a fresh Pinia instance for every test
  setActivePinia(createPinia())
  // Reset localStorage to a clean state
  if (typeof window !== 'undefined' && window.localStorage) {
    window.localStorage.clear()
  }
  // Clear all mock state
  vi.restoreAllMocks()
  vi.clearAllMocks()
})
