'use client';

import { useState, useEffect } from 'react';
import { simpleFavoriteService } from '../services/simpleFavoriteService';

interface FavoritesListModalProps {
  isOpen: boolean;
  onClose: () => void;
  onArtistClick?: (artistName: string) => void; // 添加艺术家点击回调
}

interface FavoriteArtist {
  id: string;
  name: string;
  image_url?: string;
  genres?: string[];
  created_at: string;
}

export default function FavoritesListModal({ isOpen, onClose, onArtistClick }: FavoritesListModalProps) {  
  const [favorites, setFavorites] = useState<FavoriteArtist[]>([]);

  useEffect(() => {
    if (isOpen) {
      const favs = simpleFavoriteService.getFavorites();
      setFavorites(favs);
    }
  }, [isOpen]);

  const removeFavorite = (artistId: string) => {
    simpleFavoriteService.removeFavorite(artistId);
    setFavorites(simpleFavoriteService.getFavorites());
  };

  const clearAllFavorites = () => {
    if (confirm('确定要清除所有收藏吗？')) {
      localStorage.removeItem('fuji_rock_favorites');
      setFavorites([]);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl max-w-2xl w-full max-h-[80vh] overflow-hidden shadow-2xl">
        {/* 头部 */}
{/* 头部 - 磨砂玻璃效果 */}
<div className="bg-white/20 backdrop-blur-md border-b border-white/30 text-white p-4 relative">
  {/* 背景渐变层 */}
  <div className="absolute inset-0 bg-gradient-to-r from-pink-500/30 to-purple-600/30 rounded-t-xl"></div>
  {/* 内容层 */}
  <div className="relative z-10 flex items-center justify-between">
   
    <button
      onClick={onClose}
      className="w-8 h-8 bg-white/20 hover:bg-white/30 backdrop-blur-sm rounded-full flex items-center justify-center text-white transition-all duration-200 border border-white/20 hover:border-white/40"
    >
      ×
    </button>
  </div>
</div>
        {/* 内容 */}
        <div className="p-6 max-h-[60vh] overflow-y-auto">
          {favorites.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">🎵</div>
            </div>
          ) : (
            <div className="space-y-4">
              {favorites.map((favorite) => (
                <div
                  key={favorite.id}
                  className="flex items-center gap-4 p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                >
{/* 艺术家图片 */}
{favorite.image_url ? (
  <img
    src={favorite.image_url}
    alt={favorite.name}
    className="w-16 h-16 rounded-lg object-cover cursor-pointer hover:opacity-80 transition-opacity"
    onClick={() => {
      if (onArtistClick) {
        onArtistClick(favorite.name);
        onClose(); // 关闭收藏列表
      }
    }}
  />
) : (
  <div 
    className="w-16 h-16 bg-gradient-to-br from-pink-400 to-purple-500 rounded-lg flex items-center justify-center text-white text-2xl font-bold cursor-pointer hover:opacity-80 transition-opacity"
    onClick={() => {
      if (onArtistClick) {
        onArtistClick(favorite.name);
        onClose(); // 关闭收藏列表
      }
    }}
  >
    {favorite.name ? favorite.name.charAt(0) : "?"}
  </div>
)}
                  {/* 艺术家信息 */}
                  <div className="flex-1">
                  <h3 
  className="font-semibold text-gray-800 text-lg cursor-pointer hover:text-blue-600 transition-colors"
  onClick={() => {
    if (onArtistClick) {
      onArtistClick(favorite.name);
      onClose(); // 关闭收藏列表
    }
  }}
>
  {favorite.name}
</h3>    
                    {favorite.genres && favorite.genres.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-1">
                        {favorite.genres.slice(0, 3).map((genre, index) => (
                          <span
                            key={index}
                            className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full"
                          >
                            {genre}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                  {/* 操作按钮 */}
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => removeFavorite(favorite.id)}
                      className="w-8 h-8 bg-red-100 hover:bg-red-200 text-red-600 rounded-full flex items-center justify-center transition-colors"
                      title="移除收藏"
                    >
                      ×
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
        {/* 底部操作 */}
        {favorites.length > 0 && (
          <div className="border-t border-gray-200 p-4 flex justify-between items-center">

          </div>
        )}
        {favorites.length === 0 && (
          <div className="border-t border-gray-200 p-4 flex justify-end">

          </div>
        )}
      </div>
    </div>
  );
}