import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useRoomStore } from '@/stores/room'
import { roomApi } from '@/api/room'
import type { Room, Item } from '@/types'
import type { RoomWithItemsResponse } from '@/api/room'

vi.mock('@/api/room', () => {
  return {
    roomApi: {
      getAll: vi.fn(),
      create: vi.fn(),
      update: vi.fn(),
      delete: vi.fn(),
      getRoomItems: vi.fn()
    }
  }
})

describe('store room.ts', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  const mockRoom: Room = {
    id: 1,
    name: 'Living Room',
    user_id: 1,
    created_at: '2024-01-01T00:00:00Z'
  }

  const mockItem: Item = {
    id: 1,
    name: 'Sofa',
    quantity: 1,
    price: 999.99,
    purchase_date: null,
    expiry_date: null,
    category_id: null,
    location: null,
    notes: null,
    usage: null,
    purchase_channel: null,
    user_id: 1,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z'
  }

  const mockRoomWithItems: RoomWithItemsResponse = {
    ...mockRoom,
    items: [mockItem]
  }

  describe('getRoomItems', () => {
    it('fetches items for a room and caches them', async () => {
      vi.mocked(roomApi.getRoomItems).mockResolvedValue(mockRoomWithItems)

      const store = useRoomStore()
      const items = await store.getRoomItems(1)

      expect(roomApi.getRoomItems).toHaveBeenCalledWith(1)
      expect(items).toEqual([mockItem])
      expect(store.roomsWithItems.get(1)).toEqual(mockRoomWithItems)
      expect(store.loadingRoomItems).toBe(false)
    })

    it('handles loading state correctly', async () => {
      let resolvePromise: (value: RoomWithItemsResponse) => void
      const promise = new Promise<RoomWithItemsResponse>((resolve) => {
        resolvePromise = resolve
      })
      vi.mocked(roomApi.getRoomItems).mockImplementation(() => promise)

      const store = useRoomStore()
      const itemsPromise = store.getRoomItems(1)

      expect(store.loadingRoomItems).toBe(true)

      resolvePromise!(mockRoomWithItems)
      await itemsPromise

      expect(store.loadingRoomItems).toBe(false)
    })

    it('updates cache when called again (refresh scenario)', async () => {
      const store = useRoomStore()
      
      // Initial fetch
      vi.mocked(roomApi.getRoomItems).mockResolvedValueOnce(mockRoomWithItems)
      await store.getRoomItems(1)
      expect(store.roomsWithItems.get(1)).toEqual(mockRoomWithItems)
      
      // Simulate adding a new item
      const newItem: Item = {
        id: 2,
        name: 'Table',
        quantity: 1,
        price: 500,
        purchase_date: null,
        expiry_date: null,
        category_id: null,
        location: null,
        notes: null,
        usage: null,
        purchase_channel: null,
        user_id: 1,
        created_at: '2024-01-02T00:00:00Z',
        updated_at: '2024-01-02T00:00:00Z'
      }
      
      const updatedRoomWithItems: RoomWithItemsResponse = {
        ...mockRoom,
        items: [mockItem, newItem]
      }
      
      // Second fetch (refresh) should update cache with new item
      vi.mocked(roomApi.getRoomItems).mockResolvedValueOnce(updatedRoomWithItems)
      await store.getRoomItems(1)
      
      expect(roomApi.getRoomItems).toHaveBeenCalledTimes(2)
      expect(store.roomsWithItems.get(1)).toEqual(updatedRoomWithItems)
      expect(store.roomsWithItems.get(1)?.items).toHaveLength(2)
    })
  })

  describe('fetchRoomsWithItems', () => {
    it('fetches all rooms and their items', async () => {
      const mockRooms = [mockRoom]
      const mockRoomsWithItems = [mockRoomWithItems]

      vi.mocked(roomApi.getAll).mockResolvedValue(mockRooms)
      vi.mocked(roomApi.getRoomItems).mockResolvedValue(mockRoomWithItems)

      const store = useRoomStore()
      const result = await store.fetchRoomsWithItems()

      expect(roomApi.getAll).toHaveBeenCalled()
      expect(roomApi.getRoomItems).toHaveBeenCalledWith(1)
      expect(store.rooms).toEqual(mockRooms)
      expect(store.roomsWithItems.get(1)).toEqual(mockRoomWithItems)
      expect(result).toEqual(mockRoomsWithItems)
      expect(store.loading).toBe(false)
      expect(store.loadingRoomItems).toBe(false)
    })


  })

  describe('existing methods', () => {
    it('fetchRooms populates rooms', async () => {
      const mockRooms = [mockRoom]
      vi.mocked(roomApi.getAll).mockResolvedValue(mockRooms)

      const store = useRoomStore()
      await store.fetchRooms()

      expect(roomApi.getAll).toHaveBeenCalled()
      expect(store.rooms).toEqual(mockRooms)
      expect(store.loading).toBe(false)
    })

    it('createRoom adds new room to the beginning', async () => {
      const newRoom = { ...mockRoom, id: 2, name: 'Bedroom' }
      vi.mocked(roomApi.create).mockResolvedValue(newRoom)

      const store = useRoomStore()
      const created = await store.createRoom('Bedroom')

      expect(roomApi.create).toHaveBeenCalledWith({ name: 'Bedroom' })
      expect(created).toEqual(newRoom)
      expect(store.rooms[0]).toEqual(newRoom)
    })

    it('updateRoom updates room in list and currentRoom if matches', async () => {
      const updatedRoom = { ...mockRoom, name: 'Updated Living Room' }
      vi.mocked(roomApi.update).mockResolvedValue(updatedRoom)

      const store = useRoomStore()
      store.rooms = [mockRoom]
      store.currentRoom = mockRoom

      const result = await store.updateRoom(1, { name: 'Updated Living Room' })

      expect(roomApi.update).toHaveBeenCalledWith(1, { name: 'Updated Living Room' })
      expect(result).toEqual(updatedRoom)
      expect(store.rooms[0]).toEqual(updatedRoom)
      expect(store.currentRoom).toEqual(updatedRoom)
    })

    it('deleteRoom removes room from list and clears currentRoom if matches', async () => {
      vi.mocked(roomApi.delete).mockResolvedValue(undefined)

      const store = useRoomStore()
      store.rooms = [mockRoom]
      store.currentRoom = mockRoom

      await store.deleteRoom(1)

      expect(roomApi.delete).toHaveBeenCalledWith(1)
      expect(store.rooms).toEqual([])
      expect(store.currentRoom).toBeNull()
    })
  })
})