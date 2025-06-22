'use client';

import { useState } from 'react';
import TrackPlayer from '@/components/TrackPlayer';

// 模拟一些有preview_url的歌曲数据
const mockTracks = [
  {
    id: "1",
    name: "Test Song 1",
    preview_url: "https://www.soundjay.com/misc/sounds/bell-ringing-05.wav",
    duration_ms: 180000,
    album: {
      name: "Test Album 1",
      images: [
        {
          url: "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=300",
          height: 300,
          width: 300
        }
      ]
    },
    external_urls: {
      spotify: "https://open.spotify.com/track/test1"
    }
  },
  {
    id: "2", 
    name: "Test Song 2",
    preview_url: null, // 模拟没有预览的歌曲
    duration_ms: 240000,
    album: {
      name: "Test Album 2",
      images: [
        {
          url: "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=300",
          height: 300,
          width: 300
        }
      ]
    },
    external_urls: {
      spotify: "https://open.spotify.com/track/test2"
    }
  },
  {
    id: "3",
    name: "Test Song 3 - Very Long Song Name That Should Be Truncated",
    preview_url: "https://www.soundjay.com/misc/sounds/bell-ringing-05.wav",
    duration_ms: 195000,
    album: {
      name: "Test Album 3 - Very Long Album Name",
      images: [
        {
          url: "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=300",
          height: 300,
          width: 300
        }
      ]
    },
    external_urls: {
      spotify: "https://open.spotify.com/track/test3"
    }
  }
];

export default function MusicTestPage() {
  const [currentPlayingTrack, setCurrentPlayingTrack] = useState<string | null>(null);

  const handlePlay = (trackId: string) => {
    // 如果有其他歌曲在播放，先停止
    if (currentPlayingTrack && currentPlayingTrack !== trackId) {
      setCurrentPlayingTrack(null);
    }
    setCurrentPlayingTrack(trackId);
  };

  const handlePause = () => {
    setCurrentPlayingTrack(null);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-6 py-8">
        <div className="bg-white rounded-lg p-8 shadow-sm mb-8">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">音乐播放器测试</h1>
          <p className="text-gray-600">测试TrackPlayer组件的播放功能</p>
        </div>

        <div className="bg-white rounded-lg p-6 shadow-sm">
          <h2 className="text-xl font-semibold text-gray-800 mb-6 flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
            </svg>
            测试歌曲列表
          </h2>

          <div className="space-y-4">
            {mockTracks.map((track) => (
              <TrackPlayer
                key={track.id}
                track={track}
                isPlaying={currentPlayingTrack === track.id}
                onPlay={() => handlePlay(track.id)}
                onPause={handlePause}
              />
            ))}
          </div>

          <div className="mt-8 p-4 bg-blue-50 rounded-lg">
            <h3 className="font-semibold text-blue-800 mb-2">功能说明：</h3>
            <ul className="text-sm text-blue-700 space-y-1">
              <li>• <strong>实际情况：</strong>由于Spotify API限制，大部分歌曲无法提供30秒预览</li>
              <li>• 点击播放按钮会直接跳转到Spotify进行完整播放</li>
              <li>• 悬停时显示Spotify链接</li>
              <li>• 同时只能播放一首歌曲（如果有预览的话）</li>
              <li>• <strong>注意：</strong>上面的测试音频仅为演示UI功能，实际应用中无法播放</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
} 