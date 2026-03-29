import api from './index'

export interface Family {
  id: number
  name: string
  is_default: boolean
  created_at: string
  members: FamilyMember[]
}

export interface FamilyMember {
  id: number
  user_id: number
  username: string
  role: string
  joined_at: string
}

export interface FamilyCreate {
  name: string
}

export interface AddMemberRequest {
  username: string
  role?: string
}

export const familyApi = {
  getAll: async (): Promise<Family[]> => {
    const response = await api.get<{ families: Family[] }>('/families')
    return response.data.families
  },

  getById: async (id: number): Promise<Family> => {
    const response = await api.get<Family>(`/families/${id}`)
    return response.data
  },

  create: async (data: FamilyCreate): Promise<Family> => {
    const response = await api.post<Family>('/families', data)
    return response.data
  },

  update: async (id: number, data: FamilyCreate): Promise<Family> => {
    const response = await api.put<Family>(`/families/${id}`, data)
    return response.data
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/families/${id}`)
  },

  addMember: async (familyId: number, data: AddMemberRequest): Promise<FamilyMember> => {
    const response = await api.post<FamilyMember>(`/families/${familyId}/members`, data)
    return response.data
  },

  removeMember: async (familyId: number, userId: number): Promise<void> => {
    await api.delete(`/families/${familyId}/members/${userId}`)
  }
}
