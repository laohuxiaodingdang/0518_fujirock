'use client';

import { useState } from 'react';
import { getArtistWikipedia, WikipediaArtistResponse } from '@/utils/api';

export default function TestPage() {
  const [artistName, setArtistName] = useState('');
  const [result, setResult] = useState<WikipediaArtistResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async () => {
    if (!artistName.trim()) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await getArtistWikipedia(artistName);
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <h1 className="text-3xl font-bold text-gray-800 mb-8">API 测试页面</h1>
        
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Wikipedia 艺术家搜索</h2>
          
          <div className="flex gap-4 mb-4">
            <input
              type="text"
              value={artistName}
              onChange={(e) => setArtistName(e.target.value)}
              placeholder="输入艺术家名称 (例如: radiohead, nirvana)"
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            />
            <button
              onClick={handleSearch}
              disabled={loading || !artistName.trim()}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? '搜索中...' : '搜索'}
            </button>
          </div>

          {loading && (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full"></div>
              <span className="ml-3 text-gray-600">正在搜索...</span>
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

          {result && result.success && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-green-800 mb-3">搜索结果</h3>
              
              <div className="space-y-4">
                <div>
                  <h4 className="font-medium text-gray-800">艺术家名称:</h4>
                  <p className="text-gray-700">{result.data.title}</p>
                </div>
                
                <div>
                  <h4 className="font-medium text-gray-800">简介:</h4>
                  <p className="text-gray-700 leading-relaxed">{result.data.extract}</p>
                </div>

                {result.data.thumbnail && (
                  <div>
                    <h4 className="font-medium text-gray-800">图片:</h4>
                    <img 
                      src={result.data.thumbnail.source} 
                      alt={result.data.title}
                      className="mt-2 rounded-lg max-w-xs"
                    />
                  </div>
                )}

                {result.data.categories.length > 0 && (
                  <div>
                    <h4 className="font-medium text-gray-800">分类:</h4>
                    <div className="flex flex-wrap gap-2 mt-2">
                      {result.data.categories.map((category, index) => (
                        <span
                          key={index}
                          className="px-2 py-1 bg-blue-100 text-blue-800 text-sm rounded-full"
                        >
                          {category}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {result.data.references.length > 0 && (
                  <div>
                    <h4 className="font-medium text-gray-800">相关链接:</h4>
                    <div className="space-y-1 mt-2">
                      {result.data.references.map((ref, index) => (
                        <a
                          key={index}
                          href={ref.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="block text-blue-600 hover:text-blue-800 underline"
                        >
                          {ref.title}
                        </a>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              <div className="mt-4 pt-4 border-t border-green-200">
                <h4 className="font-medium text-gray-800">原始响应数据:</h4>
                <pre className="mt-2 p-3 bg-gray-100 rounded text-xs overflow-x-auto">
                  {JSON.stringify(result, null, 2)}
                </pre>
              </div>
            </div>
          )}
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-xl font-semibold mb-4">测试说明</h2>
          <ul className="space-y-2 text-gray-700">
            <li>• 输入艺术家名称，点击搜索按钮或按回车键</li>
            <li>• 系统会调用后端 <code className="bg-gray-100 px-1 rounded">/api/wikipedia/artists/{'{artist_name}'}</code> 接口</li>
            <li>• 建议测试的艺术家: radiohead, nirvana, beatles, coldplay</li>
            <li>• 当前使用Mock数据，所以所有搜索都会返回相似的结果</li>
          </ul>
        </div>
      </div>
    </div>
  );
} 