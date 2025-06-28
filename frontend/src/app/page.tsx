'use client';

import { useState, useEffect, useRef } from 'react';
import ArtistModal from '../components/ArtistModal';

// 艺术家数据类型定义
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

// 舞台数据类型定义
interface Stage {
  id: string;
  name: string;
  color: string;
  decorationColor: string;
  artists: string[];
  position: {
    top?: string;
    bottom?: string;
    left?: string;
    right?: string;
    transform: string;
  };
}

// 搜索结果类型定义
interface SearchResult {
  type: string;
  name: string;
}

export default function Home() {
  // 状态管理
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [showResults, setShowResults] = useState(false);
  const [selectedArtist, setSelectedArtist] = useState<Artist | null>(null);
  const [showArtistModal, setShowArtistModal] = useState(false);
  
  // Canvas引用
  const canvasRef = useRef<HTMLCanvasElement>(null);

  // 舞台数据
  const stages: Stage[] = [
    {
      id: 'stage1',
      name: 'GREEN STAGE',
      color: '#209e45',
      decorationColor: '#209e45',
      position: { top: '15%', left: '40%', transform: 'rotate(2deg)' },
      artists: [
        'FRED AGAIN..', 'VULFPECK', 'VAMPIRE WEEKEND', 'Vaundy', '山下達郎',
        'RADWIMPS', 'HYUKOH & SUNSET ROLLERCOASTER', 'JAMES BLAKE', 'LITTLE SIMZ',
        'BRAHMAN', 'STUTS (Band Set)', 'Creepy Nuts', 'ROUTE 17 Rock\'n\'Roll ORCHESTRA',
        '君島大空 合奏形態', '森山直太朗', 'US', 'CA7RIEL & PACO AMOROSO', 'PIPERS (Red Hot Chilli Pipers)'
      ]
    },
    {
      id: 'stage2',
      name: 'PLANET GROOVE',
      color: '#4ecdc4',
      decorationColor: '#4ecdc4',
      position: { top: '5%', left: '10%', transform: 'rotate(-3deg)' },
      artists: [
        '坂本慎太郎', 'KIASMOS', 'Joy (Anonymous)', 'HIROKO YAMAMURA', 'CONFIDENCE MAN',
        'NIGHT TEMPO', 'JANE REMOVER', 'JYOTY', '勢喜遊 & Yohji Igarashi', 'Ovall',
        'Nujabes Metaphorical Ensemble', 'ATSUO THE PINEAPPLE DONKEY', 'パソコン音楽クラブ'
      ]
    },
    {
      id: 'stage3',
      name: 'WHITE STAGE',
      color: '#000000',
      decorationColor: '#9b5de5',
      position: { bottom: '10%', left: '20%', transform: 'rotate(1deg)' },
      artists: [
        'Suchmos', 'FOUR TET', 'HAIM', 'OK GO', 'BARRY CAN\'T SWIM', '羊文学',
        'MIYAVI', 'JJJ', 'ROYEL OTIS', 'MDOU MOCTAR', 'FAYE WEBSTER',
        '佐野元春 & THE COYOTE BAND', 'ECCA VANDAL', 'BALMING TIGER', 'SILICA GEL',
        'おとぼけビ～パ～', 'FERMIN MUGURUZA', 'MONO NO AWARE'
      ]
    },
    {
      id: 'stage4',
      name: 'FIELD OF HEAVEN',
      color: '#8ac926',
      decorationColor: '#8ac926',
      position: { bottom: '15%', right: '25%', transform: 'rotate(-2deg)' },
      artists: [
        'EZRA COLLECTIVE', 'EGO-WRAPPIN\'', 'GALACTIC Featuring Jelly Joseph', 'MAYA DELILAH',
        'AFRICAN HEAD CHARGE', 'ROBERT RANDOLPH', 'PARLOR GREENS', 'THE SKA FLAMES',
        'JAKE SHIMABUKURO BAND', 'ANSWER TO REMEMBER', '踊ってばかりの国',
        'GRACE BOWERS & THE HODGE PODGE', 'KIRINJI', 'THE PANTURAS',
        '吾妻光良 & The Swinging Boppers', 'トリプルファイヤー', 'mei ehara', 'She Her Her Hers'
      ]
    },
    {
      id: 'stage5',
      name: 'RED MARQUEE',
      color: '#ff7b00',
      decorationColor: '#ff7b00',
      position: { top: '10%', right: '10%', transform: 'rotate(-1deg)' },
      artists: [
        'TYCHO', 'サンボマスター', 'THE HIVES', 'PERFUME GENIUS', 'GINGER ROOT',
        'kanekoayano', '青葉市子', 'NEWDAD', 'ENGLISH TEACHER', 'MARCIN',
        'YHWH NAILGUN', 'まらしぃ', 'TOMOO', '離婚伝説', 'MEI SEMONES',
        'kurayamisaka (Selected by ROOKIE A GO - GO)', 'joOji', 'T字路s', 'downy', 'DYGL'
      ]
    }
  ];

  // 搜索数据
  const searchData: SearchResult[] = [
    ...stages.map(stage => ({ type: '舞台', name: stage.name })),
    ...stages.flatMap(stage => 
      stage.artists.map(artist => ({ type: '艺术家', name: artist }))
    )
  ];

  // 创建艺术家对象的辅助函数
  const createArtistObject = (artistName: string): Artist => {
    return {
      id: artistName.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, ''),
      name: artistName,
      description: `${artistName} 是一位在 Fuji Rock Festival 2025 上表演的艺术家。`,
      spotify_id: '', // 将通过 API 获取
      genres: [], // 将通过 API 获取
      wiki_data: null,
      wiki_extract: '', // 将通过 API 获取
      is_fuji_rock_artist: true,
      image_url: '', // 将通过 API 获取
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };
  };

  // Canvas波浪动画
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // 设置Canvas尺寸
    const setCanvasSize = () => {
      const container = canvas.parentElement;
      if (container) {
        canvas.width = container.clientWidth;
        canvas.height = container.clientHeight;
      }
    };

    setCanvasSize();
    window.addEventListener('resize', setCanvasSize);

    // 清除Canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = 'transparent';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // 波浪参数
    const waves: Array<{
      y: number;
      length: number;
      amplitude: number;
      frequency: number;
      phase: number;
    }> = [];
    
    const waveCount = 5;
    const baseAmplitude = canvas.height / 10;

    // 创建波浪
    for (let i = 0; i < waveCount; i++) {
      waves.push({
        y: canvas.height / 2,
        length: Math.random() * 1000 + 500,
        amplitude: baseAmplitude * (Math.random() * 0.5 + 0.5),
        frequency: Math.random() * 0.02 + 0.01,
        phase: Math.random() * Math.PI * 2
      });
    }

    let time = 0;

    // 动画函数
    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      waves.forEach((wave, index) => {
        ctx.beginPath();
        ctx.strokeStyle = `rgba(${155 + index * 20}, ${249 - index * 30}, ${255 - index * 10}, ${0.6 - index * 0.1})`;
        ctx.lineWidth = 3 - index * 0.3;

        for (let x = 0; x < canvas.width; x += 2) {
          const y = wave.y + Math.sin((x * wave.frequency) + (time * 0.2) + wave.phase) * wave.amplitude;
          if (x === 0) {
            ctx.moveTo(x, y);
          } else {
            ctx.lineTo(x, y);
          }
        }

        ctx.stroke();
      });

      time++;
      requestAnimationFrame(animate);
    };

    animate();

    return () => {
      window.removeEventListener('resize', setCanvasSize);
    };
  }, []);

  // 搜索功能
  const performSearch = (query: string) => {
    if (!query.trim()) {
      setSearchResults([]);
      setShowResults(false);
      return;
    }

    const results = searchData.filter(item => 
      item.name.toLowerCase().includes(query.toLowerCase())
    );
    setSearchResults(results);
    setShowResults(true);
  };

  const handleSearchInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const query = e.target.value;
    setSearchQuery(query);
    performSearch(query);
  };

  const handleResultClick = (result: SearchResult) => {
    if (result.type === '艺术家') {
      handleArtistClick(result.name);
    }
    setShowResults(false);
    setSearchQuery('');
  };

  // 处理艺术家点击 - 使用新的ArtistModal
  const handleArtistClick = (artistName: string) => {
    console.log('🎵 点击艺术家:', artistName);
    const artistObject = createArtistObject(artistName);
    setSelectedArtist(artistObject);
    setShowArtistModal(true);
  };

  // 关闭艺术家模态框
  const closeArtistModal = () => {
    setShowArtistModal(false);
    setSelectedArtist(null);
  };

  // 滚动到第二屏
  const scrollToSecondScreen = () => {
    const secondScreen = document.getElementById('second-screen');
    if (secondScreen) {
      const duration = 1200;
      const startPosition = window.pageYOffset;
      const targetPosition = secondScreen.offsetTop;
      const startTime = performance.now();

      const scrollAnimation = (currentTime: number) => {
        const timeElapsed = currentTime - startTime;
        const progress = Math.min(timeElapsed / duration, 1);
        const easeProgress = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);
        
        // 更新进度条
        const progressBar = document.querySelector('.progress-bar') as HTMLElement;
        if (progressBar) {
          progressBar.style.transform = `scaleX(${progress})`;
        }
        
        // 滚动
        window.scrollTo(0, startPosition + (targetPosition - startPosition) * easeProgress);
        if (progress < 1) requestAnimationFrame(scrollAnimation);
      };

      requestAnimationFrame(scrollAnimation);
    }
  };

  // 点击外部关闭搜索结果
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const searchContainer = document.querySelector('.search-container');
      if (searchContainer && !searchContainer.contains(event.target as Node)) {
        setShowResults(false);
      }
    };

    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, []);

  // 滚动进度条
  useEffect(() => {
    const handleScroll = () => {
      const scrollTop = window.pageYOffset;
      const docHeight = document.documentElement.scrollHeight - window.innerHeight;
      const scrollPercent = scrollTop / docHeight;
      const progressBar = document.querySelector('.progress-bar') as HTMLElement;
      if (progressBar) {
        progressBar.style.transform = `scaleX(${scrollPercent})`;
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <div className="min-h-screen">
      {/* 进度条 */}
      <div className="progress-bar"></div>
      
      {/* 顶部导航栏 */}
      <header className="fixed top-0 w-full z-50 px-8 py-3 flex justify-between items-center backdrop-blur-md bg-white/10 border-b border-white/20 text-lg font-bold text-white">
        {/* 左上 logo */}
        <div className="flex gap-3">
          <span>🎪</span>
          <span>🎧</span>
          <span>🌈</span>
          <span>FujiRock</span>
        </div>

        {/* 右上功能 */}
        <div className="flex gap-5 cursor-pointer">
          <span title="收藏">⭐️</span>
          <span title="登录">🔐</span>
        </div>
      </header>

      {/* 第一屏 */}
      <section id="first-screen">
        <div className="trapezoid-bg"></div>
        <div className="container">
          <canvas ref={canvasRef} id="waveCanvas"></canvas>

          {/* 花朵装饰 - 上半部分 */}
          <div className="flower-decoration absolute top-0 left-0 w-full h-[60vh] pointer-events-none z-[4]">
            {/* 第一排 */}
            <div className="flower absolute" style={{ top: '1%', left: '5%' }}>
              <img src="/flowers/flower1.png" alt="" />
            </div>
            <div className="flower absolute" style={{ top: '3%', left: '20%' }}>
              <img src="/flowers/flower2.png" alt="" />
            </div>
            <div className="flower absolute" style={{ top: '2%', left: '35%' }}>
              <img src="/flowers/flower3.png" alt="" />
            </div>
            <div className="flower absolute" style={{ top: '3%', left: '50%' }}>
              <img src="/flowers/flower4.png" alt="" />
            </div>
            <div className="flower absolute" style={{ top: '2%', left: '65%' }}>
              <img src="/flowers/flower5.png" alt="" />
            </div>
            <div className="flower absolute" style={{ top: '3%', left: '80%' }}>
              <img src="/flowers/flower6.png" alt="" />
            </div>
          
            {/* 第二排 */}
            <div className="flower absolute" style={{ top: '12%', left: '10%' }}>
              <img src="/flowers/flower7.png" alt="" />
            </div>
            <div className="flower absolute" style={{ top: '15%', left: '30%' }}>
              <img src="/flowers/flower8.png" alt="" />
            </div>
            <div className="flower absolute" style={{ top: '18%', left: '50%' }}>
              <img src="/flowers/flower9.png" alt="" />
            </div>
            <div className="flower absolute" style={{ top: '16%', left: '70%' }}>
              <img src="/flowers/flower10.png" alt="" />
            </div>
            <div className="flower absolute" style={{ top: '20%', left: '85%' }}>
              <img src="/flowers/flower11.png" alt="" />
            </div>
          
            {/* 第三排 */}
            <div className="flower absolute" style={{ top: '22%', left: '15%' }}>
              <img src="/flowers/flower12.png" alt="" />
            </div>
            <div className="flower absolute" style={{ top: '24%', left: '40%' }}>
              <img src="/flowers/flower3.png" alt="" />
            </div>
            <div className="flower absolute" style={{ top: '26%', left: '60%' }}>
              <img src="/flowers/flower2.png" alt="" />
            </div>
            <div className="flower absolute" style={{ top: '23%', left: '78%' }}>
              <img src="/flowers/flower1.png" alt="" />
            </div>
                   
            {/* 第四排 */}
            <div className="flower absolute" style={{ top: '45%', left: '85%' }}>
              <img src="/flowers/flower12.png" alt="" />
            </div>
            
            <div className="flower absolute" style={{ top: '70%', left: '95%' }}>
              <img src="/flowers/flower2.png" alt="" />
            </div>
            <div className="flower absolute" style={{ top: '7%', left: '95%' }}>
              <img src="/flowers/flower2.png" alt="" />
            </div>
                    
          </div>

          {/* 花朵装饰 - 下半部分 */}
          <div className="flower-decoration absolute bottom-[80%] left-0 w-full h-screen pointer-events-none z-[4]">
            <div className="flower absolute" style={{ top: '82%', left: '10%' }}>
              <img src="/flowers/flower7.png" alt="" />
            </div>
            <div className="flower absolute" style={{ top: '85%', left: '30%' }}>
              <img src="/flowers/flower8.png" alt="" />
            </div>
            <div className="flower absolute" style={{ top: '88%', left: '50%' }}>
              <img src="/flowers/flower9.png" alt="" />
            </div>
            <div className="flower absolute" style={{ top: '86%', left: '70%' }}>
              <img src="/flowers/flower10.png" alt="" />
            </div>
            <div className="flower absolute" style={{ top: '90%', left: '85%' }}>
              <img src="/flowers/flower11.png" alt="" />
            </div>
            
            <div className="flower absolute" style={{ top: '82%', left: '15%' }}>
              <img src="/flowers/flower3.png" alt="" />
            </div>
            <div className="flower absolute" style={{ top: '85%', left: '38%' }}>
              <img src="/flowers/flower5.png" alt="" />
            </div>
            <div className="flower absolute" style={{ top: '88%', left: '45%' }}>
              <img src="/flowers/flower7.png" alt="" />
            </div>
            <div className="flower absolute" style={{ top: '86%', left: '78%' }}>
              <img src="/flowers/flower12.png" alt="" />
            </div>
            <div className="flower absolute" style={{ top: '90%', left: '95%' }}>
              <img src="/flowers/flower8.png" alt="" />
            </div>
          </div>

          {/* 主内容 */}
          <div className="content">
            <p>get ready for</p>
            <h2>😈fujirock 2025</h2>
          </div>
          
          {/* 搜索框 */}
          <div className="search-container">
            <div className="search-box">
              <input 
                type="text" 
                id="searchInput"
                value={searchQuery}
                onChange={handleSearchInput}
                placeholder="search artist"
              />
              <button 
                id="searchButton"
                onClick={() => performSearch(searchQuery)}
              >
                🔍
              </button>
            </div>
            
            {/* 搜索结果 */}
            {showResults && (
              <div className="search-results active">
                {searchResults.length === 0 ? (
                  <div className="result-item">
                    <p>未找到相关结果</p>
                  </div>
                ) : (
                  searchResults.map((result, index) => (
                    <div 
                      key={index}
                      className="result-item"
                      onClick={() => handleResultClick(result)}
                    >
                      <div className="result-title">{result.name}</div>
                      <div className="result-type">{result.type}</div>
                    </div>
                  ))
                )}
              </div>
            )}
          </div>
        </div>
        
        {/* 滚动指示器 */}
        <div className="scroll-down" onClick={scrollToSecondScreen}>
          <div className="arrow"></div>
        </div>
      </section>
      
      {/* 第二屏 */}
      <section id="second-screen">
        <div className="second-content">
          <header>
            <h1>FUJI ROCK FESTIVAL '25</h1>
          </header>
        
          <div className="stages-container">
            {stages.map((stage) => (
              <div 
                key={stage.id}
                className="stage-card"
                id={stage.id}
                style={{
                  ...stage.position,
                  borderColor: stage.color
                }}
              >
                <div className="stage-header">
                  <h2 style={{ color: stage.color }}>{stage.name}</h2>
                  <div 
                    className="stage-decoration"
                    style={{ backgroundColor: stage.decorationColor }}
                  ></div>
                </div>
                <div className="artists-container">
                  {stage.artists.map((artist, index) => (
                    <div 
                      key={index}
                      className="artist-item"
                      onClick={() => handleArtistClick(artist)}
                    >
                      {artist}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 使用新的 ArtistModal 组件 */}
      <ArtistModal
        artist={selectedArtist}
        isOpen={showArtistModal}
        onClose={closeArtistModal}
      />
    </div>
  );
}
