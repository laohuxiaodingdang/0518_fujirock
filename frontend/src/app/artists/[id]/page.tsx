'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Image from 'next/image';
import TrackPlayer from '@/components/TrackPlayer';
import { 
  getArtistSpotify, 
  getArtistTopTracks, 
  generateArtistDescriptionStream,
  SpotifyArtistResponse,
  SpotifyTopTracksResponse,
  AIDescriptionResponse
} from '@/utils/api';

// 数据库艺术家数据接口
interface DatabaseArtistData {
  id: string;
  name: string;
  description: string;
  wiki_data: {
    title: string;
    extract: string;
    thumbnail?: {
      source: string;
      width: number;
      height: number;
    };
    categories: string[];
    references: Array<{
      title: string;
      url: string;
    }>;
  };
  wiki_extract: string;
  wiki_last_updated: string;
  spotify_id: string;
  genres: string[];
  is_fuji_rock_artist: boolean;
  created_at: string;
  updated_at: string;
  image_url: string;
}

interface ArtistData {
  database: DatabaseArtistData | null;
  spotify: SpotifyArtistResponse | null;
  topTracks: SpotifyTopTracksResponse | null;
  aiDescription: AIDescriptionResponse | null;
}

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
  const [loadingStates, setLoadingStates] = useState({
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

  // 从数据库获取艺术家信息
  const getArtistFromDatabase = async (name: string): Promise<DatabaseArtistData | null> => {
    try {
      const response = await fetch(`/api/database/artists/search?query=${encodeURIComponent(name)}&limit=1`);
      const data = await response.json();
      
      if (data.success && data.data && data.data.length > 0) {
        return data.data[0];
      }
      return null;
    } catch (error) {
      console.error('Database API 失败:', error);
      return null;
    }
  };

  useEffect(() => {
    if (!artistName) return;

    // 立即开始加载各个部分，不等待
    const loadData = async () => {
      // 1. 加载数据库数据（包含Wikipedia信息）
      try {
        const databaseResult = await getArtistFromDatabase(artistName);
        setArtistData(prev => ({ ...prev, database: databaseResult }));
        
        // 如果有Wikipedia数据，立即开始 AI 描述生成
        if (databaseResult?.wiki_extract) {
          setAiDescriptionLoading(true);
          setAiDescriptionComplete(false);
          setAiDescriptionText('');
          setLoadingStates(prev => ({ ...prev, aiDescription: true }));
          
          try {
            await generateArtistDescriptionStream(
              artistName,
              databaseResult.wiki_extract,
              8,
              // onUpdate: 实时更新
              (content: string) => {
                setAiDescriptionText(content);
              },
              // onComplete: 完成处理
              (data: any) => {
                setAiDescriptionComplete(true);
                setAiDescriptionLoading(false);
                setLoadingStates(prev => ({ ...prev, aiDescription: false }));
                setArtistData(prev => ({
                  ...prev,
                  aiDescription: {
                    success: true,
                    data: {
                      sassy_description: data.content,
                      style_metrics: data.style_metrics || { humor_level: 8, sarcasm_level: 8, fact_accuracy: 0.9 },
                      generated_at: data.generated_at,
                      model_used: data.model_used,
                      tokens_used: data.tokens_used,
                      original_content: databaseResult.wiki_extract.substring(0, 200) + '...'
                    }
                  }
                }));
              },
              // onError: 错误处理
              (error: string) => {
                console.error('AI描述生成失败:', error);
                setAiDescriptionLoading(false);
                setLoadingStates(prev => ({ ...prev, aiDescription: false }));
                setAiDescriptionText('AI 描述生成失败，请稍后重试。');
              }
            );
          } catch (error) {
            console.error('启动AI描述失败:', error);
            setAiDescriptionLoading(false);
            setLoadingStates(prev => ({ ...prev, aiDescription: false }));
            setAiDescriptionText('AI 描述生成失败，请稍后重试。');
          }
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
  const displayName = artistData.database?.name || 
                     (artistData.spotify?.success ? artistData.spotify.data.name : artistName);
  
  const artistImage = (artistData.database?.image_url) ||
                     (artistData.spotify?.success && artistData.spotify.data.images.length > 0
                       ? artistData.spotify.data.images[0].url
                       : 'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?auto=format&fit=facearea&w=256&q=80');

  const getWikipediaUrl = (title: string) => {
    const wikiTitle = artistData.database?.wiki_data?.title || title;
    return `https://en.wikipedia.org/wiki/${encodeURIComponent(wikiTitle)}`;
  };

  if (error && !artistData.database && !artistData.spotify) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-500 text-6xl mb-4">😞</div>
          <h1 className="text-2xl font-bold text-gray-800 mb-2">未找到艺术家</h1>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={() => router.back()}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
          >
            返回
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 返回按钮 */}
      <div className="bg-white px-6 py-4">
        <button
          onClick={() => router.back()}
          className="flex items-center text-gray-600 hover:text-gray-800"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Artist Profile
        </button>
      </div>

      <div className="max-w-4xl mx-auto px-6 py-8">
        {/* 艺术家头部信息 */}
        <div className="bg-white rounded-lg p-8 shadow-sm mb-8">
          <div className="flex items-start gap-6">
            {/* 艺术家头像 */}
            <div className="relative">
              {loadingStates.database && loadingStates.spotify ? (
                <div className="w-[120px] h-[120px] bg-gray-200 rounded-lg animate-pulse flex items-center justify-center">
                  <div className="animate-spin h-8 w-8 border-2 border-gray-400 border-t-transparent rounded-full"></div>
                </div>
              ) : (
                <Image
                  src={artistImage}
                  alt={displayName}
                  width={120}
                  height={120}
                  className="rounded-lg object-cover"
                  onError={(e) => {
                    e.currentTarget.src = 'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?auto=format&fit=facearea&w=256&q=80';
                  }}
                />
              )}
            </div>

            {/* 艺术家信息 */}
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                {loadingStates.database && loadingStates.spotify ? (
                  <div className="h-8 bg-gray-200 rounded w-48 animate-pulse"></div>
                ) : (
                  <>
                    <h1 className="text-3xl font-bold text-gray-800">{displayName}</h1>
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-yellow-500" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                    </svg>
                  </>
                )}
              </div>

              <div className="flex items-center gap-4 text-sm text-gray-600 mb-4">
                <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded">7月26日</span>
                <span className="bg-green-100 text-green-800 px-2 py-1 rounded">Green Stage</span>
                {loadingStates.spotify ? (
                  <div className="h-6 bg-gray-200 rounded w-20 animate-pulse"></div>
                ) : (
                  artistData.spotify?.success && (
                    <span className="bg-purple-100 text-purple-800 px-2 py-1 rounded">
                      {(artistData.spotify.data.followers.total / 1000000).toFixed(1)}M 粉丝
                    </span>
                  )
                )}
              </div>

              {/* 音乐风格标签 - 优先使用数据库数据 */}
              {loadingStates.database && loadingStates.spotify ? (
                <div className="flex gap-2">
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="h-6 bg-gray-200 rounded-full w-16 animate-pulse"></div>
                  ))}
                </div>
              ) : (
                <>
                  {artistData.database?.genres && artistData.database.genres.length > 0 ? (
                    <div className="flex flex-wrap gap-2">
                      {artistData.database.genres.slice(0, 3).map((genre, index) => (
                        <span key={index} className="bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-sm">
                          {genre}
                        </span>
                      ))}
                    </div>
                  ) : (
                    artistData.spotify?.success && artistData.spotify.data.genres.length > 0 && (
                      <div className="flex flex-wrap gap-2">
                        {artistData.spotify.data.genres.slice(0, 3).map((genre, index) => (
                          <span key={index} className="bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-sm">
                            {genre}
                          </span>
                        ))}
                      </div>
                    )
                  )}
                </>
              )}
            </div>
          </div>
        </div>

        <div className="space-y-8">
          {/* Wikipedia 部分 - 使用数据库数据 */}
          {loadingStates.database ? (
            <div className="bg-white rounded-xl p-6 shadow-md border border-gray-100">
              <div className="flex items-center mb-4">
                <div className="h-6 w-6 text-gray-700 mr-3 flex items-center justify-center font-serif font-bold text-lg">
                  <div className="animate-spin h-4 w-4 border-2 border-gray-400 border-t-transparent rounded-full"></div>
                </div>
                <div className="h-6 bg-gray-200 rounded w-32 animate-pulse"></div>
              </div>
              <div className="space-y-2">
                <div className="h-4 bg-gray-200 rounded w-full animate-pulse"></div>
                <div className="h-4 bg-gray-200 rounded w-5/6 animate-pulse"></div>
                <div className="h-4 bg-gray-200 rounded w-4/5 animate-pulse"></div>
              </div>
            </div>
          ) : (
            artistData.database?.wiki_extract && (
              <div className="bg-white rounded-xl p-6 shadow-md border border-gray-100">
                <div className="flex items-center mb-4">
                  <div className="h-6 w-6 text-gray-700 mr-3 flex items-center justify-center font-serif font-bold text-lg">
                    W
                  </div>
                  <h3 className="text-xl font-semibold text-gray-800">
                    <a 
                      href={getWikipediaUrl(artistName)}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:text-blue-800 hover:underline"
                    >
                      Wikipedia
                    </a>
                  </h3>
                </div>
                <p className="text-gray-600 leading-relaxed">
                  {artistData.database.wiki_extract.length > 300 
                    ? `${artistData.database.wiki_extract.substring(0, 300)}...` 
                    : artistData.database.wiki_extract}
                </p>
              </div>
            )
          )}

          {/* Toxic AI Intro 部分 */}
          {(loadingStates.aiDescription || aiDescriptionLoading || aiDescriptionText || artistData.aiDescription?.success) && (
            <div className="bg-gradient-to-r from-pink-50 to-purple-50 rounded-xl p-6 shadow-md border border-pink-100">
              <div className="flex items-center mb-4">
                <div className="h-6 w-6 text-pink-600 mr-3">
                  {aiDescriptionLoading ? (
                    <div className="animate-spin h-5 w-5 border-2 border-pink-600 border-t-transparent rounded-full"></div>
                  ) : (
                    <svg viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                      <path d="M12 2a2 2 0 012 2c0 .74-.4 1.39-1 1.73V7h1a7 7 0 017 7h1a1 1 0 011 1v3a1 1 0 01-1 1h-1v1a2 2 0 01-2 2H5a2 2 0 01-2-2v-1H2a1 1 0 01-1-1v-3a1 1 0 011-1h1a7 7 0 017-7h1V5.73c-.6-.34-1-.99-1-1.73a2 2 0 012-2zM7.5 13A1.5 1.5 0 006 14.5V16h2.5v-1.5a1.5 1.5 0 00-1-1.41zM16.5 13a1.5 1.5 0 00-1 1.41V16H18v-1.59a1.5 1.5 0 00-1.5-1.41zM11 16v2h2v-2h-2z"/>
                    </svg>
                  )}
                </div>
                <h3 className="text-xl font-semibold text-pink-700">
                  Toxic AI Intro
                  {aiDescriptionLoading && (
                    <span className="ml-2 text-sm text-pink-500">正在生成中...</span>
                  )}
                </h3>
              </div>
              <div className="text-pink-800 leading-relaxed">
                {aiDescriptionLoading || aiDescriptionText ? (
                  <div className="relative">
                    <p className="whitespace-pre-wrap">
                      {aiDescriptionText}
                      {aiDescriptionLoading && !aiDescriptionComplete && (
                        <span className="inline-block w-2 h-5 bg-pink-600 animate-pulse ml-1"></span>
                      )}
                    </p>
                  </div>
                ) : artistData.aiDescription?.success ? (
                  <p>{artistData.aiDescription.data.sassy_description}</p>
                ) : null}
              </div>
            </div>
          )}

          {/* Top Tracks 部分 */}
          {loadingStates.topTracks ? (
            <div className="bg-white rounded-lg p-6 shadow-sm">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center">
                  <div className="animate-spin h-5 w-5 border-2 border-gray-400 border-t-transparent rounded-full mr-2"></div>
                  <div className="h-6 bg-gray-200 rounded w-24 animate-pulse"></div>
                </div>
                <div className="h-10 bg-gray-200 rounded w-32 animate-pulse"></div>
              </div>
              <div className="space-y-4">
                {[1, 2, 3, 4, 5].map((i) => (
                  <div key={i} className="flex items-center gap-4 p-3">
                    <div className="h-5 w-5 bg-gray-200 rounded animate-pulse"></div>
                    <div className="flex-1 space-y-2">
                      <div className="h-4 bg-gray-200 rounded w-3/4 animate-pulse"></div>
                      <div className="h-3 bg-gray-200 rounded w-1/2 animate-pulse"></div>
                    </div>
                    <div className="h-4 bg-gray-200 rounded w-12 animate-pulse"></div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            artistData.topTracks?.success && (
              <div className="bg-white rounded-lg p-6 shadow-sm">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-xl font-semibold text-gray-800 flex items-center">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
                    </svg>
                    Top Tracks
                  </h2>
                  <button 
                    onClick={handleSpotifyPlaylistClick}
                    className="flex items-center gap-2 bg-green-500 text-white px-4 py-2 rounded-lg hover:bg-green-600 transition-colors duration-200"
                    title="在Spotify中查看艺术家"
                  >
                    <svg className="h-4 w-4" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S18.66 0 12 0zm5.521 17.34c-.24.359-.66.48-1.021.24-2.82-1.74-6.36-2.101-10.561-1.141-.418.122-.779-.179-.899-.539-.12-.421.18-.78.54-.9 4.56-1.021 8.52-.6 11.64 1.32.42.18.479.659.301 1.02zm1.44-3.3c-.301.42-.841.6-1.262.3-3.239-1.98-8.159-2.58-11.939-1.38-.479.12-1.02-.12-1.14-.6-.12-.48.12-1.021.6-1.141C9.6 9.9 15 10.561 18.72 12.84c.361.181.54.78.241 1.2zm.12-3.36C15.24 8.4 8.82 8.16 5.16 9.301c-.6.179-1.2-.181-1.38-.721-.18-.601.18-1.2.72-1.381 4.26-1.26 11.28-1.02 15.721 1.621.539.3.719 1.02.42 1.56-.299.421-1.02.599-1.559.3z"/>
                    </svg>
                    Spotify Playlist
                  </button>
                </div>

                {/* 预览说明 */}
                <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                  <p className="text-sm text-blue-700 flex items-center">
                    <svg className="h-4 w-4 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                    </svg>
                    <span>
                      <strong>预览说明：</strong>由于Spotify API限制，仅提供30秒预览试听。完整播放请点击Spotify图标跳转到官方应用。
                    </span>
                  </p>
                </div>

                <div className="space-y-4">
                  {artistData.topTracks.data.tracks.slice(0, 5).map((track, index) => (
                    <TrackPlayer
                      key={track.id}
                      track={track}
                      isPlaying={currentPlayingTrack === track.id}
                      onPlay={() => handlePlay(track.id)}
                      onPause={handlePause}
                    />
                  ))}
                </div>
              </div>
            )
          )}
        </div>
      </div>
    </div>
  );
} 