<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useItemStore } from '@/stores/item'
import { useCategoryStore } from '@/stores/category'
import { useRoomStore } from '@/stores/room'
import type { ItemCreate, ItemUpdate } from '@/api/item'

const router = useRouter()
const route = useRoute()
const itemStore = useItemStore()
const categoryStore = useCategoryStore()
const roomStore = useRoomStore()

const isEdit = computed(() => !!route.params.id)
const itemId = computed(() => Number(route.params.id))

const form = ref<ItemCreate>({
  name: '',
  quantity: 1,
  price: 0,
  purchase_date: null,
  expiry_date: null,
  category_id: null,
  location: '',
  notes: '',
  usage: '',
  purchase_channel: '',
  room_id: null
})

const error = ref('')
const loading = ref(false)

onMounted(async () => {
  await categoryStore.fetchCategories()
  await roomStore.fetchRooms()
  
  if (isEdit.value) {
    await itemStore.fetchItem(itemId.value)
    if (itemStore.currentItem) {
      form.value = {
        name: itemStore.currentItem.name,
        quantity: itemStore.currentItem.quantity,
        price: itemStore.currentItem.price,
        purchase_date: itemStore.currentItem.purchase_date,
        expiry_date: itemStore.currentItem.expiry_date,
        category_id: itemStore.currentItem.category_id,
        location: itemStore.currentItem.location || '',
        notes: itemStore.currentItem.notes || '',
        usage: itemStore.currentItem.usage || '',
        purchase_channel: itemStore.currentItem.purchase_channel || '',
        room_id: itemStore.currentItem.room_id ?? null
      }
    }
  }
})

// 新增分类相关
const showCategoryInput = ref(false)
const newCategoryName = ref('')
const categoryError = ref('')
const creatingCategory = ref(false)

const openCategoryInput = () => {
  showCategoryInput.value = true
  newCategoryName.value = ''
  categoryError.value = ''
}

const cancelCategoryInput = () => {
  showCategoryInput.value = false
  newCategoryName.value = ''
  categoryError.value = ''
}

const handleCreateCategory = async () => {
  if (!newCategoryName.value.trim()) {
    categoryError.value = '分类名称不能为空'
    return
  }
  
  creatingCategory.value = true
  categoryError.value = ''
  
  try {
    const newCategory = await categoryStore.createCategory(newCategoryName.value.trim())
    form.value.category_id = newCategory.id
    showCategoryInput.value = false
    newCategoryName.value = ''
  } catch (e: any) {
    categoryError.value = e.response?.data?.detail || '创建分类失败，请重试'
  } finally {
    creatingCategory.value = false
  }
}

const handleSubmit = async () => {
  error.value = ''
  loading.value = true
  
  try {
    if (isEdit.value) {
      await itemStore.updateItem(itemId.value, form.value as ItemUpdate)
    } else {
      await itemStore.createItem(form.value)
    }
    router.push('/items')
  } catch (e: any) {
    error.value = e.response?.data?.detail || '保存失败，请重试'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="px-4 sm:px-0">
    <h1 class="text-2xl font-semibold text-gray-900">
      {{ isEdit ? '编辑物品' : '添加物品' }}
    </h1>

    <form @submit.prevent="handleSubmit" class="mt-6 bg-white shadow sm:rounded-lg p-6">
      <div v-if="error" class="mb-4 bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded">
        {{ error }}
      </div>

      <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
        <div class="sm:col-span-2">
          <label class="block text-sm font-medium text-gray-700">名称 *</label>
          <input
            v-model="form.name"
            type="text"
            required
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700">数量 *</label>
          <input
            v-model.number="form.quantity"
            type="number"
            min="0"
            required
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700">价格 *</label>
          <input
            v-model.number="form.price"
            type="number"
            min="0"
            step="0.01"
            required
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700">购买日期</label>
          <input
            v-model="form.purchase_date"
            type="date"
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700">过期时间</label>
          <input
            v-model="form.expiry_date"
            type="date"
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700">分类</label>
          <div class="flex mt-1">
            <select
              v-if="!showCategoryInput"
              v-model="form.category_id"
              class="block w-full rounded-l-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            >
              <option :value="null">无</option>
              <option v-for="cat in categoryStore.categories" :key="cat.id" :value="cat.id">
                {{ cat.name }}
              </option>
            </select>
            
            <!-- 新增分类输入区域 -->
            <div v-else class="flex-1">
              <input
                v-model="newCategoryName"
                type="text"
                placeholder="输入分类名称"
                @keyup.enter="handleCreateCategory"
                @keyup.escape="cancelCategoryInput"
                class="block w-full rounded-l-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              />
            </div>
            
            <!-- 按钮区域 -->
            <div v-if="!showCategoryInput" class="flex">
              <button
                type="button"
                @click="openCategoryInput"
                class="inline-flex items-center px-3 border border-l-0 border-gray-300 rounded-r-md bg-gray-50 text-gray-500 hover:bg-gray-100"
                title="新增分类"
              >
                <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                </svg>
              </button>
            </div>
            
            <!-- 新增分类操作按钮 -->
            <div v-else class="flex">
              <button
                type="button"
                @click="handleCreateCategory"
                :disabled="creatingCategory"
                class="inline-flex items-center px-2 border border-l-0 border-gray-300 bg-indigo-500 text-white hover:bg-indigo-600 disabled:opacity-50"
                title="确定"
              >
                <svg v-if="!creatingCategory" class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                <svg v-else class="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              </button>
              <button
                type="button"
                @click="cancelCategoryInput"
                class="inline-flex items-center px-2 border border-l-0 border-gray-300 rounded-r-md bg-gray-50 text-gray-500 hover:bg-gray-100"
                title="取消"
              >
                <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
          
          <!-- 错误提示 -->
          <p v-if="categoryError" class="mt-1 text-sm text-red-600">{{ categoryError }}</p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700">房间</label>
          <select
            v-model="form.room_id"
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
          >
            <option :value="null">无</option>
            <option v-for="rm in roomStore.rooms" :key="rm.id" :value="rm.id">
              {{ rm.name }}
            </option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700">存放位置</label>
          <input
            v-model="form.location"
            type="text"
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700">用途</label>
          <input
            v-model="form.usage"
            type="text"
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700">购买途径</label>
          <input
            v-model="form.purchase_channel"
            type="text"
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
          />
        </div>

        <div class="sm:col-span-2">
          <label class="block text-sm font-medium text-gray-700">备注</label>
          <textarea
            v-model="form.notes"
            rows="3"
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
          />
        </div>
      </div>

      <div class="mt-6 flex justify-end space-x-3">
        <router-link
          to="/items"
          class="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
        >
          取消
        </router-link>
        <button
          type="submit"
          :disabled="loading"
          class="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50"
        >
          {{ loading ? '保存中...' : '保存' }}
        </button>
      </div>
    </form>
  </div>
</template>
