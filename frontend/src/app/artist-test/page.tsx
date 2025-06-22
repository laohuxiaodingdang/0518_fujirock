'use client';

import { useState } from 'react';
import { getArtistFullProfile } from '@/utils/api';

export default function ArtistTestPage() {
  const [artistName, setArtistName] = useState('');
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleTest = async () => {
    if (!artistName.trim()) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await getArtistFullProfile(artistName);
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Test failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        <h1 className="text-3xl font-bold text-gray-800 mb-8">艺术家完整信息测试</h1>
        
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">测试艺术家完整信息获取</h2>
          
          <div className="flex gap-4 mb-4">
            <input
              type="text"
              value={artistName}
              onChange={(e) => setArtistName(e.target.value)}
              placeholder="输入艺术家名称 (例如: Radiohead, Nirvana)"
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              onKeyPress={(e) => e.key === 'Enter' && handleTest()}
            />
            <button
              onClick={handleTest}
              disabled={loading || !artistName.trim()}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? '测试中...' : '测试'}
            </button>
          </div>

          {loading && (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full"></div>
              <span className="ml-3 text-gray-600">正在获取艺术家信息...</span>
            </div>
          )}

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
              <div className="flex items-center">
                <svg className="h-5 w-5 text-red-500 mr-2" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                <span className="text-red-700">错误: {error}</span>
              </div>
            </div>
          )}

          {result && (
            <div className="space-y-6">
              {/* Wikipedia 结果 */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h3 className="font-semibold text-blue-800 mb-2">Wikipedia 信息</h3>
                {result.wikipedia?.success ? (
                  <div className="space-y-2">
                    <p><strong>标题:</strong> {result.wikipedia.data.title}</p>
                    <p><strong>简介:</strong> {result.wikipedia.data.extract}</p>
                    {result.wikipedia.data.thumbnail && (
                      <div>
                        <strong>图片:</strong>
                        <img 
                          src={result.wikipedia.data.thumbnail.source} 
                          alt={result.wikipedia.data.title}
                          className="mt-2 rounded max-w-xs"
                        />
                      </div>
                    )}
                  </div>
                ) : (
                  <p className="text-red-600">Wikipedia 信息获取失败: {result.errors?.wikipedia?.message || '未知错误'}</p>
                )}
              </div>

              {/* Spotify 结果 */}
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <h3 className="font-semibold text-green-800 mb-2">Spotify 信息</h3>
                {result.spotify?.success ? (
                  <div className="space-y-2">
                    <p><strong>艺术家:</strong> {result.spotify.data.name}</p>
                    <p><strong>粉丝数:</strong> {result.spotify.data.followers.total.toLocaleString()}</p>
                    <p><strong>流行度:</strong> {result.spotify.data.popularity}/100</p>
                    <p><strong>风格:</strong> {result.spotify.data.genres.join(', ')}</p>
                    {result.spotify.data.images.length > 0 && (
                      <div>
                        <strong>头像:</strong>
                        <img 
                          src={result.spotify.data.images[0].url} 
                          alt={result.spotify.data.name}
                          className="mt-2 rounded w-32 h-32 object-cover"
                        />
                      </div>
                    )}
                  </div>
                ) : (
                  <p className="text-red-600">Spotify 信息获取失败: {result.errors?.spotify?.message || '未知错误'}</p>
                )}
              </div>

              {/* 热门歌曲结果 */}
              <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                <h3 className="font-semibold text-purple-800 mb-2">热门歌曲</h3>
                {result.topTracks?.success ? (
                  <div className="space-y-2">
                    {result.topTracks.data.tracks.slice(0, 5).map((track: any, index: number) => (
                      <div key={track.id} className="flex items-center space-x-3 p-2 bg-white rounded">
                        <span className="text-sm text-gray-500">{index + 1}</span>
                        <div className="flex-1">
                          <p className="font-medium">{track.name}</p>
                          <p className="text-sm text-gray-600">{track.album.name}</p>
                        </div>
                        <span className="text-sm text-gray-500">
                          {Math.floor(track.duration_ms / 60000)}:{Math.floor((track.duration_ms % 60000) / 1000).toString().padStart(2, '0')}
                        </span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-red-600">热门歌曲获取失败: {result.errors?.topTracks?.message || '未知错误'}</p>
                )}
              </div>

              {/* AI 描述结果 */}
              <div className="bg-pink-50 border border-pink-200 rounded-lg p-4">
                <h3 className="font-semibold text-pink-800 mb-2">AI 毒舌评价</h3>
                {result.aiDescription?.success ? (
                  <div className="space-y-2">
                    <p><strong>毒舌评价:</strong> {result.aiDescription.data.sassy_description}</p>
                    <div className="text-sm text-gray-600">
                      <p><strong>幽默程度:</strong> {result.aiDescription.data.style_metrics.humor_level}/10</p>
                      <p><strong>讽刺程度:</strong> {result.aiDescription.data.style_metrics.sarcasm_level}/10</p>
                      <p><strong>事实准确性:</strong> {result.aiDescription.data.style_metrics.fact_accuracy}</p>
                      <p><strong>使用模型:</strong> {result.aiDescription.data.model_used}</p>
                    </div>
                  </div>
                ) : (
                  <p className="text-red-600">AI 描述生成失败或跳过</p>
                )}
              </div>

              {/* 原始数据 */}
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                <h3 className="font-semibold text-gray-800 mb-2">原始响应数据</h3>
                <pre className="text-xs overflow-x-auto bg-white p-3 rounded border">
                  {JSON.stringify(result, null, 2)}
                </pre>
              </div>
            </div>
          )}
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-xl font-semibold mb-4">测试说明</h2>
          <ul className="space-y-2 text-gray-700">
            <li>• 这个页面会并行调用 Wikipedia、Spotify 和 AI 描述生成 API</li>
            <li>• 建议测试的艺术家: Radiohead, Nirvana, The Beatles, Coldplay</li>
            <li>• 当前使用Mock数据，所以结果可能相似</li>
            <li>• AI 描述生成可能会失败，这是正常的（因为需要先获取 Wikipedia 内容）</li>
          </ul>
        </div>
      </div>
    </div>
  );
} 