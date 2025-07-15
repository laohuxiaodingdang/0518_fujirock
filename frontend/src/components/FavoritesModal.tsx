'use client';

import React, { useState, useEffect } from 'react';

interface FavoritesModalProps {
  isOpen: boolean;
  onClose: () => void;
  onRemoveFavorite: () => void;
}

interface FavoriteArtist {
  id: string;
  name: string;
  addedAt: string;
}

const FavoritesModal: React.FC<FavoritesModalProps> = ({ isOpen, onClose, onRemoveFavorite }) => {
  const [favorites, setFavorites] = useState<FavoriteArtist[]>([]);

  // 从 localStorage 加载收藏列表
  useEffect(() => {
    if (isOpen) {
      const savedFavorites = localStorage.getItem('favoriteArtists');
      if (savedFavorites) {
        try {
          setFavorites(JSON.parse(savedFavorites));
        } catch (error) {
          console.error('Error parsing favorites:', error);
          setFavorites([]);
        }
      }
    }
  }, [isOpen]);

  // 移除收藏
  const removeFavorite = (artistId: string) => {
    const updatedFavorites = favorites.filter(fav => fav.id !== artistId);
    setFavorites(updatedFavorites);
    localStorage.setItem('favoriteArtists', JSON.stringify(updatedFavorites));
    onRemoveFavorite();
  };

  // 清空所有收藏
  const clearAllFavorites = () => {
    setFavorites([]);
    localStorage.removeItem('favoriteArtists');
    onRemoveFavorite();
  };

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-lg p-6 max-w-md w-full mx-4 max-h-[80vh] overflow-y-auto"
        onClick={e => e.stopPropagation()}
      >
        <div className="flex justify-between items-center mb-4">
       
          <button
            className="text-gray-400 hover:text-gray-600 text-2xl"
            onClick={onClose}
            aria-label="关闭"
          >
            ×
          </button>
        </div>

        {favorites.length === 0 ? (
          <div className="text-center py-8">
            <div className="text-4xl mb-4"></div>
            
          </div>
        ) : (
          <>
            <div className="space-y-3 mb-4">
              {favorites.map((artist) => (
                <div
                  key={artist.id}
                  className="flex justify-between items-center p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <div>
                    <h3 className="font-medium text-gray-800">{artist.name}</h3>
                    <p className="text-sm text-gray-500">
                      收藏于 {new Date(artist.addedAt).toLocaleDateString()}
                    </p>
                  </div>
                  <button
                    onClick={() => removeFavorite(artist.id)}
                    className="text-red-500 hover:text-red-700 text-lg"
                    aria-label="移除收藏"
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>

            <div className="flex justify-between items-center pt-4 border-t">
              <span className="text-sm text-gray-500">
                共 {favorites.length} 个收藏
              </span>
              <button
                onClick={clearAllFavorites}
                className="text-red-500 hover:text-red-700 text-sm"
              >
                清空所有收藏
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default FavoritesModal;
