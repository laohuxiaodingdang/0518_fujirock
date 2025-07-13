import Link from 'next/link';
import BubbleEffect from './BubbleEffect';
import { generateMusicPlatformUrls, getUrlDisplayText } from '../services/music_platforms';

interface ArtistCardProps {
  id: string | number;
  name: string;
  image: string;
  genre?: string;
  className?: string;
  layout?: 'grid' | 'compact';
  spotify_url?: string;
  qq_music_url?: string;
  netease_url?: string;
  apple_music_url?: string;
  youtube_music_url?: string;
  kkbox_url?: string;
}

export default function ArtistCard({ 
  id, 
  name, 
  image, 
  genre,
  className = '',
  layout = 'grid',
  spotify_url,
  qq_music_url,
  netease_url,
  apple_music_url,
  youtube_music_url,
  kkbox_url
}: ArtistCardProps) {
  // 如果没有提供音乐平台链接，生成搜索链接
  const musicUrls = {
    qq_music: qq_music_url || generateMusicPlatformUrls(name).qq_music_url,
    netease: netease_url || generateMusicPlatformUrls(name).netease_url,
    apple_music: apple_music_url || generateMusicPlatformUrls(name).apple_music_url,
    youtube_music: youtube_music_url || generateMusicPlatformUrls(name).youtube_music_url,
    kkbox: kkbox_url || generateMusicPlatformUrls(name).kkbox_url
  };

  const renderMusicPlatformLinks = () => (
    <div className="flex flex-wrap gap-2 mt-2 relative z-10">
      {spotify_url && (
        <a 
          href={spotify_url} 
          target="_blank" 
          rel="noopener noreferrer"
          className="text-green-500 hover:text-green-600 transition-colors"
          title="在 Spotify 中打开"
        >
          <i className="fa-brands fa-spotify text-lg"></i>
        </a>
      )}
      <a 
        href={musicUrls.qq_music} 
        target="_blank" 
        rel="noopener noreferrer"
        className="text-blue-500 hover:text-blue-600 transition-colors"
        title={getUrlDisplayText(musicUrls.qq_music, 'qq_music')}
      >
        <i className="fa-solid fa-music text-lg"></i>
      </a>
      <a 
        href={musicUrls.netease} 
        target="_blank" 
        rel="noopener noreferrer"
        className="text-red-500 hover:text-red-600 transition-colors"
        title={getUrlDisplayText(musicUrls.netease, 'netease')}
      >
        <i className="fa-solid fa-cloud text-lg"></i>
      </a>
      <a 
        href={musicUrls.apple_music} 
        target="_blank" 
        rel="noopener noreferrer"
        className="text-pink-500 hover:text-pink-600 transition-colors"
        title={getUrlDisplayText(musicUrls.apple_music, 'apple_music')}
      >
        <i className="fa-brands fa-apple text-lg"></i>
      </a>
      <a 
        href={musicUrls.youtube_music} 
        target="_blank" 
        rel="noopener noreferrer"
        className="text-red-600 hover:text-red-700 transition-colors"
        title={getUrlDisplayText(musicUrls.youtube_music, 'youtube_music')}
      >
        <i className="fa-brands fa-youtube text-lg"></i>
      </a>
      <a 
        href={musicUrls.kkbox} 
        target="_blank" 
        rel="noopener noreferrer"
        className="text-yellow-500 hover:text-yellow-600 transition-colors"
        title={getUrlDisplayText(musicUrls.kkbox, 'kkbox')}
      >
        <i className="fa-solid fa-play text-lg"></i>
      </a>
    </div>
  );

  if (layout === 'compact') {
    return (
      <Link href={`/artists/${id}`}>
        <div className={`artist-card bg-white rounded-2xl shadow-md p-3 flex flex-col items-center relative overflow-visible ${className}`}>
          <BubbleEffect 
            id={`wave-artist-${id}`}
            options={{
              bubbleCount: 20,
              bubbleColors: ['rgba(240, 240, 255, 0.25)', 'rgba(230, 230, 250, 0.2)', 'rgba(220, 220, 245, 0.15)'],
              minSize: 2,
              maxSize: 5,
              speed: 0.15
            }}
          />
          <img 
            src={image} 
            alt={name}
            className="w-20 h-20 rounded-full object-cover mb-2 border-2 border-gray-100 relative z-10" 
          />
          <span className="font-medium text-gray-900 relative z-10">{name}</span>
          {genre && (
            <span className="text-xs text-gray-400 relative z-10">{genre}</span>
          )}
          {renderMusicPlatformLinks()}
        </div>
      </Link>
    );
  }

  return (
    <Link href={`/artists/${id}`}>
      <div className={`artist-card rounded-xl p-5 bg-white flex flex-col items-center relative overflow-visible ${className}`}>
        <BubbleEffect 
          id={`wave-artist-${id}`}
          options={{
            bubbleCount: 20,
            bubbleColors: ['rgba(240, 240, 255, 0.25)', 'rgba(230, 230, 250, 0.2)', 'rgba(220, 220, 245, 0.15)'],
            minSize: 2,
            maxSize: 5,
            speed: 0.15
          }}
        />
        <img 
          src={image} 
          alt={name}
          className="w-24 h-24 rounded-full object-cover mb-4 border-2 border-gray-100 relative z-10" 
        />
        <h3 className="font-medium text-gray-900 text-lg relative z-10">{name}</h3>
        {genre && (
          <span className="text-sm text-gray-500 relative z-10">{genre}</span>
        )}
        {renderMusicPlatformLinks()}
        <button className="mt-4 bg-gray-100 hover:bg-gray-200 text-gray-800 px-4 py-2 rounded-full text-sm relative z-10">
          View Profile
        </button>
      </div>
    </Link>
  );
}
