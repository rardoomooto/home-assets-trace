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
  location: string | null
  notes: string | null
  usage: string | null
  purchase_channel: string | null
  user_id: number
  created_at: string
  updated_at: string
  category?: Category
  // Optional association to a room
  room_id?: number
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
  created_at: string
  items?: Item[]
}
