'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useState, useEffect } from 'react';
import Image from 'next/image';

interface DatabaseArtist {
  id: string;
  name: string;
  description: string;
  image_url: string;
  genres: string[];
  is_fuji_rock_artist: boolean;
  wiki_extract: string;
}

export default function ArtistsPage() {
  const router = useRouter();
  const [artists, setArtists] = useState<DatabaseArtist[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchArtists = async () => {
      try {
        setLoading(true);
        const response = await fetch('/api/database/artists/search?query=&limit=50');
        const data = await response.json();
        
        if (data.success) {
          // 只显示 Fuji Rock 艺术家
          const fujiRockArtists = data.data.filter((artist: DatabaseArtist) => artist.is_fuji_rock_artist);
          setArtists(fujiRockArtists);
        } else {
          throw new Error('Failed to fetch artists');
        }
      } catch (err) {
        console.error('Error fetching artists:', err);
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    fetchArtists();
  }, []);

  const getGenreColor = (index: number) => {
    const colors = [
      'from-green-400 to-blue-500',
      'from-purple-400 to-pink-500', 
      'from-orange-400 to-red-500',
      'from-cyan-400 to-purple-500',
      'from-yellow-400 to-orange-500',
      'from-indigo-400 to-blue-500'
    ];
    return colors[index % colors.length];
  };

  const getGenreEmoji = (genres: string[]) => {
    if (!genres || genres.length === 0) return '🎵';
    
    const genreToEmoji: { [key: string]: string } = {
      'electronic': '🎛️',
      'house': '🕺', 
      'stutter house': '🎵',
      'dance': '💃',
      'pop': '🎤',
      'rock': '🎸',
      'indie': '🎨',
      'alternative': '🎧',
      'garage rock': '🔥',
      'garage rock revival': '⚡',
      'j-pop': '🎌',
      'j-rock': '🗾',
      'soundtrack': '🎬',
      'indie pop': '🌟',
      'indie rock': '🎯'
    };
    
    for (const genre of genres) {
      const lowerGenre = genre.toLowerCase();
      for (const [key, emoji] of Object.entries(genreToEmoji)) {
        if (lowerGenre.includes(key)) {
          return emoji;
        }
      }
    }
    return '🎵';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-600 via-blue-600 to-indigo-700 p-6">
        <div className="max-w-4xl mx-auto">
          <div className="text-center py-20">
            <div className="animate-spin h-12 w-12 border-4 border-white border-t-transparent rounded-full mx-auto mb-4"></div>
            <p className="text-white/80 text-lg">Loading Fuji Rock 2025 Artists...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-600 via-blue-600 to-indigo-700 p-6">
        <div className="max-w-4xl mx-auto">
          <div className="text-center py-20">
            <div className="text-white text-6xl mb-4">😞</div>
            <h1 className="text-2xl font-bold text-white mb-2">Failed to Load Artists</h1>
            <p className="text-white/70 mb-4">{error}</p>
            <button
              onClick={() => window.location.reload()}
              className="px-6 py-3 bg-white/20 backdrop-blur-sm text-white rounded-lg hover:bg-white/30 transition-all"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-600 via-blue-600 to-indigo-700 p-6">
      <div className="max-w-4xl mx-auto">
        {/* 返回按钮 */}
        <div className="mb-8">
          <button
            onClick={() => router.back()}
            className="flex items-center text-white/80 hover:text-white bg-black/20 backdrop-blur-sm rounded-lg px-3 py-2 transition-all"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back
          </button>
        </div>

        {/* 页面标题 */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-6xl font-bold text-white mb-4">
            Fuji Rock 2025 Artists
          </h1>
          <p className="text-white/80 text-lg">
            Discover the amazing lineup for Fuji Rock Festival 2025
          </p>
        </div>

        {/* 艺术家卡片 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {artists.map((artist, index) => (
            <div key={artist.id} className="group">
              <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 hover:bg-white/20 transition-all transform hover:scale-105 cursor-pointer">
                <div className="text-center">
                  {artist.image_url ? (
                    <div className="w-20 h-20 mx-auto mb-4 rounded-full overflow-hidden">
                      <Image
                        src={artist.image_url}
                        alt={artist.name}
                        width={80}
                        height={80}
                        className="w-full h-full object-cover"
                        onError={(e) => {
                          e.currentTarget.style.display = 'none';
                          e.currentTarget.nextElementSibling?.classList.remove('hidden');
                        }}
                      />
                      <div className={`w-20 h-20 bg-gradient-to-br ${getGenreColor(index)} rounded-full flex items-center justify-center hidden`}>
                        <span className="text-white font-bold text-2xl">{getGenreEmoji(artist.genres)}</span>
                      </div>
                    </div>
                  ) : (
                    <div className={`w-20 h-20 bg-gradient-to-br ${getGenreColor(index)} rounded-full mx-auto mb-4 flex items-center justify-center`}>
                      <span className="text-white font-bold text-2xl">{getGenreEmoji(artist.genres)}</span>
                    </div>
                  )}
                  
                  <h3 className="text-xl font-bold text-white mb-2">{artist.name}</h3>
                  <p className="text-white/70 text-sm mb-3">
                    {artist.genres.slice(0, 3).join(' • ') || 'Music'}
                  </p>
                  <div className="flex justify-center gap-2">
                    <span className="bg-green-500/20 text-green-300 px-2 py-1 rounded-full text-xs">
                      Green Stage
                    </span>
                    <span className="bg-blue-500/20 text-blue-300 px-2 py-1 rounded-full text-xs">
                      July 26
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* 说明文字 */}
        <div className="mt-12 text-center">
          <p className="text-white/60 text-sm">
            Click on any artist to explore their profile with real Wikipedia content and AI-generated descriptions
          </p>
        </div>
      </div>
    </div>
  );
} 