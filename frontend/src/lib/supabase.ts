/**
 * Supabase 客户端配置
 * 用于前端与Supabase服务的连接
 */
import { createClient } from '@supabase/supabase-js'

// Supabase项目配置
// 注意：这些是公开的配置，可以在前端代码中使用
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase environment variables. Please check your .env.local file.')
}

// 创建Supabase客户端实例
// 这个客户端用于所有的认证和数据库操作
export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    // 认证相关配置
    autoRefreshToken: true,        // 自动刷新token
    persistSession: true,          // 持久化session到localStorage
    detectSessionInUrl: true       // 从URL中检测session（用于邮箱验证等）
  }
})

/**
 * 获取当前用户的JWT Token
 * 
 * @returns Promise<string | null> JWT Token字符串，如果用户未登录则返回null
 */
export const getCurrentUserToken = async (): Promise<string | null> => {
  try {
    // 获取当前session
    const { data: { session }, error } = await supabase.auth.getSession()
    
    if (error) {
      console.error('Error getting session:', error)
      return null
    }
    
    // 返回access_token，这就是JWT Token
    return session?.access_token || null
  } catch (error) {
    console.error('Error getting user token:', error)
    return null
  }
}

/**
 * 获取当前用户信息
 * 
 * @returns Promise<User | null> 用户信息对象，如果未登录则返回null
 */
export const getCurrentUser = async () => {
  try {
    const { data: { user }, error } = await supabase.auth.getUser()
    
    if (error) {
      console.error('Error getting user:', error)
      return null
    }
    
    return user
  } catch (error) {
    console.error('Error getting current user:', error)
    return null
  }
}

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