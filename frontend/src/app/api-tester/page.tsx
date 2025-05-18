export default function ApiTesterPage() {
  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-6">API测试中心</h1>
      <p className="mb-6">这个页面用于测试各种API连接是否正常工作</p>
      
      <div className="bg-gray-800 p-6 rounded-lg">
        <h2 className="text-xl font-bold mb-4">Spotify API测试</h2>
        <a href="/api/spotify/search?q=radiohead" target="_blank" className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded inline-block">
          测试Spotify搜索API
        </a>
      </div>
    </div>
  );
}