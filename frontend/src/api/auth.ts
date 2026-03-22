import api from './index'
import type { User, Token } from '@/types'

export interface LoginData {
  username: string
  password: string
}

export interface RegisterData {
  username: string
  email: string
  password: string
}

export const authApi = {
  login: async (data: LoginData): Promise<Token> => {
    const response = await api.post<Token>('/auth/login', data)
    return response.data
  },

  register: async (data: RegisterData): Promise<User> => {
    const response = await api.post<User>('/auth/register', data)
    return response.data
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await api.get<User>('/auth/me')
    return response.data
  }
}
