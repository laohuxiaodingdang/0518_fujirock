'use client';

import { useState, useEffect } from 'react';
import { simpleFavoriteService } from '../services/simpleFavoriteService';

interface SimpleFavoriteButtonProps {
  artistId: string;
  artistName: string;
  imageUrl?: string;
  genres?: string[];
  className?: string;
  onToggle?: (isFavorited: boolean) => void;
}

export default function SimpleFavoriteButton({ 
  artistId, 
  artistName, 
  imageUrl, 
  genres, 
  className = '',
  onToggle
}: SimpleFavoriteButtonProps) {
  const [isFavorited, setIsFavorited] = useState(false);
  const [isToggling, setIsToggling] = useState(false);

  // 检查初始收藏状态
  useEffect(() => {
    const favorited = simpleFavoriteService.isFavorited(artistId);
    setIsFavorited(favorited);
  }, [artistId]);

  // 切换收藏状态
  const handleToggleFavorite = async () => {
    if (isToggling) return;
    
    setIsToggling(true);
    try {
      const success = simpleFavoriteService.toggleFavorite(artistId, artistName, imageUrl, genres);
      if (success) {
        setIsFavorited(!isFavorited);
        onToggle?.(!isFavorited);
      }
    } catch (error) {
      console.error('收藏操作失败:', error);
    } finally {
      setIsToggling(false);
    }
  };

  return (
    <button
      onClick={handleToggleFavorite}
      disabled={isToggling}
      className={`
        inline-flex items-center justify-center
        w-10 h-10 rounded-full
        transition-all duration-200 ease-in-out
        ${isFavorited 
          ? 'bg-yellow-100 text-yellow-600 hover:bg-yellow-200' 
          : 'bg-gray-100 text-gray-400 hover:bg-gray-200 hover:text-gray-600'
        }
        ${isToggling ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer hover:scale-110'}
        ${className}
      `}
      title={isFavorited ? '取消收藏' : '添加到收藏'}
    >
      {isToggling ? (
        <div className="w-5 h-5 border-2 border-current border-t-transparent rounded-full animate-spin"></div>
      ) : (
        <span className="text-xl">
          {isFavorited ? '⭐' : '☆'}
        </span>
      )}
    </button>
  );
}
