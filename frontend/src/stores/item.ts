import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Item, ItemListResponse } from '@/types'
import { itemApi, type ItemQueryParams, type ItemCreate, type ItemUpdate } from '@/api/item'

export const useItemStore = defineStore('item', () => {
  const items = ref<Item[]>([])
  const total = ref(0)
  const loading = ref(false)
  const currentItem = ref<Item | null>(null)

  async function fetchItems(params?: ItemQueryParams) {
    loading.value = true
    try {
      const response: ItemListResponse = await itemApi.getAll(params)
      items.value = response.items
      total.value = response.total
    } finally {
      loading.value = false
    }
  }

  async function fetchItem(id: number) {
    loading.value = true
    try {
      currentItem.value = await itemApi.getById(id)
    } finally {
      loading.value = false
    }
  }

  async function createItem(data: ItemCreate) {
    const item = await itemApi.create(data)
    items.value.unshift(item)
    total.value++
    return item
  }

  async function updateItem(id: number, data: ItemUpdate) {
    const item = await itemApi.update(id, data)
    const index = items.value.findIndex(i => i.id === id)
    if (index !== -1) {
      items.value[index] = item
    }
    if (currentItem.value?.id === id) {
      currentItem.value = item
    }
    return item
  }

  async function deleteItem(id: number) {
    await itemApi.delete(id)
    items.value = items.value.filter(i => i.id !== id)
    total.value--
    if (currentItem.value?.id === id) {
      currentItem.value = null
    }
  }

  return {
    items,
    total,
    loading,
    currentItem,
    fetchItems,
    fetchItem,
    createItem,
    updateItem,
    deleteItem
  }
})
