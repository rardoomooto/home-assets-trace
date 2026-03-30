<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useRoomStore } from '@/stores/room'
import { useFamilyStore } from '@/stores/family'
import type { Item } from '@/types'

const roomStore = useRoomStore()
const familyStore = useFamilyStore()

const showAddModal = ref(false)
const showEditModal = ref(false)
const editingRoom = ref<number | null>(null)
const roomName = ref('')
const error = ref('')

// 展开/折叠状态
const expandedRooms = ref<Set<number>>(new Set())
const loadingItems = ref<Record<number, boolean>>({})

// 根据当前家庭过滤房间
const filteredRooms = computed(() => {
  if (!familyStore.currentFamilyId) {
    return roomStore.rooms
  }
  return roomStore.rooms.filter(room => room.family_id === familyStore.currentFamilyId)
})

onMounted(async () => {
  await familyStore.fetchFamilies()
  await fetchRoomsByCurrentFamily()
})

// 监听家庭变化，重新获取房间
watch(() => familyStore.currentFamilyId, async () => {
  await fetchRoomsByCurrentFamily()
})

// 根据当前家庭获取房间
const fetchRoomsByCurrentFamily = async () => {
  if (familyStore.currentFamilyId) {
    await roomStore.fetchRooms(familyStore.currentFamilyId)
  } else {
    await roomStore.fetchRooms()
  }
}

const openAddModal = () => {
  roomName.value = ''
  error.value = ''
  showAddModal.value = true
}

const openEditModal = (id: number, name: string) => {
  editingRoom.value = id
  roomName.value = name
  error.value = ''
  showEditModal.value = true
}

const handleAdd = async () => {
  if (!roomName.value.trim()) {
    error.value = '请输入房间名称'
    return
  }
  try {
    await roomStore.createRoom(roomName.value, familyStore.currentFamilyId)
    showAddModal.value = false
  } catch (e: any) {
    error.value = e.response?.data?.detail || '创建失败'
  }
}

const handleEdit = async () => {
  if (!roomName.value.trim()) {
    error.value = '请输入房间名称'
    return
  }
  try {
    await roomStore.updateRoom(editingRoom.value!, { name: roomName.value })
    showEditModal.value = false
  } catch (e: any) {
    error.value = e.response?.data?.detail || '更新失败'
  }
}

const handleDelete = async (id: number) => {
  if (confirm('确定要删除这个房间吗？相关物品的房间将被清空。')) {
    await roomStore.deleteRoom(id)
  }
}

// 切换房间展开/折叠
const toggleRoom = async (roomId: number) => {
  if (expandedRooms.value.has(roomId)) {
    expandedRooms.value.delete(roomId)
  } else {
    expandedRooms.value.add(roomId)
    // 每次展开都刷新数据
    await loadRoomItems(roomId, true)
  }
  // 触发响应式更新
  expandedRooms.value = new Set(expandedRooms.value)
}

// 加载房间物品
const loadRoomItems = async (roomId: number, forceRefresh = false) => {
  // 如果不强制刷新且已有缓存，跳过
  if (!forceRefresh && roomStore.roomsWithItems.has(roomId)) return
  
  loadingItems.value[roomId] = true
  try {
    await roomStore.getRoomItems(roomId)
  } finally {
    loadingItems.value[roomId] = false
  }
}

// 获取房间物品
const getRoomItems = (roomId: number): Item[] => {
  const roomWithItems = roomStore.roomsWithItems.get(roomId)
  return roomWithItems?.items || []
}

// 检查房间是否展开
const isExpanded = (roomId: number) => expandedRooms.value.has(roomId)

// 检查是否正在加载
const isLoading = (roomId: number) => loadingItems.value[roomId] || false
</script>

<template>
  <div class="px-4 sm:px-0">
    <div class="sm:flex sm:items-center sm:justify-between">
      <h1 class="text-2xl font-semibold text-gray-900">房间管理</h1>
      <button
        @click="openAddModal"
        class="mt-3 sm:mt-0 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700"
      >
        添加房间
      </button>
    </div>

    <div class="mt-6 bg-white shadow sm:rounded-md overflow-hidden">
      <div v-for="room in filteredRooms" :key="room.id" class="border-b border-gray-200 last:border-b-0">
        <!-- 房间标题行 -->
        <div 
          class="px-6 py-4 flex items-center justify-between cursor-pointer hover:bg-gray-50"
          @click="toggleRoom(room.id)"
        >
          <div class="flex items-center space-x-3">
            <svg 
              class="w-5 h-5 text-gray-400 transition-transform duration-200"
              :class="{ 'rotate-90': isExpanded(room.id) }"
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
            <span class="text-sm font-medium text-gray-900">{{ room.name }}</span>
          </div>
          <div class="flex space-x-3" @click.stop>
            <button
              @click="openEditModal(room.id, room.name)"
              class="text-sm text-indigo-600 hover:text-indigo-900"
            >
              编辑
            </button>
            <button
              @click="handleDelete(room.id)"
              class="text-sm text-red-600 hover:text-red-900"
            >
              删除
            </button>
          </div>
        </div>

        <!-- 展开的物品列表 -->
        <div v-if="isExpanded(room.id)" class="bg-gray-50 px-6 py-4">
          <!-- 加载中 -->
          <div v-if="isLoading(room.id)" class="text-center text-gray-500 py-4">
            加载中...
          </div>
          
          <!-- 物品列表 -->
          <div v-else-if="getRoomItems(room.id).length > 0">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-100">
                <tr>
                  <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">名称</th>
                  <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">数量</th>
                  <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">价格</th>
                  <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">过期时间</th>
                  <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">位置</th>
                  <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">用途</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200">
                <tr v-for="item in getRoomItems(room.id)" :key="item.id" class="bg-white">
                  <td class="px-4 py-2 text-sm text-gray-900">{{ item.name }}</td>
                  <td class="px-4 py-2 text-sm text-gray-500">{{ item.quantity }}</td>
                  <td class="px-4 py-2 text-sm text-gray-500">¥{{ item.price }}</td>
                  <td class="px-4 py-2 text-sm text-gray-500">{{ item.expiry_date || '-' }}</td>
                  <td class="px-4 py-2 text-sm text-gray-500">{{ item.location || '-' }}</td>
                  <td class="px-4 py-2 text-sm text-gray-500">{{ item.usage || '-' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          
          <!-- 无物品 -->
          <div v-else class="text-center text-gray-500 py-4">
            该房间暂无物品
          </div>
        </div>
      </div>
      
      <div v-if="filteredRooms.length === 0" class="px-6 py-4 text-center text-gray-500">
        暂无房间
      </div>
    </div>

    <!-- 添加房间模态框 -->
    <div v-if="showAddModal" class="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <h3 class="text-lg font-medium text-gray-900 mb-4">添加房间</h3>
        <div v-if="error" class="mb-4 text-sm text-red-600">{{ error }}</div>
        <input
          v-model="roomName"
          type="text"
          class="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
          placeholder="房间名称"
          @keyup.enter="handleAdd"
        />
        <div class="mt-4 flex justify-end space-x-3">
          <button
            @click="showAddModal = false"
            class="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
          >
            取消
          </button>
          <button
            @click="handleAdd"
            class="px-4 py-2 border border-transparent rounded-md text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700"
          >
            添加
          </button>
        </div>
      </div>
    </div>

    <!-- 编辑房间模态框 -->
    <div v-if="showEditModal" class="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <h3 class="text-lg font-medium text-gray-900 mb-4">编辑房间</h3>
        <div v-if="error" class="mb-4 text-sm text-red-600">{{ error }}</div>
        <input
          v-model="roomName"
          type="text"
          class="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
          placeholder="房间名称"
          @keyup.enter="handleEdit"
        />
        <div class="mt-4 flex justify-end space-x-3">
          <button
            @click="showEditModal = false"
            class="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
          >
            取消
          </button>
          <button
            @click="handleEdit"
            class="px-4 py-2 border border-transparent rounded-md text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700"
          >
            保存
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
