import { describe, it, expect, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useItemStore } from '@/stores/item'
import { itemApi } from '@/api/item'
import type { ItemQueryParams } from '@/api/item'
import { Item } from '@/types'

vi.mock('@/api/item', () => {
  return {
    itemApi: {
      getAll: vi.fn(),
      getById: vi.fn(),
      create: vi.fn(),
      update: vi.fn(),
      delete: vi.fn()
    }
  }
})

describe('store item.ts', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('fetchItems populates items and total', async () => {
    const items: Item[] = [
      { id: 1, name: 'Item1', quantity: 2, price: 9.99, purchase_date: null, expiry_date: null, category_id: null, location: null, notes: null, usage: null, purchase_channel: null, user_id: 1, created_at: '', updated_at: '' }
    ]
    const total = 1
    ;(itemApi.getAll as any).mockResolvedValue({ items, total } as any)

    const store = useItemStore()
    await store.fetchItems({ name: 'Item' } as ItemQueryParams)

    expect(store.items).toEqual(items)
    expect(store.total).toBe(total)
    expect(store.loading).toBe(false)
  })

  it('createItem adds new item and increments total', async () => {
    const newItem = { id: 2, name: 'NewItem', quantity: 1, price: 5, purchase_date: null, expiry_date: null, category_id: null, location: null, notes: null, usage: null, purchase_channel: null, user_id: 1, created_at: '', updated_at: '' }
    ;(itemApi.create as any).mockResolvedValue(newItem)

    const store = useItemStore()
    const created = await store.createItem({ name: 'NewItem' } as any)
    expect(created).toEqual(newItem)
    expect(store.items[0]).toEqual(newItem)
    expect(store.total).toBe(1)
  })
})
