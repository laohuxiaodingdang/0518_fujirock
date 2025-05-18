'use client';

import { useState } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import Navbar from '../components/Navbar';

export default function Home() {
  // Placeholder data for featured artists (would be fetched from API)
  const featuredArtists = [
    { 
      id: 1, 
      name: 'Artist A', 
      image: 'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?auto=format&fit=facearea&w=256&q=80',
      genre: 'Rock' 
    },
    { 
      id: 2, 
      name: 'Artist B', 
      image: 'https://images.unsplash.com/photo-1508214751196-bcfd4ca60f91?auto=format&fit=facearea&w=256&q=80',
      genre: 'Electronic' 
    },
    { 
      id: 3, 
      name: 'Artist C', 
      image: 'https://images.unsplash.com/photo-1465101046530-73398c7f28ca?auto=format&fit=facearea&w=256&q=80',
      genre: 'Pop' 
    },
    { 
      id: 4, 
      name: 'Artist D', 
      image: 'https://images.unsplash.com/photo-1515378791036-0648a3ef77b2?auto=format&fit=facearea&w=256&q=80',
      genre: 'Jazz' 
    },
  ];

  // Placeholder data for upcoming performances
  const upcomingPerformances = [
    { date: "JUL 26", artist: "Artist A", venue: "Green Stage", time: "8:00 PM" },
    { date: "JUL 27", artist: "Artist B", venue: "White Stage", time: "7:30 PM" },
    { date: "JUL 28", artist: "Artist C", venue: "Red Marquee", time: "9:00 PM" },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      
      <div className="flex">
        <main className="flex-1 p-6 md:p-8">
          {/* Welcome Message */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold mb-2 text-gray-800">Welcome back, music lover!</h1>
            <p className="text-gray-600">Discover artists performing at Fuji Rock 2025</p>
          </div>
          
          {/* Featured Artist */}
          <div className="bg-indigo-500 rounded-2xl p-6 mb-10 flex flex-col md:flex-row items-center gap-6 relative">
            <Image 
              src="https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?auto=format&fit=facearea&w=256&q=80" 
              alt="Artist A" 
              width={96} 
              height={96} 
              className="rounded-full object-cover border-4 border-white shadow-xl z-10"
            />
            <div className="relative z-10 text-center md:text-left">
              <h2 className="text-2xl font-bold mb-1 text-white">Artist A</h2>
              <p className="text-white text-opacity-80 mb-4">Headlining the Green Stage - July 26, 2025</p>
              <div className="flex items-center justify-center md:justify-start gap-3">
                <button className="bg-white text-indigo-700 px-4 py-2 rounded-full flex items-center gap-2 font-medium hover:bg-opacity-90">
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
          
          {/* Artists You Might Like */}
          <div className="mb-10">
            <h2 className="text-xl font-semibold text-gray-800 mb-6">Artists You Might Like</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              {featuredArtists.map((artist) => (
                <div key={artist.id} className="bg-white rounded-xl p-5 flex flex-col items-center shadow-sm">
                  <Image 
                    src={artist.image} 
                    alt={artist.name} 
                    width={96} 
                    height={96} 
                    className="rounded-full object-cover mb-4 border-2 border-gray-100"
                  />
                  <h3 className="font-medium text-gray-900 text-lg">{artist.name}</h3>
                  <span className="text-sm text-gray-500 flex items-center mt-1">
                    <svg className="h-4 w-4 text-green-500 mr-1" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S18.66 0 12 0zm5.521 17.34c-.24.359-.66.48-1.021.24-2.82-1.74-6.36-2.101-10.561-1.141-.418.122-.779-.179-.899-.539-.12-.421.18-.78.54-.9 4.56-1.021 8.52-.6 11.64 1.32.42.18.479.659.301 1.02zm1.44-3.3c-.301.42-.841.6-1.262.3-3.239-1.98-8.159-2.58-11.939-1.38-.479.12-1.02-.12-1.14-.6-.12-.48.12-1.021.6-1.141C9.6 9.9 15 10.561 18.72 12.84c.361.181.54.78.241 1.2zm.12-3.36C15.24 8.4 8.82 8.16 5.16 9.301c-.6.179-1.2-.181-1.38-.721-.18-.601.18-1.2.72-1.381 4.26-1.26 11.28-1.02 15.721 1.621.539.3.719 1.02.419 1.56-.299.421-1.02.599-1.559.3z"/>
                    </svg>
                    {artist.genre}
                  </span>
                  <Link href={`/artists/${artist.id}`} className="mt-4 bg-gray-100 hover:bg-gray-200 text-gray-800 px-4 py-2 rounded-full text-sm">
                    View Profile
                  </Link>
                </div>
              ))}
            </div>
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