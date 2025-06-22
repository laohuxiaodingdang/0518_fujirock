import { useState, useEffect, useCallback } from 'react'
import { supabase, isSupabaseAvailable } from '../lib/supabase'
import { authService } from '../lib/auth'
import type { User } from '@supabase/supabase-js'
import type { UserFavorite } from '../lib/supabase'

interface UseFavoritesReturn {
  favorites: UserFavorite[]
  loading: boolean
  error: string | null
  addFavorite: (artistId: string, tags?: string[], notes?: string) => Promise<boolean>
  removeFavorite: (artistId: string) => Promise<boolean>
  isFavorite: (artistId: string) => boolean
  refreshFavorites: () => Promise<void>
}

export function useFavorites(user: User | null): UseFavoritesReturn {
  const [favorites, setFavorites] = useState<UserFavorite[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // 获取用户收藏列表
  const fetchFavorites = useCallback(async () => {
    if (!user || !isSupabaseAvailable || !supabase) {
      setFavorites([])
      setLoading(false)
      return
    }

    try {
      setLoading(true)
      setError(null)

      const { data, error } = await supabase
        .from('user_favorites')
        .select('*')
        .eq('user_id', user.id)
        .order('created_at', { ascending: false })

      if (error) {
        throw error
      }

      setFavorites(data || [])
    } catch (err) {
      console.error('Error fetching favorites:', err)
      setError(err instanceof Error ? err.message : 'Failed to fetch favorites')
    } finally {
      setLoading(false)
    }
  }, [user])

  // 添加收藏
  const addFavorite = useCallback(async (
    artistId: string, 
    tags: string[] = [], 
    notes: string = ''
  ): Promise<boolean> => {
    if (!user || !isSupabaseAvailable || !supabase) {
      console.warn('Cannot add favorite: user not authenticated or Supabase not available')
      return false
    }

    try {
      setError(null)

      const favoriteData = {
        user_id: user.id,
        artist_id: artistId,
        tags,
        notes
      }

      const { error } = await supabase
        .from('user_favorites')
        .insert([favoriteData])

      if (error) {
        throw error
      }

      // 刷新收藏列表
      await fetchFavorites()
      return true
    } catch (err) {
      console.error('Error adding favorite:', err)
      setError(err instanceof Error ? err.message : 'Failed to add favorite')
      return false
    }
  }, [user, fetchFavorites])

  // 移除收藏
  const removeFavorite = useCallback(async (artistId: string): Promise<boolean> => {
    if (!user || !isSupabaseAvailable || !supabase) {
      console.warn('Cannot remove favorite: user not authenticated or Supabase not available')
      return false
    }

    try {
      setError(null)

      const { error } = await supabase
        .from('user_favorites')
        .delete()
        .eq('user_id', user.id)
        .eq('artist_id', artistId)

      if (error) {
        throw error
      }

      // 刷新收藏列表
      await fetchFavorites()
      return true
    } catch (err) {
      console.error('Error removing favorite:', err)
      setError(err instanceof Error ? err.message : 'Failed to remove favorite')
      return false
    }
  }, [user, fetchFavorites])

  // 检查是否已收藏
  const isFavorite = useCallback((artistId: string): boolean => {
    return favorites.some(fav => fav.artist_id === artistId)
  }, [favorites])

  // 刷新收藏列表
  const refreshFavorites = useCallback(async () => {
    await fetchFavorites()
  }, [fetchFavorites])

  // 当用户状态改变时，重新获取收藏列表
  useEffect(() => {
    fetchFavorites()
  }, [fetchFavorites])

  return {
    favorites,
    loading,
    error,
    addFavorite,
    removeFavorite,
    isFavorite,
    refreshFavorites
  }
} 