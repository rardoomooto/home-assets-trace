<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { useItemStore } from '@/stores/item'
import { useCategoryStore } from '@/stores/category'

const itemStore = useItemStore()
const categoryStore = useCategoryStore()

onMounted(async () => {
  await Promise.all([
    itemStore.fetchItems({ limit: 5 }),
    categoryStore.fetchCategories()
  ])
})

const recentItems = computed(() => itemStore.items.slice(0, 5))
const totalItems = computed(() => itemStore.total)
const totalCategories = computed(() => categoryStore.categories.length)
</script>

<template>
  <div class="px-4 sm:px-0">
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-semibold text-gray-900">仪表盘</h1>
      <router-link
        to="/items/new"
        class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
      >
        添加物品
      </router-link>
    </div>
    
    <div class="mt-6 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
      <router-link to="/items" class="block">
        <div class="bg-white overflow-hidden shadow rounded-lg hover:shadow-md transition-shadow cursor-pointer">
          <div class="px-4 py-5 sm:p-6">
            <dt class="text-sm font-medium text-gray-500 truncate">物品总数</dt>
            <dd class="mt-1 text-3xl font-semibold text-gray-900">{{ totalItems }}</dd>
          </div>
        </div>
      </router-link>
      <router-link to="/categories" class="block">
        <div class="bg-white overflow-hidden shadow rounded-lg hover:shadow-md transition-shadow cursor-pointer">
          <div class="px-4 py-5 sm:p-6">
            <dt class="text-sm font-medium text-gray-500 truncate">分类数量</dt>
            <dd class="mt-1 text-3xl font-semibold text-gray-900">{{ totalCategories }}</dd>
          </div>
        </div>
      </router-link>
      <router-link :to="{ path: '/items', query: { expiring_soon: 'true' } }" class="block">
        <div class="bg-white overflow-hidden shadow rounded-lg hover:shadow-md transition-shadow cursor-pointer">
          <div class="px-4 py-5 sm:p-6">
            <dt class="text-sm font-medium text-gray-500 truncate">即将过期</dt>
            <dd class="mt-1 text-3xl font-semibold text-gray-900">
              {{ itemStore.items.filter(i => {
                if (!i.expiry_date) return false
                const expDate = new Date(i.expiry_date)
                const today = new Date()
                const thirtyDays = new Date(today.getTime() + 30 * 24 * 60 * 60 * 1000)
                return expDate >= today && expDate <= thirtyDays
              }).length }}
            </dd>
          </div>
        </div>
      </router-link>
    </div>

    <div class="mt-8">
      <div class="flex items-center justify-between">
        <h2 class="text-lg font-medium text-gray-900">最近添加</h2>
        <router-link to="/items" class="text-sm text-indigo-600 hover:text-indigo-500">
          查看全部
        </router-link>
      </div>
      <div class="mt-4 bg-white shadow overflow-hidden sm:rounded-md">
        <ul class="divide-y divide-gray-200">
          <li v-for="item in recentItems" :key="item.id" class="px-4 py-4 sm:px-6">
    <div class="flex items-center justify-between flex-wrap gap-4">
              <div>
                <p class="text-sm font-medium text-indigo-600 truncate">{{ item.name }}</p>
                <p class="text-sm text-gray-500">数量: {{ item.quantity }} | 价格: ¥{{ item.price }}</p>
              </div>
              <div class="ml-2 flex-shrink-0 flex">
                <router-link
                  :to="`/items/${item.id}/edit`"
                  class="text-sm text-indigo-600 hover:text-indigo-500"
                >
                  编辑
                </router-link>
              </div>
            </div>
          </li>
        </ul>
        <div v-if="recentItems.length === 0" class="px-4 py-6 text-center text-gray-500">
          暂无物品，点击"添加物品"开始
        </div>
      </div>
    </div>
  </div>
</template>
