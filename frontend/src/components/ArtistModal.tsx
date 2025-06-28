'use client';

import { useEffect, useState } from 'react';
import { generateArtistDescriptionStream } from '../utils/api';

// 数据库艺术家类型定义
interface DatabaseArtist {
  id: string;
  name: string;
  description: string;
  image_url?: string;
  wiki_data?: any;
  wiki_extract?: string;
  spotify_id?: string;
  genres?: string[];
  is_fuji_rock_artist: boolean;
  created_at: string;
  updated_at: string;
}

// 组件 props 类型定义 - 简化为只需要艺术家名称
interface ArtistModalProps {
  artist: { name: string } | null;
  isOpen: boolean;
  onClose: () => void;
}

// API 响应类型
interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

export default function ArtistModal({ artist, isOpen, onClose }: ArtistModalProps) {
  // 状态管理
  const [databaseArtist, setDatabaseArtist] = useState<DatabaseArtist | null>(null);
  const [wikiData, setWikiData] = useState<any>(null);
  const [spotifyData, setSpotifyData] = useState<any>(null);
  const [toxicIntro, setToxicIntro] = useState<string>('');
  
  // 加载状态
  const [isLoadingDatabase, setIsLoadingDatabase] = useState(false);
  const [isLoadingWiki, setIsLoadingWiki] = useState(false);
  const [isLoadingSpotify, setIsLoadingSpotify] = useState(false);
  const [isGeneratingAI, setIsGeneratingAI] = useState(false);
  const [streamContent, setStreamContent] = useState<string>('');
  
  // 错误状态
  const [errors, setErrors] = useState<{
    database?: string;
    wiki?: string;
    spotify?: string;
    ai?: string;
  }>({});

  // 在组件打开时获取数据
  useEffect(() => {
    if (artist && isOpen) {
      console.log('🎵 ArtistModal 打开，开始获取数据:', artist.name);
      fetchArtistData(artist.name);
    }
  }, [artist, isOpen]);

  // 重置状态当弹窗关闭时
  useEffect(() => {
    if (!isOpen) {
      resetStates();
    }
  }, [isOpen]);

  // 重置所有状态
  const resetStates = () => {
    setDatabaseArtist(null);
    setWikiData(null);
    setSpotifyData(null);
    setToxicIntro('');
    setStreamContent('');
    setErrors({});
  };

  // 主要数据获取函数 - 实现方案A的核心逻辑
  const fetchArtistData = async (artistName: string) => {
    console.log('🔍 开始获取艺术家数据:', artistName);
    
    // 1. 优先查询数据库
    const dbArtist = await fetchFromDatabase(artistName);
    
    if (dbArtist) {
      console.log('✅ 数据库中找到艺术家数据');
      setDatabaseArtist(dbArtist);
      
      // 如果数据库有 wiki_extract，使用数据库数据
      if (dbArtist.wiki_extract) {
        setWikiData({ extract: dbArtist.wiki_extract });
      }
      
      // 如果数据库有 spotify_id，我们可以获取更多 Spotify 数据
      if (dbArtist.spotify_id) {
        fetchSpotifyById(dbArtist.spotify_id);
      }
    } else {
      console.log('❌ 数据库中未找到艺术家，尝试外部 API');
      // 2. 数据库没有数据，调用外部 API
      await fetchFromExternalAPIs(artistName);
    }
  };

  // 从数据库获取艺术家信息
  const fetchFromDatabase = async (artistName: string): Promise<DatabaseArtist | null> => {
    setIsLoadingDatabase(true);
    setErrors(prev => ({ ...prev, database: undefined }));

    try {
      console.log('📊 查询数据库:', artistName);
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/database/artists/by-name/${encodeURIComponent(artistName)}`
      );

      if (response.ok) {
        const result: ApiResponse<DatabaseArtist> = await response.json();
        if (result.success && result.data) {
          console.log('✅ 数据库查询成功:', result.data);
          return result.data;
        }
      } else if (response.status === 404) {
        console.log('📊 数据库中未找到艺术家');
        return null;
      } else {
        throw new Error(`数据库查询失败: ${response.status}`);
      }
    } catch (error) {
      console.error('❌ 数据库查询错误:', error);
      setErrors(prev => ({ ...prev, database: '数据库查询失败' }));
    } finally {
      setIsLoadingDatabase(false);
    }

    return null;
  };

  // 从外部 API 获取数据
  const fetchFromExternalAPIs = async (artistName: string) => {
    console.log('🌐 开始调用外部 API');
    
    // 并行调用 Wikipedia 和 Spotify API
    const [wikiResult, spotifyResult] = await Promise.allSettled([
      fetchWikipediaData(artistName),
      fetchSpotifyData(artistName)
    ]);

    // 处理结果
    const wikiData = wikiResult.status === 'fulfilled' ? wikiResult.value : null;
    const spotifyData = spotifyResult.status === 'fulfilled' ? spotifyResult.value : null;

    // 如果获取到了数据，存储到数据库
    if (wikiData || spotifyData) {
      await saveToDatabase(artistName, wikiData, spotifyData);
    }
  };

  // 获取 Wikipedia 数据
  const fetchWikipediaData = async (artistName: string) => {
    setIsLoadingWiki(true);
    setErrors(prev => ({ ...prev, wiki: undefined }));

    try {
      console.log('📚 调用 Wikipedia API');
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/wikipedia/artists/${encodeURIComponent(artistName)}?language=zh`
      );

      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          console.log('✅ Wikipedia 数据获取成功');
          setWikiData(result.data);
          return result.data;
        }
      }
      
      // 尝试英文版本
      console.log('🔄 尝试英文 Wikipedia');
      const enResponse = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/wikipedia/artists/${encodeURIComponent(artistName)}?language=en`
      );
      
      if (enResponse.ok) {
        const enResult = await enResponse.json();
        if (enResult.success) {
          console.log('✅ 英文 Wikipedia 数据获取成功');
          setWikiData(enResult.data);
          return enResult.data;
        }
      }

      throw new Error('Wikipedia 数据获取失败');
    } catch (error) {
      console.error('❌ Wikipedia API 错误:', error);
      setErrors(prev => ({ ...prev, wiki: 'Wikipedia 信息获取失败' }));
      return null;
    } finally {
      setIsLoadingWiki(false);
    }
  };

  // 获取 Spotify 数据
  const fetchSpotifyData = async (artistName: string) => {
    setIsLoadingSpotify(true);
    setErrors(prev => ({ ...prev, spotify: undefined }));

    try {
      console.log('🎵 调用 Spotify API');
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/spotify/artist-by-name/${encodeURIComponent(artistName)}`
      );

      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          console.log('✅ Spotify 数据获取成功');
          setSpotifyData(result.data);
          return result.data;
        }
      }

      throw new Error('Spotify 数据获取失败');
    } catch (error) {
      console.error('❌ Spotify API 错误:', error);
      setErrors(prev => ({ ...prev, spotify: 'Spotify 信息获取失败' }));
      return null;
    } finally {
      setIsLoadingSpotify(false);
    }
  };

  // 根据 Spotify ID 获取数据
  const fetchSpotifyById = async (spotifyId: string) => {
    setIsLoadingSpotify(true);
    
    try {
      console.log('🎵 根据 Spotify ID 获取数据:', spotifyId);
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/spotify/artists/${spotifyId}`
      );

      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          console.log('✅ Spotify ID 数据获取成功');
          setSpotifyData(result.data);
        }
      }
    } catch (error) {
      console.error('❌ Spotify ID API 错误:', error);
    } finally {
      setIsLoadingSpotify(false);
    }
  };

  // 保存数据到数据库
  const saveToDatabase = async (artistName: string, wikiData: any, spotifyData: any) => {
    try {
      console.log('💾 保存数据到数据库');
      
      const artistData = {
        name: artistName,
        description: wikiData?.extract?.substring(0, 200) || `${artistName} 是一位在 Fuji Rock Festival 2025 上表演的艺术家。`,
        wiki_data: wikiData,
        wiki_extract: wikiData?.extract,
        spotify_id: spotifyData?.id,
        genres: spotifyData?.genres || [],
        image_url: spotifyData?.images?.[0]?.url,
        is_fuji_rock_artist: true
      };

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/database/artists`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(artistData)
        }
      );

      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          console.log('✅ 数据保存到数据库成功');
          setDatabaseArtist(result.data);
        }
      } else {
        console.log('⚠️ 数据库保存失败，可能艺术家已存在');
      }
    } catch (error) {
      console.error('❌ 保存到数据库错误:', error);
    }
  };

  // 生成毒舌介绍
  const generateToxicIntro = async () => {
    if (!artist) return;
    
    setIsGeneratingAI(true);
    setStreamContent('');
    setToxicIntro('');
    setErrors(prev => ({ ...prev, ai: undefined }));

    // 使用可用的内容作为 AI 输入
    const contentForAI = wikiData?.extract || 
                        databaseArtist?.wiki_extract || 
                        databaseArtist?.description || 
                        `${artist.name} 是一位艺术家`;

    try {
      await generateArtistDescriptionStream(
        artist.name,
        contentForAI,
        7, // 毒舌程度
        // onUpdate 回调
        (content: string) => {
          setStreamContent(content);
        },
        // onComplete 回调
        (data: any) => {
          setToxicIntro(data.content);
          setStreamContent('');
          setIsGeneratingAI(false);
        },
        // onError 回调
        (error: string) => {
          console.error('AI 生成失败:', error);
          setErrors(prev => ({ ...prev, ai: 'AI 生成失败' }));
          setToxicIntro('😈 准备好被音乐摧毁吧！这位艺术家的作品绝对会让你重新定义什么叫"与众不同"！🔥');
          setStreamContent('');
          setIsGeneratingAI(false);
        }
      );
    } catch (error) {
      console.error('AI 生成错误:', error);
      setErrors(prev => ({ ...prev, ai: 'AI 生成错误' }));
      setToxicIntro('😈 准备好被音乐摧毁吧！这位艺术家的作品绝对会让你重新定义什么叫"与众不同"！🔥');
      setIsGeneratingAI(false);
    }
  };

  // 处理 ESC 键关闭弹窗
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  if (!isOpen || !artist) return null;

 
  // 获取显示用的数据
const displayData = {
  name: artist.name,
  genres: spotifyData?.genres || databaseArtist?.genres || [],
  image: spotifyData?.images?.[0]?.url || databaseArtist?.image_url,
  wikiContent: wikiData?.extract || databaseArtist?.wiki_extract,
  spotifyId: spotifyData?.id || databaseArtist?.spotify_id,
  // 添加数据源判断
  hasWikiData: !!(wikiData?.extract || databaseArtist?.wiki_extract),
  dataSource: databaseArtist?.wiki_data?.source || 'wikipedia' // 新增：数据来源标识
};

  const spotifyUrl = displayData.spotifyId 
    ? `https://open.spotify.com/artist/${displayData.spotifyId}`
    : `https://open.spotify.com/search/${encodeURIComponent(artist.name)}`;

  return (
    <div 
      className="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-50 p-4"
      onClick={onClose}
    >
      <div 
        className="bg-white rounded-xl p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto relative shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        {/* 关闭按钮 */}
        <button 
          onClick={onClose}
          className="absolute top-4 right-4 w-8 h-8 bg-gray-100 hover:bg-gray-200 rounded-full flex items-center justify-center text-gray-500 hover:text-gray-700 text-xl transition-colors z-10"
          aria-label="关闭弹窗"
        >
          ×
        </button>

        {/* 艺术家头部信息 */}
        <div className="mb-6 pr-10">
          <h2 className="text-3xl font-bold mb-3 text-gray-800">{displayData.name}</h2>
          
          {/* 流派标签 */}
          {displayData.genres.length > 0 && (
            <div className="flex flex-wrap gap-2 mb-4">
              {displayData.genres.slice(0, 5).map((genre: string, index: number) => (
                <span 
                  key={index}
                  className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium"
                >
                  {genre}
                </span>
              ))}
            </div>
          )}

          {/* 加载状态指示器 */}
          {(isLoadingDatabase || isLoadingWiki || isLoadingSpotify) && (
            <div className="flex items-center gap-2 text-sm text-gray-500 mb-3">
              <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
              正在获取艺术家信息...
            </div>
          )}
        </div>

        {/* 艺术家图片 */}
        {displayData.image && (
          <div className="mb-6 flex justify-center">
            <img 
              src={displayData.image} 
              alt={displayData.name}
              className="w-48 h-48 rounded-lg object-cover shadow-lg"
            />
          </div>
        )}


{/* Wikipedia/Spotify 信息部分 */}
<div className="mb-6">
  <div className="flex items-center mb-3">
    <div className="w-6 h-6 bg-gray-100 rounded-full flex items-center justify-center mr-3">
      {isLoadingWiki ? (
        <div className="w-4 h-4 border-2 border-gray-600 border-t-transparent rounded-full animate-spin"></div>
      ) : (
        <span className="text-gray-600 font-bold text-sm">
          {displayData.dataSource === 'spotify' ? 'S' : 'W'}
        </span>
      )}
    </div>
    <h3 className="text-xl font-semibold text-gray-800">
      {displayData.dataSource === 'spotify' ? 'Artist Info' : 'About This Artist'}
      {isLoadingWiki && <span className="ml-2 text-sm text-gray-500">加载中...</span>}
    </h3>
  </div>
  <div className="bg-gray-50 rounded-lg p-4 border border-gray-100">
    {isLoadingWiki ? (
      <div className="text-gray-500 text-center py-4">
        <div className="w-6 h-6 border-2 border-gray-400 border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
        正在获取{displayData.dataSource === 'spotify' ? 'Spotify' : 'Wikipedia'}信息...
      </div>
    ) : errors.wiki ? (
      <p className="text-red-600 leading-relaxed">
        ❌ {errors.wiki}
      </p>
    ) : displayData.wikiContent ? (
      <p className="text-gray-700 leading-relaxed">
        {displayData.wikiContent}
      </p>
    ) : (
      <p className="text-gray-500 leading-relaxed">
        暂无{displayData.dataSource === 'spotify' ? 'Spotify' : 'Wikipedia'}信息
      </p>
    )}
  </div>
</div>

        {/* Toxic AI 介绍部分 */}
        <div className="mb-6">
          <div className="flex items-center mb-3">
            <div className="w-6 h-6 bg-pink-100 rounded-full flex items-center justify-center mr-3">
              {isGeneratingAI ? (
                <div className="w-4 h-4 border-2 border-pink-600 border-t-transparent rounded-full animate-spin"></div>
              ) : (
                <span className="text-pink-600">😈</span>
              )}
            </div>
            <h3 className="text-xl font-semibold text-pink-700">
            My Take on Them 😈
              {isGeneratingAI && (
                <span className="ml-2 text-sm text-pink-500">正在生成中...</span>
              )}
            </h3>
          </div>
          <div className="bg-gradient-to-r from-pink-50 to-purple-50 rounded-lg p-4 border border-pink-100">
            {errors.ai ? (
              <p className="text-red-600 leading-relaxed">
                ❌ {errors.ai}
              </p>
            ) : (
              <p className="text-pink-800 leading-relaxed">
                {isGeneratingAI ? (
                  streamContent || '正在生成毒舌介绍...'
                ) : (
                  toxicIntro || '点击生成按钮获取毒舌介绍...'
                )}
              </p>
            )}
            {!isGeneratingAI && !toxicIntro && !errors.ai && (
              <button
                onClick={generateToxicIntro}
                className="mt-3 bg-pink-500 hover:bg-pink-600 text-white px-4 py-2 rounded-lg text-sm transition-colors"
                disabled={isLoadingWiki || isLoadingDatabase}
              >
                {(isLoadingWiki || isLoadingDatabase) ? '等待数据加载...' : '生成毒舌介绍'}
              </button>
            )}
          </div>
        </div>

        {/* Spotify 链接部分 */}
        <div className="flex justify-center">
          <a
            href={spotifyUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="bg-green-500 hover:bg-green-600 text-white px-6 py-3 rounded-lg flex items-center gap-2 transition-colors font-medium shadow-lg hover:shadow-xl"
          >
            <span className="text-lg">🎧</span>
            <span>在 Spotify 上{displayData.spotifyId ? '收听' : '搜索'}</span>
          </a>
        </div>

        {/* 数据来源指示器 */}
        <div className="mt-4 text-xs text-gray-500 text-center">
          数据来源: 
          {databaseArtist && <span className="ml-1 text-green-600">✅ 数据库</span>}
          {wikiData && <span className="ml-1 text-blue-600">✅ Wikipedia</span>}
          {spotifyData && <span className="ml-1 text-green-600">✅ Spotify</span>}
        </div>

        {/* 调试信息（仅开发环境显示） */}
        {process.env.NODE_ENV === 'development' && (
          <div className="mt-4 p-3 bg-gray-100 rounded text-xs text-gray-600">
            <p>🔧 调试信息:</p>
            <p>数据库: {databaseArtist ? '✅ 已加载' : '❌ 未加载'}</p>
            <p>Wiki: {wikiData ? '✅ 已加载' : '❌ 未加载'}</p>
            <p>Spotify: {spotifyData ? '✅ 已加载' : '❌ 未加载'}</p>
            {errors.database && <p className="text-red-600">DB错误: {errors.database}</p>}
            {errors.wiki && <p className="text-red-600">Wiki错误: {errors.wiki}</p>}
            {errors.spotify && <p className="text-red-600">Spotify错误: {errors.spotify}</p>}
          </div>
        )}
      </div>
    </div>
  );
}