'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { ArrowLeft, ExternalLink, Play, Pause, Volume2, Music, Sparkles } from 'lucide-react';
//import { 
//  getArtistDatabase, 
//  getArtistSpotify, 
//  getArtistTopTracks,
//  generateArtistDescriptionStream,
//  getCachedAIDescription
//} from '@/utils/api';

interface ArtistData {
  database: any;
  spotify: any;
  topTracks: any;
  aiDescription: any;
}

interface LoadingStates {
  database: boolean;
  spotify: boolean;
  topTracks: boolean;
  aiDescription: boolean;
}

interface TrackPlayerProps {
  track: any;
  isPlaying: boolean;
  onPlay: () => void;
  onPause: () => void;
}

const TrackPlayer: React.FC<TrackPlayerProps> = ({ track, isPlaying, onPlay, onPause }) => {
  const [audio, setAudio] = useState<HTMLAudioElement | null>(null);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);

  useEffect(() => {
    if (track.preview_url && !audio) {
      const audioElement = new Audio(track.preview_url);
      setAudio(audioElement);

      audioElement.addEventListener('loadedmetadata', () => {
        setDuration(audioElement.duration);
      });

      audioElement.addEventListener('timeupdate', () => {
        setCurrentTime(audioElement.currentTime);
      });

      audioElement.addEventListener('ended', () => {
        onPause();
      });
    }
  }, [track.preview_url, audio, onPause]);

  useEffect(() => {
    if (audio) {
      if (isPlaying) {
        audio.play();
      } else {
        audio.pause();
      }
    }
  }, [isPlaying, audio]);

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  const progressPercentage = duration > 0 ? (currentTime / duration) * 100 : 0;

  return (
    <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
      <button
        onClick={isPlaying ? onPause : onPlay}
        className="flex items-center justify-center w-10 h-10 bg-green-500 text-white rounded-full hover:bg-green-600 transition-colors"
        disabled={!track.preview_url}
      >
        {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5 ml-0.5" />}
      </button>
      
      <div className="flex-1">
        <div className="flex items-center justify-between text-sm text-gray-600 mb-1">
          <span>{formatTime(currentTime)}</span>
          <span>{formatTime(duration)}</span>
        </div>
        <div className="w-full bg-gray-300 rounded-full h-2">
          <div 
            className="bg-green-500 h-2 rounded-full transition-all duration-100"
            style={{ width: `${progressPercentage}%` }}
          ></div>
        </div>
      </div>
      
      <Volume2 className="w-5 h-5 text-gray-400" />
    </div>
  );
};

export default function ArtistProfilePage() {
  const params = useParams();
  const router = useRouter();
  const artistName = decodeURIComponent(params.id as string);
  
  const [artistData, setArtistData] = useState<ArtistData>({
    database: null,
    spotify: null,
    topTracks: null,
    aiDescription: null
  });
  
  // 分别管理每个部分的加载状态
  const [loadingStates, setLoadingStates] = useState<LoadingStates>({
    database: true,
    spotify: true,
    topTracks: true,
    aiDescription: false
  });
  
  const [error, setError] = useState<string | null>(null);
  
  // AI 描述流式状态
  const [aiDescriptionText, setAiDescriptionText] = useState<string>('');
  const [aiDescriptionLoading, setAiDescriptionLoading] = useState(false);
  const [aiDescriptionComplete, setAiDescriptionComplete] = useState(false);

  // 播放状态管理
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

  // 处理Spotify Playlist按钮点击
  const handleSpotifyPlaylistClick = () => {
    if (artistData.spotify?.success && artistData.spotify.data.external_urls?.spotify) {
      // 如果有Spotify数据，跳转到艺术家的Spotify主页
      window.open(artistData.spotify.data.external_urls.spotify, '_blank');
    } else {
      // 如果没有Spotify数据，使用艺术家名称搜索
      const searchQuery = encodeURIComponent(artistName);
      window.open(`https://open.spotify.com/search/${searchQuery}`, '_blank');
    }
  };

  // 处理AI描述的逻辑
// 处理AI描述的逻辑 - 纯展示，不生成
const handleAIDescription = async (databaseResult: any) => {
  console.log('🔍 检查数据库中的AI描述');
  console.log('📝 ai_description:', databaseResult?.ai_description);
  
  // 只检查数据库中是否有 ai_description，有就显示，没有就不显示
  if (databaseResult?.ai_description && databaseResult.ai_description.trim()) {
    console.log('✅ 数据库中有AI描述，直接显示');
    setAiDescriptionText(databaseResult.ai_description);
    setAiDescriptionComplete(true);
    setArtistData(prev => ({
      ...prev,
      aiDescription: {
        success: true,
        data: {
          sassy_description: databaseResult.ai_description,
          style_metrics: { humor_level: 8, sarcasm_level: 8, fact_accuracy: 0.9 },
          generated_at: databaseResult.updated_at,
          model_used: 'database',
          tokens_used: 0,
          original_content: databaseResult.wiki_extract?.substring(0, 200) + '...' || ''
        }
      }
    }));
  } else {
    console.log('⚠️ 数据库中没有AI描述');
    // 不做任何事，不显示AI描述区域
  }
  
  // 设置loading状态为完成
  setLoadingStates(prev => ({ ...prev, aiDescription: false }));
};

  useEffect(() => {
    if (!artistName) return;

    const loadData = async () => {
      // 1. 优先加载数据库数据（包含基本信息和可能的AI描述）
      try {
        const databaseResult = await getArtistDatabase(artistName);
        setArtistData(prev => ({ ...prev, database: databaseResult }));
        
        // 处理AI描述逻辑
        if (databaseResult?.success && databaseResult.data) {
          await handleAIDescription(databaseResult.data);
        }
      } catch (error) {
        console.error('Database API 失败:', error);
      } finally {
        setLoadingStates(prev => ({ ...prev, database: false }));
      }

      // 2. 加载 Spotify 数据（通常最快）
      try {
        const spotifyResult = await getArtistSpotify(artistName);
        setArtistData(prev => ({ ...prev, spotify: spotifyResult }));
      } catch (error) {
        console.error('Spotify API 失败:', error);
      } finally {
        setLoadingStates(prev => ({ ...prev, spotify: false }));
      }

      // 3. 加载 Top Tracks 数据
      try {
        const topTracksResult = await getArtistTopTracks(artistName);
        setArtistData(prev => ({ ...prev, topTracks: topTracksResult }));
      } catch (error) {
        console.error('Top Tracks API 失败:', error);
      } finally {
        setLoadingStates(prev => ({ ...prev, topTracks: false }));
      }
    };

    loadData();
  }, [artistName]);

  // 页面立即显示，不等待任何 API
  const displayName = artistData.database?.data?.name || 
                     (artistData.spotify?.success ? artistData.spotify.data.name : artistName);
  
  const artistImage = (artistData.database?.data?.image_url) ||
                     (artistData.spotify?.success && artistData.spotify.data.images.length > 0
                       ? artistData.spotify.data.images[0].url
                       : 'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?auto=format&fit=facearea&w=256&q=80');

  const getWikipediaUrl = (title: string) => {
    const wikiTitle = artistData.database?.data?.wiki_data?.title || title;
    return `https://en.wikipedia.org/wiki/${encodeURIComponent(wikiTitle)}`;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-pink-50">
      {/* 返回按钮 */}
      <div className="sticky top-0 z-10 bg-white/80 backdrop-blur-md border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 py-3">
          <button
            onClick={() => router.back()}
            className="flex items-center text-gray-600 hover:text-gray-900 transition-colors"
          >
            <ArrowLeft className="w-5 h-5 mr-2" />
            返回
          </button>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* 艺术家头部信息 */}
        <div className="bg-white rounded-2xl shadow-lg overflow-hidden mb-8">
          <div className="relative h-64 bg-gradient-to-r from-purple-500 to-pink-500">
            <img
              src={artistImage}
              alt={displayName}
              className="absolute inset-0 w-full h-full object-cover mix-blend-overlay"
            />
            <div className="absolute inset-0 bg-black/20"></div>
            <div className="absolute bottom-6 left-6 text-white">
              <h1 className="text-4xl font-bold mb-2">{displayName}</h1>
              {artistData.spotify?.success && (
                <div className="flex items-center space-x-4 text-white/90">
                  <span className="flex items-center">
                    <Music className="w-4 h-4 mr-1" />
                    {artistData.spotify.data.followers?.total?.toLocaleString()} 关注者
                  </span>
                  <span>流行度: {artistData.spotify.data.popularity}/100</span>
                </div>
              )}
            </div>
          </div>

          {/* 基本信息和操作按钮 */}
          <div className="p-6">
            <div className="flex flex-wrap items-center justify-between mb-6">
              <div className="flex flex-wrap gap-2 mb-4 sm:mb-0">
                {artistData.spotify?.success && artistData.spotify.data.genres?.map((genre: string, index: number) => (
                  <span
                    key={index}
                    className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm font-medium"
                  >
                    {genre}
                  </span>
                ))}
              </div>
              
              <div className="flex space-x-3">
                <button
                  onClick={handleSpotifyPlaylistClick}
                  className="flex items-center px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
                >
                  <ExternalLink className="w-4 h-4 mr-2" />
                  Spotify
                </button>
                
                {artistData.database?.data?.wiki_data?.title && (
                  <a
                    href={getWikipediaUrl(artistData.database.data.wiki_data.title)}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
                  >
                    <ExternalLink className="w-4 h-4 mr-2" />
                    Wikipedia
                  </a>
                )}
              </div>
            </div>

            {/* Wikipedia 描述 */}
            {artistData.database?.data?.wiki_extract && (
              <div className="mb-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-3">艺术家简介</h3>
                <p className="text-gray-700 leading-relaxed">
                  {artistData.database.data.wiki_extract}
                </p>
              </div>
            )}
          </div>
        </div>

        {/* AI 毒舌描述区域 */}
{/* AI 毒舌描述区域 - 只在有数据时显示 */}
{aiDescriptionText && (
  <div className="mb-8">
    <div className="bg-gradient-to-r from-pink-50 to-purple-50 rounded-xl p-6 shadow-md border border-pink-100">
      <div className="flex items-center mb-4">
        <div className="h-6 w-6 text-pink-600 mr-3">
          <svg viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2a2 2 0 012 2c0 .74-.4 1.39-1 1.73V7h1a7 7 0 017 7h1a1 1 0 011 1v3a1 1 0 01-1 1h-1v1a2 2 0 01-2 2H5a2 2 0 01-2-2v-1H2a1 1 0 01-1-1v-3a1 1 0 011-1h1a7 7 0 017-7h1V5.73c-.6-.34-1-.99-1-1.73a2 2 0 012-2z"/>
          </svg>
        </div>
        <h3 className="text-xl font-semibold text-pink-700">
          Toxic AI Intro
          <span className="ml-2 text-sm text-pink-500">来自数据库</span>
        </h3>
      </div>
      
      <div className="prose prose-pink max-w-none">
        <p className="text-gray-800 leading-relaxed whitespace-pre-wrap">
          {aiDescriptionText}
        </p>
      </div>
    </div>
  </div>
)}
        {/* 热门歌曲 */}
        {artistData.topTracks?.success && artistData.topTracks.data.tracks.length > 0 && (
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="text-xl font-semibold text-gray-900 mb-6 flex items-center">
              <Sparkles className="w-5 h-5 mr-2 text-yellow-500" />
              热门歌曲
            </h3>
            <div className="space-y-4">
              {artistData.topTracks.data.tracks.slice(0, 5).map((track: any, index: number) => (
                <div key={track.id} className="flex items-center space-x-4 p-3 rounded-lg hover:bg-gray-50 transition-colors">
                  <div className="flex-shrink-0 w-8 text-center">
                    <span className="text-lg font-semibold text-gray-500">{index + 1}</span>
                  </div>
                  
                  <div className="flex-shrink-0">
                    <img
                      src={track.album.images[0]?.url || '/default-album.png'}
                      alt={track.album.name}
                      className="w-12 h-12 rounded-md object-cover"
                    />
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <h4 className="font-medium text-gray-900 truncate">{track.name}</h4>
                    <p className="text-sm text-gray-500 truncate">{track.album.name}</p>
                  </div>
                  
                  <div className="flex-shrink-0 text-sm text-gray-500">
                    {Math.floor(track.duration_ms / 60000)}:{Math.floor((track.duration_ms % 60000) / 1000).toString().padStart(2, '0')}
                  </div>
                  
                  {track.preview_url && (
                    <div className="flex-shrink-0">
                      <TrackPlayer
                        track={track}
                        isPlaying={currentPlayingTrack === track.id}
                        onPlay={() => handlePlay(track.id)}
                        onPause={handlePause}
                      />
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 加载状态指示器 */}
        {(loadingStates.database || loadingStates.spotify || loadingStates.topTracks) && (
          <div className="mt-8 bg-white rounded-xl shadow-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">加载中...</h3>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">数据库信息</span>
                <div className={`w-4 h-4 rounded-full ${loadingStates.database ? 'bg-yellow-400 animate-pulse' : 'bg-green-400'}`}></div>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Spotify 数据</span>
                <div className={`w-4 h-4 rounded-full ${loadingStates.spotify ? 'bg-yellow-400 animate-pulse' : 'bg-green-400'}`}></div>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">热门歌曲</span>
                <div className={`w-4 h-4 rounded-full ${loadingStates.topTracks ? 'bg-yellow-400 animate-pulse' : 'bg-green-400'}`}></div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}