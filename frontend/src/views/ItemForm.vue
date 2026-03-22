<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useItemStore } from '@/stores/item'
import { useCategoryStore } from '@/stores/category'
import type { ItemCreate, ItemUpdate } from '@/api/item'

const router = useRouter()
const route = useRoute()
const itemStore = useItemStore()
const categoryStore = useCategoryStore()

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
  purchase_channel: ''
})

const error = ref('')
const loading = ref(false)

onMounted(async () => {
  await categoryStore.fetchCategories()
  
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
        purchase_channel: itemStore.currentItem.purchase_channel || ''
      }
    }
  }
})

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
          <select
            v-model="form.category_id"
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
          >
            <option :value="null">无</option>
            <option v-for="cat in categoryStore.categories" :key="cat.id" :value="cat.id">
              {{ cat.name }}
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
