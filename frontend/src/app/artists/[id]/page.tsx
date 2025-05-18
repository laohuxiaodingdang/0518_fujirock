'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import Link from 'next/link';

// Tabs for different sections
const tabs = [
  { id: 'info', label: '基本信息' },
  { id: 'songs', label: '热门歌曲' },
  { id: 'similar', label: '相似艺术家' },
];

export default function ArtistPage({ params }: { params: { id: string } }) {
  const [activeTab, setActiveTab] = useState('info');
  
  // Placeholder artist data (would be fetched from API)
  const artist = {
    id: params.id,
    name: '示例艺术家',
    description: '这是一个AI生成的毒舌风格介绍，内容会根据Wikipedia数据动态生成，加入一些趣味性解读但保持关键事实的准确性。',
    image: 'https://via.placeholder.com/800x400',
    songs: [
      { id: '1', title: '热门歌曲 1', album: '专辑1', duration: '3:45' },
      { id: '2', title: '热门歌曲 2', album: '专辑2', duration: '4:12' },
      { id: '3', title: '热门歌曲 3', album: '专辑1', duration: '3:28' },
    ],
    similarArtists: [
      { id: '101', name: '相似艺术家 1', image: 'https://via.placeholder.com/300x300' },
      { id: '102', name: '相似艺术家 2', image: 'https://via.placeholder.com/300x300' },
    ],
    performanceTime: '2025-07-26T18:30:00',
    stage: 'Green Stage',
  };

  return (
    <main className="min-h-screen pb-20">
      {/* Hero section with artist image */}
      <section className="relative h-[50vh] min-h-[400px]">
        <div className="absolute inset-0 bg-cover bg-center" style={{ backgroundImage: `url(${artist.image})` }} />
        <div className="absolute inset-0 bg-gradient-to-t from-deep-space via-deep-space/70 to-transparent" />
        
        <div className="absolute bottom-0 left-0 w-full p-6 md:p-10">
          <div className="container mx-auto">
            <Link href="/" className="inline-block mb-6 text-white hover:text-neon-blue transition-colors">
              &larr; 返回首页
            </Link>
            <h1 className="font-display text-4xl md:text-6xl text-white mb-4">
              {artist.name}
            </h1>
            <div className="flex items-center space-x-4 text-sm text-gray-300">
              <span className="px-2 py-1 rounded bg-neon-purple/30 border border-neon-purple/50">
                {new Date(artist.performanceTime).toLocaleDateString('zh-CN', { month: 'long', day: 'numeric' })}
              </span>
              <span className="px-2 py-1 rounded bg-neon-green/30 border border-neon-green/50">
                {artist.stage}
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* Content section */}
      <section className="container mx-auto px-4 -mt-10">
        <div className="glass-panel p-6 md:p-8">
          {/* Tabs */}
          <div className="flex border-b border-white/10 mb-6 overflow-x-auto scrollbar-hide">
            {tabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-2 font-medium transition-colors ${
                  activeTab === tab.id 
                    ? 'text-neon-blue border-b-2 border-neon-blue' 
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                {tab.label}
              </button>
            ))}
            <div className="flex-1 border-b border-white/10 -mb-px"></div>
          </div>

          {/* Tab content */}
          <div className="min-h-[400px]">
            {activeTab === 'info' && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.3 }}
              >
                <h2 className="font-display text-2xl mb-4 text-white">艺术家介绍</h2>
                <div className="text-gray-300 space-y-4">
                  <p>{artist.description}</p>
                  <p>这里将显示更多详细内容，包括艺术家生平、风格特点等，来源于Wikipedia并经过AI改写...</p>
                </div>
                
                <div className="mt-8">
                  <h3 className="font-display text-xl mb-4 text-white">演出信息</h3>
                  <div className="cyber-card p-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <p className="text-gray-400">日期 & 时间</p>
                        <p className="text-white">
                          {new Date(artist.performanceTime).toLocaleString('zh-CN', {
                            year: 'numeric',
                            month: 'long',
                            day: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit'
                          })}
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-400">舞台</p>
                        <p className="text-white">{artist.stage}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}

            {activeTab === 'songs' && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.3 }}
              >
                <h2 className="font-display text-2xl mb-6 text-white">热门歌曲</h2>
                <div className="space-y-2">
                  {artist.songs.map((song, index) => (
                    <div 
                      key={song.id}
                      className="cyber-card p-4 flex items-center justify-between group hover:bg-deep-space/90"
                    >
                      <div className="flex items-center">
                        <div className="w-8 text-center text-gray-400 mr-4">{index + 1}</div>
                        <div>
                          <h3 className="text-white group-hover:text-neon-blue transition-colors">
                            {song.title}
                          </h3>
                          <p className="text-sm text-gray-400">{song.album}</p>
                        </div>
                      </div>
                      <div className="text-gray-400">{song.duration}</div>
                    </div>
                  ))}
                </div>
                <div className="mt-6 text-center">
                  <button className="cyber-button">
                    在 Spotify 上播放
                  </button>
                </div>
              </motion.div>
            )}

            {activeTab === 'similar' && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.3 }}
              >
                <h2 className="font-display text-2xl mb-6 text-white">相似艺术家</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {artist.similarArtists.map(similarArtist => (
                    <Link key={similarArtist.id} href={`/artists/${similarArtist.id}`}>
                      <div className="cyber-card p-4 flex items-center space-x-4 group hover:bg-deep-space/90">
                        <div 
                          className="w-16 h-16 rounded-full bg-cover bg-center"
                          style={{ backgroundImage: `url(${similarArtist.image})` }}
                        />
                        <h3 className="text-white group-hover:text-neon-blue transition-colors">
                          {similarArtist.name}
                        </h3>
                      </div>
                    </Link>
                  ))}
                </div>
              </motion.div>
            )}
          </div>
        </div>
      </section>
    </main>
  );
} 