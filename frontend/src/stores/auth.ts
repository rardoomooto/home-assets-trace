import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User, Token } from '@/types'
import { authApi } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('token'))
  const user = ref<User | null>(null)

  const isAuthenticated = computed(() => !!token.value)

  async function login(username: string, password: string) {
    const response: Token = await authApi.login({ username, password })
    token.value = response.access_token
    localStorage.setItem('token', response.access_token)
    await fetchUser()
    window.location.href = '/'
  }

  async function register(username: string, email: string, password: string) {
    await authApi.register({ username, email, password })
  }

  async function fetchUser() {
    if (!token.value) return
    try {
      user.value = await authApi.getCurrentUser()
    } catch {
      logout()
    }
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
    window.location.href = '/login'
  }

  if (token.value) {
    fetchUser()
  }

  return {
    token,
    user,
    isAuthenticated,
    login,
    register,
    fetchUser,
    logout
  }
})
