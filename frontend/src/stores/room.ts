import { defineStore } from 'pinia'
import { ref, watch } from 'vue'
import type { Room, Item } from '@/types'
import { roomApi } from '@/api/room'
import type { RoomUpdate, RoomWithItemsResponse } from '@/api/room'
import { useFamilyStore } from './family'

// Pinia store for Rooms with CRUD operations using roomApi
export const useRoomStore = defineStore('room', () => {
  const rooms = ref<Room[]>([])
  const loading = ref(false)
  const currentRoom = ref<Room | null>(null)
  const roomsWithItems = ref<Map<number, RoomWithItemsResponse>>(new Map())
  const loadingRoomItems = ref(false)
  const familyStore = useFamilyStore()
  
  // 监听当前家庭变化，自动重新获取房间
  watch(
    () => familyStore.currentFamilyId,
    (newFamilyId) => {
      if (newFamilyId !== null) {
        fetchRooms(newFamilyId)
      }
    },
    { immediate: false }
  )

  async function fetchRooms(familyId?: number) {
    loading.value = true
    try {
      rooms.value = await roomApi.getAll(familyId)
    } finally {
      loading.value = false
    }
  }

  async function createRoom(name: string, familyId?: number | null) {
    const room = await roomApi.create({ name, family_id: familyId })
    rooms.value.unshift(room)
    return room
  }

  async function updateRoom(id: number, data: RoomUpdate) {
    const room = await roomApi.update(id, data)
    const index = rooms.value.findIndex(r => r.id === id)
    if (index !== -1) {
      rooms.value[index] = room
    }
    if (currentRoom.value?.id === id) {
      currentRoom.value = room
    }
    return room
  }

  async function deleteRoom(id: number) {
    await roomApi.delete(id)
    rooms.value = rooms.value.filter(r => r.id !== id)
    if (currentRoom.value?.id === id) {
      currentRoom.value = null
    }
  }

  async function getRoomItems(roomId: number): Promise<Item[]> {
    loadingRoomItems.value = true
    try {
      const roomWithItems = await roomApi.getRoomItems(roomId)
      roomsWithItems.value.set(roomId, roomWithItems)
      return roomWithItems.items
    } finally {
      loadingRoomItems.value = false
    }
  }

  async function fetchRoomsWithItems(familyId?: number): Promise<RoomWithItemsResponse[]> {
    loading.value = true
    loadingRoomItems.value = true
    try {
      // First fetch all rooms (filtered by family if provided)
      const roomsList = await roomApi.getAll(familyId)
      rooms.value = roomsList
      
      // Then fetch items for each room in parallel
      const roomsWithItemsList = await Promise.all(
        roomsList.map(room => roomApi.getRoomItems(room.id))
      )
      
      // Cache the results
      roomsWithItemsList.forEach(roomWithItems => {
        roomsWithItems.value.set(roomWithItems.id, roomWithItems)
      })
      
      return roomsWithItemsList
    } finally {
      loading.value = false
      loadingRoomItems.value = false
    }
  }

  return {
    rooms,
    loading,
    currentRoom,
    roomsWithItems,
    loadingRoomItems,
    fetchRooms,
    createRoom,
    updateRoom,
    deleteRoom,
    getRoomItems,
    fetchRoomsWithItems,
  }
})
