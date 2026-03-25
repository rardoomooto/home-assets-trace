import { describe, it, expect, vi } from 'vitest'
import { itemApi } from '@/api/item'
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

describe('api/item.ts', () => {
  it('getAll should return items and total', async () => {
    const items = [{ id: 1, name: 'Item1', quantity: 2, price: 9.99, purchase_date: null, expiry_date: null, category_id: null, location: null, notes: null, usage: null, purchase_channel: null, user_id: 1, created_at: '', updated_at: '' }]
    const total = 1
    ;(api as any).get.mockResolvedValue({ data: { items, total } })

    const res = await itemApi.getAll({ name: 'Item' } as any)
    expect(res).toEqual({ items, total })
  })

  it('getById should return a single item', async () => {
    const item = { id: 2, name: 'Item2', quantity: 1, price: 5, purchase_date: null, expiry_date: null, category_id: null, location: null, notes: null, usage: null, purchase_channel: null, user_id: 1, created_at: '', updated_at: '' }
    ;(api as any).get.mockResolvedValue({ data: item })
    const res = await itemApi.getById(2)
    expect(res).toEqual(item)
  })

  it('getAll should throw on failure', async () => {
    ;(api as any).get.mockRejectedValue(new Error('request failed'))
    await expect(itemApi.getAll({} as any)).rejects.toThrow('request failed')
  })
})
