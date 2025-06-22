'use client';

import { useState } from 'react';
import { getArtistWikipedia, getArtistSpotify } from '@/utils/api';

export default function SearchDebugPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [results, setResults] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;

    setLoading(true);
    setError(null);
    setResults(null);

    try {
      console.log('开始搜索:', searchQuery);
      
      const [wikipediaResult, spotifyResult] = await Promise.allSettled([
        getArtistWikipedia(searchQuery),
        getArtistSpotify(searchQuery),
      ]);

      console.log('Wikipedia结果:', wikipediaResult);
      console.log('Spotify结果:', spotifyResult);

      setResults({
        wikipedia: wikipediaResult.status === 'fulfilled' ? wikipediaResult.value : { error: wikipediaResult.reason },
        spotify: spotifyResult.status === 'fulfilled' ? spotifyResult.value : { error: spotifyResult.reason },
      });
    } catch (error) {
      console.error('搜索错误:', error);
      setError(error instanceof Error ? error.message : '搜索失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8 text-gray-800">搜索功能调试</h1>
        
        <div className="bg-white rounded-lg p-6 shadow-sm mb-8">
          <div className="flex gap-4 mb-4">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="输入艺术家名称..."
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            />
            <button
              onClick={handleSearch}
              disabled={loading || !searchQuery.trim()}
              className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? '搜索中...' : '搜索'}
            </button>
          </div>
          
          <div className="text-sm text-gray-600">
            尝试搜索: Radiohead, Nirvana, The Beatles, Coldplay
          </div>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-8">
            <h3 className="text-red-800 font-medium">错误</h3>
            <p className="text-red-600">{error}</p>
          </div>
        )}

        {results && (
          <div className="space-y-8">
            {/* Wikipedia 结果 */}
            <div className="bg-white rounded-lg p-6 shadow-sm">
              <h2 className="text-xl font-semibold mb-4 text-gray-800">Wikipedia API 结果</h2>
              {results.wikipedia.error ? (
                <div className="text-red-600">
                  错误: {JSON.stringify(results.wikipedia.error, null, 2)}
                </div>
              ) : (
                <div className="space-y-4">
                  <div>
                    <h3 className="font-medium text-gray-700">标题:</h3>
                    <p className="text-gray-600">{results.wikipedia.data?.title}</p>
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-700">描述:</h3>
                    <p className="text-gray-600">{results.wikipedia.data?.extract}</p>
                  </div>
                  {results.wikipedia.data?.thumbnail && (
                    <div>
                      <h3 className="font-medium text-gray-700">图片:</h3>
                      <img 
                        src={results.wikipedia.data.thumbnail.source} 
                        alt="Artist"
                        className="w-32 h-32 object-cover rounded-lg"
                      />
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Spotify 结果 */}
            <div className="bg-white rounded-lg p-6 shadow-sm">
              <h2 className="text-xl font-semibold mb-4 text-gray-800">Spotify API 结果</h2>
              {results.spotify.error ? (
                <div className="text-red-600">
                  错误: {JSON.stringify(results.spotify.error, null, 2)}
                </div>
              ) : (
                <div className="space-y-4">
                  <div>
                    <h3 className="font-medium text-gray-700">艺术家:</h3>
                    <p className="text-gray-600">{results.spotify.data?.name}</p>
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-700">流行度:</h3>
                    <p className="text-gray-600">{results.spotify.data?.popularity}</p>
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-700">粉丝数:</h3>
                    <p className="text-gray-600">{results.spotify.data?.followers?.total?.toLocaleString()}</p>
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-700">风格:</h3>
                    <p className="text-gray-600">{results.spotify.data?.genres?.join(', ')}</p>
                  </div>
                  {results.spotify.data?.images?.[0] && (
                    <div>
                      <h3 className="font-medium text-gray-700">图片:</h3>
                      <img 
                        src={results.spotify.data.images[0].url} 
                        alt="Artist"
                        className="w-32 h-32 object-cover rounded-lg"
                      />
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
} 