import { describe, it, expect, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '@/stores/auth'
import { authApi } from '@/api/auth'
import { User } from '@/types'

vi.mock('@/api/auth', () => {
  return {
    authApi: {
      login: vi.fn(),
      register: vi.fn(),
      getCurrentUser: vi.fn()
    }
  }
})

describe('store auth.ts', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('login stores token and user and redirects to home', async () => {
    const token = { access_token: 'token-123', token_type: 'bearer' }
    const user: User = { id: 1, username: 'john', email: 'john@example.com', created_at: '2020-01-01' }

    ;(authApi.login as any).mockResolvedValue(token)
    ;(authApi.getCurrentUser as any).mockResolvedValue(user)

    const originalLocation = (window as any).location
    delete (window as any).location
    ;(window as any).location = { href: '' } as any

    const store = useAuthStore()
    await store.login('john', 'password')

    expect(store.token).toBe(token.access_token)
    expect(store.user).toEqual(user)
    expect(window.localStorage.getItem('token')).toBe(token.access_token)
    expect((window as any).location.href).toBe('/')

    // restore
    ;(window as any).location = originalLocation
  })

  it('logout clears auth state and redirects to login', () => {
    const originalLocation = (window as any).location
    delete (window as any).location
    ;(window as any).location = { href: '' } as any

    const store = useAuthStore()
    store.token = 'token-123'
    store.user = { id: 1, username: 'john', email: 'john@example.com', created_at: '2020-01-01' } as User
    store.logout()

    expect(store.token).toBe(null)
    expect(store.user).toBe(null)
    expect(window.localStorage.getItem('token')).toBe(null)
    expect((window as any).location.href).toBe('/login')

    ;(window as any).location = originalLocation
  })

  it('fetchUser loads user when token exists', async () => {
    const user: User = { id: 2, username: 'alice', email: 'alice@example.com', created_at: '2020-01-02' }
    ;(authApi.getCurrentUser as any).mockResolvedValue(user)
    window.localStorage.setItem('token', 'token')
    const store = useAuthStore()
    await store.fetchUser()
    expect(store.user).toEqual(user)
  })
})
