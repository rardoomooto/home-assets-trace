<script setup lang="ts">
import { ref, watch } from 'vue'
import { useFamilyStore } from '@/stores/family'
import { useAuthStore } from '@/stores/auth'

const props = defineProps<{
  familyId: number
  familyName: string
}>()

const emit = defineEmits<{
  (e: 'close'): void
}>()

const familyStore = useFamilyStore()
const authStore = useAuthStore()

const newMemberUsername = ref('')
const newMemberRole = ref('member')
const error = ref('')
const loading = ref(false)

// 获取当前家庭详情
const currentFamily = ref<any>(null)
const loadingFamily = ref(false)

const fetchFamilyDetail = async () => {
  loadingFamily.value = true
  try {
    const response = await import('@/api/family').then(m => m.familyApi.getById(props.familyId))
    currentFamily.value = response
  } catch (e: any) {
    error.value = e.response?.data?.detail || '获取家庭详情失败'
  } finally {
    loadingFamily.value = false
  }
}

watch(() => props.familyId, () => {
  fetchFamilyDetail()
}, { immediate: true })

const handleAddMember = async () => {
  if (!newMemberUsername.value.trim()) {
    error.value = '请输入用户名'
    return
  }
  
  loading.value = true
  error.value = ''
  
  try {
    await familyStore.addMember(props.familyId, newMemberUsername.value.trim(), newMemberRole.value)
    newMemberUsername.value = ''
    newMemberRole.value = 'member'
    await fetchFamilyDetail() // 刷新成员列表
  } catch (e: any) {
    error.value = e.response?.data?.detail || '添加成员失败'
  } finally {
    loading.value = false
  }
}

const handleRemoveMember = async (userId: number, username: string) => {
  if (userId === authStore.user?.id) {
    if (!confirm('确定要退出这个家庭吗？')) {
      return
    }
  } else {
    if (!confirm(`确定要移除用户「${username}」吗？`)) {
      return
    }
  }
  
  try {
    await familyStore.removeMember(props.familyId, userId)
    await fetchFamilyDetail() // 刷新成员列表
  } catch (e: any) {
    alert(e.response?.data?.detail || '移除成员失败')
  }
}

const getRoleLabel = (role: string) => {
  switch (role) {
    case 'owner': return '所有者'
    case 'admin': return '管理员'
    case 'member': return '成员'
    default: return role
  }
}

const canManageMembers = () => {
  if (!currentFamily.value || !authStore.user) return false
  const myMembership = currentFamily.value.members?.find((m: any) => m.user_id === authStore.user?.id)
  return myMembership?.role === 'owner' || myMembership?.role === 'admin'
}
</script>

<template>
  <div class="fixed inset-0 z-50 overflow-y-auto">
    <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
      <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" @click="emit('close')"></div>
      
      <div class="inline-block align-bottom bg-white rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full sm:p-6">
        <div>
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-lg font-medium text-gray-900">管理成员 - {{ familyName }}</h3>
            <button
              @click="emit('close')"
              class="text-gray-400 hover:text-gray-500"
            >
              <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          <div v-if="error" class="mb-4 bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded">
            {{ error }}
          </div>
          
          <!-- 加载状态 -->
          <div v-if="loadingFamily" class="text-center py-4">
            加载中...
          </div>
          
          <template v-else>
            <!-- 成员列表 -->
            <div class="mb-6">
              <h4 class="text-sm font-medium text-gray-700 mb-3">当前成员 ({{ currentFamily?.members?.length || 0 }})</h4>
              <div class="space-y-3">
                <div
                  v-for="member in currentFamily?.members"
                  :key="member.id"
                  class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                >
                  <div class="flex items-center">
                    <div class="w-10 h-10 rounded-full bg-indigo-100 flex items-center justify-center">
                      <span class="text-indigo-600 font-medium">{{ member.username.charAt(0).toUpperCase() }}</span>
                    </div>
                    <div class="ml-3">
                      <div class="text-sm font-medium text-gray-900">{{ member.username }}</div>
                      <div class="text-xs text-gray-500">{{ getRoleLabel(member.role) }}</div>
                    </div>
                  </div>
                  <div>
                    <span
                      v-if="member.user_id === authStore.user?.id"
                      class="text-xs text-gray-400"
                    >
                      (我)
                    </span>
                    <button
                      v-if="canManageMembers() && member.user_id !== authStore.user?.id"
                      @click="handleRemoveMember(member.user_id, member.username)"
                      class="ml-2 text-sm text-red-600 hover:text-red-900"
                    >
                      移除
                    </button>
                    <button
                      v-if="member.user_id === authStore.user?.id && member.role !== 'owner'"
                      @click="handleRemoveMember(member.user_id, member.username)"
                      class="ml-2 text-sm text-red-600 hover:text-red-900"
                    >
                      退出
                    </button>
                  </div>
                </div>
                
                <div v-if="!currentFamily?.members?.length" class="text-center py-4 text-gray-500">
                  暂无成员数据
                </div>
              </div>
            </div>
            
            <!-- 添加成员 -->
            <div v-if="canManageMembers()" class="border-t pt-4">
              <h4 class="text-sm font-medium text-gray-700 mb-3">添加成员</h4>
              <form @submit.prevent="handleAddMember" class="space-y-3">
                <div>
                  <label class="block text-sm font-medium text-gray-700">用户名</label>
                  <input
                    v-model="newMemberUsername"
                    type="text"
                    required
                    class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                    placeholder="输入要添加的用户名"
                  />
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-gray-700">角色</label>
                  <select
                    v-model="newMemberRole"
                    class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                  >
                    <option value="member">成员</option>
                    <option value="admin">管理员</option>
                  </select>
                </div>
                
                <button
                  type="submit"
                  :disabled="loading"
                  class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-indigo-600 text-base font-medium text-white hover:bg-indigo-700 focus:outline-none sm:ml-3 sm:w-auto sm:text-sm disabled:opacity-50"
                >
                  {{ loading ? '添加中...' : '添加成员' }}
                </button>
              </form>
            </div>
            
            <div v-else class="text-center text-sm text-gray-500 mt-4">
              只有家庭所有者或管理员可以添加成员
            </div>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>