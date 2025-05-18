import Link from 'next/link';
import BubbleEffect from './BubbleEffect';

interface ArtistCardProps {
  id: string | number;
  name: string;
  image: string;
  genre?: string;
  className?: string;
  layout?: 'grid' | 'compact';
}

export default function ArtistCard({ 
  id, 
  name, 
  image, 
  genre,
  className = '',
  layout = 'grid' 
}: ArtistCardProps) {
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
            <span className="text-xs text-gray-400 flex items-center mt-1 relative z-10">
              <i className="fa-brands fa-spotify text-green-500 mr-1"></i>{genre}
            </span>
          )}
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
          <span className="text-sm text-gray-500 flex items-center mt-1 relative z-10">
            <i className="fa-brands fa-spotify text-green-500 mr-1"></i>{genre}
          </span>
        )}
        <button className="mt-4 bg-gray-100 hover:bg-gray-200 text-gray-800 px-4 py-2 rounded-full text-sm relative z-10">View Profile</button>
      </div>
    </Link>
  );
} 