<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useFamilyStore } from '@/stores/family'
import FamilyMembers from '@/components/FamilyMembers.vue'

const familyStore = useFamilyStore()

const showCreateModal = ref(false)
const showMembersModal = ref(false)
const selectedFamily = ref<{ id: number; name: string } | null>(null)
const newFamilyName = ref('')
const error = ref('')
const loading = ref(false)

onMounted(async () => {
  await familyStore.fetchFamilies()
})

const handleCreate = async () => {
  if (!newFamilyName.value.trim()) {
    error.value = '请输入家庭名称'
    return
  }
  
  loading.value = true
  error.value = ''
  
  try {
    await familyStore.createFamily(newFamilyName.value.trim())
    showCreateModal.value = false
    newFamilyName.value = ''
  } catch (e: any) {
    error.value = e.response?.data?.detail || '创建失败，请重试'
  } finally {
    loading.value = false
  }
}

const handleDelete = async (id: number, name: string) => {
  if (!confirm(`确定要删除家庭「${name}」吗？此操作不可恢复。`)) {
    return
  }
  
  try {
    await familyStore.deleteFamily(id)
  } catch (e: any) {
    alert(e.response?.data?.detail || '删除失败')
  }
}

const handleSwitch = (id: number) => {
  familyStore.setCurrentFamily(id)
}

const openMembersModal = (family: { id: number; name: string }) => {
  selectedFamily.value = family
  showMembersModal.value = true
}

const closeMembersModal = () => {
  showMembersModal.value = false
  selectedFamily.value = null
  // 刷新家庭列表
  familyStore.fetchFamilies()
}
</script>

<template>
  <div class="px-4 sm:px-0">
    <div class="flex justify-between items-center">
      <h1 class="text-2xl font-semibold text-gray-900">家庭管理</h1>
      <button
        @click="showCreateModal = true"
        class="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700"
      >
        新增家庭
      </button>
    </div>

    <div class="mt-6 bg-white shadow overflow-hidden sm:rounded-md">
      <ul class="divide-y divide-gray-200">
        <li v-for="family in familyStore.families" :key="family.id">
          <div class="px-4 py-4 flex items-center sm:px-6">
            <div class="min-w-0 flex-1 sm:flex sm:items-center sm:justify-between">
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <svg class="h-8 w-8 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                  </svg>
                </div>
                <div class="ml-4">
                  <div class="flex items-center">
                    <span class="text-lg font-medium text-indigo-600">{{ family.name }}</span>
                    <span v-if="family.is_default" class="ml-2 px-2 py-0.5 text-xs bg-gray-100 text-gray-600 rounded">
                      默认
                    </span>
                    <span v-if="family.id === familyStore.currentFamilyId" class="ml-2 px-2 py-0.5 text-xs bg-green-100 text-green-800 rounded">
                      当前
                    </span>
                  </div>
                  <div class="mt-1 text-sm text-gray-500">
                    {{ family.members?.length || 0 }} 位成员 · 创建于 {{ new Date(family.created_at).toLocaleDateString() }}
                  </div>
                </div>
              </div>
            </div>
            <div class="ml-4 flex-shrink-0 flex space-x-2">
              <button
                @click="openMembersModal(family)"
                class="px-3 py-1 text-sm text-indigo-600 hover:text-indigo-900"
              >
                管理成员
              </button>
              <button
                v-if="family.id !== familyStore.currentFamilyId"
                @click="handleSwitch(family.id)"
                class="px-3 py-1 text-sm text-indigo-600 hover:text-indigo-900"
              >
                切换到此家庭
              </button>
              <button
                v-if="!family.is_default"
                @click="handleDelete(family.id, family.name)"
                class="px-3 py-1 text-sm text-red-600 hover:text-red-900"
              >
                删除
              </button>
            </div>
          </div>
        </li>
        <li v-if="familyStore.families.length === 0" class="px-4 py-8 text-center text-gray-500">
          暂无家庭数据
        </li>
      </ul>
    </div>

    <!-- 创建家庭模态框 -->
    <div v-if="showCreateModal" class="fixed inset-0 z-50 overflow-y-auto">
      <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" @click="showCreateModal = false"></div>
        
        <div class="inline-block align-bottom bg-white rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full sm:p-6">
          <div>
            <h3 class="text-lg font-medium text-gray-900 mb-4">新增家庭</h3>
            
            <div v-if="error" class="mb-4 bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded">
              {{ error }}
            </div>
            
            <form @submit.prevent="handleCreate">
              <div>
                <label class="block text-sm font-medium text-gray-700">家庭名称</label>
                <input
                  v-model="newFamilyName"
                  type="text"
                  required
                  class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                  placeholder="例如：父母家、自己家"
                />
              </div>
              
              <div class="mt-5 sm:mt-4 sm:flex sm:flex-row-reverse">
                <button
                  type="submit"
                  :disabled="loading"
                  class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-indigo-600 text-base font-medium text-white hover:bg-indigo-700 focus:outline-none sm:ml-3 sm:w-auto sm:text-sm disabled:opacity-50"
                >
                  {{ loading ? '创建中...' : '创建' }}
                </button>
                <button
                  type="button"
                  @click="showCreateModal = false"
                  class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none sm:mt-0 sm:w-auto sm:text-sm"
                >
                  取消
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 家庭成员管理模态框 -->
    <FamilyMembers
      v-if="showMembersModal && selectedFamily"
      :family-id="selectedFamily.id"
      :family-name="selectedFamily.name"
      @close="closeMembersModal"
    />
  </div>
</template>
