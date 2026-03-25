import { describe, it, expect, vi } from 'vitest'
import { authApi } from '@/api/auth'
import api from '@/api/index'

// Mock the underlying API client used by authApi
vi.mock('@/api/index', () => {
  const m = {
    post: vi.fn(),
    get: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  }
  return {
    __esModule: true,
    default: m,
  }
})

describe('api/auth.ts', () => {
  it('login should return token data on success', async () => {
    const mockToken = { access_token: 'token-123', token_type: 'bearer' }
    ;(api as any).post.mockResolvedValue({ data: mockToken })

    const res = await authApi.login({ username: 'user', password: 'pass' })
    expect(res).toEqual(mockToken)
  })

  it('getCurrentUser should return user data on success', async () => {
    const mockUser = { id: 1, username: 'john', email: 'john@example.com', created_at: '2020-01-01' }
    ;(api as any).get.mockResolvedValue({ data: mockUser })

    const res = await authApi.getCurrentUser()
    expect(res).toEqual(mockUser)
  })

  it('login should throw on failure', async () => {
    ;(api as any).post.mockRejectedValue(new Error('Invalid credentials'))
    await expect(authApi.login({ username: 'bad', password: 'bad' })).rejects.toThrow('Invalid credentials')
  })
})
