import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase environment variables. Please check your .env.local file.')
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: true
  }
})

// 数据库类型定义（基于我们的数据库设计）
export interface Artist {
  id: string
  name: string
  name_zh?: string
  name_en?: string
  name_ja?: string
  description?: string
  wiki_data?: any
  wiki_extract?: string
  spotify_id?: string
  spotify_data?: any
  external_urls?: any
  genres?: string[]
  popularity: number
  followers_count: number
  image_url?: string
  images?: any
  is_fuji_rock_artist: boolean
  created_at: string
  updated_at: string
}

export interface UserFavorite {
  id: string
  user_id: string
  artist_id: string
  tags?: string[]
  notes?: string
  created_at: string
}

export interface Song {
  id: string
  artist_id: string
  title: string
  album_name?: string
  duration_seconds?: number
  preview_url?: string
  spotify_id?: string
  spotify_data?: any
  itunes_data?: any
  release_date?: string
  created_at: string
  updated_at: string
} 