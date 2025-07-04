'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { ArrowLeft, ExternalLink, Play, Pause, Volume2, Music, Sparkles } from 'lucide-react';
import { 
  getArtistDatabase, 
  getArtistSpotify, 
  getArtistTopTracks
} from '@/utils/api';

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
  
  const [loadingStates, setLoadingStates] = useState<LoadingStates>({
    database: true,
    spotify: true,
    topTracks: true,
    aiDescription: false
  });
  
  const [error, setError] = useState<string | null>(null);
  
  const [aiDescriptionText, setAiDescriptionText] = useState<string>('');
  const [aiDescriptionLoading, setAiDescriptionLoading] = useState(false);
  const [aiDescriptionComplete, setAiDescriptionComplete] = useState(false);

  const [currentPlayingTrack, setCurrentPlayingTrack] = useState<string | null>(null);

  const handlePlay = (trackId: string) => {
    if (currentPlayingTrack && currentPlayingTrack !== trackId) {
      setCurrentPlayingTrack(null);
    }
    setCurrentPlayingTrack(trackId);
  };

  const handlePause = () => {
    setCurrentPlayingTrack(null);
  };

  const handleSpotifyPlaylistClick = () => {
    if (artistData.spotify?.success && artistData.spotify.data.external_urls?.spotify) {
      window.open(artistData.spotify.data.external_urls.spotify, '_blank');
    } else {
      const searchQuery = encodeURIComponent(artistName);
      window.open(`https://open.spotify.com/search/${searchQuery}`, '_blank');
    }
  };

  const handleAIDescription = async (databaseResult: any) => {
    console.log('🔍 检查数据库中的AI描述');
    console.log('📝 ai_description:', databaseResult?.ai_description);
    
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
    }
    
    setLoadingStates(prev => ({ ...prev, aiDescription: false }));
  };

  useEffect(() => {
    if (!artistName) return;

    const loadData = async () => {
      try {
        const databaseResult = await getArtistDatabase(artistName);
        setArtistData(prev => ({ ...prev, database: databaseResult }));
        
        if (databaseResult?.success && databaseResult.data) {
          await handleAIDescription(databaseResult.data);
        }
      } catch (error) {
        console.error('Database API 失败:', error);
      } finally {
        setLoadingStates(prev => ({ ...prev, database: false }));
      }

      try {
        const spotifyResult = await getArtistSpotify(artistName);
        setArtistData(prev => ({ ...prev, spotify: spotifyResult }));
      } catch (error) {
        console.error('Spotify API 失败:', error);
      } finally {
        setLoadingStates(prev => ({ ...prev, spotify: false }));
      }

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

  const displayName = artistData.database?.data?.name || 
                     (artistData.spotify?.success ? artistData.spotify.data.name : artistName);
  
  const artistImage = (artistData.database?.data?.image_url) ||
                     (artistData.spotify?.success && artistData.spotify.data.images.length > 0
                       ? artistData.spotify.data.images[0].url
                       : 'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?auto=format&fit=facearea&w=256&q=80');

  const getWikipediaUrl = (title: string) => {
    return `https://zh.wikipedia.org/wiki/${encodeURIComponent(title)}`;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <button
                onClick={() => router.back()}
                className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-gray-500 bg-white hover:text-gray-700 focus:outline-none transition"
              >
                <ArrowLeft className="h-5 w-5 mr-1" />
                返回
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="bg-white shadow rounded-lg overflow-hidden">
          <div className="p-6">
            <div className="flex items-start space-x-6">
              <div className="flex-shrink-0">
                <img
                  src={artistImage}
                  alt={displayName}
                  className="h-32 w-32 object-cover rounded-lg shadow-sm"
                />
              </div>

              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  <h1 className="text-2xl font-bold text-gray-900 truncate">
                    {displayName}
                  </h1>
                </div>

                <div className="mt-2 flex flex-wrap gap-2">
                  {artistData.spotify?.success && artistData.spotify.data.genres.map((genre: string) => (
                    <span
                      key={genre}
                      className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800"
                    >
                      {genre}
                    </span>
                  ))}
                </div>

                <p className="mt-4 text-sm text-gray-500">
                  {artistData.database?.data?.description || 
                   artistData.database?.data?.wiki_extract || 
                   '加载中...'}
                </p>

                <div className="mt-4 flex space-x-4">
                  <button
                    onClick={handleSpotifyPlaylistClick}
                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                  >
                    <Music className="h-4 w-4 mr-2" />
                    在 Spotify 上收听
                  </button>

                  {artistData.database?.data?.wiki_data?.title && (
                    <a
                      href={getWikipediaUrl(artistData.database.data.wiki_data.title)}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                    >
                      <ExternalLink className="h-4 w-4 mr-2" />
                      维基百科
                    </a>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>

        {aiDescriptionComplete && (
          <div className="mt-6 bg-white shadow rounded-lg overflow-hidden">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-medium text-gray-900">AI 生成的毒舌介绍</h2>
                <Sparkles className="h-5 w-5 text-yellow-500" />
              </div>
              <p className="text-gray-600">{aiDescriptionText}</p>
            </div>
          </div>
        )}

        {artistData.topTracks?.success && artistData.topTracks.data.tracks.length > 0 && (
          <div className="mt-6 bg-white shadow rounded-lg overflow-hidden">
            <div className="p-6">
              <h2 className="text-lg font-medium text-gray-900 mb-4">热门歌曲</h2>
              <div className="space-y-4">
                {artistData.topTracks.data.tracks.map((track: any) => (
                  <div key={track.id} className="flex items-center space-x-4">
                    <img
                      src={track.album.images[0]?.url}
                      alt={track.name}
                      className="h-16 w-16 object-cover rounded-md shadow-sm"
                    />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {track.name}
                      </p>
                      <p className="text-sm text-gray-500 truncate">
                        {track.album.name}
                      </p>
                    </div>
                    {track.preview_url && (
                      <TrackPlayer
                        track={track}
                        isPlaying={currentPlayingTrack === track.id}
                        onPlay={() => handlePlay(track.id)}
                        onPause={handlePause}
                      />
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
