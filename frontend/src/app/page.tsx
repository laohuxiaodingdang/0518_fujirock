'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import Navbar from '../components/Navbar';

interface Artist {
  id: string;
  name: string;
  description: string;
  spotify_id: string;
  genres: string[];
  wiki_data: any;
  wiki_extract: string;
  is_fuji_rock_artist: boolean;
  image_url?: string;
  created_at: string;
  updated_at: string;
}

export default function Home() {
  const [featuredArtists, setFeaturedArtists] = useState<Artist[]>([]);
  const [loading, setLoading] = useState(true);
  const [fredAgainArtist, setFredAgainArtist] = useState<Artist | null>(null);

  // Spotify URL for the featured artist (Fred again..)
  const spotifyUrl = "https://open.spotify.com/artist/4oLeXFyACqeem2VImYeBFe"; // Fred again..

  useEffect(() => {
    const fetchArtists = async () => {
      try {
        // 1. 首先获取 Fred again.. 的数据
        const fredResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/database/artists/search?query=Fred again..&limit=1`);
        let fredArtist = null;
        
        if (fredResponse.ok) {
          const fredResult = await fredResponse.json();
          if (fredResult.success && fredResult.data.length > 0) {
            fredArtist = fredResult.data[0];
            setFredAgainArtist(fredArtist);
          }
        }
        
        // 如果没有找到 Fred again..，使用模拟数据
        if (!fredArtist) {
          fredArtist = {
            id: '1dfc9307-9078-4963-ad5a-33284e040c30',
            name: 'Fred again..',
            description: 'British electronic music producer and DJ',
            spotify_id: '4oLeXFyACqeem2VImYeBFe',
            genres: ['electronic', 'house', 'dance'],
            wiki_data: {},
            wiki_extract: 'Fred again.. is a British electronic music producer and DJ known for his innovative approach to electronic music.',
            is_fuji_rock_artist: true,
            image_url: 'https://cdn.fujirockfestival.com/smash/artist/7xIutJWkNtlLSlxcUUwIqbBY7NGyDzuV7SKboAnx.jpg',
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
          };
          setFredAgainArtist(fredArtist);
        }

        // 2. 获取其他艺术家数据
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/database/artists/search?query=&limit=10`);
        
        if (response.ok) {
          const result = await response.json();
          if (result.success && result.data.length > 0) {
            // 过滤掉 Fred again..，然后随机选择3个
            const otherArtists = result.data.filter((artist: Artist) => 
              artist.name.toLowerCase() !== 'fred again..'
            );
            
            // 随机选择3个艺术家
            const shuffled = otherArtists.sort(() => 0.5 - Math.random());
            const selectedArtists = shuffled.slice(0, 3);
            
            // 将 Fred again.. 放在第一位，其他艺术家跟随
            setFeaturedArtists([fredArtist, ...selectedArtists]);
          } else {
            // 如果数据库没有数据，使用模拟数据
            setFeaturedArtists([
              fredArtist,
              {
                id: '2',
                name: 'VAMPIRE WEEKEND',
                description: 'American rock band',
                spotify_id: '5BvJzeQpmsdsFp4HGUYUEx',
                genres: ['indie rock', 'alternative rock'],
                wiki_data: {},
                wiki_extract: 'Vampire Weekend is an American rock band from New York City.',
                is_fuji_rock_artist: true,
                image_url: 'https://cdn.fujirockfestival.com/smash/artist/zBfoeCGpXD1fT76b9YQXAif4AKAXkFfZmZszlTyF.jpg',
                created_at: new Date().toISOString(),
                updated_at: new Date().toISOString()
              },
              {
                id: '3',
                name: 'RADWIMPS',
                description: 'Japanese rock band',
                spotify_id: '1EowJ1WwkMzkCkRomFhui7',
                genres: ['j-rock', 'alternative rock'],
                wiki_data: {},
                wiki_extract: 'Radwimps is a Japanese rock band.',
                is_fuji_rock_artist: true,
                image_url: 'https://cdn.fujirockfestival.com/smash/artist/QC0fzOzWqR1MiTBlP1Z8OCJCAR9w8BqdvNnDxcmg.jpg',
                created_at: new Date().toISOString(),
                updated_at: new Date().toISOString()
              },
              {
                id: '4',
                name: 'JAMES BLAKE',
                description: 'British singer-songwriter',
                spotify_id: '53KwLdlmrlCelAZMaLVZqU',
                genres: ['electronic', 'soul'],
                wiki_data: {},
                wiki_extract: 'James Blake is a British singer, songwriter, and record producer.',
                is_fuji_rock_artist: true,
                image_url: 'https://cdn.fujirockfestival.com/smash/artist/MwZCrWPJELxJIGCR0bsI8hxrCYpoIRdWYQjU8KdQ.jpg',
                created_at: new Date().toISOString(),
                updated_at: new Date().toISOString()
              }
            ]);
          }
        } else {
          // API 调用失败，使用模拟数据（带有真实头像）
          setFeaturedArtists([
            fredArtist,
            {
              id: '2',
              name: 'VAMPIRE WEEKEND',
              description: 'American rock band',
              spotify_id: '5BvJzeQpmsdsFp4HGUYUEx',
              genres: ['indie rock', 'alternative rock'],
              wiki_data: {},
              wiki_extract: 'Vampire Weekend is an American rock band from New York City.',
              is_fuji_rock_artist: true,
              image_url: 'https://cdn.fujirockfestival.com/smash/artist/zBfoeCGpXD1fT76b9YQXAif4AKAXkFfZmZszlTyF.jpg',
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString()
            },
            {
              id: '3',
              name: 'RADWIMPS',
              description: 'Japanese rock band',
              spotify_id: '1EowJ1WwkMzkCkRomFhui7',
              genres: ['j-rock', 'alternative rock'],
              wiki_data: {},
              wiki_extract: 'Radwimps is a Japanese rock band.',
              is_fuji_rock_artist: true,
              image_url: 'https://cdn.fujirockfestival.com/smash/artist/QC0fzOzWqR1MiTBlP1Z8OCJCAR9w8BqdvNnDxcmg.jpg',
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString()
            },
            {
              id: '4',
              name: 'JAMES BLAKE',
              description: 'British singer-songwriter',
              spotify_id: '53KwLdlmrlCelAZMaLVZqU',
              genres: ['electronic', 'soul'],
              wiki_data: {},
              wiki_extract: 'James Blake is a British singer, songwriter, and record producer.',
              is_fuji_rock_artist: true,
              image_url: 'https://cdn.fujirockfestival.com/smash/artist/MwZCrWPJELxJIGCR0bsI8hxrCYpoIRdWYQjU8KdQ.jpg',
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString()
            }
          ]);
        }
      } catch (error) {
        console.error('Error fetching artists:', error);
        // 错误情况下使用模拟数据（带有真实头像）
        const fredArtist = {
          id: '1dfc9307-9078-4963-ad5a-33284e040c30',
          name: 'Fred again..',
          description: 'British electronic music producer and DJ',
          spotify_id: '4oLeXFyACqeem2VImYeBFe',
          genres: ['electronic', 'house', 'dance'],
          wiki_data: {},
          wiki_extract: 'Fred again.. is a British electronic music producer and DJ known for his innovative approach to electronic music.',
          is_fuji_rock_artist: true,
          image_url: 'https://cdn.fujirockfestival.com/smash/artist/7xIutJWkNtlLSlxcUUwIqbBY7NGyDzuV7SKboAnx.jpg',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        };
        
        setFredAgainArtist(fredArtist);
        setFeaturedArtists([fredArtist]);
      } finally {
        setLoading(false);
      }
    };

    fetchArtists();
  }, []);

  // 获取艺术家图片 - 优先使用数据库中的真实头像
  const getArtistImage = (artist: Artist, index: number) => {
    // 如果有数据库中的真实头像，优先使用
    if (artist.image_url) {
      return artist.image_url;
    }
    
    // 为每个艺术家提供不同的默认图片作为后备
    const defaultImages = [
      'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?auto=format&fit=crop&w=400&q=80',
      'https://images.unsplash.com/photo-1508214751196-bcfd4ca60f91?auto=format&fit=crop&w=400&q=80',
      'https://images.unsplash.com/photo-1465101046530-73398c7f28ca?auto=format&fit=crop&w=400&q=80',
      'https://images.unsplash.com/photo-1515378791036-0648a3ef77b2?auto=format&fit=crop&w=400&q=80'
    ];
    
    return defaultImages[index] || defaultImages[0];
  };

  // 获取艺术家主要风格
  const getMainGenre = (genres: string[]) => {
    if (!genres || genres.length === 0) return 'Music';
    return genres[0].charAt(0).toUpperCase() + genres[0].slice(1);
  };

  // Placeholder data for upcoming performances (使用真实艺术家数据)
  const upcomingPerformances = featuredArtists.slice(0, 3).map((artist, index) => ({
    date: `JUL ${26 + index}`,
    artist: artist.name,
    venue: index === 0 ? "Green Stage" : index === 1 ? "White Stage" : "Red Marquee",
    time: index === 0 ? "8:00 PM" : index === 1 ? "7:30 PM" : "9:00 PM"
  }));

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      
      <div className="flex">
        <main className="flex-1 p-6 md:p-8">
          {/* Welcome Message */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold mb-2 text-gray-800">Welcome back, music lover!</h1>
            <p className="text-gray-600">Discover artists performing at Fuji Rock 2025</p>
            
            {/* 快速搜索示例 */}
            <div className="mt-6">
              <p className="text-sm text-gray-500 mb-3">🔍 试试搜索这些艺术家：</p>
              <div className="flex flex-wrap gap-2">
                {['Nirvana', 'Radiohead', 'The Beatles', 'Coldplay', 'Green Day'].map((artist) => (
                  <button
                    key={artist}
                    onClick={() => window.location.href = `/artists/${encodeURIComponent(artist)}`}
                    className="bg-blue-100 hover:bg-blue-200 text-blue-800 px-3 py-1 rounded-full text-sm transition-colors"
                  >
                    {artist}
                  </button>
                ))}
              </div>
            </div>
          </div>
          
          {/* Featured Artist (Fred again..) */}
          {fredAgainArtist && (
            <div className="bg-indigo-500 rounded-2xl p-6 mb-10 flex flex-col md:flex-row items-center gap-6 relative">
              <Image 
                src={getArtistImage(fredAgainArtist, 0)}
                alt={fredAgainArtist.name}
                width={96} 
                height={96} 
                className="rounded-full object-cover border-4 border-white shadow-xl z-10"
                onError={(e) => {
                  e.currentTarget.src = 'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?auto=format&fit=crop&w=400&q=80';
                }}
              />
              <div className="relative z-10 text-center md:text-left">
                <h2 className="text-2xl font-bold mb-1 text-white">{fredAgainArtist.name}</h2>
                <p className="text-white text-opacity-80 mb-4">Headlining the Green Stage - July 26, 2025</p>
                <div className="flex items-center justify-center md:justify-start gap-3">
                  <button 
                    onClick={() => window.open(spotifyUrl, "_blank")}
                    className="bg-white text-indigo-700 px-4 py-2 rounded-full flex items-center gap-2 font-medium hover:bg-opacity-90"
                  >
                    <svg className="h-5 w-5 text-green-500" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S18.66 0 12 0zm5.521 17.34c-.24.359-.66.48-1.021.24-2.82-1.74-6.36-2.101-10.561-1.141-.418.122-.779-.179-.899-.539-.12-.421.18-.78.54-.9 4.56-1.021 8.52-.6 11.64 1.32.42.18.479.659.301 1.02zm1.44-3.3c-.301.42-.841.6-1.262.3-3.239-1.98-8.159-2.58-11.939-1.38-.479.12-1.02-.12-1.14-.6-.12-.48.12-1.021.6-1.141C9.6 9.9 15 10.561 18.72 12.84c.361.181.54.78.241 1.2zm.12-3.36C15.24 8.4 8.82 8.16 5.16 9.301c-.6.179-1.2-.181-1.38-.721-.18-.601.18-1.2.72-1.381 4.26-1.26 11.28-1.02 15.721 1.621.539.3.719 1.02.419 1.56-.299.421-1.02.599-1.559.3z"/>
                    </svg>
                    <span>Listen on Spotify</span>
                  </button>
                  <button className="bg-white bg-opacity-20 hover:bg-opacity-30 text-white p-2 rounded-full">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          )}
          
          {/* Artists You Might Like */}
          <div className="mb-10">
            <h2 className="text-xl font-semibold text-gray-800 mb-6">Artists You Might Like</h2>
            {loading ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                {[1, 2, 3, 4].map((i) => (
                  <div key={i} className="bg-white rounded-xl p-5 flex flex-col items-center shadow-sm animate-pulse">
                    <div className="w-24 h-24 bg-gray-200 rounded-full mb-4"></div>
                    <div className="h-4 bg-gray-200 rounded w-20 mb-2"></div>
                    <div className="h-3 bg-gray-200 rounded w-16"></div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                {featuredArtists.map((artist, index) => (
                  <div key={artist.id} className="bg-white rounded-xl p-5 flex flex-col items-center shadow-sm hover:shadow-md transition-shadow">
                    <Image 
                      src={getArtistImage(artist, index)}
                      alt={artist.name}
                      width={96} 
                      height={96} 
                      className="rounded-full object-cover mb-4 border-2 border-gray-100"
                      onError={(e) => {
                        const defaultImages = [
                          'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?auto=format&fit=crop&w=400&q=80',
                          'https://images.unsplash.com/photo-1508214751196-bcfd4ca60f91?auto=format&fit=crop&w=400&q=80',
                          'https://images.unsplash.com/photo-1465101046530-73398c7f28ca?auto=format&fit=crop&w=400&q=80',
                          'https://images.unsplash.com/photo-1515378791036-0648a3ef77b2?auto=format&fit=crop&w=400&q=80'
                        ];
                        e.currentTarget.src = defaultImages[index] || defaultImages[0];
                      }}
                    />
                    <h3 className="font-medium text-gray-900 text-lg text-center">{artist.name}</h3>
                    <span className="text-sm text-gray-500 flex items-center mt-1">
                      <svg className="h-4 w-4 text-green-500 mr-1" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S18.66 0 12 0zm5.521 17.34c-.24.359-.66.48-1.021.24-2.82-1.74-6.36-2.101-10.561-1.141-.418.122-.779-.179-.899-.539-.12-.421.18-.78.54-.9 4.56-1.021 8.52-.6 11.64 1.32.42.18.479.659.301 1.02zm1.44-3.3c-.301.42-.841.6-1.262.3-3.239-1.98-8.159-2.58-11.939-1.38-.479.12-1.02-.12-1.14-.6-.12-.48.12-1.021.6-1.141C9.6 9.9 15 10.561 18.72 12.84c.361.181.54.78.241 1.2zm.12-3.36C15.24 8.4 8.82 8.16 5.16 9.301c-.6.179-1.2-.181-1.38-.721-.18-.601.18-1.2.72-1.381 4.26-1.26 11.28-1.02 15.721 1.621.539.3.719 1.02.419 1.56-.299.421-1.02.599-1.559.3z"/>
                      </svg>
                      {getMainGenre(artist.genres)}
                    </span>
                    <Link 
                      href={artist.name === 'Fred again..' ? '/artists/fred-again' : `/artists/${encodeURIComponent(artist.name)}`}
                      className="mt-4 bg-gray-100 hover:bg-gray-200 text-gray-800 px-4 py-2 rounded-full text-sm transition-colors"
                    >
                      View Profile
                    </Link>
                  </div>
                ))}
              </div>
            )}
          </div>
          
          {/* Upcoming Performances */}
          <div className="mb-10">
            <h2 className="text-xl font-semibold text-gray-800 mb-6">Upcoming Performances</h2>
            <div className="bg-white rounded-xl p-6 shadow-sm">
              <div className="flex flex-col divide-y">
                {upcomingPerformances.map((performance, index) => (
                  <div key={index} className="py-4 flex items-center gap-4">
                    <div className="text-center min-w-[60px]">
                      <span className="text-gray-500 text-sm">{performance.date.split(' ')[0]}</span>
                      <div className="text-2xl font-bold">{performance.date.split(' ')[1]}</div>
                    </div>
                    <div className="flex-1">
                      <h3 className="font-medium">{performance.artist}</h3>
                      <p className="text-gray-500 text-sm">{performance.venue}, {performance.time}</p>
                    </div>
                    <button className="bg-gray-100 hover:bg-gray-200 text-gray-800 px-3 py-1 rounded-full text-sm">
                      Add to Calendar
                    </button>
                  </div>
                ))}
              </div>
              
              <div className="mt-6 text-center">
                <button className="text-indigo-600 font-medium hover:text-indigo-700">
                  View Full Schedule
                </button>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
} 