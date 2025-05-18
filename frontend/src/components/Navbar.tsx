'use client';

import { useState } from 'react';
import Link from 'next/link';
import Image from 'next/image';

export default function Navbar() {
  const [searchQuery, setSearchQuery] = useState('');

  return (
    <header className="sticky top-0 z-50 bg-white shadow-sm px-6 py-4 flex items-center justify-between">
      <div className="flex items-center">
        <Link href="/" className="flex items-center">
          <Image 
            src="https://upload.wikimedia.org/wikipedia/commons/2/2e/Fujirock_logo.png" 
            alt="Fuji Rock Logo" 
            width={32} 
            height={32} 
            className="rounded-full mr-3"
          />
          <h1 className="text-xl font-bold tracking-wide hidden md:block text-gray-800">
            Fuji Rock 2025
          </h1>
        </Link>
      </div>
      
      <div className="flex items-center bg-gray-100 rounded-full px-4 py-2 w-full max-w-md mx-4">
        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-gray-500 mr-2" viewBox="0 0 20 20" fill="currentColor">
          <path fillRule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clipRule="evenodd" />
        </svg>
        <input 
          type="text" 
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search artists, genres, or stages..." 
          className="bg-transparent outline-none flex-1 text-gray-800 placeholder-gray-400"
        />
      </div>
      
      <div className="flex items-center gap-4">
        <button className="text-gray-700 hover:text-gray-900">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
        </button>
        <button className="text-gray-700 hover:text-gray-900">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
          </svg>
        </button>
            </div>
     </header>
   );
} 