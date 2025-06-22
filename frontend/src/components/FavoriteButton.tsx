'use client'

import { useState } from 'react'
import { useFavorites } from '../hooks/useFavorites'
import { useAuth } from '../hooks/useAuth'
import SimpleAuth from './SimpleAuth'

interface FavoriteButtonProps {
  artistId: string
  artistName?: string
  className?: string
}

export default function FavoriteButton({ 
  artistId, 
  artistName = '艺术家',
  className = '' 
}: FavoriteButtonProps) {
  const { user, isAuthenticated } = useAuth()
  const { isFavorite, addFavorite, removeFavorite } = useFavorites(user)
  const [showAuth, setShowAuth] = useState(false)
  const [loading, setLoading] = useState(false)

  const toggleFavorite = async (artistId: string): Promise<boolean> => {
    if (isFavorite(artistId)) {
      return await removeFavorite(artistId)
    } else {
      return await addFavorite(artistId)
    }
  }

  const handleClick = async () => {
    if (!isAuthenticated) {
      setShowAuth(true)
      return
    }

    setLoading(true)
    try {
      const success = await toggleFavorite(artistId)
      if (success) {
        // 可以添加成功提示
        console.log(isFavorite(artistId) ? '已取消收藏' : '已添加收藏', artistName)
      }
    } catch (err) {
      console.error('收藏操作失败:', err)
    } finally {
      setLoading(false)
    }
  }

  const isCurrentlyFavorite = isFavorite(artistId)

  return (
    <>
      <button
        onClick={handleClick}
        disabled={loading}
        className={`
          group relative flex items-center justify-center
          w-10 h-10 rounded-full
          transition-all duration-200 ease-in-out
          ${isCurrentlyFavorite 
            ? 'bg-red-100 hover:bg-red-200 text-red-600' 
            : 'bg-gray-100 hover:bg-gray-200 text-gray-400 hover:text-red-500'
          }
          ${loading ? 'opacity-50 cursor-not-allowed' : 'hover:scale-110'}
          ${className}
        `}
        title={
          !isAuthenticated 
            ? '登录后收藏' 
            : isCurrentlyFavorite 
              ? `取消收藏 ${artistName}` 
              : `收藏 ${artistName}`
        }
      >
        {/* 心形图标 */}
        <svg
          className={`
            w-5 h-5 transition-all duration-200
            ${isCurrentlyFavorite ? 'fill-current' : 'stroke-current fill-none'}
            ${loading ? 'animate-pulse' : ''}
          `}
          viewBox="0 0 24 24"
          strokeWidth="2"
        >
          <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
        </svg>

        {/* 加载动画 */}
        {loading && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
          </div>
        )}

        {/* 未登录提示 */}
        {!isAuthenticated && (
          <div className="absolute -top-1 -right-1 w-3 h-3 bg-blue-500 rounded-full flex items-center justify-center">
            <span className="text-white text-xs">!</span>
          </div>
        )}
      </button>

      {/* 登录弹窗 */}
      {showAuth && (
        <SimpleAuth
          onSuccess={() => setShowAuth(false)}
          onClose={() => setShowAuth(false)}
        />
      )}
    </>
  )
} 