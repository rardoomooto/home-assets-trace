import { describe, it, expect, vi } from 'vitest'
import { roomApi } from '@/api/room'
import api from '@/api/index'

vi.mock('@/api/index', () => {
  const m = {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  }
  return {
    __esModule: true,
    default: m,
  }
})

describe('api/room.ts', () => {
  it('getAll should extract rooms array from { rooms, total } response', async () => {
    const rooms = [
      { id: 1, name: 'Living Room', user_id: 1, created_at: '2024-01-01' },
      { id: 2, name: 'Bedroom', user_id: 1, created_at: '2024-01-02' }
    ]
    const total = 2
    ;(api as any).get.mockResolvedValue({ data: { rooms, total } })

    const res = await roomApi.getAll()
    // 关键断言：确保 getAll 方法正确从 { rooms, total } 中提取 rooms 数组
    expect(res).toEqual(rooms)
    expect(res).toHaveLength(2)
    expect(res[0].name).toBe('Living Room')
    expect(res[1].name).toBe('Bedroom')
  })

  it('getAll should return empty array when no rooms', async () => {
    ;(api as any).get.mockResolvedValue({ data: { rooms: [], total: 0 } })

    const res = await roomApi.getAll()
    expect(res).toEqual([])
    expect(res).toHaveLength(0)
  })

  it('create should return created room', async () => {
    const room = { id: 3, name: 'Kitchen', user_id: 1, created_at: '2024-01-03' }
    ;(api as any).post.mockResolvedValue({ data: room })

    const res = await roomApi.create({ name: 'Kitchen' })
    expect(res).toEqual(room)
    expect(res.name).toBe('Kitchen')
  })

  it('update should return updated room', async () => {
    const room = { id: 1, name: 'Updated Room', user_id: 1, created_at: '2024-01-01' }
    ;(api as any).put.mockResolvedValue({ data: room })

    const res = await roomApi.update(1, { name: 'Updated Room' })
    expect(res).toEqual(room)
    expect(res.name).toBe('Updated Room')
  })

  it('delete should call api.delete', async () => {
    ;(api as any).delete.mockResolvedValue({})

    await roomApi.delete(1)
    expect(api.delete).toHaveBeenCalledWith('/rooms/1')
  })
})