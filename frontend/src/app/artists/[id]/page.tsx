'use client';

import { useState, useRef } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { motion } from 'framer-motion';

export default function ArtistPage({ params }: { params: { id: string } }) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTrack, setCurrentTrack] = useState<number | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  
  // Placeholder artist data (would be fetched from API)
  const artist = {
    id: params.id,
    name: 'Artist A',
    wikipediaDesc: 'Artist A is a renowned musician known for their innovative style and energetic performances. They have released multiple chart-topping albums and are a highlight of Fuji Rock 2025.',
    aiDesc: "Sure, Artist A is 'famous'—if you count being overrated as a talent. But hey, at least their hair is always on point. Get ready for a show you'll never forget (or forgive).",
    image: 'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?auto=format&fit=facearea&w=256&q=80',
    tracks: [
      { id: '1', title: '热门歌曲 1', album: '专辑1', duration: '3:45', previewUrl: 'https://p.scdn.co/mp3-preview/fc1dd43539886b6d5f3c1a141ce36d2c4a2cb2c4' },
      { id: '2', title: '热门歌曲 2', album: '专辑2', duration: '4:12', previewUrl: 'https://p.scdn.co/mp3-preview/8250051dd8245c5b7a2e6281dd9571994f37370c' },
      { id: '3', title: '热门歌曲 3', album: '专辑1', duration: '3:28', previewUrl: 'https://p.scdn.co/mp3-preview/4aaab38bf44b89ef76a89636f6b2f17f0b320816' },
    ],
    performanceDate: '7月26日',
    stage: 'Green Stage',
    playlistCoverUrl: 'https://images.unsplash.com/photo-1509773896068-7fd415d91e2e?ixlib=rb-1.2.1&auto=format&fit=crop&w=300&q=80',
  };

  const playTrack = (index: number) => {
    if (audioRef.current) {
      if (currentTrack === index && isPlaying) {
        audioRef.current.pause();
        setIsPlaying(false);
      } else {
        audioRef.current.src = artist.tracks[index].previewUrl;
        audioRef.current.play().catch(error => console.error("Playback failed:", error));
        setIsPlaying(true);
        setCurrentTrack(index);
      }
    }
  };

  const handleBackNavigation = () => {
    if (audioRef.current) {
      audioRef.current.pause();
    }
    window.history.back();
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Hidden audio element for track playback */}
      <audio ref={audioRef} onEnded={() => setIsPlaying(false)} />
      
      {/* Header with back button */}
      <header className="sticky top-0 z-10 bg-white shadow-sm p-4">
        <div className="max-w-3xl mx-auto flex items-center">
          <button 
            onClick={handleBackNavigation}
            className="w-10 h-10 flex items-center justify-center rounded-full bg-gray-100 mr-4"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <h1 className="text-xl font-semibold text-gray-800">Artist Profile</h1>
        </div>
      </header>
      
      <main className="max-w-3xl mx-auto p-4 pt-2">
        {/* Artist Header */}
        <section className="flex items-center mb-6">
          <div className="w-28 h-28 mr-4 relative overflow-hidden rounded-full border-4 border-white shadow-lg">
            <Image 
              src={artist.image} 
              alt={artist.name}
              width={112}
              height={112}
              className="object-cover"
              priority
            />
          </div>
          <div>
            <div className="flex items-center">
              <h2 className="text-3xl font-bold text-gray-800">{artist.name}</h2>
              <svg className="h-6 w-6 ml-2 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118l-2.8-2.034c-.783-.57-.38-1.81.588-1.81h3.462a1 1 0 00.95-.69l1.07-3.292z" />
              </svg>
            </div>
            <div className="flex space-x-2 mt-1">
              <span className="px-2 py-1 bg-indigo-100 text-indigo-800 text-xs font-medium rounded-full">
                {artist.performanceDate}
              </span>
              <span className="px-2 py-1 bg-green-100 text-green-800 text-xs font-medium rounded-full">
                {artist.stage}
              </span>
            </div>
          </div>
        </section>
        
        {/* Wikipedia Section */}
        <section className="mb-6 p-6 bg-white rounded-xl shadow-md border border-gray-100">
          <div className="flex items-center mb-3">
            <div className="h-6 w-6 text-gray-700 mr-2 flex items-center justify-center font-serif font-bold">
              W
            </div>
            <h3 className="text-xl font-semibold text-gray-800">Wikipedia</h3>
          </div>
          <p className="text-gray-600 leading-relaxed">
            {artist.wikipediaDesc}
          </p>
        </section>
        
        {/* AI Commentary Section */}
        <section className="mb-6 p-6 bg-gradient-to-r from-pink-50 to-purple-50 rounded-xl shadow-md border border-pink-100">
          <div className="flex items-center mb-3">
            <div className="h-6 w-6 text-pink-600 mr-2">
              <svg viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2a2 2 0 012 2c0 .74-.4 1.39-1 1.73V7h1a7 7 0 017 7h1a1 1 0 011 1v3a1 1 0 01-1 1h-1v1a2 2 0 01-2 2H5a2 2 0 01-2-2v-1H2a1 1 0 01-1-1v-3a1 1 0 011-1h1a7 7 0 017-7h1V5.73c-.6-.34-1-.99-1-1.73a2 2 0 012-2zM7.5 13A1.5 1.5 0 006 14.5V16h2.5v-1.5a1.5 1.5 0 00-1-1.41zM16.5 13a1.5 1.5 0 00-1 1.41V16H18v-1.59a1.5 1.5 0 00-1.5-1.41zM11 16v2h2v-2h-2z"/>
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-pink-700">Toxic AI Intro</h3>
          </div>
          <p className="text-pink-800 leading-relaxed">
            {artist.aiDesc}
          </p>
        </section>
        
        {/* Top Tracks Section */}
        <section className="mb-6 p-6 bg-white rounded-xl shadow-md border border-gray-100">
          <div className="flex justify-between items-center mb-4">
            <div className="flex items-center">
              <div className="w-16 h-16 rounded-md mr-3 overflow-hidden shadow-sm">
                <Image 
                  src={artist.playlistCoverUrl} 
                  alt="Top Tracks" 
                  width={64}
                  height={64}
                  className="object-cover"
                />
              </div>
              <h3 className="text-xl font-semibold text-gray-800">Top Tracks</h3>
            </div>
            <div className="flex items-center text-green-600">
              <svg className="h-5 w-5 mr-1" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S18.66 0 12 0zm5.521 17.34c-.24.359-.66.48-1.021.24-2.82-1.74-6.36-2.101-10.561-1.141-.418.122-.779-.179-.899-.539-.12-.421.18-.78.54-.9 4.56-1.021 8.52-.6 11.64 1.32.42.18.479.659.301 1.02zm1.44-3.3c-.301.42-.841.6-1.262.3-3.239-1.98-8.159-2.58-11.939-1.38-.479.12-1.02-.12-1.14-.6-.12-.48.12-1.021.6-1.141C9.6 9.9 15 10.561 18.72 12.84c.361.181.54.78.241 1.2zm.12-3.36C15.24 8.4 8.82 8.16 5.16 9.301c-.6.179-1.2-.181-1.38-.721-.18-.601.18-1.2.72-1.381 4.26-1.26 11.28-1.02 15.721 1.621.539.3.719 1.02.419 1.56-.299.421-1.02.599-1.559.3z"/>
              </svg>
              <span className="text-sm font-medium">Spotify Playlist</span>
            </div>
          </div>
          
          <div className="space-y-2">
            {artist.tracks.map((track, index) => (
              <div 
                key={track.id}
                className="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg transition-colors cursor-pointer"
                onClick={() => playTrack(index)}
              >
                <div className="flex items-center">
                  <div className="w-8 h-8 flex items-center justify-center mr-3 rounded-full bg-gray-100">
                    {currentTrack === index && isPlaying ? (
                      <svg className="h-4 w-4 text-gray-800" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zM7 8a1 1 0 012 0v4a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v4a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                      </svg>
                    ) : (
                      <svg className="h-4 w-4 text-gray-800" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
                      </svg>
                    )}
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-800">{track.title}</h4>
                    <p className="text-sm text-gray-500">{track.album}</p>
                  </div>
                </div>
                <span className="text-sm text-gray-500">{track.duration}</span>
              </div>
            ))}
          </div>
          
          <div className="mt-4 flex justify-center">
            <button 
              onClick={() => window.open("https://open.spotify.com/artist/4Z8W4fKeB5YxbusRsdQVPb", "_blank")}
              className="px-4 py-2 bg-green-500 text-white rounded-full flex items-center space-x-2 hover:bg-green-600 transition-colors"
            >
              <svg className="h-4 w-4" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S18.66 0 12 0zm5.521 17.34c-.24.359-.66.48-1.021.24-2.82-1.74-6.36-2.101-10.561-1.141-.418.122-.779-.179-.899-.539-.12-.421.18-.78.54-.9 4.56-1.021 8.52-.6 11.64 1.32.42.18.479.659.301 1.02zm1.44-3.3c-.301.42-.841.6-1.262.3-3.239-1.98-8.159-2.58-11.939-1.38-.479.12-1.02-.12-1.14-.6-.12-.48.12-1.021.6-1.141C9.6 9.9 15 10.561 18.72 12.84c.361.181.54.78.241 1.2zm.12-3.36C15.24 8.4 8.82 8.16 5.16 9.301c-.6.179-1.2-.181-1.38-.721-.18-.601.18-1.2.72-1.381 4.26-1.26 11.28-1.02 15.721 1.621.539.3.719 1.02.419 1.56-.299.421-1.02.599-1.559.3z"/>
              </svg>
              <span>在 Spotify 上播放</span>
            </button>
          </div>
        </section>
      </main>
    </div>
  );
} 