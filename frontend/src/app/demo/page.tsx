'use client';

import Link from 'next/link';
import ArtistCard from '@/components/ArtistCard';

export default function DemoPage() {
  const demoArtists = [
    {
      id: '1',
      name: 'Radiohead',
      image: 'https://i.scdn.co/image/ab6761610000e5eba03696716c9ee605006047fd',
      genre: 'Alternative Rock'
    },
    {
      id: '2', 
      name: 'Nirvana',
      image: 'https://images.unsplash.com/photo-1508214751196-bcfd4ca60f91?auto=format&fit=facearea&w=256&q=80',
      genre: 'Grunge'
    },
    {
      id: '3',
      name: 'The Beatles', 
      image: 'https://images.unsplash.com/photo-1465101046530-73398c7f28ca?auto=format&fit=facearea&w=256&q=80',
      genre: 'Rock'
    },
    {
      id: '4',
      name: 'Coldplay',
      image: 'https://images.unsplash.com/photo-1515378791036-0648a3ef77b2?auto=format&fit=facearea&w=256&q=80',
      genre: 'Pop Rock'
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-4">🎸 Fuji Rock 2025 演示</h1>
          <p className="text-gray-600 text-lg">前后端联调功能演示页面</p>
        </div>

        {/* 功能测试区域 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
          <Link href="/test" className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
            <div className="text-center">
              <div className="text-4xl mb-3">🔍</div>
              <h3 className="text-xl font-semibold text-gray-800 mb-2">Wikipedia 搜索测试</h3>
              <p className="text-gray-600 text-sm">测试 Wikipedia API 搜索功能</p>
            </div>
          </Link>

          <Link href="/artist-test" className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
            <div className="text-center">
              <div className="text-4xl mb-3">🎵</div>
              <h3 className="text-xl font-semibold text-gray-800 mb-2">完整信息测试</h3>
              <p className="text-gray-600 text-sm">测试 Wikipedia + Spotify + AI 集成</p>
            </div>
          </Link>

          <Link href="/" className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
            <div className="text-center">
              <div className="text-4xl mb-3">🏠</div>
              <h3 className="text-xl font-semibold text-gray-800 mb-2">主页</h3>
              <p className="text-gray-600 text-sm">返回主页查看完整界面</p>
            </div>
          </Link>
        </div>

        {/* 艺术家卡片演示 */}
        <div className="bg-white rounded-lg shadow-md p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-6 text-center">🎤 艺术家详情页面测试</h2>
          <p className="text-gray-600 text-center mb-8">
            点击任意艺术家卡片，查看集成了真实 Wikipedia、Spotify 和 AI 数据的详情页面
          </p>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {demoArtists.map((artist) => (
              <ArtistCard
                key={artist.id}
                id={artist.id}
                name={artist.name}
                image={artist.image}
                genre={artist.genre}
                className="shadow-sm hover:shadow-md transition-shadow"
              />
            ))}
          </div>
        </div>

        {/* API 状态说明 */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-8">
          <h3 className="text-lg font-semibold text-blue-800 mb-3">📡 API 状态说明</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div className="bg-white rounded p-3">
              <div className="flex items-center mb-2">
                <div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
                <strong>Wikipedia API</strong>
              </div>
              <p className="text-gray-600">✅ 正常工作 (Mock 数据)</p>
            </div>
            <div className="bg-white rounded p-3">
              <div className="flex items-center mb-2">
                <div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
                <strong>Spotify API</strong>
              </div>
              <p className="text-gray-600">✅ 正常工作 (Mock 数据)</p>
            </div>
            <div className="bg-white rounded p-3">
              <div className="flex items-center mb-2">
                <div className="w-3 h-3 bg-yellow-500 rounded-full mr-2"></div>
                <strong>DeepSeek AI</strong>
              </div>
              <p className="text-gray-600">⚠️ Mock 模式 (开发环境)</p>
            </div>
          </div>
        </div>

        {/* 使用说明 */}
        <div className="bg-white rounded-lg shadow-md p-8">
          <h3 className="text-2xl font-bold text-gray-800 mb-4">📖 使用说明</h3>
          <div className="space-y-4 text-gray-700">
            <div>
              <h4 className="font-semibold text-gray-800">1. 搜索功能测试</h4>
              <p>在主页顶部搜索框输入艺术家名称，或访问 <code className="bg-gray-100 px-1 rounded">/test</code> 页面进行详细测试。</p>
            </div>
            <div>
              <h4 className="font-semibold text-gray-800">2. 艺术家详情页面</h4>
              <p>点击任意艺术家卡片，查看集成了 Wikipedia 简介、AI 毒舌评价和 Spotify 热门歌曲的详情页面。</p>
            </div>
            <div>
              <h4 className="font-semibold text-gray-800">3. API 集成测试</h4>
              <p>访问 <code className="bg-gray-100 px-1 rounded">/artist-test</code> 页面，查看所有 API 的详细响应数据。</p>
            </div>
            <div>
              <h4 className="font-semibold text-gray-800">4. 支持的艺术家</h4>
              <p>当前支持: Radiohead (ID: 1), Nirvana (ID: 2), The Beatles (ID: 3), Coldplay (ID: 4)</p>
            </div>
          </div>
        </div>

        {/* 技术栈信息 */}
        <div className="mt-8 text-center text-gray-500 text-sm">
          <p>🛠️ 技术栈: Next.js + TypeScript + Tailwind CSS + FastAPI + Python</p>
          <p>🔗 前后端联调: Next.js API 代理 + CORS 配置</p>
        </div>
      </div>
    </div>
  );
} 