<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useCategoryStore } from '@/stores/category'

const categoryStore = useCategoryStore()

const showAddModal = ref(false)
const showEditModal = ref(false)
const editingCategory = ref<number | null>(null)
const categoryName = ref('')
const error = ref('')

onMounted(() => {
  categoryStore.fetchCategories()
})

const openAddModal = () => {
  categoryName.value = ''
  error.value = ''
  showAddModal.value = true
}

const openEditModal = (id: number, name: string) => {
  editingCategory.value = id
  categoryName.value = name
  error.value = ''
  showEditModal.value = true
}

const handleAdd = async () => {
  if (!categoryName.value.trim()) {
    error.value = '请输入分类名称'
    return
  }
  
  try {
    await categoryStore.createCategory(categoryName.value)
    showAddModal.value = false
  } catch (e: any) {
    error.value = e.response?.data?.detail || '创建失败'
  }
}

const handleEdit = async () => {
  if (!categoryName.value.trim()) {
    error.value = '请输入分类名称'
    return
  }
  
  try {
    await categoryStore.updateCategory(editingCategory.value!, categoryName.value)
    showEditModal.value = false
  } catch (e: any) {
    error.value = e.response?.data?.detail || '更新失败'
  }
}

const handleDelete = async (id: number) => {
  if (confirm('确定要删除这个分类吗？相关物品的分类将被清空。')) {
    await categoryStore.deleteCategory(id)
  }
}
</script>

<template>
  <div class="px-4 sm:px-0">
    <div class="sm:flex sm:items-center sm:justify-between">
      <h1 class="text-2xl font-semibold text-gray-900">分类管理</h1>
      <button
        @click="openAddModal"
        class="mt-3 sm:mt-0 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700"
      >
        添加分类
      </button>
    </div>

    <div class="mt-6 bg-white shadow sm:rounded-md overflow-hidden">
      <ul class="divide-y divide-gray-200">
        <li
          v-for="category in categoryStore.categories"
          :key="category.id"
          class="px-6 py-4 flex items-center justify-between"
        >
          <span class="text-sm font-medium text-gray-900">{{ category.name }}</span>
          <div class="flex space-x-3">
            <button
              @click="openEditModal(category.id, category.name)"
              class="text-sm text-indigo-600 hover:text-indigo-900"
            >
              编辑
            </button>
            <button
              @click="handleDelete(category.id)"
              class="text-sm text-red-600 hover:text-red-900"
            >
              删除
            </button>
          </div>
        </li>
      </ul>
      
      <div v-if="categoryStore.categories.length === 0" class="px-6 py-4 text-center text-gray-500">
        暂无分类
      </div>
    </div>

    <div v-if="showAddModal" class="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <h3 class="text-lg font-medium text-gray-900 mb-4">添加分类</h3>
        <div v-if="error" class="mb-4 text-sm text-red-600">{{ error }}</div>
        <input
          v-model="categoryName"
          type="text"
          class="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
          placeholder="分类名称"
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

    <div v-if="showEditModal" class="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <h3 class="text-lg font-medium text-gray-900 mb-4">编辑分类</h3>
        <div v-if="error" class="mb-4 text-sm text-red-600">{{ error }}</div>
        <input
          v-model="categoryName"
          type="text"
          class="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
          placeholder="分类名称"
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
