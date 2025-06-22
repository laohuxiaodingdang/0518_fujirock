'use client';

import { useState } from 'react';
import { getArtistWikipedia, getArtistSpotify } from '@/utils/api';

export default function SearchTestPage() {
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
      const [wikipediaResult, spotifyResult] = await Promise.allSettled([
        getArtistWikipedia(searchQuery),
        getArtistSpotify(searchQuery),
      ]);

      setResults({
        wikipedia: wikipediaResult.status === 'fulfilled' ? wikipediaResult.value : { error: wikipediaResult.reason },
        spotify: spotifyResult.status === 'fulfilled' ? spotifyResult.value : { error: spotifyResult.reason }
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : '搜索失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-800 mb-8">搜索功能测试</h1>
        
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <div className="flex gap-4 mb-4">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="输入艺术家名称（如：Radiohead, Nirvana）"
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
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-8">
            <p className="text-red-700">错误: {error}</p>
          </div>
        )}

        {results && (
          <div className="space-y-8">
            {/* Wikipedia 结果 */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">Wikipedia 结果</h2>
              <pre className="bg-gray-100 p-4 rounded-lg overflow-auto text-sm">
                {JSON.stringify(results.wikipedia, null, 2)}
              </pre>
            </div>

            {/* Spotify 结果 */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">Spotify 结果</h2>
              <pre className="bg-gray-100 p-4 rounded-lg overflow-auto text-sm">
                {JSON.stringify(results.spotify, null, 2)}
              </pre>
            </div>

            {/* 组合显示 */}
            {results.wikipedia?.success && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-semibold text-gray-800 mb-4">艺术家信息</h2>
                <div className="flex items-start space-x-6">
                  {results.spotify?.success && results.spotify.data.images.length > 0 && (
                    <img
                      src={results.spotify.data.images[0].url}
                      alt={results.wikipedia.data.title}
                      className="w-32 h-32 rounded-lg object-cover"
                    />
                  )}
                  <div className="flex-1">
                    <h3 className="text-2xl font-bold text-gray-800 mb-2">
                      {results.wikipedia.data.title}
                    </h3>
                    {results.spotify?.success && (
                      <div className="mb-4 space-y-1">
                        <p><strong>粉丝数:</strong> {results.spotify.data.followers.total.toLocaleString()}</p>
                        <p><strong>流行度:</strong> {results.spotify.data.popularity}/100</p>
                        {results.spotify.data.genres.length > 0 && (
                          <p><strong>音乐风格:</strong> {results.spotify.data.genres.join(', ')}</p>
                        )}
                      </div>
                    )}
                    <p className="text-gray-700 leading-relaxed">
                      {results.wikipedia.data.extract}
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
} 