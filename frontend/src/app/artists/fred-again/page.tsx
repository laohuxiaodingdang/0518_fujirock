'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Image from 'next/image';
import TrackPlayer from '@/components/TrackPlayer';

interface Artist {
  id: string;
  name: string;
  spotify_id: string | null;
  genres: string[];
  followers: number;
  popularity: number;
  image_url: string | null;
  wikipedia_extract: string | null;
  ai_description: string | null;
  created_at: string;
  updated_at: string;
}

export default function FredAgainPage() {
  const router = useRouter();
  const [artist, setArtist] = useState<Artist | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentPlayingTrack, setCurrentPlayingTrack] = useState<string | null>(null);

  const handlePlay = (trackId: string) => {
    setCurrentPlayingTrack(trackId);
  };

  const handlePause = () => {
    setCurrentPlayingTrack(null);
  };

  useEffect(() => {
    const fetchFredAgain = async () => {
      try {
        setLoading(true);
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/database/artists/search?name=Fred again..`);
        
        if (!response.ok) {
          throw new Error('Failed to fetch artist data');
        }
        
        const data = await response.json();
        
        if (data.success && data.artist) {
          setArtist(data.artist);
        } else {
          throw new Error('Artist not found');
        }
      } catch (err) {
        console.error('Error fetching Fred again..:', err);
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    fetchFredAgain();
  }, []);

  const handleSpotifyClick = () => {
    if (artist?.spotify_id) {
      window.open(`https://open.spotify.com/artist/${artist.spotify_id}`, '_blank');
    } else {
      window.open('https://open.spotify.com/search/Fred%20again..', '_blank');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin h-12 w-12 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-gray-600">Loading Fred again..</p>
        </div>
      </div>
    );
  }

  if (error || !artist) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-500 text-6xl mb-4">😞</div>
          <h1 className="text-2xl font-bold text-gray-800 mb-2">未找到艺术家</h1>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={() => router.back()}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
          >
            返回
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 返回按钮 */}
      <div className="bg-white px-6 py-4">
        <button
          onClick={() => router.back()}
          className="flex items-center text-gray-600 hover:text-gray-800"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Artist Profile
        </button>
      </div>

      <div className="max-w-4xl mx-auto px-6 py-8">
        {/* 艺术家头部信息 */}
        <div className="bg-white rounded-lg p-8 shadow-sm mb-8">
          <div className="flex items-start gap-6">
            {/* 艺术家头像 */}
            <div className="relative">
              <Image
                src={artist.image_url || 'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?auto=format&fit=facearea&w=256&q=80'}
                alt={artist.name}
                width={120}
                height={120}
                className="rounded-lg object-cover"
                onError={(e) => {
                  e.currentTarget.src = 'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?auto=format&fit=facearea&w=256&q=80';
                }}
              />
            </div>

            {/* 艺术家信息 */}
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <h1 className="text-3xl font-bold text-gray-800">{artist.name}</h1>
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-yellow-500" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                </svg>
              </div>

              <div className="flex items-center gap-4 text-sm text-gray-600 mb-4">
                <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded">7月26日</span>
                <span className="bg-green-100 text-green-800 px-2 py-1 rounded">Green Stage</span>
                <span className="bg-purple-100 text-purple-800 px-2 py-1 rounded">
                  {(artist.followers / 1000000).toFixed(1)}M 粉丝
                </span>
              </div>

              {/* 音乐风格标签 */}
              {artist.genres && artist.genres.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {artist.genres.slice(0, 3).map((genre, index) => (
                    <span key={index} className="bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-sm">
                      {genre}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="space-y-8">
          {/* Wikipedia 部分 */}
          {artist.wikipedia_extract && (
            <div className="bg-white rounded-xl p-6 shadow-md border border-gray-100">
              <div className="flex items-center mb-4">
                <div className="h-6 w-6 text-gray-700 mr-3 flex items-center justify-center font-serif font-bold text-lg">
                  W
                </div>
                <h3 className="text-xl font-semibold text-gray-800">
                  <a 
                    href={`https://en.wikipedia.org/wiki/${encodeURIComponent(artist.name)}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-800 hover:underline"
                  >
                    Wikipedia
                  </a>
                </h3>
              </div>
              <p className="text-gray-600 leading-relaxed">
                {artist.wikipedia_extract.length > 300 
                  ? `${artist.wikipedia_extract.substring(0, 300)}...` 
                  : artist.wikipedia_extract}
              </p>
            </div>
          )}

          {/* AI 描述部分 */}
          {artist.ai_description && (
            <div className="bg-gradient-to-r from-pink-50 to-purple-50 rounded-xl p-6 shadow-md border border-pink-100">
              <div className="flex items-center mb-4">
                <div className="h-6 w-6 text-pink-600 mr-3">
                  <svg viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2a2 2 0 012 2c0 .74-.4 1.39-1 1.73V7h1a7 7 0 017 7h1a1 1 0 011 1v3a1 1 0 01-1 1h-1v1a2 2 0 01-2 2H5a2 2 0 01-2-2v-1H2a1 1 0 01-1-1v-3a1 1 0 011-1h1a7 7 0 017-7h1V5.73c-.6-.34-1-.99-1-1.73a2 2 0 012-2zM7.5 13A1.5 1.5 0 006 14.5V16h2.5v-1.5a1.5 1.5 0 00-1-1.41zM16.5 13a1.5 1.5 0 00-1 1.41V16H18v-1.59a1.5 1.5 0 00-1.5-1.41zM11 16v2h2v-2h-2z"/>
                  </svg>
                </div>
                <h3 className="text-xl font-semibold text-pink-700">Toxic AI Intro</h3>
              </div>
              <div className="text-pink-800 leading-relaxed">
                <p>{artist.ai_description}</p>
              </div>
            </div>
          )}

          {/* Spotify 播放列表部分 */}
          <div className="bg-white rounded-lg p-6 shadow-sm">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-gray-800 flex items-center">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
                </svg>
                Top Tracks
              </h2>
              <button 
                onClick={handleSpotifyClick}
                className="flex items-center gap-2 bg-green-500 text-white px-4 py-2 rounded-lg hover:bg-green-600 transition-colors duration-200"
                title="在Spotify中查看艺术家"
              >
                <svg className="h-4 w-4" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S18.66 0 12 0zm5.521 17.34c-.24.359-.66.48-1.021.24-2.82-1.74-6.36-2.101-10.561-1.141-.418.122-.779-.179-.899-.539-.12-.421.18-.78.54-.9 4.56-1.021 8.52-.6 11.64 1.32.42.18.479.659.301 1.02zm1.44-3.3c-.301.42-.841.6-1.262.3-3.239-1.98-8.159-2.58-11.939-1.38-.479.12-1.02-.12-1.14-.6-.12-.48.12-1.021.6-1.141C9.6 9.9 15 10.561 18.72 12.84c.361.181.54.78.241 1.2zm.12-3.36C15.24 8.4 8.82 8.16 5.16 9.301c-.6.179-1.2-.181-1.38-.721-.18-.601.18-1.2.72-1.381 4.26-1.26 11.28-1.02 15.721 1.621.539.3.719 1.02.42 1.56-.299.421-1.02.599-1.559.3z"/>
                </svg>
                Spotify Playlist
              </button>
            </div>

            {/* 预览说明 */}
            <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-sm text-blue-700 flex items-center">
                <svg className="h-4 w-4 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                </svg>
                <span>
                  <strong>预览说明：</strong>由于Spotify API限制，仅提供30秒预览试听。完整播放请点击Spotify图标跳转到官方应用。
                </span>
              </p>
            </div>

            {/* 示例歌曲列表 */}
            <div className="space-y-4">
              {[
                { id: '1', name: 'Rumble', album: 'Actual Life 3 (January 1 - September 9 2022)', duration: '3:45' },
                { id: '2', name: 'Turn On The Lights again', album: 'Actual Life 3', duration: '4:12' },
                { id: '3', name: 'Jungle', album: 'Actual Life 2', duration: '3:28' },
                { id: '4', name: "Marea (We've Lost Dancing)", album: 'Actual Life', duration: '5:36' },
                { id: '5', name: 'Julia (Deep Diving)', album: 'Actual Life', duration: '4:01' }
              ].map((track, index) => (
                <div key={track.id} className="flex items-center space-x-4 p-3 hover:bg-gray-50 rounded-lg transition-colors">
                  <div className="flex-shrink-0 w-12 h-12 bg-gray-200 rounded flex items-center justify-center text-gray-600 font-medium">
                    {index + 1}
                  </div>
                  <div className="flex-1 min-w-0">
                    <h4 className="text-gray-800 font-medium truncate">{track.name}</h4>
                    <p className="text-gray-500 text-sm truncate">{track.album}</p>
                  </div>
                  <div className="text-gray-500 text-sm">
                    {track.duration}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 