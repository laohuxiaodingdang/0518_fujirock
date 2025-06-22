'use client';

interface SpotifyApiNoticeProps {
  className?: string;
}

export default function SpotifyApiNotice({ className = "" }: SpotifyApiNoticeProps) {
  return (
    <div className={`bg-yellow-50 border border-yellow-200 rounded-lg p-4 ${className}`}>
      <div className="flex items-start">
        <div className="flex-shrink-0">
          <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
        </div>
        <div className="ml-3">
          <h3 className="text-sm font-medium text-yellow-800">
            Spotify API 限制说明
          </h3>
          <div className="mt-2 text-sm text-yellow-700">
            <p className="mb-2">
              由于Spotify在2024年11月对API进行了重大变更，30秒音频预览功能已被限制：
            </p>
            <ul className="list-disc list-inside space-y-1 text-xs">
              <li>新的开发模式应用无法访问 <code className="bg-yellow-100 px-1 rounded">preview_url</code></li>
              <li>只有已获得扩展访问权限的应用才能使用音频预览</li>
              <li>点击播放按钮将直接跳转到Spotify进行完整播放</li>
              <li>这是Spotify平台策略调整的结果，不是我们应用的问题</li>
            </ul>
            <div className="mt-3 p-2 bg-yellow-100 rounded text-xs">
              <strong>替代方案：</strong> 我们已经集成了iTunes API来提供30秒音频预览功能。
              <br />
              <span className="text-yellow-600">
                • iTunes API提供免费的30秒预览，无需API密钥
                <br />
                • 覆盖数百万首歌曲，包括大部分热门音乐
                <br />
                • 点击播放按钮将尝试播放iTunes预览，如果没有则跳转到Spotify
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 