<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useItemStore } from '@/stores/item'
import { useCategoryStore } from '@/stores/category'
import { useRoomStore } from '@/stores/room'
import type { ItemQueryParams } from '@/api/item'

const route = useRoute()
const itemStore = useItemStore()
const categoryStore = useCategoryStore()
const roomStore = useRoomStore()
const selectedRoom = ref<number | null>(null)

const searchName = ref('')
const selectedCategory = ref<number | null>(null)
const filterExpired = ref<boolean | null>(null)
const filterExpiringSoon = ref(false)
const currentPage = ref(1)
const pageSize = 20

onMounted(async () => {
  // 读取URL查询参数并初始化筛选状态
  if (route.query.expiring_soon === 'true') {
    filterExpiringSoon.value = true
  }
  if (route.query.name) {
    searchName.value = String(route.query.name)
  }
  if (route.query.category_id) {
    selectedCategory.value = Number(route.query.category_id)
  }
  if (route.query.room_id) {
    selectedRoom.value = Number(route.query.room_id)
  }
  if (route.query.expired !== undefined) {
    filterExpired.value = route.query.expired === 'true' ? true : (route.query.expired === 'false' ? false : null)
  }
  
  await Promise.all([
    categoryStore.fetchCategories(),
    roomStore.fetchRooms(),
    fetchItems()
  ])
})

const fetchItems = async () => {
  const params: ItemQueryParams = {
    skip: (currentPage.value - 1) * pageSize,
    limit: pageSize
  }
  
  if (searchName.value) params.name = searchName.value
  if (selectedCategory.value) params.category_id = selectedCategory.value
  if (selectedRoom.value) params.room_id = selectedRoom.value
  if (filterExpired.value !== null) params.expired = filterExpired.value
  if (filterExpiringSoon.value) params.expiring_soon = true
  
  await itemStore.fetchItems(params)
}

// 监听筛选条件变化，重置页码并重新获取数据
watch([searchName, selectedCategory, selectedRoom, filterExpired, filterExpiringSoon], () => {
  currentPage.value = 1
  fetchItems()
}, { deep: true })

// 监听页码变化，重新获取数据
watch(currentPage, () => {
  fetchItems()
})

const totalPages = computed(() => Math.ceil(itemStore.total / pageSize))

const deleteItem = async (id: number) => {
  if (confirm('确定要删除这个物品吗？')) {
    await itemStore.deleteItem(id)
  }
}

const getExpiryStatus = (expiryDate: string | null) => {
  if (!expiryDate) return null
  const expDate = new Date(expiryDate)
  const today = new Date()
  if (expDate < today) return 'expired'
  const thirtyDays = new Date(today.getTime() + 30 * 24 * 60 * 60 * 1000)
  if (expDate <= thirtyDays) return 'expiring'
  return 'ok'
}

const getRoomName = (item: any) => {
  if (item?.room?.name) return item.room.name
  const rid = item?.room_id ?? null
  if (rid && roomStore.rooms.length > 0) {
    const r = roomStore.rooms.find((r) => r.id === rid)
    if (r) return r.name
  }
  return '-' 
}
</script>

<template>
  <div class="px-4 sm:px-0">
    <div class="sm:flex sm:items-center sm:justify-between">
      <h1 class="text-2xl font-semibold text-gray-900">物品管理</h1>
      <router-link
        to="/items/new"
        class="mt-3 sm:mt-0 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700"
      >
        添加物品
      </router-link>
    </div>

    <div class="mt-6 bg-white shadow sm:rounded-lg p-4">
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div>
          <label class="block text-sm font-medium text-gray-700">搜索名称</label>
          <input
            v-model="searchName"
            type="text"
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            placeholder="输入物品名称"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700">分类</label>
          <select
            v-model="selectedCategory"
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
          >
            <option :value="null">全部</option>
            <option v-for="cat in categoryStore.categories" :key="cat.id" :value="cat.id">
              {{ cat.name }}
            </option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700">房间</label>
          <select
            v-model="selectedRoom"
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
          >
            <option :value="null">全部</option>
            <option v-for="room in roomStore.rooms" :key="room.id" :value="room.id">
              {{ room.name }}
            </option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700">过期状态</label>
          <select
            v-model="filterExpired"
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
          >
            <option :value="null">全部</option>
            <option :value="false">未过期</option>
            <option :value="true">已过期</option>
          </select>
        </div>
        <div class="flex items-end">
          <label class="flex items-center">
            <input
              v-model="filterExpiringSoon"
              type="checkbox"
              class="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
            />
            <span class="ml-2 text-sm text-gray-600">即将过期（30天内）</span>
          </label>
        </div>
      </div>
    </div>

    <div class="mt-6 bg-white shadow overflow-hidden sm:rounded-md">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">名称</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">数量</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">价格</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">过期时间</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">房间</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">位置</th>
            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="item in itemStore.items" :key="item.id">
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="text-sm font-medium text-gray-900">{{ item.name }}</div>
              <div class="text-sm text-gray-500">{{ item.usage }}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ item.quantity }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">¥{{ item.price }}</td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span v-if="item.expiry_date" class="inline-flex px-2 py-1 text-xs font-semibold rounded-full"
                :class="{
                  'bg-red-100 text-red-800': getExpiryStatus(item.expiry_date) === 'expired',
                  'bg-yellow-100 text-yellow-800': getExpiryStatus(item.expiry_date) === 'expiring',
                  'bg-green-100 text-green-800': getExpiryStatus(item.expiry_date) === 'ok'
                }">
                {{ item.expiry_date }}
              </span>
              <span v-else class="text-sm text-gray-400">-</span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ getRoomName(item) }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ item.location || '-' }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
              <router-link :to="`/items/${item.id}/edit`" class="text-indigo-600 hover:text-indigo-900 mr-4">
                编辑
              </router-link>
              <button @click="deleteItem(item.id)" class="text-red-600 hover:text-red-900">
                删除
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      
      <div v-if="itemStore.loading" class="px-6 py-4 text-center text-gray-500">
        加载中...
      </div>
      
      <div v-if="!itemStore.loading && itemStore.items.length === 0" class="px-6 py-4 text-center text-gray-500">
        暂无数据
      </div>
    </div>

    <div v-if="totalPages > 1" class="mt-4 flex items-center justify-between">
      <div class="text-sm text-gray-500">
        共 {{ itemStore.total }} 条记录
      </div>
      <div class="flex space-x-2">
        <button
          @click="currentPage--"
          :disabled="currentPage === 1"
          class="px-3 py-1 rounded border border-gray-300 text-sm disabled:opacity-50"
        >
          上一页
        </button>
        <span class="px-3 py-1 text-sm text-gray-700">{{ currentPage }} / {{ totalPages }}</span>
        <button
          @click="currentPage++"
          :disabled="currentPage >= totalPages"
          class="px-3 py-1 rounded border border-gray-300 text-sm disabled:opacity-50"
        >
          下一页
        </button>
      </div>
    </div>
  </div>
</template>
