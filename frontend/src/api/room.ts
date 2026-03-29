import api from './index'
import type { Room, Item } from '@/types'

export interface RoomCreate {
  name: string
}

export interface RoomUpdate {
  name?: string
}

export interface RoomListResponse {
  rooms: Room[]
  total: number
}

export interface RoomWithItemsResponse extends Room {
  items: Item[]
}

export const roomApi = {
  getAll: async (familyId?: number): Promise<Room[]> => {
    const params = familyId !== undefined ? { family_id: familyId } : {}
    const response = await api.get<RoomListResponse>('/rooms', { params })
    return response.data.rooms
  },

  create: async (data: RoomCreate): Promise<Room> => {
    const response = await api.post<Room>('/rooms', data)
    return response.data
  },

  update: async (id: number, data: RoomUpdate): Promise<Room> => {
    const response = await api.put<Room>(`/rooms/${id}`, data)
    return response.data
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/rooms/${id}`)
  },

  getRoomItems: async (roomId: number): Promise<RoomWithItemsResponse> => {
    const response = await api.get<RoomWithItemsResponse>(`/rooms/${roomId}/items`)
    return response.data
  }
}