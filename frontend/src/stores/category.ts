import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Category } from '@/types'
import { categoryApi } from '@/api/category'

export const useCategoryStore = defineStore('category', () => {
  const categories = ref<Category[]>([])
  const loading = ref(false)

  async function fetchCategories() {
    loading.value = true
    try {
      categories.value = await categoryApi.getAll()
    } finally {
      loading.value = false
    }
  }

  async function createCategory(name: string) {
    const category = await categoryApi.create({ name })
    categories.value.push(category)
    return category
  }

  async function updateCategory(id: number, name: string) {
    const category = await categoryApi.update(id, { name })
    const index = categories.value.findIndex(c => c.id === id)
    if (index !== -1) {
      categories.value[index] = category
    }
    return category
  }

  async function deleteCategory(id: number) {
    await categoryApi.delete(id)
    categories.value = categories.value.filter(c => c.id !== id)
  }

  return {
    categories,
    loading,
    fetchCategories,
    createCategory,
    updateCategory,
    deleteCategory
  }
})
