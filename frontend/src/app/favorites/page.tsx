'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

interface FavoriteArtist {
  id: string;
  name: string;
  image_url?: string;
  genres?: string[];
  created_at: string;
}

export default function FavoritesPage() {
  const [favorites, setFavorites] = useState<FavoriteArtist[]>([]);

  useEffect(() => {
    // 从localStorage读取收藏数据
    const loadFavorites = () => {
      try {
        const stored = localStorage.getItem('fuji_rock_favorites');
        const favs = stored ? JSON.parse(stored) : [];
        setFavorites(favs);
      } catch (error) {
        console.error('Error loading favorites:', error);
        setFavorites([]);
      }
    };

    loadFavorites();
  }, []);

  const removeFavorite = (artistId: string) => {
    try {
      const stored = localStorage.getItem('fuji_rock_favorites');
      const favs = stored ? JSON.parse(stored) : [];
      const filtered = favs.filter((fav: FavoriteArtist) => fav.id !== artistId);
      localStorage.setItem('fuji_rock_favorites', JSON.stringify(filtered));
      setFavorites(filtered);
    } catch (error) {
      console.error('Error removing favorite:', error);
    }
  };

  const clearAllFavorites = () => {
    if (confirm('确定要清除所有收藏吗？')) {
      localStorage.removeItem('fuji_rock_favorites');
      setFavorites([]);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-600 via-blue-600 to-indigo-700">
      {/* 导航栏 */}
      <header className="bg-white/10 backdrop-blur-md border-b border-white/20 px-4 py-3">
        <div className="max-w-6xl mx-auto flex justify-between items-center">
          <Link href="/" className="text-white font-bold text-xl hover:text-gray-200 transition-colors">
            ← 返回首页
          </Link>
          <h1 className="text-white font-bold text-xl"></h1>
          <div className="text-white">
            共 {favorites.length} 个收藏
          </div>
        </div>
      </header>

      {/* 主要内容 */}
      <div className="max-w-6xl mx-auto p-4">
        {favorites.length === 0 ? (
          <div className="text-center py-20">
            <div className="text-6xl mb-4">💔</div>
            <h2 className="text-2xl font-bold text-white mb-4">还没有收藏任何艺术家</h2>
            <p className="text-white/80 mb-6">去首页发现更多优秀的艺术家吧！</p>
            <Link
              href="/"
              className="bg-white text-purple-600 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
            >
              去发现艺术家
            </Link>
          </div>
        ) : (
          <div>
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold text-white mb-2">
                 ({favorites.length})
              </h2>
              <p className="text-white/80 mb-4"></p>
              <button
                onClick={clearAllFavorites}
                className="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600 transition-colors text-sm"
              >
                清除所有收藏
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {favorites.map((favorite) => (
                <div
                  key={favorite.id}
                  className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20 hover:bg-white/20 transition-all duration-300"
                >
                  <div className="flex items-start justify-between mb-4">
                    <h3 className="text-xl font-bold text-white">
                      {favorite.name}
                    </h3>
                    <div className="flex items-center gap-2">
                      <span className="text-yellow-400 text-2xl">⭐</span>
                      <button
                        onClick={() => removeFavorite(favorite.id)}
                        className="text-red-400 hover:text-red-300 text-lg transition-colors"
                        title="移除收藏"
                      >
                        ×
                      </button>
                    </div>
                  </div>
                  
                  {favorite.image_url && (
                    <div className="mb-4 flex justify-center">
                      <img 
                        src={favorite.image_url} 
                        alt={favorite.name}
                        className="w-24 h-24 rounded-lg object-cover"
                      />
                    </div>
                  )}
                  
                  {favorite.genres && favorite.genres.length > 0 && (
                    <div className="flex flex-wrap gap-2 mb-4">
                      {favorite.genres.slice(0, 3).map((genre, index) => (
                        <span
                          key={index}
                          className="bg-white/20 text-white px-2 py-1 rounded-full text-xs"
                        >
                          {genre}
                        </span>
                      ))}
                    </div>
                  )}
                  
                  <div className="text-white/60 text-sm">
                    收藏于 {new Date(favorite.created_at).toLocaleDateString('zh-CN')}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
