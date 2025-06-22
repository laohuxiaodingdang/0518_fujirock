'use client';

import { useState, useRef, useEffect } from 'react';

interface Track {
  id: string;
  name: string;
  preview_url: string | null;
  duration_ms: number;
  album: {
    name: string;
    images: Array<{
      url: string;
      height: number;
      width: number;
    }>;
  };
  external_urls?: {
    spotify?: string;
  };
  artists?: Array<{
    name: string;
  }>;
}

interface TrackPlayerProps {
  track: Track;
  isPlaying: boolean;
  onPlay: () => void;
  onPause: () => void;
}

interface iTunesPreview {
  preview_url: string;
  source: 'iTunes';
  track_name: string;
  artist_name: string;
}

export default function TrackPlayer({ track, isPlaying, onPlay, onPause }: TrackPlayerProps) {
  const audioRef = useRef<HTMLAudioElement>(null);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [iTunesPreview, setITunesPreview] = useState<iTunesPreview | null>(null);
  const [previewSource, setPreviewSource] = useState<'Spotify' | 'iTunes' | null>(null);
  const [loadingItunes, setLoadingItunes] = useState(false);

  // 获取艺术家名称 - 改进版本
  const getArtistName = () => {
    // 首先尝试从 track.artists 获取
    if (track.artists && track.artists.length > 0) {
      return track.artists[0].name;
    }
    
    // 如果没有 artists 字段，尝试从专辑名称中推断
    // 这是一个备用方案，通常专辑名称可能包含艺术家信息
    const albumName = track.album?.name || '';
    
    // 如果专辑名称包含常见的分隔符，尝试提取艺术家名称
    if (albumName.includes(' - ')) {
      const parts = albumName.split(' - ');
      if (parts.length >= 2) {
        return parts[0].trim();
      }
    }
    
    // 最后的备用方案：从歌曲名称中尝试提取
    // 这种情况下，我们可能需要使用更智能的搜索策略
    return null; // 返回 null 表示无法确定艺术家
  };

  // 从iTunes获取预览 - 改进版本
  const fetchITunesPreview = async (autoPlay: boolean = false) => {
    if (loadingItunes || iTunesPreview) return;
    
    setLoadingItunes(true);
    try {
      const artistName = getArtistName();
      
      // 如果无法获取艺术家名称，尝试只用歌曲名称搜索
      let searchQuery;
      if (artistName) {
        searchQuery = `artist=${encodeURIComponent(artistName)}&track=${encodeURIComponent(track.name)}`;
      } else {
        // 只用歌曲名称搜索，增加搜索结果数量以提高匹配概率
        searchQuery = `artist=${encodeURIComponent('')}&track=${encodeURIComponent(track.name)}`;
      }
      
      const response = await fetch(`/api/itunes/search-track?${searchQuery}&limit=5`);
      
      if (response.ok) {
        const data = await response.json();
        if (data.success && data.data.preview_url) {
          const newPreview = {
            preview_url: data.data.preview_url,
            source: 'iTunes' as const,
            track_name: data.data.track_name,
            artist_name: data.data.artist_name
          };
          setITunesPreview(newPreview);
          
          // 如果需要自动播放，设置预览源并开始播放
          if (autoPlay) {
            setPreviewSource('iTunes');
            // 使用setTimeout确保状态更新完成后再触发播放
            setTimeout(() => {
              onPlay();
            }, 100);
          }
        }
      }
    } catch (error) {
      console.error('Failed to fetch iTunes preview:', error);
    } finally {
      setLoadingItunes(false);
    }
  };

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const updateTime = () => setCurrentTime(audio.currentTime);
    const updateDuration = () => setDuration(audio.duration);
    const handleLoadStart = () => setIsLoading(true);
    const handleCanPlay = () => setIsLoading(false);
    const handleEnded = () => onPause();

    audio.addEventListener('timeupdate', updateTime);
    audio.addEventListener('loadedmetadata', updateDuration);
    audio.addEventListener('loadstart', handleLoadStart);
    audio.addEventListener('canplay', handleCanPlay);
    audio.addEventListener('ended', handleEnded);

    return () => {
      audio.removeEventListener('timeupdate', updateTime);
      audio.removeEventListener('loadedmetadata', updateDuration);
      audio.removeEventListener('loadstart', handleLoadStart);
      audio.removeEventListener('canplay', handleCanPlay);
      audio.removeEventListener('ended', handleEnded);
    };
  }, [onPause]);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    if (isPlaying) {
      audio.play().catch(console.error);
    } else {
      audio.pause();
    }
  }, [isPlaying]);

  const handlePlayPause = async () => {
    // 如果有Spotify预览，直接播放
    if (track.preview_url) {
      setPreviewSource('Spotify');
      if (isPlaying) {
        onPause();
      } else {
        onPlay();
      }
      return;
    }

    // 如果有iTunes预览，播放
    if (iTunesPreview) {
      setPreviewSource('iTunes');
      if (isPlaying) {
        onPause();
      } else {
        onPlay();
      }
      return;
    }

    // 如果没有预览且正在搜索，不做任何操作
    if (loadingItunes) {
      return;
    }

    // 如果没有预览，尝试iTunes搜索
    if (!iTunesPreview && !loadingItunes) {
      try {
        await fetchITunesPreview(true);
        // 搜索完成后会自动开始播放
      } catch (error) {
        console.error('iTunes搜索失败:', error);
      }
      return;
    }

    // 如果都没有预览，跳转到Spotify
    const spotifyUrl = track.external_urls?.spotify;
    if (spotifyUrl) {
      window.open(spotifyUrl, '_blank');
    } else {
      const artistName = getArtistName();
      const searchQuery = artistName 
        ? encodeURIComponent(`${track.name} ${artistName}`)
        : encodeURIComponent(track.name);
      window.open(`https://open.spotify.com/search/${searchQuery}`, '_blank');
    }
  };

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  const progressPercentage = duration > 0 ? (currentTime / duration) * 100 : 0;
  const hasPreview = !!(track.preview_url || iTunesPreview);
  const currentPreviewUrl = track.preview_url || iTunesPreview?.preview_url;

  return (
    <div className="flex items-center gap-4 p-3 hover:bg-gray-50 rounded-lg group">
      {/* 播放按钮 */}
      <button 
        onClick={handlePlayPause}
        className="flex items-center justify-center w-10 h-10 rounded-full bg-gray-100 hover:bg-gray-200 text-gray-600 hover:text-gray-800 transition-all duration-200"
        disabled={isLoading || loadingItunes}
        title={isPlaying ? '暂停' : '播放'}
      >
        {(isLoading || loadingItunes) ? (
          <div className="animate-spin h-4 w-4 border-2 border-current border-t-transparent rounded-full"></div>
        ) : isPlaying ? (
          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="currentColor" viewBox="0 0 24 24">
            <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z"/>
          </svg>
        ) : (
          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 ml-0.5" fill="currentColor" viewBox="0 0 24 24">
            <path d="M8 5v14l11-7z"/>
          </svg>
        )}
      </button>

      {/* 歌曲信息 */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <h3 className="font-medium text-gray-900 truncate">{track.name}</h3>
          {/* 显示预览来源 - 只在播放时显示 */}
          {previewSource && isPlaying && (
            <span className={`text-xs px-2 py-1 rounded-full font-medium ${
              previewSource === 'iTunes' 
                ? 'bg-orange-100 text-orange-700 border border-orange-200' 
                : 'bg-green-100 text-green-700 border border-green-200'
            }`}>
              {previewSource === 'iTunes' ? '🎵 iTunes预览' : '🎧 Spotify'}
            </span>
          )}
          {loadingItunes && (
            <span className="text-xs bg-blue-100 text-blue-600 px-2 py-1 rounded-full border border-blue-200 font-medium">
              🔍 搜索中...
            </span>
          )}
        </div>
        <p className="text-sm text-gray-500 truncate">{track.album.name}</p>
        
        {/* 进度条 - 只在播放时显示 */}
        {isPlaying && hasPreview && (
          <div className="mt-2">
            <div className="w-full bg-gray-200 rounded-full h-1">
              <div 
                className={`h-1 rounded-full transition-all duration-100 ${
                  previewSource === 'iTunes' ? 'bg-orange-500' : 'bg-green-500'
                }`}
                style={{ width: `${progressPercentage}%` }}
              ></div>
            </div>
            <div className="flex justify-between text-xs text-gray-400 mt-1">
              <span>{formatTime(currentTime)}</span>
              <span>{formatTime(duration)}</span>
            </div>
          </div>
        )}
      </div>

      {/* 时长 */}
      <span className="text-sm text-gray-500 min-w-[40px] text-right">
        {Math.floor(track.duration_ms / 60000)}:{String(Math.floor((track.duration_ms % 60000) / 1000)).padStart(2, '0')}
      </span>

      {/* Spotify链接 */}
      {track.external_urls?.spotify && (
        <a
          href={track.external_urls.spotify}
          target="_blank"
          rel="noopener noreferrer"
          className="opacity-0 group-hover:opacity-100 transition-opacity p-1 text-gray-400 hover:text-green-500"
          title="在Spotify中打开"
        >
          <svg className="h-4 w-4" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S18.66 0 12 0zm5.521 17.34c-.24.359-.66.48-1.021.24-2.82-1.74-6.36-2.101-10.561-1.141-.418.122-.779-.179-.899-.539-.12-.421.18-.78.54-.9 4.56-1.021 8.52-.6 11.64 1.32.42.18.479.659.301 1.02zm1.44-3.3c-.301.42-.841.6-1.262.3-3.239-1.98-8.159-2.58-11.939-1.38-.479.12-1.02-.12-1.14-.6-.12-.48.12-1.021.6-1.141C9.6 9.9 15 10.561 18.72 12.84c.361.181.54.78.241 1.2zm.12-3.36C15.24 8.4 8.82 8.16 5.16 9.301c-.6.179-1.2-.181-1.38-.721-.18-.601.18-1.2.72-1.381 4.26-1.26 11.28-1.02 15.721 1.621.539.3.719 1.02.419 1.56-.299.421-1.02.599-1.559.3z"/>
          </svg>
        </a>
      )}

      {/* 隐藏的音频元素 */}
      {currentPreviewUrl && (
        <audio
          ref={audioRef}
          src={currentPreviewUrl}
          preload="none"
        />
      )}
    </div>
  );
} 