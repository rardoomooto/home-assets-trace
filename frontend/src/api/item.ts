import api from './index'
import type { Item, ItemListResponse } from '@/types'

export interface ItemCreate {
  name: string
  quantity?: number
  price?: number
  purchase_date?: string | null
  expiry_date?: string | null
  category_id?: number | null
  location?: string | null
  notes?: string | null
  usage?: string | null
  purchase_channel?: string | null
  room_id?: number | null
}

export interface ItemUpdate {
  name?: string
  quantity?: number
  price?: number
  purchase_date?: string | null
  expiry_date?: string | null
  category_id?: number | null
  location?: string | null
  notes?: string | null
  usage?: string | null
  purchase_channel?: string | null
  room_id?: number | null
}

export interface ItemQueryParams {
  name?: string
  category_id?: number
  expired?: boolean
  expiring_soon?: boolean
  skip?: number
  limit?: number
  room_id?: number
}

export const itemApi = {
  getAll: async (params?: ItemQueryParams): Promise<ItemListResponse> => {
    const response = await api.get<ItemListResponse>('/items', { params })
    return response.data
  },

  getById: async (id: number): Promise<Item> => {
    const response = await api.get<Item>(`/items/${id}`)
    return response.data
  },

  create: async (data: ItemCreate): Promise<Item> => {
    const response = await api.post<Item>('/items', data)
    return response.data
  },

  update: async (id: number, data: ItemUpdate): Promise<Item> => {
    const response = await api.put<Item>(`/items/${id}`, data)
    return response.data
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/items/${id}`)
  }
}
