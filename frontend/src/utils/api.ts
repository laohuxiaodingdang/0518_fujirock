// API 基础配置 - 直接连接后端服务器
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
// const API_V1_PREFIX = '/api/v1';
const API_V1_PREFIX = '';

// 完整的 API URL
const FULL_API_URL = `${API_BASE_URL}${API_V1_PREFIX}`;

// API 响应类型定义
export interface WikipediaArtistResponse {
  success: boolean;
  data: {
    title: string;
    extract: string;
    thumbnail?: {
      source: string;
      width: number;
      height: number;
    };
    categories: string[];
    references: Array<{
      title: string;
      url: string;
    }>;
  };
}

// Spotify API 响应类型
export interface SpotifyArtistResponse {
  success: boolean;
  data: {
    id: string;
    name: string;
    popularity: number;
    followers: {
      total: number;
    };
    genres: string[];
    images: Array<{
      url: string;
      height: number;
      width: number;
    }>;
    external_urls: {
      spotify: string;
    };
  };
}

// Spotify 热门歌曲响应类型
export interface SpotifyTopTracksResponse {
  success: boolean;
  data: {
    tracks: Array<{
      id: string;
      name: string;
      duration_ms: number;
      preview_url: string | null;
      album: {
        name: string;
        images: Array<{
          url: string;
          height: number;
          width: number;
        }>;
      };
      external_urls: {
        spotify: string;
      };
    }>;
  };
}

// AI 描述生成响应类型
export interface AIDescriptionResponse {
  success: boolean;
  data: {
    original_content: string;
    sassy_description: string;
    style_metrics: {
      humor_level: number;
      sarcasm_level: number;
      fact_accuracy: number;
    };
    generated_at: string;
    model_used: string;
    tokens_used: number;
  };
}

// 错误响应类型
export interface ApiError {
  success: false;
  error: string;
  message: string;
}

// 通用API请求函数
const apiRequest = async <T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> => {
  const url = `${FULL_API_URL}${endpoint}`;
  
  const defaultOptions: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, defaultOptions);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
};

// 获取艺术家数据库信息（包含 ai_description）
export const getArtistDatabase = async (
  artistName: string
): Promise<any> => {
  console.log('🔍 getArtistDatabase called with:', artistName);
  
  if (!artistName.trim()) {
    throw new Error('Artist name is required');
  }

  // 🔧 直接调用后端API，不通过前端路由
  const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  const encodedArtistName = encodeURIComponent(artistName.trim());
  const url = `${backendUrl}/api/database/artists/by-name/${encodedArtistName}`;
  
  console.log('🌐 直接调用后端API:', url);
  
  try {
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    console.log('📊 后端返回数据:', data.success ? '成功' : '失败');
    
    if (data.success && data.data?.ai_description) {
      console.log('📝 包含AI描述:', !!data.data.ai_description);
    }
    
    return data;
  } catch (error) {
    console.error('❌ 直接调用后端API失败:', error);
    throw error;
  }
};

// 获取艺术家Wikipedia信息
export const getArtistWikipedia = async (
  artistName: string,
  language: string = "zh"
): Promise<WikipediaArtistResponse> => {
  if (!artistName.trim()) {
    throw new Error('Artist name is required');
  }

  const encodedArtistName = encodeURIComponent(artistName.trim());
  return apiRequest<WikipediaArtistResponse>(
    `/wikipedia/artists/${encodedArtistName}?language=${language}`
  );
};

// 获取艺术家Spotify信息
export const getArtistSpotify = async (
  artistName: string
): Promise<SpotifyArtistResponse> => {
  if (!artistName.trim()) {
    throw new Error('Artist name is required');
  }

  const encodedArtistName = encodeURIComponent(artistName.trim());
  return apiRequest<SpotifyArtistResponse>(
    `/api/spotify/artist-by-name/${encodedArtistName}`
  );
};

// 获取艺术家热门歌曲
export const getArtistTopTracks = async (
  artistName: string
): Promise<SpotifyTopTracksResponse> => {
  if (!artistName.trim()) {
    throw new Error('Artist name is required');
  }

  const encodedArtistName = encodeURIComponent(artistName.trim());
  return apiRequest<SpotifyTopTracksResponse>(
    `/api/spotify/artist-by-name/${encodedArtistName}/top-tracks`
  );
};

// 获取艺术家完整信息（组合多个API）
export const getArtistFullProfile = async (artistName: string) => {
  try {
    // 并行调用多个API
    const [wikipediaData, spotifyData, topTracksData] = await Promise.allSettled([
      getArtistWikipedia(artistName),
      getArtistSpotify(artistName),
      getArtistTopTracks(artistName),
    ]);

    // 处理Wikipedia数据
    const wikipedia = wikipediaData.status === 'fulfilled' ? wikipediaData.value : null;
    
    // 处理Spotify数据
    const spotify = spotifyData.status === 'fulfilled' ? spotifyData.value : null;
    
    // 处理热门歌曲数据
    const topTracks = topTracksData.status === 'fulfilled' ? topTracksData.value : null;

    return {
      wikipedia,
      spotify,
      topTracks,
      aiDescription: null, // 不再生成AI描述
      errors: {
        wikipedia: wikipediaData.status === 'rejected' ? wikipediaData.reason : null,
        spotify: spotifyData.status === 'rejected' ? spotifyData.reason : null,
        topTracks: topTracksData.status === 'rejected' ? topTracksData.reason : null,
      }
    };
  } catch (error) {
    console.error('Failed to get artist full profile:', error);
    throw error;
  }
};
