export interface User {
  id: number
  username: string
  email: string
  created_at: string
}

export interface Category {
  id: number
  name: string
  user_id: number
  family_id?: number | null
  created_at: string
}

export interface Item {
  id: number
  name: string
  quantity: number
  price: number
  purchase_date: string | null
  expiry_date: string | null
  category_id: number | null
  room_id: number | null
  family_id: number | null
  is_private: boolean
  location: string | null
  notes: string | null
  usage: string | null
  purchase_channel: string | null
  user_id: number
  created_at: string
  updated_at: string
  category?: Category
  room?: {
    id: number
    name: string
  }
}

export interface ItemListResponse {
  items: Item[]
  total: number
}

export interface Token {
  access_token: string
  token_type: string
}

// Room model alignment with backend
export interface Room {
  id: number
  name: string
  user_id: number
  family_id?: number | null
  created_at: string
  items?: Item[]
}

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
