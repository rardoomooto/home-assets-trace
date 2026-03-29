import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Family } from '@/api/family'
import { familyApi } from '@/api/family'

const CURRENT_FAMILY_KEY = 'current_family_id'

export const useFamilyStore = defineStore('family', () => {
  const families = ref<Family[]>([])
  const currentFamilyId = ref<number | null>(localStorage.getItem(CURRENT_FAMILY_KEY) ? Number(localStorage.getItem(CURRENT_FAMILY_KEY)) : null)
  const loading = ref(false)

  const currentFamily = computed(() => 
    families.value.find(f => f.id === currentFamilyId.value) || null
  )

  const hasMultipleFamilies = computed(() => families.value.length > 1)

  async function fetchFamilies() {
    loading.value = true
    try {
      families.value = await familyApi.getAll()
      
      // 如果没有当前家庭或当前家庭不在列表中，设置默认值
      if (!currentFamilyId.value || !families.value.find(f => f.id === currentFamilyId.value)) {
        if (families.value.length > 0) {
          setCurrentFamily(families.value[0].id)
        }
      }
    } finally {
      loading.value = false
    }
  }

  function setCurrentFamily(familyId: number) {
    currentFamilyId.value = familyId
    localStorage.setItem(CURRENT_FAMILY_KEY, String(familyId))
  }

  async function createFamily(name: string) {
    const newFamily = await familyApi.create({ name })
    families.value.push(newFamily)
    setCurrentFamily(newFamily.id)
    return newFamily
  }

  async function updateFamily(id: number, name: string) {
    const updated = await familyApi.update(id, { name })
    const index = families.value.findIndex(f => f.id === id)
    if (index !== -1) {
      families.value[index] = updated
    }
    return updated
  }

  async function deleteFamily(id: number) {
    await familyApi.delete(id)
    families.value = families.value.filter(f => f.id !== id)
    
    // 如果删除的是当前家庭，切换到第一个
    if (currentFamilyId.value === id && families.value.length > 0) {
      setCurrentFamily(families.value[0].id)
    }
  }

  async function addMember(familyId: number, username: string, role: string = 'member') {
    return await familyApi.addMember(familyId, { username, role })
  }

  async function removeMember(familyId: number, userId: number) {
    await familyApi.removeMember(familyId, userId)
  }

  return {
    families,
    currentFamilyId,
    currentFamily,
    hasMultipleFamilies,
    loading,
    fetchFamilies,
    setCurrentFamily,
    createFamily,
    updateFamily,
    deleteFamily,
    addMember,
    removeMember
  }
})
