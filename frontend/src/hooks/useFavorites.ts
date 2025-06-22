import { useState, useEffect } from 'react'
import { supabase } from '../lib/supabase'
import { authService } from '../lib/auth'
import type { User } from '@supabase/supabase-js'
import type { UserFavorite } from '../lib/supabase'

export function useFavorites() {
  const [favorites, setFavorites] = useState<string[]>([])
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // 初始化：检查用户状态和加载收藏
    const initializeAuth = async () => {
      const currentUser = await authService.getCurrentUser()
      setUser(currentUser)
      
      if (currentUser) {
        await loadFavorites(currentUser.id)
      }
      
      setLoading(false)
    }

    initializeAuth()

    // 监听认证状态变化
    const subscription = authService.onAuthStateChange(async (newUser) => {
      setUser(newUser)
      
      if (newUser) {
        await loadFavorites(newUser.id)
      } else {
        setFavorites([])
      }
    })

    return () => subscription.unsubscribe()
  }, [])

  /**
   * 加载用户收藏列表
   */
  const loadFavorites = async (userId: string) => {
    try {
      const { data, error } = await supabase
        .from('user_favorites')
        .select('artist_id')
        .eq('user_id', userId)

      if (error) {
        console.error('加载收藏失败:', error.message)
        return
      }

      if (data) {
        const artistIds = data.map((item: { artist_id: string }) => item.artist_id)
        setFavorites(artistIds)
        console.log('加载收藏成功:', artistIds.length, '个艺术家')
      }
    } catch (err) {
      console.error('加载收藏异常:', err)
    }
  }

  /**
   * 添加收藏
   */
  const addFavorite = async (artistId: string): Promise<boolean> => {
    if (!user) {
      console.warn('用户未登录，无法添加收藏')
      return false
    }

    if (favorites.includes(artistId)) {
      console.warn('艺术家已在收藏列表中')
      return true
    }

    try {
      const { error } = await supabase
        .from('user_favorites')
        .insert({
          user_id: user.id,
          artist_id: artistId
        })

      if (error) {
        console.error('添加收藏失败:', error.message)
        return false
      }

      setFavorites(prev => [...prev, artistId])
      console.log('添加收藏成功:', artistId)
      return true
    } catch (err) {
      console.error('添加收藏异常:', err)
      return false
    }
  }

  /**
   * 删除收藏
   */
  const removeFavorite = async (artistId: string): Promise<boolean> => {
    if (!user) {
      console.warn('用户未登录，无法删除收藏')
      return false
    }

    try {
      const { error } = await supabase
        .from('user_favorites')
        .delete()
        .eq('user_id', user.id)
        .eq('artist_id', artistId)

      if (error) {
        console.error('删除收藏失败:', error.message)
        return false
      }

      setFavorites(prev => prev.filter(id => id !== artistId))
      console.log('删除收藏成功:', artistId)
      return true
    } catch (err) {
      console.error('删除收藏异常:', err)
      return false
    }
  }

  /**
   * 切换收藏状态
   */
  const toggleFavorite = async (artistId: string): Promise<boolean> => {
    if (isFavorite(artistId)) {
      return await removeFavorite(artistId)
    } else {
      return await addFavorite(artistId)
    }
  }

  /**
   * 检查是否已收藏
   */
  const isFavorite = (artistId: string): boolean => {
    return favorites.includes(artistId)
  }

  /**
   * 获取收藏的艺术家详情
   */
  const getFavoriteArtists = async () => {
    if (!user || favorites.length === 0) {
      return []
    }

    try {
      const { data, error } = await supabase
        .from('artists')
        .select('*')
        .in('id', favorites)

      if (error) {
        console.error('获取收藏艺术家详情失败:', error.message)
        return []
      }

      return data || []
    } catch (err) {
      console.error('获取收藏艺术家详情异常:', err)
      return []
    }
  }

  return {
    favorites,
    user,
    loading,
    addFavorite,
    removeFavorite,
    toggleFavorite,
    isFavorite,
    getFavoriteArtists,
    isLoggedIn: !!user
  }
} 