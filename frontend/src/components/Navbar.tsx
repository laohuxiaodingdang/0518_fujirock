'use client';

import { useState } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { useRouter } from 'next/navigation';
import { getArtistSpotify } from '@/utils/api';

export default function Navbar() {
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const router = useRouter();

  const handleSearch = async () => {
    if (!searchQuery.trim() || isSearching) {
      return;
    }

    setIsSearching(true);

    try {
      // 为一些常见的艺术家名称添加消歧义
      const disambiguatedName = getDisambiguatedArtistName(searchQuery.trim());
      
      // 先搜索艺术家获取ID
      const spotifyResult = await getArtistSpotify(disambiguatedName);
      
      if (spotifyResult.success) {
        // 跳转到艺术家详情页面，使用消歧义后的名称
        router.push(`/artists/${encodeURIComponent(disambiguatedName)}`);
      } else {
        // 如果搜索失败，仍然跳转但会显示错误信息
        router.push(`/artists/${encodeURIComponent(disambiguatedName)}`);
      }
    } catch (error) {
      console.error('搜索错误:', error);
      // 即使出错也跳转，让详情页面处理错误
      const disambiguatedName = getDisambiguatedArtistName(searchQuery.trim());
      router.push(`/artists/${encodeURIComponent(disambiguatedName)}`);
    } finally {
      setIsSearching(false);
      setSearchQuery(''); // 清空搜索框
    }
  };

  // 艺术家名称消歧义函数
  const getDisambiguatedArtistName = (artistName: string): string => {
    const name = artistName.toLowerCase();
    
    // 常见的需要消歧义的艺术家名称
    const disambiguationMap: { [key: string]: string } = {
      'nirvana': 'Nirvana (band)',
      'genesis': 'Genesis (band)',
      'chicago': 'Chicago (band)',
      'boston': 'Boston (band)',
      'kansas': 'Kansas (band)',
      'asia': 'Asia (band)',
      'europe': 'Europe (band)',
      'america': 'America (band)',
      'journey': 'Journey (band)',
      'foreigner': 'Foreigner (band)',
      'survivor': 'Survivor (band)',
      'tesla': 'Tesla (band)',
      'rush': 'Rush (band)',
      'yes': 'Yes (band)',
      'cream': 'Cream (band)',
      'wings': 'Wings (band)',
      'heart': 'Heart (band)',
      'kiss': 'Kiss (band)',
      'queen': 'Queen (band)',
      'prince': 'Prince (musician)',
      'madonna': 'Madonna (entertainer)',
      'cher': 'Cher',
      'beck': 'Beck',
      'seal': 'Seal (musician)',
      'sting': 'Sting (musician)',
      'moby': 'Moby',
      'bjork': 'Björk',
      'enya': 'Enya',
      'adele': 'Adele',
      'sia': 'Sia (musician)',
      'lorde': 'Lorde',
      'grimes': 'Grimes (musician)',
      'banks': 'Banks (singer)',
      'lana del rey': 'Lana Del Rey',
      'lady gaga': 'Lady Gaga',
      'ariana grande': 'Ariana Grande',
      'taylor swift': 'Taylor Swift',
      'billie eilish': 'Billie Eilish',
      'dua lipa': 'Dua Lipa',
      'the weeknd': 'The Weeknd',
      'drake': 'Drake (musician)',
      'kanye west': 'Kanye West',
      'jay z': 'Jay-Z',
      'eminem': 'Eminem',
      '50 cent': '50 Cent',
      'snoop dogg': 'Snoop Dogg',
      'dr dre': 'Dr. Dre',
      'ice cube': 'Ice Cube',
      'nas': 'Nas',
      'tupac': 'Tupac Shakur',
      'biggie': 'The Notorious B.I.G.',
      'notorious big': 'The Notorious B.I.G.',
      'wu tang clan': 'Wu-Tang Clan',
      'public enemy': 'Public Enemy (band)',
      'run dmc': 'Run-DMC',
      'beastie boys': 'Beastie Boys',
      'outkast': 'Outkast',
      'black sabbath': 'Black Sabbath',
      'iron maiden': 'Iron Maiden',
      'metallica': 'Metallica',
      'megadeth': 'Megadeth',
      'slayer': 'Slayer',
      'anthrax': 'Anthrax (American band)',
      'judas priest': 'Judas Priest',
      'deep purple': 'Deep Purple',
      'led zeppelin': 'Led Zeppelin',
      'pink floyd': 'Pink Floyd',
      'the who': 'The Who',
      'the rolling stones': 'The Rolling Stones',
      'the beatles': 'The Beatles',
      'the doors': 'The Doors',
      'the kinks': 'The Kinks',
      'the clash': 'The Clash',
      'sex pistols': 'Sex Pistols',
      'ramones': 'Ramones',
      'the velvet underground': 'The Velvet Underground',
      'sonic youth': 'Sonic Youth',
      'pixies': 'Pixies',
      'radiohead': 'Radiohead',
      'oasis': 'Oasis (band)',
      'blur': 'Blur (band)',
      'pulp': 'Pulp (band)',
      'suede': 'Suede (band)',
      'stone temple pilots': 'Stone Temple Pilots',
      'pearl jam': 'Pearl Jam',
      'soundgarden': 'Soundgarden',
      'alice in chains': 'Alice in Chains',
      'red hot chili peppers': 'Red Hot Chili Peppers',
      'jane\'s addiction': 'Jane\'s Addiction',
      'smashing pumpkins': 'The Smashing Pumpkins',
      'nine inch nails': 'Nine Inch Nails',
      'marilyn manson': 'Marilyn Manson (band)',
      'white zombie': 'White Zombie (band)',
      'rob zombie': 'Rob Zombie',
      'korn': 'Korn',
      'limp bizkit': 'Limp Bizkit',
      'linkin park': 'Linkin Park',
      'system of a down': 'System of a Down',
      'rage against the machine': 'Rage Against the Machine',
      'tool': 'Tool (band)',
      'a perfect circle': 'A Perfect Circle',
      'deftones': 'Deftones',
      'incubus': 'Incubus (band)',
      'foo fighters': 'Foo Fighters',
      'green day': 'Green Day',
      'the offspring': 'The Offspring',
      'bad religion': 'Bad Religion',
      'nofx': 'NOFX',
      'rancid': 'Rancid (band)',
      'social distortion': 'Social Distortion',
      'black flag': 'Black Flag (band)',
      'minor threat': 'Minor Threat',
      'fugazi': 'Fugazi',
      'dead kennedys': 'Dead Kennedys',
      'misfits': 'Misfits (band)',
      'the cure': 'The Cure',
      'depeche mode': 'Depeche Mode',
      'new order': 'New Order (band)',
      'joy division': 'Joy Division',
      'bauhaus': 'Bauhaus (band)',
      'siouxsie and the banshees': 'Siouxsie and the Banshees',
      'the smiths': 'The Smiths',
      'morrissey': 'Morrissey',
      'u2': 'U2',
      'r.e.m.': 'R.E.M.',
      'rem': 'R.E.M.',
      'talking heads': 'Talking Heads',
      'david bowie': 'David Bowie',
      'iggy pop': 'Iggy Pop',
      'lou reed': 'Lou Reed',
      'patti smith': 'Patti Smith',
      'television': 'Television (band)',
      'blondie': 'Blondie (band)',
      'devo': 'Devo',
      'kraftwerk': 'Kraftwerk',
      'tangerine dream': 'Tangerine Dream',
      'can': 'Can (band)',
      'neu!': 'Neu!',
      'king crimson': 'King Crimson',
      'jethro tull': 'Jethro Tull (band)',
      'emerson lake and palmer': 'Emerson, Lake & Palmer',
      'the moody blues': 'The Moody Blues',
      'procol harum': 'Procol Harum',
      'van der graaf generator': 'Van der Graaf Generator',
      'gentle giant': 'Gentle Giant',
      'camel': 'Camel (band)',
      'hawkwind': 'Hawkwind',
      'space': 'Space (English band)',
      'coldplay': 'Coldplay',
      'muse': 'Muse (band)',
      'arctic monkeys': 'Arctic Monkeys',
      'kasabian': 'Kasabian',
      'the strokes': 'The Strokes',
      'the white stripes': 'The White Stripes',
      'the black keys': 'The Black Keys',
      'kings of leon': 'Kings of Leon',
      'vampire weekend': 'Vampire Weekend',
      'mgmt': 'MGMT',
      'tame impala': 'Tame Impala',
      'foster the people': 'Foster the People',
      'imagine dragons': 'Imagine Dragons',
      'onerepublic': 'OneRepublic',
      'maroon 5': 'Maroon 5',
      'the killers': 'The Killers',
      'franz ferdinand': 'Franz Ferdinand (band)',
      'interpol': 'Interpol (band)',
      'the national': 'The National (band)',
      'arcade fire': 'Arcade Fire',
      'modest mouse': 'Modest Mouse',
      'death cab for cutie': 'Death Cab for Cutie',
      'the shins': 'The Shins',
      'belle and sebastian': 'Belle and Sebastian',
      'sufjan stevens': 'Sufjan Stevens',
      'bon iver': 'Bon Iver',
      'fleet foxes': 'Fleet Foxes',
      'animal collective': 'Animal Collective',
      'of montreal': 'Of Montreal',
      'neutral milk hotel': 'Neutral Milk Hotel',
      'pavement': 'Pavement (band)',
      'built to spill': 'Built to Spill',
      'dinosaur jr': 'Dinosaur Jr.',
      'my bloody valentine': 'My Bloody Valentine (band)',
      'slowdive': 'Slowdive',
      'ride': 'Ride (band)',
      'lush': 'Lush (band)',
      'cocteau twins': 'Cocteau Twins',
      'this mortal coil': 'This Mortal Coil',
      'dead can dance': 'Dead Can Dance',
      'sisters of mercy': 'The Sisters of Mercy',
      'christian death': 'Christian Death',
      '45 grave': '45 Grave',
      'alien sex fiend': 'Alien Sex Fiend',
      'specimen': 'Specimen (band)',
      'london after midnight': 'London After Midnight (band)',
      'rozz williams': 'Rozz Williams',
      'drab majesty': 'Drab Majesty',
      'lebanon hanover': 'Lebanon Hanover',
      'ritual howls': 'Ritual Howls',
      'twin tribes': 'Twin Tribes'
    };
    
    // 检查是否需要消歧义
    if (disambiguationMap[name]) {
      return disambiguationMap[name];
    }
    
    // 如果没有找到消歧义，返回原始名称
    return artistName;
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

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
      
      <div className="relative flex items-center bg-gray-100 rounded-full px-4 py-2 w-full max-w-md mx-4">
        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-gray-500 mr-2" viewBox="0 0 20 20" fill="currentColor">
          <path fillRule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clipRule="evenodd" />
        </svg>
        <input 
          type="text" 
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="输入艺术家名称，如 'nirvana', 'radiohead'..." 
          className="bg-transparent outline-none flex-1 text-gray-800 placeholder-gray-400"
          aria-label="Search for artists"
        />
        <button
          onClick={handleSearch}
          disabled={!searchQuery.trim() || isSearching}
          className={`ml-2 p-1 transition-colors ${
            !searchQuery.trim() 
              ? 'text-gray-300 cursor-not-allowed' 
              : isSearching 
                ? 'text-blue-500' 
                : 'text-gray-500 hover:text-blue-600 cursor-pointer'
          }`}
          aria-label="Search"
          title={!searchQuery.trim() ? '请先输入艺术家名称' : '搜索艺术家'}
        >
          {isSearching ? (
            <div className="animate-spin h-4 w-4 border-2 border-blue-500 border-t-transparent rounded-full"></div>
          ) : (
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          )}
        </button>
        
        {/* 搜索提示 */}
        {searchQuery.trim() && (
          <div className="absolute top-full left-0 right-0 mt-1 bg-white rounded-lg shadow-lg border border-gray-200 z-50">
            <div className="p-3 text-sm text-gray-600">
              <div className="flex items-center">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-2 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                按 Enter 或点击搜索按钮来查找 "{searchQuery}"
              </div>
            </div>
          </div>
        )}
      </div>
      
      <div className="flex items-center gap-4">
        <button className="text-gray-700 hover:text-gray-900" aria-label="User profile">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
        </button>
        <button className="text-gray-700 hover:text-gray-900" aria-label="Favorites">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
          </svg>
        </button>
      </div>
    </header>
  );
} 